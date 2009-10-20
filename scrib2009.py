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
from itools.gettext import MSG
from itools.web import get_context

# Import from ikaaro
from ikaaro.folder_views import Folder_BrowseContent
from ikaaro.registry import register_resource_class, get_resource_class
from ikaaro.user import UserFolder
from ikaaro.utils import crypt_password
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
    class_title = MSG(u"Scrib 2009")

    # Views
    login = Scrib_Login()
    unauthorized = Scrib_Login()
    permissions_form = Scrib_PermissionsForm()
    export_form = Scrib_ExportForm()
    help = Scrib_Help()
    browse_content = Folder_BrowseContent(access='is_admin_or_consultant')
    xchangepassword = Scrib_ChangePassword()


    ########################################################################
    # Skeleton
    @staticmethod
    def _make_resource(cls, folder, name):
        # Créé les utilisateurs d'abord pour avoir user_ids
        print "Génération de la liste des utilisateurs..."
        users = [# TODO Responsable équivalent de Marie Sotto pour Pelleas
                 ('VoirSCRIB', 'BMBDP', 'TODO')]
        user_ids = set()
        users_csv = UsersCSV(get_abspath('ui/users.csv'))
        for row in users_csv.get_rows():
            email = row.get_value('mel').strip() or 'TODO'
            # Contre les adresses avec des accents
            try:
                unicode(email)
            except UnicodeDecodeError:
                raise TypeError, 'accent dans email : %s' % email
            username = row.get_value('utilisateur')
            password = row.get_value('motdepasse')
            users.append((username, password, email))
        print "  ", len(users), "utilisateurs"
        print "Création des utilisateurs..."
        # XXX remonte au niveau resource
        users_resource = UserFolder(folder.get_handler('users.metadata'))
        user_id = users_resource.get_next_user_id()
        # FIXME le init user n'est pas connu
        if user_id == '0':
            user_id = '1'
        print "  à partir de", user_id
        user_class =  get_resource_class('user')
        for username, password, email in users:
            # Bypasse set_user car trop lent
            # FIXME l'uri de users n'est pas "...database/users"
            user_class._make_resource(user_class, folder, "users/" + user_id,
                                      # XXX l'adresse par défaut sera utilisée
                                      # plusieurs fois
                                      email=email,
                                      password=crypt_password(password),
                                      username=username)
            user_ids.add(user_id)
            user_id = str(int(user_id) + 1)
        # Maintenant les créations de l'application/année
        # et ses sous-ressources
        print "Création de l'application..."
        WebSite._make_resource(cls, folder, name, website_languages=('fr',),
                               title={'fr': u"Scrib 2009"},
                               # Donne un rôle dans ce website
                               # = accès à cette année
                               members=user_ids)
        # BM
        print "Création des BM..."
        rows = users_csv.search(categorie='BM')
        for row in users_csv.get_rows(rows):
            code = row.get_value('code')
            title = row.get_value('nom')
            departement = row.get_value('departement')
            id = row.get_value('id')
            BM2009._make_resource(BM2009, folder, '%s/%s' % (name, code),
                    code=code, title={'fr': title}, departement=departement,
                    id=id)
        # TODO Créer les BDP
        print "Indexation de la base..."


    ########################################################################
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
register_resource_class(Scrib2009)
