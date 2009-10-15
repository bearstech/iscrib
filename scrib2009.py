# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Hervé Cauwelier <herve@itaapy.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Import from ikaaro
from folder_views import Folder_BrowseContent
from website import WebSite

# Import from scrib
from form import Form
from scrib_views import Scrib_Login, Scrib_PermissionsForm, Scrib_ExportForm
from scrib_views import Scrib_Help, Scrib_ChangePassword


class Scrib2009(WebSite):
    class_id = 'Scrib2009'

    # Views
    login = Scrib_Login()
    unauthorized = Scrib_Login()
    permissions_form = Scrib_PermissionsForm()
    export_form = Scrib_ExportForm()
    help = Scrib_Help()
    browse_content = Folder_BrowseContent(access='is_admin_or_consultant')
    xchangepassword = Scrib_ChangePassword()


    # Security
    def is_consultant(self, user, resource):
        if user is None:
            return False
        return user.name == 'VoirSCRIB'


    def is_admin_or_consultant(self, user, resource):
        if user is None:
            return False
        return (self.is_admin(user, resource)
                or self.is_consultant(user, resource))


    def is_allowed_to_view(self, user, resource):
        # Anonymous
        if user is None:
            return False
        # Admin
        if self.is_admin(user, resource):
            return True
        # VoirSCRIB
        if user.name == 'VoirSCRIB':
            return True
        if isinstance(resource, Form):
            # Check the year
            if user.get_year() != resource.parent.get_year():
                return False
            # Check the department
            if user.is_BM():
                if user.get_BM_code() != resource.name:
                    return False
            elif user.is_BDP():
                if user.get_department() != resource.name:
                    return False
        return True


    def is_allowed_to_edit(self, user, resource):
        # Admin
        if self.is_admin(user, resource):
            return True
        # Anonymous
        if user is None or user.name == 'VoirSCRIB':
            return False
        if isinstance(resource, Form):
            # Check the year
            if user.get_year() != resource.parent.get_year():
                return False
            # Check the department
            if user.is_BM():
                if user.get_BM_code() != resource.name:
                    return False
            elif user.is_BDP():
                if user.get_department() != resource.name:
                    return False
            # Only if 'private' -> 'Vide', 'En cours'
            return resource.get_workflow_state() == 'private'
        return False


    def is_allowed_to_trans(self, user, resource, name):
        if user is None:
            return False
        context = get_context()
        root = context.root
        # XXX Check that !!
        if isinstance(resource, Form):
            namespace = resource.get_namespace(context)
            is_admin = self.is_admin(user, resource)

            if is_admin:
                if name in ['request', 'accept', 'publish']:
                    return namespace['is_ready']
                else:
                    return True
            else:
                if name in ['request']:
                    return namespace['is_ready']
                elif name in ['unrequest']:
                    return True
                else:
                    return False
        return WebSite.is_allowed_to_trans(self, user, resource, name)
