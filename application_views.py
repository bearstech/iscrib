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
from itools.database import PhraseQuery, TextQuery, StartQuery, AndQuery
from itools.database import OrQuery, NotQuery
from itools.datatypes import Integer, Unicode, Email, String
from itools.gettext import MSG
from itools.log import log_error
from itools.stl import stl
from itools.uri import get_reference, get_uri_path
from itools.web import INFO, ERROR, BaseView, FormError, STLForm

# Import from ikaaro
from ikaaro.access import is_admin
from ikaaro.autoform import FileWidget, TextWidget, SelectWidget
from ikaaro.buttons import BrowseButton
from ikaaro.datatypes import FileDataType
from ikaaro.file import ODS
from ikaaro.folder_views import Folder_BrowseContent, GoToSpecificDocument
from ikaaro.messages import MSG_PASSWORD_MISMATCH
from ikaaro.resource_views import DBResource_Edit
from ikaaro.views import SearchForm
from ikaaro.views_new import NewInstance
from ikaaro.workflow import get_workflow_preview

# Import from iscrib
from base_views import LoginView, IconsView
from form import Form
from formpage import FormPage
from utils import force_encode
from workflow import WorkflowState, NOT_REGISTERED, EMPTY, PENDING, FINISHED


MSG_ERR_PAGE_NAME = ERROR(u'In the "${name}" sheet, page "${page}" is not '
        u'related to any variable in the schema.')
MSG_EXPORT_ERROR = ERROR(u"Export Failed. Please contact the administrator.")
MSG_NO_DATA = ERROR(u"No data to collect for now.")
MSG_NO_MORE_ALLOWED = ERROR(u"You have reached the maximum allowed users. "
        u'Contact <a href="http://www.itaapy.com/contact">Itaapy</a> for '
        u"more.", html=True)
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



def get_users_query(query, context):
    """Filter forms from users list with same name.
    """
    query = AndQuery(PhraseQuery('format', 'user'), query)
    results = context.root.search(query)
    users = (brain.name for brain in results.get_documents())
    return (PhraseQuery('name', user) for user in users)



class ExportButton(BrowseButton):
    access = 'is_allowed_to_edit'
    name = 'export'
    title = MSG(u"Export this List")



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
              title=MSG(u"Subscribe Users"),
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
        allowed_users = resource.get_allowed_users()
        if not bool(allowed_users):
            item['title'] = MSG_NO_MORE_ALLOWED
            return False
        return True


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

    schema = {}

    # Search Form
    search_schema = merge_dicts(Folder_BrowseContent.search_schema,
            SearchForm.search_schema,
            search_state=String)
    search_fields = []
    search_template = '/ui/iscrib/application/search.xml'

    # Table
    table_columns = [
            ('name', MSG(u"Form")),
            ('state', MSG(u"State")),
            ('mtime', MSG(u"Last Modified")),
            ('firstname', MSG(u"First Name")),
            ('lastname', MSG(u"Last Name")),
            ('company', MSG(u"Company/Organization")),
            ('email', MSG(u"E-mail"))]
    table_actions = [ExportButton]


    def get_items(self, resource, context, *args):
        query = PhraseQuery('format', Form.class_id)
        # Filter on state
        search_state = context.query['search_state']
        if search_state:
            if search_state == NOT_REGISTERED:
                search_query = PhraseQuery('has_password', False)
                users_query = get_users_query(search_query, context)
                query = AndQuery(query, OrQuery(*users_query))
            else:
                search_query = PhraseQuery('has_password', True)
                users_query = get_users_query(search_query, context)
                state_query = PhraseQuery('workflow_state', search_state)
                query = AndQuery(query, state_query, OrQuery(*users_query))
        # Filter on user properties
        search_term = context.query['search_term'].strip()
        if search_term:
            search_query = OrQuery(
                TextQuery('firstname', search_term),
                TextQuery('lastname', search_term),
                TextQuery('company', search_term),
                StartQuery('username', search_term),
                StartQuery('email_domain', search_term))
            users_query = get_users_query(search_query, context)
            query = AndQuery(query, OrQuery(*users_query))
        # Filter out default form
        default_form_query = PhraseQuery('name', resource.default_form)
        query = AndQuery(query, NotQuery(default_form_query))
        return super(Application_View, self).get_items(resource, context,
                query, *args)


    def get_item_value(self, resource, context, item, column):
        brain, item_resource = item
        if column == 'name':
            return (brain.name, context.get_link(item_resource))
        elif column in ('state', 'firstname', 'lastname', 'company',
                'email'):
            user = context.root.get_user(brain.name)
            if column == 'state':
                if user is not None and not user.get_property('password'):
                    return WorkflowState.get_value(NOT_REGISTERED)
                return (get_workflow_preview(item_resource, context),
                        '{0}/;send'.format(context.get_link(item_resource)))
            elif column in ('firstname', 'lastname', 'company'):
                if user is None:
                    return u""
                return user.get_property(column)
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
        return super(Application_View, self).get_item_value(resource,
                context, item, column)



    def get_key_sorted_by_name(self, resource, context, item):
        return int(item.name)


    def get_key_sorted_by_state(self, resource, context, item):
        user = context.root.get_user(item.name)
        if user is not None and not user.get_property('password'):
            state = NOT_REGISTERED
        else:
            state = item.workflow_state
        value = WorkflowState.get_value(state)
        return value.gettext().lower()


    def get_key_sorted_by_user(self, resource, context, item):
        user = context.root.get_user(item.name)
        if user is None:
            return None
        return user.get_title().lower()


    def get_key_sorted_by_email(self, resource, context, item):
        user = context.root.get_user(item.name)
        if user is None:
            return None
        return user.get_property('email').lower()


    def get_search_namespace(self, resource, context):
        namespace = SearchForm.get_search_namespace(self, resource, context)
        namespace['state_widget'] = SelectWidget('search_state',
                datatype=WorkflowState, value=context.query['search_state'])
        return namespace


    def get_namespace(self, resource, context):
        namespace = {}
        namespace['menu'] = Application_Menu().GET(resource, context)
        namespace['n_forms'] = resource.get_n_forms()
        namespace['max_users'] = resource.get_property('max_users')

        # Search
        search_template = resource.get_resource(self.search_template)
        search_namespace = self.get_search_namespace(resource, context)
        namespace['search'] = stl(search_template, search_namespace)

        # Batch
        results = self.get_items(resource, context)
        query = context.query
        if results or query['search_state'] or query['search_term']:
            template = resource.get_resource(self.batch_template)
            batch_namespace = self.get_batch_namespace(resource, context,
                    results)
            namespace['batch'] = stl(template, batch_namespace)
        else:
            namespace['batch'] = None

        # Table
        if results:
            items = self.sort_and_batch(resource, context, results)
            template = resource.get_resource(self.table_template)
            table_namespace = self.get_table_namespace(resource, context,
                    items)
            namespace['table'] = stl(template, table_namespace)
        else:
            namespace['table'] = None

        return namespace


    def action_export(self, resource, context, form, encoding='cp1252'):
        csv = CSVFile()
        header = [title.gettext().encode(encoding)
                for column, title in self.table_columns]
        csv.add_row(header)
        results = self.get_items(resource, context)
        context.query['batch_size'] = 0
        for item in self.sort_and_batch(resource, context, results):
            row = []
            for column, title in self.table_columns:
                if column == 'state':
                    item_brain, item_resource = item
                    user = context.root.get_user(item_brain.name)
                    if (user is not None
                            and user.get_property('password') is None):
                        state = NOT_REGISTERED
                    else:
                        state = item_brain.workflow_state
                    value = WorkflowState.get_value(state)
                else:
                    value = self.get_item_value(resource, context, item,
                            column)
                if type(value) is tuple:
                    value = value[0]
                elif type(value) is MSG:
                    value = value.gettext()
                if type(value) is unicode:
                    value = value.encode(encoding)
                elif type(value) is str:
                    pass
                else:
                    raise NotImplementedError, str(type(value))
                row.append(value)
            csv.add_row(row)

        csv = csv.to_str(separator=';')
        if type(csv) is not str:
            raise TypeError, str(type(csv))

        context.set_content_type('text/comma-separated-values')
        context.set_content_disposition('attachment',
                filename="%s-users.csv" % (resource.name))

        return csv



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



class Application_Register(STLForm):
    access = 'is_allowed_to_edit'
    title = MSG(u"Subscribe Users")
    template = '/ui/iscrib/application/register.xml'

    schema = {'new_users': Unicode}

    table_columns = [
            ('user', MSG(u"User")),
            ('email', MSG(u"E-mail"))]


    def get_namespace(self, resource, context):
        namespace = super(Application_Register, self).get_namespace(resource,
                context)
        namespace['title'] = self.title
        namespace['max_users'] = resource.get_property('max_users')
        namespace['n_forms'] = resource.get_n_forms()
        namespace['allowed_users'] = resource.get_allowed_users()
        namespace['MSG_NO_MORE_ALLOWED'] = MSG_NO_MORE_ALLOWED
        namespace['new_users'] = context.get_form_value('new_users')
        namespace['registered_users'] = 0
        namespace['unconfirmed_users'] = 0
        namespace['empty_forms'] = 0
        namespace['pending_forms'] = 0
        namespace['finished_forms'] = 0
        users = resource.get_resource('/users')
        for form in resource.get_forms():
            namespace['registered_users'] += 1
            user = users.get_resource(form.name)
            if user.get_property('password') is None:
                namespace['unconfirmed_users'] += 1
            else:
                state = form.get_workflow_state()
                if state == EMPTY:
                    namespace['empty_forms'] += 1
                elif state == PENDING:
                    namespace['pending_forms'] += 1
                elif state == FINISHED:
                    namespace['finished_forms'] += 1
        namespace['url_user'] = resource.get_user_url(context)
        namespace['url_admin'] = resource.get_admin_url(context)
        return namespace


    def action(self, resource, context, form):
        new_users = form['new_users'].strip()
        users = resource.get_resource('/users')
        root = context.root
        site_root = resource.get_site_root()
        added = []
        allowed = resource.get_allowed_users()
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
            if (site_root.get_user_role(username) is None
                    # Except to top-level admins
                    and not site_root.is_admin(user, resource)):
                site_root.set_user_role(username, 'guests')
            # Add the form
            if resource.get_resource(username, soft=True) is not None:
                continue
            resource.make_resource(username, Form, title={'en': lastname})
            added.append(username)
            if len(added) == allowed:
                break

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
