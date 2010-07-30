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
from itools.core import merge_dicts
from itools.datatypes import String, DateTime, Unicode
from itools.database import PhraseQuery
from itools.gettext import MSG
from itools.uri import get_reference
from itools.web import INFO

# Import from ikaaro
from ikaaro.autoform import TextWidget
from ikaaro.folder_views import Folder_BrowseContent
from ikaaro.root import Root as BaseRoot
from ikaaro.user import User as BaseUser
from ikaaro.user_views import User_EditAccount as BaseUser_EditAccount
from ikaaro.website_views import RegisterForm as BaseRegisterForm

# Import from iscrib
from form import Form
from form_views import Form_View, Form_Send
from param import Param
from param_views import Param_NewInstance
from utils import get_page_number


class ParamForm_NewInstance(Param_NewInstance):
    access = True


    def GET(self, resource, context):
        ac = resource.get_access_control()
        class_id = context.get_query_value('type')
        if (class_id != ParamForm.class_id
                or ac.is_allowed_to_add(context.user, resource)):
            return super(ParamForm_NewInstance, self).GET(resource, context)
        return get_reference('/;register')



class ParamForm_View(Form_View):
    access = True


    def GET(self, resource, context):
        ac = resource.get_access_control()
        if ac.is_allowed_to_view(context.user, resource):
            return super(ParamForm_View, self).GET(resource, context)
        return get_reference('/;register')



class ParamForm_Send(Form_Send):

    def get_namespace(self, resource, context):
        # FIXME
        namespace = super(ParamForm_Send, self).get_namespace(resource,
                context)
        namespace['first_time'] = resource.is_first_time()
        return namespace


    def action_send(self, resource, context, form):
        message = INFO(u"Votre rapport a bien été envoyé.")
        context.message = message


    def action_export(self, resource, context, form):
        message = INFO(u"Votre rapport a bien été exporté.")
        context.message = message



class ParamForm(Param, Form):
    class_id = 'Param'
    class_title = MSG(u"Application de collecte")
    class_views = ['pageA'] + Form.class_views
    class_schema = merge_dicts(Form.class_schema, Param.class_schema,
            author=String(source='metadata', indexed=False, stored=True),
            ctime=DateTime(source='metadata', indexed=False, stored=True))

    # Views
    new_instance = ParamForm_NewInstance()
    envoyer = ParamForm_Send()


    def __getattr__(self, name):
        page_number = get_page_number(name)
        page = self.get_formpage(page_number)
        if page is None:
            return super(ParamForm, self).__getattr__(name)
        view = ParamForm_View(page_number=page.get_page_number(),
                title=MSG(u"Commencer la saisie"))
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



class Root_BrowseContent(Folder_BrowseContent):
    access = 'is_allowed_to_view'
    template = '/ui/iscrib/root_view.xml'
    title = MSG(u"Voir")

    table_columns = [
            ('form', MSG(u"Formulaire")),
            ('file', MSG(u"Fichier")),
            ('author', MSG(u"Auteur")),
            ('ctime', MSG(u"Date de création"))]
    table_actions = []

    search_schema = merge_dicts(Folder_BrowseContent.search_schema,
            search_type=String(default=ParamForm.class_id))


    def get_items(self, resource, context, *args):
        return super(Root_BrowseContent, self).get_items(resource, context,
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
            ods = item_resource.get_resource('parameters')
            return (ods.get_property('filename'),
                    '%s/parameters/;download' % brain.name)
        elif column == 'author':
            author =  brain.author
            return context.root.get_user_title(author) if author else None
        elif column == 'ctime':
            return context.format_datetime(brain.ctime)
        return super(Root_BrowseContent, self).get_item_value(resource,
                context, item, column)



class Root_Register(BaseRegisterForm):
    schema = merge_dicts(BaseRegisterForm.schema,
        company=Unicode(mandatory=True))
    widgets = (BaseRegisterForm.widgets[:2]
        + [TextWidget('company', title=MSG(u"Société"))]
        + BaseRegisterForm.widgets[2:])


    def action(self, resource, context, form):
        goto = super(Root_Register, self).action(resource, context, form)
        # FIXME get user
        users = resource.get_resource('users')
        next_user_id = users.get_next_user_id()
        user_id = str(int(next_user_id) - 1)
        user = users.get_resource(user_id)
        # Set company
        user.set_property('company', form['company'].strip())
        return goto



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



class Root(BaseRoot):
    # Views
    view = Root_BrowseContent()
    register = Root_Register()



# FIXME
from ikaaro.registry import register_resource_class
register_resource_class(User)
register_resource_class(Root)
