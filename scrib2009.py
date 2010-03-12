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
from sys import stdout, stdin

# Import from itools
from itools.core import get_abspath, merge_dicts
from itools.datatypes import Unicode, Integer, Date, Boolean, Tokens
from itools.gettext import MSG
from itools.uri import resolve_uri2
from itools.web import get_context

# Import from ikaaro
from ikaaro.folder_views import Folder_BrowseContent, Folder_PreviewContent
from ikaaro.forms import XHTMLBody
from ikaaro.registry import register_resource_class
from ikaaro.resource_views import DBResource_Backlinks
from ikaaro.revisions_views import DBResource_LastChanges
from ikaaro.utils import crypt_password
from ikaaro.webpage import WebPage
from ikaaro.website import WebSite

# Import from scrib
from bm2009 import BM2009Form
from bdp2009 import BDP2009Form
from form import Form, MultipleForm
from forms import Forms
from scrib2009_views import Scrib_Admin, Scrib_Login, Scrib_Edit
from scrib2009_views import Scrib_Register, Scrib_Confirm
from scrib2009_views import Scrib_ExportSql, Scrib_ChangePassword
from scrib2009_views import Scrib_ForgottenPassword, Scrib_Importer
from user import ScribUser
from utils import UsersCSV, get_config, get_adresse, ProgressMeter


class Scrib2009(WebSite):
    class_id = 'Scrib2009'
    class_title = MSG(u"Scrib 2009")
    class_skin = 'ui/scrib2009'
    class_views = ['admin'] + WebSite.class_views

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
    export_sql = Scrib_ExportSql()
    importer = Scrib_Importer()
    browse_content = Folder_BrowseContent(access='is_admin_or_voir_scrib')
    preview_content = Folder_PreviewContent(access='is_admin_or_voir_scrib')
    backlinks = DBResource_Backlinks(access='is_admin_or_voir_scrib')
    last_changes = DBResource_LastChanges(access='is_admin_or_voir_scrib')
    xchangepassword = Scrib_ChangePassword()


    ########################################################################
    # Skeleton
    @staticmethod
    def _make_resource(cls, folder, name, annee=2009):
        """Création de l'application/année et ses sous-ressources
        """
        # FIXME Accès MySQL à l'initialisation
        target = resolve_uri2(folder.uri, '..')
        config = get_config(target=target)
        if config.get_value('sql-host') is None:
            context = get_context()
            try:
                context.server
            except AttributeError:
                # Faux contexte de icms-init
                config.append_comment('\nScrib MySQL')
                for arg, default in [('host', 'localhost'), ('port', 3306),
                        ('db', 'scrib'), ('user', 'scrib'), ('passwd', ''),
                        ('encoding', 'latin1')]:
                    stdout.write("sql-%s = [%s] " % (arg, default))
                    value = stdin.readline().strip() or default
                    config.set_value('sql-%s' % arg, value)
                config.save_state()
            else:
                # contexte web
                raise ValueError, "%s: sql-* undefined" % config.uri
        print "Création de l'application..."
        WebSite._make_resource(cls, folder, name,
                title={'fr': u"Scrib %s" % annee},
                vhosts=('localhost', 'scrib%s' % annee),
                # Le compte VoirSCRIB est toujours le suivant après l'admin
                members=('1',),
                # Spécifique à l'année
                annee=annee,
                echeance_bm=date(2010, 4, 30),
                echeance_bdp=date(2010, 9, 15))
        # Pages
        print "Création des pages d'aide..."
        base_path = 'ui/scrib%s' % annee
        for filename, title in [('aide.xhtml', u"Aide"),
                                ('bm/PageA.xhtml', u"Page A"),
                                ('bm/PageB.xhtml', u"Page B"),
                                ('bm/PageC.xhtml', u"Page C"),
                                ('bm/PageD.xhtml', u"Page D"),
                                ('bm/PageE.xhtml', u"Page E"),
                                ('bm/PageF.xhtml', u"Page F"),
                                ('bm/PageG.xhtml', u"Page G"),
                                ('bm/PageH.xhtml', u"Page H")]:
            with open(get_abspath('%s/%s' % (base_path, filename))) as file:
                id = filename[filename.rfind('/') + 1:filename.rfind('.')]
                WebPage._make_resource(WebPage, folder, '%s/%s' % (name, id),
                        title={'fr': title}, state='public', language='fr',
                        body=file.read())
        # BM et BDP
        users_csv = UsersCSV(get_abspath('%s/users.csv' % base_path))
        for categorie, form_class in [('BM', cls.bm_class),
                ('BDP', cls.bdp_class)]:
            path = categorie.lower()
            print "Création des %s..." % categorie
            Forms._make_resource(Forms, folder, "%s/%s" % (name, path),
                                 title={'fr': unicode(categorie)})
            rows = users_csv.search(categorie=categorie)
            meter = ProgressMeter(len(rows))
            for i, row in enumerate(users_csv.get_rows(rows)):
                code_ua = row.get_value('code_ua')
                title = row.get_value('nom')
                departement = row.get_value('departement')
                # 0008082 handler avec données de la table adresse09
                try:
                    kw = get_adresse(code_ua,
                            'adresse%s' % str(annee)[-2:], target=target)
                except KeyError, e:
                    print str(e)
                    kw = {}
                if categorie == 'BM':
                    kw['A100'] = code_ua
                else:
                    kw['0'] = code_ua
                handler = form_class.class_handler(**kw)
                form_class._make_resource(form_class, folder,
                    '%s/%s/%s' % (name, path, code_ua),
                    body=handler.to_str(), code_ua=code_ua,
                    departement=departement, title={'fr': title})
                meter.show(i)
        # Compte spécial VoirSCRIB
        print "Création du compte VoirSCRIB..."
        try:
            users_handler = folder.get_handler('users')
        except LookupError:
            # Dans icms-init, on est les premiers à créer le compte
            ScribUser._make_resource(ScribUser, folder, "users/1",
                    username='VoirSCRIB', password=crypt_password('BMBDP'),
                    email='VoirSCRIB')
        else:
            print "  Déjà créé."
        print "Indexation de la base... (long)"


    ########################################################################
    # Metadata
    @classmethod
    def get_metadata_schema(cls):
        return merge_dicts(WebSite.get_metadata_schema(),
                # Surcharge de Website commune à toutes les années
                website_languages=Tokens(default=('fr',)),
                website_is_open=Boolean(default=True),
                # Spécifique à chaque année
                annee=Integer,
                echeance_bm=Date,
                echeance_bdp=Date,
                # Spécifique à toutes les années
                adresse=XHTMLBody(default=XHTMLBody.decode("""\
<p><span style="color: #000000;">Direction du livre et de la lecture</span></p>
<p><span style="color: #000000;">Bureau des bibliothèques territoriales</span></p>
<p><span style="color: #000000;">182, rue Saint-Honoré</span></p>
<p><span style="color: #000000;">75033 PARIS CEDEX 01</span></p>""")),
                contacts=XHTMLBody(default=XHTMLBody.decode("""\
<p><span style="color: #000000;">BDP : <strong><span style="color: #ffffff;"><a href="mailto:christophe.sene@culture.gouv.fr">christophe.sene@culture.gouv.fr</a></span></strong> 01 40 15 73 74</span></p>
<p><span style="color: #000000;">BM : <strong><span style="color: #ffffff;"><a href="mailto:denis.cordazzo@culture.gouv.fr">denis.cordazzo@culture.gouv.fr</a></span></strong> 01 40 15 74 85</span></p>""")),
                responsable_bm=Unicode(default=(u'Denis Cordazzo '
                    u'<denis.cordazzo@culture.gouv.fr>')),
                responsable_bdp=Unicode(default=(u'Christophe Sene '
                                 u'<christophe.sene@culture.gouv.fr>')))


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
            if self.is_admin(user, resource):
                if name in ['request', 'accept', 'publish']:
                    return resource.is_ready()
                else:
                    return True
            else:
                if name in ['request']:
                    return resource.is_ready()
                elif name in ['unrequest']:
                    return True
                else:
                    return False
        return WebSite.is_allowed_to_trans(self, user, resource, name)


    ########################################################################
    # API
    def get_year_suffix(self):
        # int(2009) -> '09'
        return str(self.get_property('annee'))[-2:]


    def get_scrib_user(self, categorie, identifiant, context):
        if categorie == 'BM':
            results = context.root.search(format='user', code_ua=identifiant)
        else:
            results = context.root.search(format='user',
                    departement=identifiant)
        if len(results):
            return results.get_documents()[0]
        return None


    def get_scrib_form(self, categorie, identifiant, context):
        if categorie == 'BM':
            results = context.root.search(format=self.bm_class.class_id,
                    code_ua=identifiant)
        else:
            results = context.root.search(format=self.bdp_class.class_id,
                    departement=identifiant)
        if len(results):
            return results.get_documents()[0]
        return None


###########################################################################
# Register
register_resource_class(Scrib2009)
