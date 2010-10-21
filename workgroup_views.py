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
from itools.database import PhraseQuery
from itools.datatypes import Unicode, Email, String, PathDataType
from itools.gettext import MSG
from itools.stl import stl

# Import from ikaaro
from ikaaro.autoform import TextWidget, ImageSelectorWidget, PasswordWidget
from ikaaro.folder_views import Folder_BrowseContent
from ikaaro.messages import MSG_PASSWORD_MISMATCH
from ikaaro.resource_views import DBResource_Edit
from ikaaro.theme_views import Theme_Edit
from ikaaro.views import IconsView
from ikaaro.views_new import NewInstance

# Import from iscrib
from application import Application


class Workgroup_NewInstance(NewInstance):
    access = True
    schema = merge_dicts(NewInstance.schema,
            title=Unicode(mandatory=True),
            email=Email,
            firstname=Unicode,
            lastname=Unicode,
            company=Unicode,
            password=String,
            password2=String)
    widgets = NewInstance.widgets[:-1]


    def get_schema(self, resource, context):
        schema = self.schema.copy()
        if context.user is None:
            for key in ('email', 'password', 'password2'):
                schema[key] = schema[key](mandatory=True)
        return schema

    
    def get_widgets(self, resource, context):
        widgets = self.widgets[:]
        if context.user is None:
            widgets.extend([
                TextWidget('email', title=MSG(u"Your e-mail address")),
                TextWidget('firstname', title=MSG(u"First Name")),
                TextWidget('lastname', title=MSG(u"Last Name")),
                TextWidget('company', title=MSG(u"Company")),
                PasswordWidget('password', title=MSG(u"Password")),
                PasswordWidget('password2', title=MSG(u"Repeat Password"))])
        return widgets


    def action(self, resource, context, form):
        goto = super(Workgroup_NewInstance, self).action(resource, context,
                form)
        workgroup = resource.get_resource(form['name'])
        # Create the user if necessary
        user_was_created = False
        user = context.user
        if user is None:
            email = form['email']
            root = context.root
            user = root.get_user_from_login(email)
            password = form['password']
            if user is None:
                # Create user
                if password != form['password2']:
                    context.message = MSG_PASSWORD_MISMATCH
                    context.commit = False
                    return
                users = resource.get_resource('/users')
                user = users.set_user(email, password)
                # Send e-mail with login
                wg_path = '{0}/;login'.format(context.get_link(workgroup))
                site_uri = context.uri.resolve(wg_path)
                user.send_workgroup_registration(context, email, site_uri,
                        password)
            else:
                # XXX existing user but new password
                pass
            # Automatic login
            user.set_auth_cookie(context, password)
            context.user = user
        # Update user info
        for key in ('firstname', 'lastname', 'company'):
            if form[key]:
                user.set_property(key, form[key])
        # Set the user as workgroup member
        username = user.name
        workgroup.set_user_role(username, 'members')
        # Come back
        return goto



class Workgroup_Menu(IconsView):

    items = [{'icon': '/ui/iscrib/images/download48.png',
              'title': MSG(u"Download the Template"),
              'description': MSG(u"Download this template and use it to define to design your form."),
              'url': '/gabarit/;download'},
             {'icon': '/ui/iscrib/images/upload48.png',
              'title': MSG(u"Create a Data Collection Application"),
              'description': MSG(u"Uploading this spreadsheet file in iScrib will generate in one click your data collection application."),
              'url': ';new_resource?type=Application'},
             {'icon': '/ui/iscrib/images/logo48.png',
              'title': MSG(u"Edit Title and Logo"),
              'description': MSG(u"Configure your client space"),
              'url': ';edit'}]


    def get_namespace(self, resource, context):
        return {'batch': None, 'items': self.items}



class Workgroup_View(Folder_BrowseContent):
    access = 'is_allowed_to_edit'
    template = '/ui/iscrib/workgroup/view.xml'
    title = MSG(u"Manage your client space")
    search_template = None

    table_columns = [
            ('form', MSG(u"Application")),
            ('subscribed', MSG(u"Users Subscribed")),
            ('file', MSG(u"Source ODS File")),
            ('ctime', MSG(u"Creation Date"))]
    table_actions = []


    def get_namespace(self, resource, context):
        # Menu
        theme = resource.get_resource('theme')
        menu = Workgroup_Menu().GET(resource, context)

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

        return {'menu': menu, 'batch': batch, 'table': table}


    def get_items(self, resource, context, *args):
        query = PhraseQuery('format', Application.class_id)
        return super(Workgroup_View, self).get_items(resource, context,
                query, *args)


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
        elif column == 'subscribed':
            return len(list(item_resource.get_forms()))
        elif column == 'file':
            parameters = item_resource.get_resource('parameters')
            return (parameters.get_property('filename') or u"Source",
                    '{0}/;download'.format(context.get_link(parameters)))
        elif column == 'ctime':
            return context.format_datetime(brain.ctime)
        return super(Workgroup_View, self).get_item_value(resource, context,
                item, column)



class Workgroup_Edit(Theme_Edit, DBResource_Edit):
    title = MSG(u"Edit Title and Logo")
    schema = merge_dicts(DBResource_Edit.schema,
            favicon=PathDataType,
            logo=PathDataType)
    widgets = DBResource_Edit.widgets + ([
                ImageSelectorWidget('logo', action='add_logo',
                    title=MSG(u'Replace logo file')) ])


    def get_value(self, resource, context, name, datatype):
        if name == 'favicon':
            return ''
        elif name == 'logo':
            # Path must be resolved relative to here
            theme = resource.get_resource('theme')
            path = theme.get_property(name)
            if path in ('', '.'):
                return ''
            logo = theme.get_resource(path)
            return resource.get_pathto(logo)
        return super(Workgroup_Edit, self).get_value(resource, context, name,
                datatype)


    def set_value(self, resource, context, name, form):
        if name == 'favicon':
            return False
        elif name == 'logo':
            # Path must be saved relative to the theme
            path = form[name]
            theme = resource.get_resource('theme')
            if path in ('', '.'):
                theme.set_property(name, '')
                return False
            logo = resource.get_resource(path)
            logo.set_workflow_state('public')
            theme.set_property(name, theme.get_pathto(logo))
            # TODO detect first time logo and call set_neutral_header()
            return False
        return super(Workgroup_Edit, self).set_value(resource, context, name,
                form)
