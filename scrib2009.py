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
from ikaaro.folder_views import Folder_BrowseContent, Folder_PreviewContent
from ikaaro.folder_views import GoToSpecificDocument
from ikaaro.forms import XHTMLBody
from ikaaro.registry import register_resource_class
from ikaaro.resource_views import DBResource_Backlinks
from ikaaro.revisions_views import DBResource_LastChanges
from ikaaro.user import UserFolder
from ikaaro.utils import crypt_password
from ikaaro.webpage import WebPage
from ikaaro.website import WebSite

# Import from scrib
from bm2009 import BM2009Form
from bdp2009 import BDP2009Form
from form import Form, MultipleForm
from forms import Forms
from scrib_views import Scrib_Admin, Scrib_Login, Scrib_Edit
from scrib_views import Scrib_Register, Scrib_Confirm
from scrib_views import Scrib_ExportForm, Scrib_ChangePassword
from scrib_views import Scrib_ForgottenPassword, GoToHome
from user import User


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
    class_skin = 'ui/scrib2009'
    class_views = ['admin'] + WebSite.class_views + ['aide', 'home']

    __fixed_handlers__ = WebSite.__fixed_handlers__ + ['bm', 'bdp', 'aide']

    bm_class = BM2009Form
    bdp_class = BDP2009Form

    # Views
    admin = Scrib_Admin()
    login = unauthorized = Scrib_Login()
    register = Scrib_Register()
    forgotten_password = Scrib_ForgottenPassword()
    confirm = Scrib_Confirm()
    edit = Scrib_Edit()
    export_form = Scrib_ExportForm()
    browse_content = Folder_BrowseContent(access='is_admin_or_voir_scrib')
    preview_content = Folder_PreviewContent(access='is_admin_or_voir_scrib')
    backlinks = DBResource_Backlinks(access='is_admin_or_voir_scrib')
    last_changes = DBResource_LastChanges(access='is_admin_or_voir_scrib')
    aide = GoToSpecificDocument(specific_document='aide', title=MSG(u"Aide"))
    home = GoToHome()
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
        users = [# FIXME VoirSCRIB ne devrait être créé qu'une fois...
                 {'username': 'VoirSCRIB',
                  'password': crypt_password('BMBDP'),
                  'email': 'TODO'}]
        user_ids = set()
        print "  ", len(users), "utilisateurs"
        print "Création des utilisateurs..."
        # XXX remonte au niveau resource
        users_resource = UserFolder(folder.get_handler('users.metadata'))
        user_id = users_resource.get_next_user_id()
        # FIXME le init user n'est pas connu
        if user_id == '0':
            user_id = '1'
        print "  à partir de", user_id
        for metadata in users:
            # Bypasse set_user car trop lent
            # FIXME l'uri de users n'est pas "...database/users"
            User._make_resource(User, folder, "users/" + user_id,
                                # XXX Pas de vérification de doublon d'e-mail
                                **metadata)
            user_ids.add(user_id)
            user_id = str(int(user_id) + 1)
        # Maintenant les créations de l'application/année
        # et ses sous-ressources
        print "Création de l'application..."
        WebSite._make_resource(cls, folder, name, annee=2009,
                               echeance_bm=date(2010, 4, 30),
                               echeance_bdp=date(2010, 9, 15),
                               adresse=XHTMLBody.decode("""\
<p><span style="color: #000000;">Direction du livre et de la lecture</span></p>
<p><span style="color: #000000;">Bureau des bibliothèques territoriales</span></p>
<p><span style="color: #000000;">182, rue Saint-Honoré</span></p>
<p><span style="color: #000000;">75033 PARIS CEDEX 01</span></p>"""),
                               contacts=XHTMLBody.decode("""\
<p><span style="color: #000000;">BDP : <strong><span style="color: #ffffff;"><a href="mailto:christophe.sene@culture.gouv.fr">christophe.sene@culture.gouv.fr</a></span></strong> 01 40 15 73 74</span></p>
<p><span style="color: #000000;">BM : <strong><span style="color: #ffffff;"><a href="mailto:denis.cordazzo@culture.gouv.fr">denis.cordazzo@culture.gouv.fr</a></span></strong> 01 40 15 74 85</span></p>"""),
                               title={'fr': u"Scrib 2009"},
                               website_languages=('fr',),
                               vhosts=('localhost', 'scrib2009'),
                               # Donne un rôle dans ce website
                               # = accès à cette année
                               members=user_ids,
                               # Enregistrement volontaire
                               website_is_open=True)
        # Pages
        print "Création des pages..."
        for filename, title in [('aide.xhtml', u"Aide"),
                                ('PageA.xhtml', u"Page A"),
                                ('PageB.xhtml', u"Page B"),
                                ('PageC.xhtml', u"Page C"),
                                ('PageD.xhtml', u"Page D"),
                                ('PageE.xhtml', u"Page E"),
                                ('PageF.xhtml', u"Page F"),
                                ('PageG.xhtml', u"Page G"),
                                ('PageH.xhtml', u"Page H")]:
            with open(get_abspath('ui/scrib2009/' + filename)) as file:
                id = filename.split('.')[0]
                WebPage._make_resource(WebPage, folder, '/'.join((name, id)),
                        title={'fr': title}, state='public', language='fr',
                        body=file.read())
        # BM
        print "Création des BM..."
        Forms._make_resource(Forms, folder, "%s/bm" % name,
                             title={'fr': u"BM"})
        users_csv = UsersCSV(get_abspath('ui/scrib2009/users.csv'))
        rows = users_csv.search(categorie='BM')
        for row in users_csv.get_rows(rows):
            code_ua = row.get_value('code_ua')
            title = row.get_value('nom')
            departement = row.get_value('departement')
            cls.bm_class._make_resource(cls.bm_class, folder, '%s/bm/%s' %
                    (name, code_ua), code_ua=code_ua, title={'fr': title},
                    departement=departement)
        print "Création des BDP..."
        Forms._make_resource(Forms, folder, "%s/bdp" % name,
                             title={'fr': u"BDP"})
        rows = users_csv.search(categorie='BDP')
        for row in users_csv.get_rows(rows):
            code_ua =  row.get_value('code_ua')
            title = row.get_value('nom')
            departement = row.get_value('departement')
            cls.bdp_class._make_resource(cls.bdp_class, folder,
                    '%s/bdp/%s' % (name, departement), title={'fr': title},
                    departement=departement)
        print "Indexation de la base..."


    ########################################################################
    # Metadata
    @classmethod
    def get_metadata_schema(cls):
        return merge_dicts(WebSite.get_metadata_schema(),
                annee=Integer,
                echeance_bm=Date,
                echeance_bdp=Date,
                adresse=XHTMLBody,
                contacts=XHTMLBody)


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
        if isinstance(resource, (Form, MultipleForm)):
            # Check the code UA or departement
            if user.is_bm():
                if not (resource.is_bm()
                        and user.get_property('code_ua')
                            == resource.get_code_ua()):
                    return False
            elif user.is_bdp():
                if not (resource.is_bdp()
                        and user.get_property('departement')
                            == resource.get_departement()):
                    return False
            # Must be registered for this year
            return self.has_user_role(user.name, 'members')
        return False


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
                if not (resource.is_bm()
                        and user.get_property('code_ua')
                            == resource.get_code_ua()):
                    return False
            elif user.is_bdp():
                if not (resource.is_bdp()
                        and user.get_property('departement')
                            == resource.get_departement()):
                    return False
            # Must be registered for this year
            if not self.has_user_role(user.name, 'members'):
                return False
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
