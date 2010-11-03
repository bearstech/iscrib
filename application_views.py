# -*- coding: UTF-8 -*-
# Copyright (C) 2010 Hervé Cauwelier <herve@itaapy.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

# Import from the Standard Library
from cStringIO import StringIO
from email.utils import parseaddr
from urllib import quote

# Import from lpod
from lpod import ODF_SPREADSHEET
from lpod.document import odf_get_document

# Import from itools
from itools.core import merge_dicts
from itools.csv import CSVFile
from itools.database import PhraseQuery, AndQuery, NotQuery
from itools.datatypes import Integer, Unicode, Email, String
from itools.gettext import MSG
from itools.log import log_error
from itools.stl import stl
from itools.uri import get_reference, get_uri_path
from itools.web import INFO, ERROR, BaseView, FormError

# Import from ikaaro
from ikaaro.access import is_admin
from ikaaro.autoform import FileWidget, TextWidget
from ikaaro.datatypes import FileDataType
from ikaaro.file import ODS
from ikaaro.folder_views import Folder_BrowseContent, GoToSpecificDocument
from ikaaro.messages import MSG_PASSWORD_MISMATCH
from ikaaro.resource_views import DBResource_Edit
from ikaaro.views_new import NewInstance
from ikaaro.workflow import get_workflow_preview

# Import from iscrib
from base_views import LoginView, IconsView
from form import Form
from formpage import FormPage
from utils import force_encode
from workflow import WorkflowState, EMPTY


MSG_ERR_PAGE_NAME = ERROR(u'In the "${name}" sheet, page "${page}" is not '
        u'related to any variable in the schema.')
MSG_EXPORT_ERROR = ERROR(u"Export Failed. Please contact the administrator.")
MSG_NO_DATA = ERROR(u"No data to collect for now.")
MSG_NEW_APPLICATION = INFO(u'Your application is created. Now register '
        u'users.')
MSG_PASSWORD_MISSING = ERROR(u"The password is missing.")

MAILTO_SUBJECT = MSG(u'{workgroup_title}, form "{application_title}"')
MAILTO_BODY = MSG(u'Please fill in the form "{application_title}" available '
        u'here:\r\n'
        u'<{application_url}>.\r\n')


def find_title(table):
    for values in table.iter_values():
        for value in values:
            value = value.strip() if value is not None else u""
            if value.startswith(u'**'):
                continue
            elif value.startswith(u"*"):
                return value[1:].strip()
    return None



class Application_NewInstance(NewInstance):
    schema = merge_dicts(NewInstance.schema,
            title=Unicode(mandatory=True),
            file=FileDataType(mandatory=True))
    widgets = (NewInstance.widgets
            + [FileWidget('file', title=MSG(u"ODS File"))])


    def action(self, resource, context, form):
        goto = NewInstance.action(self, resource, context, form)
        child = resource.get_resource(form['name'])
        filename, mimetype, body = form['file']
        if mimetype != ODF_SPREADSHEET:
            context.message = ERROR(u"not an ODS file")
            return
        # Save file used
        ods = child.make_resource('parameters', ODS, body=body,
                filename=filename, title={'en': u"Parameters"})
        stringio = StringIO(body)
        document = odf_get_document(stringio)
        if document.get_mimetype() != ODF_SPREADSHEET:
            context.message = ERROR(u"not an ODS file")
            return
        tables = iter(document.get_body().get_tables())
        # Controls and Schema
        for name, title, cls in [
                ('controls', u"Controls", child.controls_class),
                ('schema', u"Schema", child.schema_class)]:
            table = tables.next()
            table.rstrip(aggressive=True)
            try:
                child.make_resource(name, cls, title={'en': title},
                        # cls va transformer le CSV en table
                        body=table.to_csv())
            except ValueError, exception:
                context.commit = False
                context.message = ERROR(unicode(exception))
                return
        handler = child.get_resource('schema').handler
        schema, pages = handler.get_schema_pages()
        # Pages
        for table in tables:
            table.rstrip(aggressive=True)
            name = table.get_name().split(None, 1)
            # Page number
            if len(name) == 1:
                page_number = name[0]
                title = None
            else:
                page_number, title = name
            if page_number not in pages:
                context.commit = False
                context.message = MSG_ERR_PAGE_NAME(name=name,
                        page=page_number)
                return
            # Name
            name = 'page' + page_number.lower().encode()
            # Title
            if title is None:
                # Find a "*Title"
                title = find_title(table)
                if title is None:
                    raise ValueError
                    title = u"Page {0}".format(page_number)
            try:
                child.make_resource(name, FormPage, title={'en': title},
                        body=table.to_csv())
            except ValueError, exception:
                context.commit = False
                context.message = ERROR(unicode(exception))
                return
        # Initial form
        child.make_resource(child.default_form, Form)
        return context.come_back(MSG_NEW_APPLICATION, goto)



class Application_Menu(IconsView):
    make_item = IconsView.make_item
    items = [make_item(icon='/ui/iscrib/images/register48.png',
              title=MSG(u"Register Users"),
              url=';register',
              access='is_allowed_to_register'),
             make_item(icon='/ui/iscrib/images/export48.png',
              title=MSG(u"Export Collected Data"),
              description=MSG(u"""
<div id="choose-format">
  <span><a href="#" title="Close"
    onclick="$('#choose-format').hide(); return false">X</a></span>
  <ul>
    <li>Download <a href=";export">ODS Version</a></li>
    <li>Download XLS Version (soon)</li>
  </ul>
</div>""", html=True),
              url='#',
              onclick='$("#choose-format").show(); return false',
              access='is_allowed_to_export'),
             make_item(icon='/ui/iscrib/images/form48.png',
              title=MSG(u"Show Test Form"),
              url=';show')]


    def is_allowed_to_register(self, item, resource, context):
        max_users = resource.get_property('max_users')
        allowed_users = resource.get_allowed_users()
        return bool(allowed_users)


    def is_allowed_to_export(self, item, resource, context):
        for form in resource.get_forms():
            if form.get_workflow_state() != EMPTY:
                return True
        item['title'] = MSG_NO_DATA
        return False



class Application_View(Folder_BrowseContent):
    access = 'is_allowed_to_edit'
    title = MSG(u"Manage your Data Collection Application")
    template = '/ui/iscrib/application/view.xml'
    search_template = None

    table_columns = [
            ('name', MSG(u"Form")),
            ('state', MSG(u"State")),
            ('mtime', MSG(u"Last Modified")),
            ('user', MSG(u"User")),
            ('email', MSG(u"E-mail")),
            ('registered', MSG(u"Registered"))]
    table_actions = []


    def get_items(self, resource, context, *args):
        query = AndQuery(PhraseQuery('format', Form.class_id),
                    NotQuery(PhraseQuery('name', resource.default_form)))
        return super(Application_View, self).get_items(resource, context,
                query, *args)


    def get_item_value(self, resource, context, item, column):
        brain, item_resource = item
        if column == 'name':
            return (brain.name, context.get_link(item_resource))
        elif column == 'state':
            return (get_workflow_preview(item_resource, context),
                    '{0}/;send'.format(context.get_link(item_resource)))
        if column in ('user', 'email', 'registered'):
            user = context.root.get_user(brain.name)
            if column == 'user':
                if user is None:
                    return brain.name
                return user.get_title()
            elif column == 'email':
                email = user.get_property('email')
                application_title = resource.get_title()
                subject = MAILTO_SUBJECT.gettext().format(
                        workgroup_title=resource.parent.get_title(),
                        application_title=application_title)
                subject = quote(subject.encode('utf8'))
                application_url = resource.get_user_url(context, email)
                body = MAILTO_BODY.gettext().format(
                        application_title=application_title,
                        application_url=application_url)
                body = quote(body.encode('utf8'))
                url = 'mailto:{0}?subject={1}&body={2}'.format(email,
                        subject, body)
                return (email, url)
            elif column == 'registered':
                password = user.get_property('password')
                return MSG(u"Yes") if password else MSG(u"No")
        return super(Application_View, self).get_item_value(resource,
                context, item, column)


    def get_namespace(self, resource, context):
        # Menu
        menu = Application_Menu().GET(resource, context)
        n_forms = resource.get_n_forms()
        max_users = resource.get_property('max_users')

        # Batch
        batch = None
        items = self.get_items(resource, context)
        if items and self.batch_template is not None:
            template = resource.get_resource(self.batch_template)
            namespace = self.get_batch_namespace(resource, context, items)
            batch = stl(template, namespace)

        # Table
        table = None
        if batch:
            if self.table_template is not None:
                items = self.sort_and_batch(resource, context, items)
                template = resource.get_resource(self.table_template)
                namespace = self.get_table_namespace(resource, context,
                        items)
                table = stl(template, namespace)

        return {'menu': menu, 'n_forms': n_forms, 'max_users': max_users,
                'batch': batch, 'table': table}



class Application_Export(BaseView):
    access = 'is_allowed_to_edit'
    title = MSG(u"Export Collected Data")


    def GET(self, resource, context, encoding='cp1252'):
        for form in resource.get_forms():
            state = form.get_workflow_state()
            if state != 'private':
                break
        else:
            return context.come_back(MSG_NO_DATA)

        csv = CSVFile()
        handler = resource.get_resource('schema').handler
        schema, pages = handler.get_schema_pages()
        # Main header
        header = [title.gettext().encode(encoding)
                for title in (MSG(u"Form"), MSG(u"First Name"),
                    MSG(u"Last Name"), MSG(u"E-mail"), MSG(u"State"))]
        for name in sorted(schema):
            header.append(name)
        csv.add_row(header)
        # Subheader with titles
        header = [""] * 5
        for name, datatype in sorted(schema.iteritems()):
            header.append(datatype.title.encode(encoding))
        csv.add_row(header)
        users = resource.get_resource('/users')

        try:
            for form in resource.get_forms():
                user = users.get_resource(form.name, soft=True)
                if user:
                    get_property = user.get_property
                    email = get_property('email')
                    firstname = get_property('firstname').encode(encoding)
                    lastname = get_property('lastname').encode(encoding)
                else:
                    email = ""
                    firstname = ""
                    lastname = form.name
                state = WorkflowState.get_value(form.get_workflow_state())
                state = state.gettext().encode(encoding)
                row = [form.name, firstname, lastname, email, state]
                handler = form.handler
                for name, datatype in sorted(schema.iteritems()):
                    value = handler.get_value(name, schema)
                    if datatype.multiple:
                        data = '\n'.join(value.encode(encoding) for value in
                                datatype.get_values(value))
                    else:
                        data = force_encode(value, datatype, encoding)
                    row.append(data)
                csv.add_row(row)

            csv = csv.to_str(separator=';')
            if type(csv) is not str:
                raise TypeError, str(type(csv))
        except Exception, e:
            log_error(e)
            return context.come_back(MSG_EXPORT_ERROR)

        context.set_content_type('text/comma-separated-values')
        context.set_content_disposition('attachment',
                filename="%s.csv" % (resource.name))

        return csv



class Application_Register(Application_View):
    access = 'is_allowed_to_edit'
    title = MSG(u"Register Users")
    template = '/ui/iscrib/application/register.xml'

    schema = {'new_users': Unicode}

    table_columns = [
            ('user', MSG(u"User")),
            ('email', MSG(u"E-mail"))]


    def get_namespace(self, resource, context):
        namespace = super(Application_Register, self).get_namespace(resource,
                context)
        namespace['title'] = self.title
        namespace['allowed_users'] = resource.get_allowed_users()
        namespace['new_users'] = context.get_form_value('new_users')
        namespace['url_user'] = resource.get_user_url(context)
        namespace['url_admin'] = resource.get_admin_url(context)
        return namespace


    def action(self, resource, context, form):
        new_users = form['new_users'].strip()
        users = resource.get_resource('/users')
        root = context.root
        site_root = resource.get_site_root()
        added = []
        for lineno, line in enumerate(new_users.splitlines()):
            lastname, email = parseaddr(line)
            try:
                email = email.encode('ascii')
            except UnicodeEncodeError:
                email = None
            if not email or not Email.is_valid(email):
                context.commit = False
                message = u"Unrecognized line {lineno}: {line}"
                context.message = ERROR(message, lineno=lineno+1, line=line)
                return
            if type(lastname) is str:
                lastname = unicode(lastname)
            # Is the user already known?
            user = root.get_user_from_login(email)
            if user is None:
                # Register the user
                user = users.set_user(email, None)
                user.set_property('lastname', lastname)
            username = user.name
            # Give the role "guests" to see public resources (logo, etc.)
            if site_root.get_user_role(username) is None:
                site_root.set_user_role(username, 'guests')
            # Add the form
            if resource.get_resource(username, soft=True) is not None:
                continue
            resource.make_resource(username, Form, title={'en': lastname})
            added.append(username)

        if not added:
            context.message = ERROR(u"No user added.")
            return

        context.body['new_users'] = u""

        message = u"{n} user(s) added. See below to send them the form URL."
        context.message = INFO(message, n=len(added))



class Application_Edit(DBResource_Edit):
    title = MSG(u"Rename Application")

    def _get_schema(self, resource, context):
        schema = super(Application_Edit, self)._get_schema(resource, context)
        if is_admin(context.user, resource):
            schema['max_users'] = Integer
        return schema


    def _get_widgets(self, resource, context):
        widgets = super(Application_Edit, self)._get_widgets(resource, context)
        if is_admin(context.user, resource):
            widgets.append(TextWidget('max_users',
                title=MSG(u"Maximum form users (0 = unlimited)")))
        return widgets



class Application_Login(LoginView):
    template = '/ui/iscrib/application/login.xml'
    schema = merge_dicts(LoginView.schema,
            newpass=String,
            newpass2=String)


    def _get_form(self, resource, context):
        form = super(Application_Login, self)._get_form(resource, context)
        if not (form['password'].strip() or form['newpass'].strip()):
            raise FormError, MSG_PASSWORD_MISSING
        return form


    def action_register(self, resource, context, form):
        email = form['username'].strip()
        if not Email.is_valid(email):
            message = u'The given username is not an e-mail address.'
            context.message = ERROR(message)
            return

        user = context.root.get_user_from_login(email)

        # Is allowed?
        if user is None:
            error = u"You are not allowed to register."
            context.message = ERROR(error)
            return

        # Is already registered?
        if user.get_property('password') is not None:
            message = (u"You are already registered. "
                    u"Log in using your password.")
            context.message = ERROR(message)
            return

        # Register
        password = form['newpass']
        if password != form['newpass2']:
            context.message = MSG_PASSWORD_MISMATCH
            return

        user.set_password(password)

        # Send e-mail with login
        site_uri = context.uri.resolve(';login')
        user.send_form_registration(context, email, site_uri, password)

        # Automatic login
        user.set_auth_cookie(context, password)
        context.user = user

        # Come back
        referrer = context.get_referrer()
        if referrer is None:
            goto = get_reference('./')
        else:
            path = get_uri_path(referrer)
            if path.endswith(';login'):
                goto = get_reference('./')
            else:
                goto = referrer

        return context.come_back(INFO(u"Welcome!"), goto)



class Application_RedirectToForm(GoToSpecificDocument):
    access = 'is_allowed_to_view'
    title = MSG(u"Show Test Form")


    def get_form_name(self, user, resource):
        ac = resource.get_access_control()
        if ac.is_allowed_to_edit(user, resource):
            return resource.default_form
        if resource.get_resource(user.name, soft=True) is not None:
            return user.name
        return None


    def get_specific_document(self, resource, context):
        return self.get_form_name(context.user, resource)
