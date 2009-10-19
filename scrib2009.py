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

# Import from itools
from itools.core import get_abspath
from itools.csv import CSVFile
from itools.datatypes import String, Unicode, Integer
from itools.web import get_context

# Import from ikaaro
from ikaaro.folder_views import Folder_BrowseContent
from ikaaro.registry import register_resource_class
from ikaaro.website import WebSite

# Import from scrib
from bm2009 import BM2009
from form import Form
from scrib_views import Scrib_Login, Scrib_PermissionsForm, Scrib_ExportForm
from scrib_views import Scrib_Help, Scrib_ChangePassword


class UsersCSV(CSVFile):
    schema = {'annee': Unicode,
              'code': Integer,
              'categorie': String(is_indexed=True),
              'nom': Unicode,
              'departement': String, # Corse « 2A » et « 2B »
              'id': String, # Corse « 2A004 »
              'mel': String,
              'utilisateur': String,
              'motdepasse': String}
    columns = ['annee', 'code', 'categorie', 'nom', 'departement', 'id',
               'mel', 'utilisateur', 'motdepasse']
    skip_header = True



class Scrib2009(WebSite):
    class_id = 'Scrib2009'
    class_title = u"Scrib 2009"

    # Views
    login = Scrib_Login()
    unauthorized = Scrib_Login()
    permissions_form = Scrib_PermissionsForm()
    export_form = Scrib_ExportForm()
    help = Scrib_Help()
    browse_content = Folder_BrowseContent(access='is_admin_or_consultant')
    xchangepassword = Scrib_ChangePassword()


    # Skeleton
    @staticmethod
    def make_resource(cls, container, name, *args, **kw):
        # Ici les créations annexes à l'application/année
        website = WebSite.make_resource(cls, container, name, *args, **kw)
        # Users
        users_csv = UsersCSV(get_abspath('ui/users.csv'))
        users_folder = container.get_resource('/users')
        users = [# TODO Responsable équivalent de Marie Sotto pour Pelleas
                 ('VoirSCRIB', 'BMBDP', 'TODO')]
        user_ids = set()
        for row in users_csv.get_rows():
            email = row.get_value('mel').strip() or 'TODO'
            # Contre les adresses avec des accents
            try:
                unicode(email)
            except UnicodeDecodeError:
                raise TypeError, 'accent dans email : %s' % email
            login = row.get_value('utilisateur')
            password = row.get_value('motdepasse')
            users.append((login, password, email))
        for login, password, email in users:
            # XXX l'adresse par défaut sera utilisée plusieurs fois
            user = users_folder.set_user(email, password)
            user.set_property('username', login)
            user_ids.add(user.name)
        # Donne un rôle dans ce website = accès à cette année
        website.set_user_role(user_ids, 'members')
        return website


    @staticmethod
    def _make_resource(cls, folder, name):
        # Ici les créations de l'application/année et ses sous-ressources
        WebSite._make_resource(cls, folder, name, website_languages=('fr',),
                               title={'fr': u"Scrib 2009"})
        # BM
        users_csv = UsersCSV(get_abspath('ui/users.csv'))
        rows = users_csv.search(categorie='BM')
        for row in users_csv.get_rows(rows):
            code = row.get_value('code')
            title = row.get_value('nom')
            departement = row.get_value('departement')
            id = row.get_value('id')
            BM2009._make_resource(BM2009, folder, '%s/%s' % (name, code))
        # TODO Créer les BDP


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


###########################################################################
# Register
###########################################################################
register_resource_class(Scrib2009)
