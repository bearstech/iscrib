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
from itools.datatypes import String, DateTime, Integer
from itools.gettext import MSG

# Import from ikaaro
from ikaaro.folder import Folder

# Import from iscrib
from application_views import Application_Edit, Application_Export
from application_views import Application_NewInstance, Application_View
from application_views import Application_RedirectToForm
from application_views import Application_Register, Application_Login
from controls import Controls
from form import Form
from schema import Schema


class Application(Folder):
    class_id = 'Application'
    class_title = MSG(u"Collection Application")
    class_description = MSG(u"Create from an OpenDocument Spreadsheet file")
    class_icon16 = 'icons/16x16/tasks.png'
    class_icon48 = 'icons/48x48/tasks.png'
    allowed_users = 10
    class_schema = merge_dicts(Folder.class_schema,
            author=String(source='metadata', indexed=False, stored=True),
            ctime=DateTime(source='metadata', indexed=False, stored=True),
            max_users=Integer(source='metadata', default=allowed_users))
    class_views = Folder.class_views + ['export', 'register', 'show']

    schema_class = Schema
    controls_class = Controls
    default_form = '0'

    # Views
    new_instance = Application_NewInstance()
    view = Application_View()
    edit = Application_Edit()
    export = Application_Export()
    register = Application_Register()
    login = Application_Login()
    show = Application_RedirectToForm()


    def get_form(self):
        return self.get_resource(self.default_form, soft=True)


    def get_forms(self):
        for form in self.search_resources(cls=Form):
            if form.name != self.default_form:
                yield form


    def get_n_forms(self):
        return len(list(self.get_forms()))


    def get_param_folder(self):
        return self


    def get_allowed_users(self):
        max_users = self.get_property('max_users')
        n_forms = self.get_n_forms()
        return (max_users - n_forms) if max_users else self.allowed_users


    def get_admin_url(self, context):
        base_url = context.uri.resolve(self.get_abspath())
        return base_url.resolve2(';view')


    def get_user_url(self, context, email=None):
        base_url = context.uri.resolve(self.get_abspath())
        user_url = base_url.resolve2(';login')
        if email is not None:
            user_url.query['username'] = email
        return user_url


    def get_catalog_values(self):
        author = (self.get_property('author')
                or self.get_property('last_author'))
        ctime = self.get_property('ctime') or self.get_property('mtime')
        return merge_dicts(Folder.get_catalog_values(self),
                author=author, ctime=ctime)
