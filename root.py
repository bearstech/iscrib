# -*- coding: UTF-8 -*-
# Copyright (C) 2006-2008 Hervé Cauwelier <herve@itaapy.com>
# Copyright (C) 2006-2008 ALPantin  <anne-laure.pantin@culture.gouv.fr>
# Copyright (C) 2009 Sylvain Taverne <sylvain@itaapy.com>
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

# Import from itools
from itools import vfs
from itools.gettext import MSG
from itools.web import get_context

# Import from ikaaro
from ikaaro.folder_views import Folder_BrowseContent
from ikaaro.registry import register_resource_class
from ikaaro.root import Root as BaseRoot

# Import from scrib
from root_views import Root_Login, Root_PermissionsForm, NewReportsForm
from root_views import Root_CreerVoirSCRIB, Root_ExportForm
from root_views import Root_NewBmForm, Root_HELP
from form import Form


class Root(BaseRoot):

    class_id = 'Culture'
    class_version = '20080410'
    class_title = MSG(u"SCRIB")
    class_skin = 'ui/scrib'


    # XXX Ancien menu à deux niveaux
    #class_views = [['browse_content'],
    #               ['new_reports_form', 'new_bm_form', 'creer_VoirSCRIB'],
    #               ['export_form'],
    #               ['permissions_form', 'new_user_form'],
    #               ['edit_metadata_form'],
    #               ['help']]

    class_views = ['browse_content',
                   'new_reports_form', 'new_bm_form', 'creer_VoirSCRIB',
                   'export_form',
                   'permissions_form', 'add_user',
                   'edit', 'help']

    __roles__ = [{'name': 'admins', 'title': u'Admin'}]


    login = Root_Login()
    login_form = Root_Login()
    unauthorized = Root_Login()

    permissions_form = Root_PermissionsForm()
    new_reports_form = NewReportsForm()
    new_bm_form = Root_NewBmForm()
    creer_VoirSCRIB = Root_CreerVoirSCRIB()
    export_form = Root_ExportForm()
    permissions_form = Root_PermissionsForm()
    help = Root_HELP()
    browse_content = Folder_BrowseContent(access='is_admin_or_consultant')


    def before_traverse(self, context):
        # Set french as default language, whatever the browser config is
        context.accept_language.set('fr', 2.0)


    #########################################################################
    # Security
    #########################################################################


    def is_consultant(self, user, resource):
        if user is None:
            return False
        return user.name == 'VoirSCRIB'


    def is_admin_or_consultant(self, user, resource):
        if user is None:
            return False
        return self.is_admin(user, resource) or self.is_consultant(user, resource)


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
        return BaseRoot.is_allowed_to_trans(self, user, resource, name)


    #########################################################################
    # User interface
    #########################################################################

    def get_available_languages(self):
        return ['fr']


    def get_default_language(self):
        return 'fr'


    #########################################################################
    # Upgrade
    #########################################################################
    def update_20080410(self):
        root = vfs.open(self.handler.uri)
        # Remove handlers
        for obsolete in ('.archive', '.users', '.admins.users', 'admins',
                'admins.metadata', 'reviewers', 'reviewers.metadata',
                'en.po', 'en.metadata'):
            if root.exists(obsolete):
                root.remove(obsolete)
        # Set admin
        self.set_user_role('admin', 'admins')



register_resource_class(Root)
