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

# Import from itools
from itools.core import freeze, merge_dicts
from itools.datatypes import String, DateTime, Unicode, Email
from itools.database import PhraseQuery
from itools.gettext import MSG
from itools.stl import stl
from itools.uri import get_reference, get_uri_path
from itools.web import INFO, ERROR

# Import from ikaaro
from ikaaro import messages
from ikaaro.autoform import AutoForm, HiddenWidget, PasswordWidget, RTEWidget
from ikaaro.autoform import TextWidget, XHTMLBody
from ikaaro.folder_views import Folder_BrowseContent
from ikaaro.resource_ import DBResource
from ikaaro.resource_views import LoginView as BaseLoginView
from ikaaro.skins import Skin
from ikaaro.user import User as BaseUser
from ikaaro.user_views import User_EditAccount as BaseUser_EditAccount
from ikaaro.website import WebSite as BaseWebSite

# Import from iscrib
from form import Form
from form_views import Form_View, Form_Send
from param import Param
from utils import get_page_number
from utils_views import AutomaticEditView



class ParamForm_Send(Form_Send):

    def get_namespace(self, resource, context):
        # FIXME
        namespace = super(ParamForm_Send, self).get_namespace(resource,
                context)
        namespace['first_time'] = resource.is_first_time()
        return namespace


    def action_send(self, resource, context, form):
        message = INFO(u"Your report was successfully sent.")
        context.message = message


    def action_export(self, resource, context, form):
        message = INFO(u"Your report was successfully exported.")
        context.message = message



class ParamForm(Param, Form):
    class_id = 'Param'
    class_title = MSG(u"Collection Application")
    class_views = ['pageA'] + Form.class_views
    class_schema = merge_dicts(Form.class_schema, Param.class_schema,
            author=String(source='metadata', indexed=False, stored=True),
            ctime=DateTime(source='metadata', indexed=False, stored=True))

    # Views
    envoyer = ParamForm_Send()


    def __getattr__(self, name):
        page_number = get_page_number(name)
        page = self.get_formpage(page_number)
        if page is None:
            return super(ParamForm, self).__getattr__(name)
        view = Form_View(page_number=page.get_page_number(),
                title=MSG(u"Start filling"))
        # TODO make it lazy
        self.__dict__[name] = view
        return view


    def get_form_handler(self):
        return self.get_resource('0').handler


    def is_ready(self):
        return self.get_workflow_state() == 'pending'


    def get_catalog_values(self):
        author = (self.get_property('author')
                or self.get_property('last_author'))
        ctime = self.get_property('ctime') or self.get_property('mtime')
        return merge_dicts(Param.get_catalog_values(self),
                Form.get_catalog_values(self), author=author, ctime=ctime)



class User_ConfirmRegistration(AutoForm):

    access = True
    title = MSG(u'Choose your password')

    schema = {
        'key': String(mandatory=True),
        'company': Unicode(mandatory=True),
        'newpass': String(mandatory=True),
        'newpass2': String(mandatory=True)}

    widgets = [
        HiddenWidget('key', title=None),
        TextWidget('company', title=MSG(u'Company')),
        PasswordWidget('newpass', title=MSG(u'Password')),
        PasswordWidget('newpass2', title=MSG(u'Repeat your password'))]


    def get_namespace(self, resource, context):
        # Check register key
        must_confirm = resource.get_property('user_must_confirm')
        username = context.get_form_value('username', default='')
        if must_confirm is None:
            return context.come_back(messages.MSG_REGISTERED,
                    goto='/;login?username=%s' % username)
        elif context.get_form_value('key') != must_confirm:
            return context.come_back(messages.MSG_BAD_KEY,
                    goto='/;login?username=%s' % username)
        return AutoForm.get_namespace(self, resource, context)


    def get_value(self, resource, context, name, datatype):
        if name == 'key':
            return resource.get_property('user_must_confirm')
        return AutoForm.get_value(self, resource, context, name, datatype)


    def action(self, resource, context, form):
        # Check register key
        must_confirm = resource.get_property('user_must_confirm')
        if form['key'] != must_confirm:
            context.message = messages.MSG_BAD_KEY
            return

        # Check passwords
        password = form['newpass']
        password2 = form['newpass2']
        if password != password2:
            context.message = messages.MSG_PASSWORD_MISMATCH
            return

        # Set user
        resource.set_password(password)
        resource.del_property('user_must_confirm')

        # Company
        resource.set_property('company', form['company'])

        # Set cookie
        resource.set_auth_cookie(context, password)

        # Ok
        message = INFO(u"Your account was created! You can create a "
                u"collection application.")
        return context.come_back(message, goto='/')



class User_EditAccount(BaseUser_EditAccount):
    schema = merge_dicts(BaseUser_EditAccount.schema,
        company=Unicode(mandatory=True))
    widgets = (BaseUser_EditAccount.widgets[:2]
        + [TextWidget('company', title=MSG(u"Société"))]
        + BaseUser_EditAccount.widgets[2:])



class User(BaseUser):
    class_schema = merge_dicts(BaseUser.class_schema,
            company=Unicode(source='metadata'))

    # Views
    edit_account = User_EditAccount()
    confirm_registration = User_ConfirmRegistration()



# Pas d'héritage pour pas de méthode "action"
class LoginView(BaseLoginView):
    template = '/ui/iscrib/login.xml'


    def action_login(self, resource, context, form):
        email = form['username'].strip()
        password = form['password']

        user = context.root.get_user_from_login(email)
        if user is None or not user.authenticate(password, clear=True):
            message = u'The email or the password is incorrect.'
            context.message = ERROR(message)
            return

        # Set cookie & context
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


    def action_register(self, resource, context, form):
        email = form['username'].strip()
        if not Email.is_valid(email):
            message = u'The given username is not an email address.'
            context.message = ERROR(message)
            return

        user = context.root.get_user_from_login(email)

        # Case 1: Register
        if user is None:
            if context.site_root.is_allowed_to_register():
                return self._register(resource, context, email)
            error = u"You are not allowed to register."
            context.message = ERROR(error)
            return

        # Case 2: Forgotten password
        email = user.get_property('email')
        user.send_forgotten_password(context, email)
        path = '/ui/website/forgotten_password.xml'
        handler = resource.get_resource(path)
        return stl(handler)



class WebSite_BrowseContent(Folder_BrowseContent):
    access = 'is_allowed_to_view'
    template = '/ui/iscrib/root_view.xml'
    search_template = None
    title = MSG(u"View")

    table_columns = [
            ('form', MSG(u"Application")),
            ('file', MSG(u"Source ODS File")),
            ('ctime', MSG(u"Creation Date"))]
    table_actions = []


    def get_page_title(self, resource, context):
        return None


    def get_namespace(self, resource, context):
        return merge_dicts(
            Folder_BrowseContent.get_namespace(self, resource, context),
            homepage=resource.get_property('homepage'))


    def get_items(self, resource, context, *args):
        return super(WebSite_BrowseContent, self).get_items(resource, context,
                PhraseQuery('format', ParamForm.class_id), *args)


    def sort_and_batch(self, resource, context, results):
        start = context.query['batch_start']
        size = context.query['batch_size']
        sort_by = context.query['sort_by']
        reverse = context.query['reverse']
        items = results.get_documents(sort_by=sort_by, reverse=reverse,
                                      start=start, size=size)

        # FIXME This must be done in the catalog.
        if sort_by == 'title':
            items.sort(cmp=lambda x,y: cmp(x.title, y.title))
            if reverse:
                items.reverse()

        # Access Control (FIXME this should be done before batch)
        user = context.user
        root = context.root
        allowed_items = []
        for item in items:
            resource = root.get_resource(item.abspath)
            # On regarde mais sans toucher
            #ac = resource.get_access_control()
            #if ac.is_allowed_to_view(user, resource):
            allowed_items.append((item, resource))

        return allowed_items


    def get_item_value(self, resource, context, item, column):
        brain, item_resource = item
        if column == 'form':
            return brain.title, brain.name
        elif column == 'file':
            return (u'Source de %s' % brain.title,
                    '%s/parameters/;download' % brain.name)
        elif column == 'ctime':
            return context.format_datetime(brain.ctime)
        return super(WebSite_BrowseContent, self).get_item_value(resource,
                context, item, column)



class WebSite(BaseWebSite):
    class_views = ['view', 'edit']
    class_skin = 'ui/iscrib'
    class_roles = freeze(['members', 'admins'])

    class_schema = merge_dicts(BaseWebSite.class_schema,
            homepage=XHTMLBody(source='metadata', indexed=False, stored=False,
                           multilingual=True))

    # Views
    view = WebSite_BrowseContent()
    unauthorized = LoginView()

    # Edit view
    edit_show_meta = True
    edit_schema = {'homepage': XHTMLBody(multilingual=True)}
    edit_widgets = [RTEWidget('homepage', title=MSG(u'Homepage'))]
    edit = AutomaticEditView(access='is_admin')

    def get_document_types(self):
        return [Param]



class Website_Skin(Skin):

    def build_namespace(self, context):
        return merge_dicts(Skin.build_namespace(self, context),
                  website_title=context.site_root.get_property('title'))



from ikaaro.registry import register_resource_class
register_resource_class(User)
register_resource_class(WebSite)
DBResource.login = LoginView()
