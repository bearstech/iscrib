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

# Import from the Standard Library
from datetime import date

# Import from itools
from itools.core import get_abspath, merge_dicts
from itools.csv import CSVFile
from itools.datatypes import String, Unicode, Integer, Date
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
from bdp2009 import BDP2009
from form import Form
from forms import Forms
from scrib_views import Scrib_Login, Scrib_Edit
from scrib_views import Scrib_ExportForm, Scrib_Help, Scrib_ChangePassword


class UsersCSV(CSVFile):
    schema = {'annee': Unicode,
              'code_ua': Integer,
              'categorie': String(is_indexed=True),
              'nom': Unicode,
              'departement': String, # Corse « 2A » et « 2B »
              'id': String, # Corse « 2A004 »
              'mel': String,
              'utilisateur': String,
              'motdepasse': String}
    columns = ['annee', 'code_ua', 'categorie', 'nom', 'departement', 'id',
               'mel', 'utilisateur', 'motdepasse']
    skip_header = True



class Scrib2009(WebSite):
    class_id = 'Scrib2009'
    class_title = MSG(u"Scrib 2009")
    class_skin = 'ui/scrib'

    bm_class = BM2009
    bpd_class = BDP2009

    # Views
    login = Scrib_Login()
    edit = Scrib_Edit()
    unauthorized = Scrib_Login()
    export_form = Scrib_ExportForm()
    help = Scrib_Help()
    browse_content = Folder_BrowseContent(access='is_admin_or_voir_scrib')
    xchangepassword = Scrib_ChangePassword()


    ########################################################################
    # Skeleton
    @staticmethod
    def _make_resource(cls, folder, name):
        """La création d'une application/année centralise tout ce qui peut
        dépendre de l'année : utilisateurs, formulaires...
        """
        # Créé les utilisateurs d'abord pour avoir user_ids
        print "Génération de la liste des utilisateurs..."
        users = [# TODO Responsable équivalent de Marie Sotto pour Pelleas
                 # TODO VoirSCRIB ne devrait être créé qu'une fois...
                 {'username': 'VoirSCRIB',
                  'password': crypt_password('BMBDP'),
                  'email': 'TODO'}]
        user_ids = set()
        users_csv = UsersCSV(get_abspath('ui/users.csv'))
        for row in users_csv.get_rows():
            email = row.get_value('mel').strip() or 'TODO'
            # Contre les adresses avec des accents
            try:
                unicode(email)
            except UnicodeDecodeError:
                raise TypeError, 'accent dans email : %s' % email
            password = row.get_value('motdepasse')
            users.append({'username': row.get_value('utilisateur'),
                          'password': crypt_password(password),
                          'email': email,
                          'title': {'fr': row.get_value('nom')},
                          'code_ua': row.get_value('code_ua'),
                          'departement': row.get_value('departement'),
                          'id': row.get_value('id')})
        print "  ", len(users), "utilisateurs"
        print "Création des utilisateurs..."
        # XXX remonte au niveau resource
        users_resource = UserFolder(folder.get_handler('users.metadata'))
        user_id = users_resource.get_next_user_id()
        # FIXME le init user n'est pas connu
        if user_id == '0':
            user_id = '1'
        print "  à partir de", user_id
        user_class = get_resource_class('user')
        for metadata in users:
            # Bypasse set_user car trop lent
            # FIXME l'uri de users n'est pas "...database/users"
            user_class._make_resource(user_class, folder,
                                      "users/" + user_id,
                                      # XXX l'adresse par défaut sera
                                      # utilisée plusieurs fois
                                      **metadata)
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
        Forms._make_resource(Forms, folder, "%s/bm" % name,
                             title={'fr': u"BM"})
        rows = users_csv.search(categorie='BM')
        for row in users_csv.get_rows(rows):
            code_ua = row.get_value('code_ua')
            title = row.get_value('nom')
            departement = row.get_value('departement')
            id = row.get_value('id')
            cls.bm_class._make_resource(cls.bm_class, folder, '%s/bm/%s' %
                    (name, code_ua), code_ua=code_ua, title={'fr': title},
                    departement=departement, id=id)
        # TODO Créer les BDP
        Forms._make_resource(Forms, folder, "%s/bdp" % name,
                             title={'fr': u"BDP"})
        print "Indexation de la base..."


    ########################################################################
    # Metadata
    @classmethod
    def get_metadata_schema(cls):
        return merge_dicts(WebSite.get_metadata_schema(),
                           echeance_bm=Date(default=date(2010, 4, 30)),
                           echeance_bdp=Date(default=date(2010, 9, 15)))


    ########################################################################
    # Security
    def is_admin_or_voir_scrib(self, user, resource):
        if user is None:
            return False
        return self.is_admin(user, resource) or user.is_voir_scrib()


    def is_allowed_to_view(self, user, resource):
        # Anonymous
        if user is None:
            return False
        # Admin
        if self.is_admin(user, resource):
            return True
        # VoirSCRIB
        if user.is_voir_scrib():
            return True
        if isinstance(resource, Form):
            # Check the code UA or departement
            if user.is_bm():
                if (user.get_property('code_ua')
                        != resource.get_property('code_ua')):
                    return False
            elif user.is_bdp():
                if (user.get_property('departement')
                        != resource.get_property('departement')):
                    return False
            # Must be registered for this year
            return self.has_user_role(user.name, 'members')
        return True


    def is_allowed_to_edit(self, user, resource):
        # Anonymous
        if user is None:
            return False
        # Admin
        if self.is_admin(user, resource):
            return True
        # VoirSCRIB
        if user.is_voir_scrib():
            return False
        if isinstance(resource, Form):
            # Check the code UA or departement
            if user.is_bm():
                if (user.get_property('code_ua')
                        != resource.get_property('code_ua')):
                    return False
            elif user.is_bdp():
                if (user.get_property('departement')
                        != resource.get_property('departement')):
                    return False
            # Must be registered for this year
            return self.has_user_role(user.name, 'members')
            # Only if 'private' -> 'Vide', 'En cours'
            return resource.get_workflow_state() == 'private'
        return False


    def is_allowed_to_trans(self, user, resource, name):
        if user is None:
            return False
        if isinstance(resource, Form):
            context = get_context()
            namespace = resource.get_namespace(context)
            if self.is_admin(user, resource):
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
