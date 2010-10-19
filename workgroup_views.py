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
from itools.datatypes import Unicode, Email, String
from itools.gettext import MSG

# Import from ikaaro
from ikaaro.autoform import TextWidget
from ikaaro.folder_views import Folder_BrowseContent
from ikaaro.messages import MSG_PASSWORD_MISMATCH
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
                TextWidget('password', title=MSG(u"Password")),
                TextWidget('password2', title=MSG(u"Repeat Password"))])
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



class Workgroup_BrowseContent(Folder_BrowseContent):
    access = 'is_allowed_to_edit'
    template = '/ui/iscrib/workgroup/view.xml'
    title = MSG(u"View")
    search_template = None

    table_columns = [
            ('form', MSG(u"Application")),
            ('file', MSG(u"Source ODS File")),
            ('ctime', MSG(u"Creation Date"))]
    table_actions = []


    def get_page_title(self, resource, context):
        return None


    def get_items(self, resource, context, *args):
        return super(Workgroup_BrowseContent, self).get_items(resource,
                context, PhraseQuery('format', Application.class_id), *args)


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
            parameters = item_resource.get_resource('parameters')
            return (parameters.get_property('filename') or u"Source",
                    '%s/;download' % context.get_link(parameters))
        elif column == 'ctime':
            return context.format_datetime(brain.ctime)
        return super(Workgroup_BrowseContent,
                self).get_item_value(resource, context, item, column)
