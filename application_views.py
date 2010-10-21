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
from itools.uri import get_reference, get_uri_path
from itools.web import INFO, ERROR, BaseView

# Import from ikaaro
from ikaaro.access import is_admin
from ikaaro.autoform import FileWidget, TextWidget
from ikaaro.datatypes import FileDataType
from ikaaro.file import ODS
from ikaaro.folder_views import Folder_BrowseContent, GoToSpecificDocument
from ikaaro.messages import MSG_PASSWORD_MISMATCH
from ikaaro.resource_views import DBResource_Edit
from ikaaro.views import IconsView
from ikaaro.views_new import NewInstance
from ikaaro.workflow import get_workflow_preview

# Import from iscrib
from base_views import LoginView
from form import Form
from formpage import FormPage
from workflow import WorkflowState


MSG_ERR_PAGE_NAME = ERROR(u'Page names must be in the form "C Title..."')
MSG_EXPORT_ERROR = ERROR(u"Export Failed. Please contact the administrator.")

MAILTO_SUBJECT = MSG(u'{workgroup_title}, form "{application_title}"')
MAILTO_BODY = MSG(u'Please fill in the form "{application_title}" available '
        u'here:\r\n'
        u'<{application_url}>.\r\n')


class Application_NewInstance(NewInstance):
    schema = merge_dicts(NewInstance.schema,
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
        for name, cls in [('controls', child.controls_class),
                          ('schema', child.schema_class)]:
            table = tables.next()
            table.rstrip(aggressive=True)
            # Remove header
            table.delete_row(0)
            try:
                child.make_resource(name, cls, title={'en': table.get_name()},
                        # cls va transformer le CSV en table
                        body=table.to_csv())
            except ValueError, exception:
                context.commit = False
                context.message = ERROR(unicode(exception))
                return
        # Pages
        for table in tables:
            table.rstrip(aggressive=True)
            title = table.get_name()
            if title[1] != u" ":
                context.commit = False
                context.message = MSG_ERR_PAGE_NAME
                return
            page_number, _ = title.split(u" ", 1)
            name = 'page' + page_number.lower().encode()
            body = table.to_csv()
            try:
                child.make_resource(name, FormPage, title={'en': title},
                        body=body)
            except Exception, exception:
                context.commit = False
                context.message = ERROR(unicode(exception))
                return
        # Initial form
        child.make_resource(child.default_form, Form,
                title={'en': u"Test Form"})
        return goto



class Application_Menu(IconsView):
    items = [{'icon': '/ui/iscrib/images/register48.png',
              'title': MSG(u"Register Users"),
              'description': None,
              'url': ';register'},
             {'icon': '/ui/iscrib/images/export48.png',
              'title': MSG(u"Export Collected Data"),
              'description': None,
              'url': ';export'},
             {'icon': '/ui/iscrib/images/form48.png',
              'title': MSG(u"Show Test Form"),
              'description': None,
              'url': ';show'}]


    def get_namespace(self, resource, context):
        items = self.items
        max_users = resource.get_property('max_users')
        allowed_users = resource.get_allowed_users()
        if not allowed_users:
            items = items[1:]
        return {'batch': None, 'items': items}



class Application_View(Folder_BrowseContent):
    access = 'is_allowed_to_edit'
    title = MSG(u"View")
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
        namespace = super(Application_View, self).get_namespace( resource,
                context)
        namespace['menu'] = Application_Menu().GET(resource, context)
        namespace['n_forms'] = resource.get_n_forms()
        namespace['max_users'] = resource.get_property('max_users')
        return namespace



class Application_Export(BaseView):
    access = 'is_allowed_to_edit'
    title = MSG(u"Export Collected Data")


    def GET(self, resource, context, encoding='cp1252'):
        csv = CSVFile()
        header = ["Form", "User", "E-mail", "State"]
        handler = resource.get_resource('schema').handler
        schema, pages = handler.get_schema_pages()
        for name in sorted(schema):
            header.append(name)
        csv.add_row(header)
        users = resource.get_resource('/users')

        try:
            for form in resource.get_forms():
                user = users.get_resource(form.name, soft=True)
                if user:
                    email = user.get_property('email')
                    user = user.get_title().encode(encoding)
                else:
                    email = ""
                    user = form.name
                state = WorkflowState.get_value(form.get_workflow_state())
                state = state.gettext().encode(encoding)
                row = [form.name, user, email, state]
                handler = form.handler
                for name, datatype in sorted(schema.iteritems()):
                    value = handler.get_value(name, schema)
                    try:
                        value = datatype.encode(value, encoding)
                    except TypeError:
                        value = datatype.encode(value)
                    row.append(value)
                csv.add_row(row)

            csv = csv.to_str(separator=';')
            if type(csv) is not str:
                raise TypeError, str(type(csv))
        except Exception:
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
            if not email:
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
            password=String(mandatory=True),
            password2=String)


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
        password = form['password']
        password2 = form['password2']
        if password != password2:
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
    title = MSG(u"Show Form")


    def get_form_name(self, user, resource):
        ac = resource.get_access_control()
        if ac.is_allowed_to_edit(user, resource):
            return resource.default_form
        if resource.get_resource(user.name, soft=True) is not None:
            return user.name
        return None


    def get_specific_document(self, resource, context):
        return self.get_form_name(context.user, resource)
