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
from email.utils import parseaddr
from urllib import quote

# Import from itools
from itools.core import merge_dicts
from itools.database import PhraseQuery, TextQuery, StartQuery, AndQuery
from itools.database import OrQuery, NotQuery
from itools.datatypes import Integer, Unicode, Email, String
from itools.gettext import MSG
from itools.handlers.utils import transmap
from itools.stl import stl
from itools.uri import get_reference, get_uri_path
from itools.web import INFO, ERROR, BaseView, STLForm, get_context

# Import from ikaaro
from ikaaro.access import is_admin
from ikaaro.autoform import FileWidget, TextWidget, SelectWidget, file_widget
from ikaaro.buttons import BrowseButton
from ikaaro.datatypes import FileDataType
from ikaaro.folder_views import Folder_BrowseContent, GoToSpecificDocument
from ikaaro.messages import MSG_PASSWORD_MISMATCH
from ikaaro.resource_views import DBResource_Edit
from ikaaro.views import SearchForm
from ikaaro.views_new import NewInstance
from ikaaro.workflow import get_workflow_preview

# Import from iscrib
from base_views import LoginView, IconsView
from datatypes import Subscription
from form import Form
from formpage import FormPage
from rw import ODSWriter, XLSWriter
from utils import force_encode, is_production, is_print
from workflow import WorkflowState, NOT_REGISTERED, EMPTY, PENDING, FINISHED


ERR_NO_DATA = ERROR(u"No data to collect for now.")
ERR_NO_MORE_ALLOWED = ERROR(u"You have reached the maximum allowed users. "
        u'Contact <a href="http://www.itaapy.com/contact">Itaapy</a> for '
        u"more.", html=True)
INFO_NEW_APPLICATION = INFO(u'Your application is created. Now register '
        u'users.')
ERR_PASSWORD_MISSING = ERROR(u"The password is missing.")
ERR_BAD_EMAIL = ERROR(u"The given username is not an e-mail address.")
ERR_SUBSCRIPTION_FULL = ERROR(u"No more users are allowed to register.")
ERR_NOT_ALLOWED = ERROR(u"You are not allowed to register.")
ERR_ALREADY_REGISTERED = ERROR(u"You are already registered. "
        u"Log in using your password.")
MSG_APPLICATION_TITLE = MSG(u'''<span class="application-title">Title of your
application:</span> {title}
<a href=";edit" title="Edit and configure application" rel="fancybox">
  <img src="/ui/icons/16x16/edit.png"/></a>''', html=True)

MAILTO_SUBJECT = MSG(u'{workgroup_title}, form "{application_title}"')
MAILTO_BODY = MSG(u'Please fill in the form "{application_title}" available '
        u'here:\r\n'
        u'<{application_url}>.\r\n')


def get_users_query(query, context):
    """Filter forms from users list with same name.
    """
    query = AndQuery(PhraseQuery('format', 'user'), query)
    results = context.root.search(query)
    users = (brain.name for brain in results.get_documents())
    return (PhraseQuery('name', user) for user in users)



class ExportODSButton(BrowseButton):
    access = 'is_allowed_to_edit'
    name = 'export'
    title = MSG(u"Export This List in ODS Format")



class ExportXLSButton(ExportODSButton):
    name = 'export_xls'
    title = MSG(u"Export This List in XLS Format")



class Application_NewInstance(NewInstance):
    schema = merge_dicts(NewInstance.schema,
            title=Unicode(mandatory=True),
            file=FileDataType(mandatory=True))
    widgets = (NewInstance.widgets
            + [FileWidget('file', title=MSG(u"ODS or XLS File"))])


    def action(self, resource, context, form):
        goto = NewInstance.action(self, resource, context, form)
        child = resource.get_resource(form['name'])
        try:
            child._load_from_file(form['file'], context)
        except ValueError, exception:
            if not is_production:
                raise
            context.commit = False
            context.message = ERROR(unicode(exception))
            return
        return context.come_back(INFO_NEW_APPLICATION, goto)



class Application_Menu(IconsView):
    cols = 5
    make_item = IconsView.make_item
    items = [
        make_item(icon='/ui/iscrib/images/form48.png',
           title=MSG(u"Show Test Form"),
           url='0/;pageA'),
        make_item(icon='/ui/iscrib/images/register48.png',
           title=MSG(u"Add Users"),
           url=';register',
           access='is_allowed_to_register'),
        make_item(icon='/ui/iscrib/images/users48.png',
            title=MSG(u"Manage Users"),
            url=';view#users'),
        # "Spread your Form" here
        make_item(icon='/ui/iscrib/images/export48.png',
           title=MSG(u"Collect Data"),
           extra=MSG(u"""
<div id="choose-format">
  <span><a href="#" title="Close"
    onclick="$('#choose-format').hide(); return false">X</a></span>
  <ul>
    <li>Download <a href=";export">ODS Version</a></li>
    <li>Download <a href=";export?format=xls">XLS Version</a></li>
  </ul>
</div>
<script type="text/javascript">
  $("#choose-format").hide();
</script>""", html=True),
           url='#',
           onclick='$("#choose-format").show(); return false',
           access='is_allowed_to_export')]


    def is_allowed_to_register(self, item, resource, context):
        allowed_users = resource.get_allowed_users()
        if not bool(allowed_users):
            item['title'] = ERR_NO_MORE_ALLOWED
            return False
        return True


    def is_allowed_to_export(self, item, resource, context):
        for form in resource.get_forms():
            if form.get_workflow_state() != EMPTY:
                return True
        item['title'] = ERR_NO_DATA
        return False


    def get_items(self, resource, context):
        items = super(Application_Menu, self).get_items(resource, context)
        spread_url = resource.get_spread_url(context)
        items.insert(3, self.make_item(
            icon='/ui/iscrib/images/spread48.png',
            title=MSG(u"Spread your Form"),
            extra=MSG(u"""
<div id="spread-url">
  <span><a href="#" title="Close"
    onclick="return hide_spread_url()">X</a></span>
  <ul>
    <li>You can send this URL to your users:<br/>
      <input id="spread-url-text" type="text" readonly="readonly"
        value="{spread_url}"/>
      <div id="spread-url-copy">
        <a href="javascript:alert('You need Flash plugin to copy!');">
          Copy</a>
      </div>
    </li>
  </ul>
</div>
<script type="text/javascript">
  $("#spread-url-text").focus(function() {{
      this.select();
  }});
  path = '/ui/iscrib/zeroclipboard/ZeroClipboard.swf'
  ZeroClipboard.setMoviePath(path);
  var clip = new ZeroClipboard.Client();
  clip.setHandCursor(true);
  clip.setText("{spread_url}");
  function hide_spread_url() {{
    $('#spread-url').hide();
    clip.hide();
    return false;
  }}
  function show_spread_url() {{
    $('#spread-url').show();
    clip.show();
    return false;
  }}
  $(document).ready(function() {{
    clip.glue("spread-url-copy");
    /* Hide #spread-url after the Flash movie is positioned */
    hide_spread_url();
  }});
</script>""", html=True).gettext(spread_url=spread_url),
            url='#',
            onclick='return show_spread_url()'))
        return items



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
    table_actions = [ExportODSButton, ExportXLSButton]


    def get_page_title(self, resource, context):
        title = resource.get_page_title()
        return MSG_APPLICATION_TITLE.gettext(title=title)


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
        search_term_str = search_term.encode('utf_8')
        if search_term:
            search_query = OrQuery(
                TextQuery('firstname', search_term),
                TextQuery('lastname', search_term),
                TextQuery('company', search_term),
                StartQuery('username', search_term_str),
                StartQuery('email_domain', search_term_str))
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
                subject = MAILTO_SUBJECT.gettext(
                        workgroup_title=resource.parent.get_title(),
                        application_title=application_title)
                subject = quote(subject.encode('utf8'))
                application_url = resource.get_spread_url(context, email)
                body = MAILTO_BODY.gettext(
                        application_title=application_title,
                        application_url=application_url)
                body = quote(body.encode('utf8'))
                url = 'mailto:{0}?subject={1}&body={2}'.format(email,
                        subject, body)
                return (email, url)
        return super(Application_View, self).get_item_value(resource,
                context, item, column)



    def get_key_sorted_by_name(self):
        def key(item):
            return int(item.name)
        return key


    def get_key_sorted_by_state(self):
        get_user = get_context().root.get_user
        def key(item, cache={}):
            name =  item.name
            if name in cache:
                return cache[name]
            user = get_user(name)
            if user is not None and not user.get_property('password'):
                state = NOT_REGISTERED
            else:
                state = item.workflow_state
            title = WorkflowState.get_value(state)
            value = title.gettext().lower().translate(transmap)
            cache[name] = value
            return value
        return key


    def get_key_sorted_by_user(self):
        get_user = get_context().root.get_user
        def key(item, cache={}):
            name = item.name
            if name in cache:
                return cache[name]
            user = get_user(name)
            if user is None:
                value = None
            else:
                value = user.get_title().lower().translate(transmap)
            cache[name] = value
            return value
        return key


    def get_key_sorted_by_email(self):
        get_user = get_context().root.get_user
        def key(item, cache={}):
            name = item.name
            if name in cache:
                return cache[name]
            user = get_user(name)
            if user is None:
                value = None
            else:
                email = user.get_property('email').lower()
                # Group by domain
                username, domain = email.split('@')
                value = (domain, username)
            cache[name] = value
            return value
        return key


    def get_search_namespace(self, resource, context):
        namespace = SearchForm.get_search_namespace(self, resource, context)
        namespace['state_widget'] = SelectWidget('search_state',
                datatype=WorkflowState, value=context.query['search_state'])
        return namespace


    def get_namespace(self, resource, context):
        namespace = {}
        namespace['menu'] = resource.menu.GET(resource, context)
        namespace['n_forms'] = resource.get_n_forms()
        namespace['max_users'] = resource.get_property('max_users')
        namespace['spread_url'] = resource.get_spread_url(context)

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


    def action_export(self, resource, context, form, writer_cls=ODSWriter):
        name = MSG(u"{title} Users").gettext(title=resource.get_title())
        writer = writer_cls(name)

        header = [title.gettext() for column, title in self.table_columns]
        writer.add_row(header, is_header=True)
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
                if type(value) is unicode:
                    pass
                elif type(value) is MSG:
                    value = value.gettext()
                elif type(value) is str:
                    value = unicode(value)
                else:
                    raise NotImplementedError, str(type(value))
                row.append(value)
            writer.add_row(row)

        body = writer.to_str()

        context.set_content_type(writer_cls.mimetype)
        context.set_content_disposition('attachment',
                filename="{0}-users.{1}".format(resource.name,
                    writer_cls.extension))

        return body


    def action_export_xls(self, resource, context, form):
        return self.action_export(resource, context, form,
                writer_cls=XLSWriter)



class Application_Export(BaseView):
    access = 'is_allowed_to_edit'
    title = MSG(u"Export Collected Data")
    query_schema = {'format': String}


    def GET(self, resource, context):
        for form in resource.get_forms():
            state = form.get_workflow_state()
            if state != 'private':
                break
        else:
            return context.come_back(ERR_NO_DATA)

        format = context.query['format']
        if format == 'xls':
            writer_cls = XLSWriter
        else:
            writer_cls = ODSWriter
        name = MSG(u"{title} Data").gettext(title=resource.get_title())
        writer = writer_cls(name)

        handler = resource.get_resource('schema').handler
        schema, pages = handler.get_schema_pages()
        # Main header
        header = [title.gettext()
                for title in (MSG(u"Form"), MSG(u"First Name"),
                    MSG(u"Last Name"), MSG(u"E-mail"), MSG(u"State"))]
        for name in sorted(schema):
            header.append(name)
        writer.add_row(header, is_header=True)
        # Subheader with titles
        header = [""] * 5
        for name, datatype in sorted(schema.iteritems()):
            header.append(datatype.title)
        writer.add_row(header, is_header=True)
        users = resource.get_resource('/users')

        for form in resource.get_forms():
            user = users.get_resource(form.name, soft=True)
            if user:
                get_property = user.get_property
                email = get_property('email')
                firstname = get_property('firstname')
                lastname = get_property('lastname')
            else:
                email = ""
                firstname = ""
                lastname = form.name
            state = WorkflowState.get_value(form.get_workflow_state())
            state = state.gettext()
            row = [form.name, firstname, lastname, email, state]
            handler = form.handler
            for name, datatype in sorted(schema.iteritems()):
                value = handler.get_value(name, schema)
                if datatype.multiple:
                    value = '\n'.join(value
                            for value in datatype.get_values(value))
                else:
                    data = force_encode(value, datatype, 'utf_8')
                    value = unicode(data, 'utf_8')
                row.append(value)
            writer.add_row(row)

        body = writer.to_str()

        context.set_content_type(writer.mimetype)
        context.set_content_disposition('attachment',
                filename="{0}.{1}".format(resource.name, writer.extension))

        return body



class Application_Register(STLForm):
    access = 'is_allowed_to_edit'
    title = MSG(u"Subscribe Users")
    template = '/ui/iscrib/application/register.xml'

    schema = {'new_users': Unicode}


    def get_page_title(self, resource, context):
        title = resource.get_page_title()
        return MSG_APPLICATION_TITLE.gettext( title=title)


    def get_namespace(self, resource, context):
        namespace = super(Application_Register, self).get_namespace(resource,
                context)
        namespace['menu'] = resource.menu.GET(resource, context)
        namespace['title'] = self.title
        namespace['max_users'] = resource.get_property('max_users')
        namespace['n_forms'] = resource.get_n_forms()
        namespace['allowed_users'] = resource.get_allowed_users()
        namespace['MSG_NO_MORE_ALLOWED'] = ERR_NO_MORE_ALLOWED
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
        return namespace


    def action(self, resource, context, form):
        new_users = form['new_users'].strip()
        users = resource.get_resource('/users')
        root = context.root
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
            resource.subscribe_user(user)
            added.append(user.name)
            if len(added) == allowed:
                break

        if not added:
            context.message = ERROR(u"No user added.")
            return

        context.body['new_users'] = u""

        message = u"{n} user(s) added."
        context.message = INFO(message, n=len(added))



class Application_Edit(DBResource_Edit):
    schema = merge_dicts(DBResource_Edit.schema,
            subscription=Subscription(mandatory=True),
            file=FileDataType)
    widgets = DBResource_Edit.widgets + [
            SelectWidget('subscription', has_empty_option=False,
                title=MSG(u"Subscription Mode")),
            file_widget]
    admin_schema = {
            'max_users': Integer(mandatory=True)}
    admin_widgets = [
            TextWidget('max_users',
                title=MSG(u"Maximum form users (0 = unlimited)"))]


    def _get_schema(self, resource, context):
        schema = super(Application_Edit, self)._get_schema(resource, context)
        if not is_print(context) and is_admin(context.user, resource):
            schema = merge_dicts(schema, self.admin_schema)
        return schema


    def _get_widgets(self, resource, context):
        widgets = super(Application_Edit, self)._get_widgets(resource,
                context)
        if not is_print(context) and is_admin(context.user, resource):
            widgets.extend(self.admin_widgets)
        return widgets


    def get_value(self, resource, context, name, datatype):
        if name == 'file':
            return None
        return super(Application_Edit, self).get_value(resource, context,
                name, datatype)


    def set_value(self, resource, context, name, form):
        if name == 'file':
            file = form['file']
            if file is None:
                return False
            for name in ('parameters', 'schema', 'controls'):
                resource.del_resource(name)
            for formpage in resource.search_resources(cls=FormPage):
                resource.del_resource(formpage.name)
            try:
                return resource._load_from_file(file, context)
            except ValueError, exception:
                if not is_production:
                    raise
                context.commit = False
                context.message = ERROR(unicode(exception))
                return True
        return super(Application_Edit, self).set_value(resource, context,
                name, form)



class Application_Login(LoginView):
    template = '/ui/iscrib/application/login.xml'
    schema = merge_dicts(LoginView.schema,
            password=String(default=''),
            newpass=String(default=''),
            newpass2=String)


    def action_register(self, resource, context, form):
        email = form['username'].strip()
        if not Email.is_valid(email):
            context.message = ERR_BAD_EMAIL
            return

        user = context.root.get_user_from_login(email)
        subscription = resource.get_property('subscription')

        # New user?
        if user is None:
            if subscription == 'open':
                # Create the user
                if not resource.get_allowed_users():
                    context.message = ERR_SUBSCRIPTION_FULL
                    return
                users = context.root.get_resource('users')
                user = users.set_user(email, None)
            else:
                context.message = ERR_NOT_ALLOWED
                return

        # Is already registered?
        if user.get_property('password') is not None:
            context.message = ERR_ALREADY_REGISTERED
            return

        # Create the form if necessary
        if subscription == 'open':
            resource.subscribe_user(user)

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
        context.login(user)

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


    def action_login(self, resource, context, form):
        goto = super(Application_Login, self).action_login(resource, context,
                form)

        if type(context.message) is not ERROR:
            # Create the form if necessary
            if resource.get_property('subscription') == 'open':
                user = context.user
                resource.subscribe_user(user)

        return goto


    def action_forgotten_password(self, resource, context, form):
        email = form['username'].strip()
        if not Email.is_valid(email):
            message = u'The given username is not an e-mail address.'
            context.message = ERROR(message)
            return

        user = context.root.get_user_from_login(email)
        if user is None:
            # Silently fail
            path = '/ui/website/forgotten_password.xml'
            handler = resource.get_resource(path)
            return stl(handler)

        user.send_forgotten_password(context, email)
        path = '/ui/website/forgotten_password.xml'
        handler = resource.get_resource(path)
        return stl(handler)



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
