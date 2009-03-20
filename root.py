# -*- coding: UTF-8 -*-
# Copyright (C) 2006-2008 Hervé Cauwelier <herve@itaapy.com>
# Copyright (C) 2006-2008 ALPantin  <anne-laure.pantin@culture.gouv.fr>
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

# Import from the Standard Library
from os import getcwd
from os.path import join
from datetime import datetime, date
from time import time
from operator import itemgetter

# Import from itools
from itools import uri
from itools import vfs
from itools.catalog import EqQuery, AndQuery, OrQuery
from itools.datatypes import Unicode, Integer
from itools.web import get_context
from itools.stl import stl

# Import from ikaaro
from ikaaro.registry import register_object_class
from ikaaro.root import Root as BaseRoot
from ikaaro.file import File
from ikaaro.widgets import batch, table
from ikaaro.users import crypt_password

# Import from scrib
from form import Form
from form_bm import FormBM
from form_bdp import FormBDP
from forms import Forms
from user import ScribUser
from utils import all_bm, all_bdp, get_bm, get_connection


class Root(BaseRoot):

    class_id = 'Culture'
    class_version = '20080410'
    class_title = u"SCRIB"
    class_views = [['browse_content'], ['new_reports_form', 'new_bm_form'],
                   ['export_form'], ['permissions_form', 'new_user_form'],
                   ['edit_metadata_form'], ['help']]

    __roles__ = [{'name': 'admins', 'title': u'Admin'}]


    def before_traverse(self, context):
        # Set french as default language, whatever the browser config is
        context.accept_language.set('fr', 2.0)


    #########################################################################
    # Security
    #########################################################################
    browse_content__access__ = 'is_admin_or_consultant'


    def is_consultant(self, user, object):
        if user is None:
            return False
        return user.name == 'VoirSCRIB'


    def is_admin_or_consultant(self, user, object):
        if user is None:
            return False
        return self.is_admin(user, object) or self.is_consultant(user, object)


    def is_allowed_to_view(self, user, object):
        # Anonymous
        if user is None:
            return False
        # Admin
        if self.is_admin(user, object):
            return True
        # VoirSCRIB
        if user.name == 'VoirSCRIB':
            return True
        if isinstance(object, Form):
            # Check the year
            if user.get_year() != object.parent.get_year():
                return False
            # Check the department
            if user.is_BM():
                if user.get_BM_code() != object.name:
                    return False
            elif user.is_BDP():
                if user.get_department() != object.name:
                    return False
        return True


    def is_allowed_to_edit(self, user, object):
        # Admin
        if self.is_admin(user, object):
            return True
        # Anonymous
        if user is None or user.name == 'VoirSCRIB':
            return False
        if isinstance(object, Form):
            # Check the year
            if user.get_year() != object.parent.get_year():
                return False
            # Check the department
            if user.is_BM():
                if user.get_BM_code() != object.name:
                    return False
            elif user.is_BDP():
                if user.get_department() != object.name:
                    return False
            # Only if 'private' -> 'Vide', 'En cours'
            return object.get_workflow_state() == 'private'
        return False


    def is_allowed_to_trans(self, user, object, name):
        if user is None:
            return False

        context = get_context()
        root = context.root

        namespace = self.get_namespace()
        is_admin = self.is_admin(user, object)

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


    #########################################################################
    # User interface
    #########################################################################
    def get_skin(self):
        return self.get_object('ui/scrib')


    def get_available_languages(self):
        return ['fr']


    def get_default_language(self):
        return 'fr'


    #########################################################################
    # Login
    login_form__access__ = True
    def login_form(self, context):
        namespace = {}
        here = context.object
        site_root = here.get_site_root()
        namespace['action'] = '%s/;login' % here.get_pathto(site_root)
        namespace['username'] = context.get_form_value('username')

        template = self.get_object('/ui/scrib/Root_login.xml')
        return stl(template, namespace)


    def login(self, context):
        goto = BaseRoot.login(self, context)
        user = context.user
        if user is None:
            return goto
        if user.name == 'VoirSCRIB' or user.is_admin(user, self):
            return uri.get_reference(';%s' % self.get_firstview())
        elif user.is_BM():
            path = 'BM%s/%s' % (user.get_year(), user.get_BM_code())
            report = self.get_object(path)
            return uri.get_reference('%s/;%s' % (path, report.get_firstview()))
        else:
            path = 'BDP%s/%s' % (user.get_year(), user.get_department())
            report = self.get_object(path)
            return uri.get_reference('%s/;%s' % (path, report.get_firstview()))


    #########################################################################
    # New reports
    new_reports_form__access__ = 'is_admin'
    new_reports_form__label__ = u'Ajouter'
    new_reports_form__sublabel__ = u'Rapport'
    new_reports_form__icon__ = BaseRoot.new_resource_form__icon__
    def new_reports_form(self, context):
        namespace = {}
        today = date.today()
        ### BDP form
        years = [ {'value': x,
                   'is_disabled': self.has_object('BDP'+str(x)),
                   'is_selected': False}
                  for x in range(today.year - 2, today.year + 4) ]
        # Select one
        for i in [2, 3, 4, 5, 1, 0]:
            if years[i]['is_disabled'] is False:
                years[i]['is_selected'] = True
                break
        namespace['years'] = years
        ### BM form
        years = [ {'value': x,
                   'is_disabled': self.has_object('BM'+str(x)),
                   'is_selected': False}
                  for x in range(today.year - 2, today.year + 4) ]
        # Select one
        for i in [2, 3, 4, 5, 1, 0]:
            if years[i]['is_disabled'] is False:
                years[i]['is_selected'] = True
                break
        namespace['BMyears'] = years
        template = self.get_object('/ui/scrib/Root_new_reports.xml')
        return stl(template, namespace)


    new_BM_reports__access__ = 'is_admin'
    def new_BM_reports(self, context):
        """ """
        # Add reports container
        year = context.get_form_value('year')
        report_name = 'BM' + str(year)
        # Add reports and users, one per department
        reports = Forms.make_object(Forms, self, report_name)
        t = time()

        users = self.get_object('users')
        users.set_handler('VoirSCRIB', ScribUser(),
                **{'ikaaro:password': crypt_password('BMBDP')})
        report_c = int(time() -t); print 'get users, deep copy', report_c

        bm_len =  all_bm.get_nrows()
        bib_municipales = list(all_bm.get_rows())
        # so we sort by integers values
        bib_municipales.sort(key=itemgetter(0))
        for i, bib in enumerate(bib_municipales):
            code = bib.get_value('code')
            name = bib.get_value('name')
            dep = bib.get_value('dep')
            # Add report
            FormBM.make_object(FormBM, reports, code, **{'title': name})
            # Add user
            username = 'BM%s' % code
            if not users.has_object(username):
                user = ScribUser.make_object(ScribUser, users, username)
                user.set_password('BM%s' % code)
                self.set_user_role(username, 'bm')
            print '%s/%s' % (i, bm_len), dep, code, username
        report_m = int(time() -t)
        print 'users and reperts set ', report_m
        secondes = int(time() - t)
        minutes = secondes // 60
        message = (u"Les rapports des BM pour l'année $year ont été "
                   u"ajoutés, ainsi que les utilisateurs associés : "
                   u"BMxxxx:BMxxxx, BMyyyy:BMyyyy, etc. "
                   u"en ${temps} ${unite}")
        return context.come_back(message, goto=';browse_content',
                **{'year': year, 'temps': minutes or secondes,
                   'unite': minutes and u'minutes' or u'secondes'})


    new_BDP_reports__access__ = 'is_admin'
    def new_BDP_reports(self, context):
        """ patern for BDP users is BDPxx_Year"""
        # Add reports container
        year = context.get_form_value('year')
        name = 'BDP' + str(year)
        reports = Forms.make_object(Forms, self, name)
        # Add reports and users, one per department
        users = self.get_object('users')
        for bib in all_bdp.get_rows():
            name = bib.get('code')
            title = bib.get('name')
            # Add report
            FormBDP.make_object(FormBDP, reports, name, **{'title': title})
            # Add user
            username = 'BDP%s' % name
            if not users.has_object(username):
                user = ScribUser.make_object(ScribUser, users, username)
                user.set_password('BDP%s' % name)
                self.set_user_role(username, 'bdp')

        message = (u"Les rapports des BDP pour l'année $year ont été "
                   u"ajoutés, et leurs utilisateurs associés BDPxx:BDPxx, "
                   u"BDPyy:BDPyy, etc.")
        return context.come_back(message, goto=';browse_content', year=year)


    #########################################################################
    # Help
    help__access__ = True
    help__label__ = u'Aide'
    help__icon__ = '/ui/icons/16x16/help.png'
    def help(self, context):
        template = self.get_object('/ui/scrib/Form_help.xml')
        return template.to_str()


    #########################################################################
    # Export
    export_form__access__ = 'is_admin'
    export_form__label__ = u"Export"
    export_form__icon__ = File.download_form__icon__
    def export_form(self, context):
        template = self.get_object('/ui/scrib/Root_export.xml')
        return template.to_str()


    export__access__ = 'is_admin'
    def export(self, context):

        __cache__ = {}

        def get_form_and_namespace(container, name):
            if name not in __cache__:
                form = container.get_object(name)
                schema = form.get_schema()
                namespace = form.get_namespace(context)
                for key, value in namespace.items():
                    field_def = schema.get(key)
                    if field_def is not None:
                        ftype = field_def[0]
                        if ftype is Unicode:
                               if value is not None:
                                   value = (value.replace(u"€", u"eur")
                                                 .replace(u'"', u'\\"')
                                                 .replace(u"&quot;", u'\\"')
                                                 .replace(u"'", u"\\'"))
                               namespace[key] = value
                __cache__[name] = (form, namespace)

            return __cache__[name]


        def export_adr(container, output, context):
            """Ajout ALP - 27 nov 2007
            """
            folder = container.handler
            names = [name for name in container.get_names()
                        if name.isdigit() and (
                            folder.get_handler('%s.metadata' % name)\
                                    .get_property('state') == 'public')]
            for name in names:
                form, namespace = get_form_and_namespace(container, name)
                query = (u'UPDATE adresse SET libelle1="%(field1)s",'
                         u'libelle2="%(field2)s",local="%(field30)s",'
                         u'voie_num="%(field31)s",'
                         u'voie_type="%(field32)s",'
                         u'voie_nom="%(field33)s",cpbiblio="%(field4)s",'
                         u'ville="%(field5)s",cedexb="%(field6)s",'
                         u'directeu="%(field7)s",st_dir="%(field8)s",'
                         u'tele="%(field9)s",fax="%(field10)s",'
                         u'mel="%(field11)s",www="%(field12)s",'
                         u'intercom="%(field13)s",gestion="%(field14)s",'
                         u'gestion_autre="%(field15)s" where code_bib=')
                query = query % namespace
                query = query + name + ';'
                output.write(query.encode('latin1') + '\n')


        def export_bib(container, ouput, context):
            connexion = get_connection()
            cursor = connexion.cursor()
            folder = container.handler
            names = [name for name in container.get_names()
                        if name.isdigit() and (
                            folder.get_handler('%s.metadata' % name)\
                                    .get_property('state') == 'public')]
            if len(names) == 0:
                output.write(u'-- aucune bibliothèque exportée'.encode('latin1'))
                return

            # adresse
            keys = ', '.join(names)
            if container.is_BM():
                query = "select * from adresse where insee is not null and code_bib in (%s)" % keys
            else:
                query = "select * from adresse where type_adr='3' and code_ua is not null and dept in (%s)" % keys
            cursor.execute(query)
            resultset = cursor.fetchall()
            cursor.close()
            connexion.close()
            if not resultset:
                context.commit = False
                return context.come_back(u'La requête "$query" a échoué',
                        query=query)

            for result in resultset:
                values = []
                for value in result:
                    if value is None:
                        values.append('NULL')
                    elif isinstance(value, str):
                        if "'" in value:
                            value = value.replace("'", "\\'")
                        values.append("'%s'" % value)
                    else:
                        values.append(str(value))
                values = ','.join(values)
                output.write('INSERT INTO adresse VALUES (%s);\n' % values)

            output.write('\n')

            # (bm|bdp)07
            for name in names:
                form, namespace = get_form_and_namespace(container, name)
                query = form.get_export_query(namespace)
                output.write(query.encode('latin1') + '\n')

        output_path = join(getcwd(), 'exportscrib.sql')
        output = open(output_path, 'w')
        output.write(u'-- Généré le %s\n'.encode('latin1') % datetime.now())
        output.write('\n')

        output.write(u'-- Réinitialisation'.encode('latin1'))
        output.write('\n')
        #output.write('DELETE FROM adresse;\n')
        output.write('DELETE FROM bm07;\n')
        output.write('DELETE FROM bdp07;\n')
        output.write('\n')

        BM2007 = self.get_object('BM2007')
        BDP2007 = self.get_object('BDP2007')
        output.write('-- ADRESSE\n')
        output.write('\n')
        export_adr(BM2007, output, context)
        export_adr(BDP2007, output, context)

        output.write('-- BM2007\n')
        output.write('\n')
        export_bib(BM2007, output, context)

        output.write('\n')
        output.write('-- BDP2007\n')
        output.write('\n')
        export_bib(BDP2007, output, context)

        output.close()

        return context.come_back(u"Fichier exporté dans '$output_path'",
                output_path=output_path)


    #########################################################################
    # New User
    new_bm_form__access__ = 'is_admin'
    new_bm_form__sublabel__ = u"Nouvelle BM"
    def new_bm_form(self, context):
        template = self.get_object('/ui/scrib/Root_new_bm.xml')
        return template.to_str()


    new_bm__access__ = 'is_admin'
    def new_bm(self, context):
        code_bib = context.get_form_value('code_bib')
        codes = []

        for code in code_bib.split():
            if not all_bm.search(code=code):
                return context.come_back(u"Le code_bib $code n'est pas "
                        u"dans le fichier input_data/init_BM.txt installé.",
                        code=repr(code))
            codes.append(int(code))

        users = self.get_object('users')
        bm2007 = self.get_object('BM2007')

        for code in codes:
            name = str(code)
            # Add report
            bib = get_bm(name)
            ville = bib.get_value('name')
            if not bm2007.has_object(name):
                FormBM.make_object(FormBM, bm2007, name, **{'title': ville})
            # Add user
            username = 'BM%s' % code
            if not users.has_object(username):
                user = ScribUser.make_object(ScribUser, users, username)
                user.set_password(username)
                self.set_user_role(username, 'bm')

        message = (u"Formulaire et utilisateur ajoutés : "
                   u"code_bib=$code_bib ville=$ville dept=$dept "
                   u"code_insee=$code_insee login=$login password=$password")

        return context.come_back(message, goto=';new_bm_form',
                **{'code_bib': code, 'ville': ville,
                    'dept': bib.get_value('dep'),
                    'code_insee': bib.get_value('id'), 'login': username,
                    'password': username})


    #########################################################################
    # Users
    #########################################################################
    permissions_form__label__ = u"Utilisateurs"
    def permissions_form(self, context):
        namespace = {}

        # Get values from the request
        sortby = context.get_form_values('sortby', default=['login_name'])
        sortorder = context.get_form_value('sortorder', default='up')
        start = context.get_form_value('batchstart', type=Integer, default=0)
        size = 20

        # The search form
        search_bib = context.get_form_value('bib')
        search_ville = context.get_form_value('ville', type=Unicode)
        search_dep = context.get_form_value('dep', default='').upper()
        search_annee = context.get_form_value('annee')

        namespace['search_admins'] = search_bib == 'admins'
        namespace['search_bm'] = search_bib == 'bm'
        namespace['search_bdp'] = search_bib == 'bdp'
        namespace['search_all'] = not search_bib
        namespace['ville'] = search_ville
        namespace['dep'] = search_dep
        namespace['annee'] = search_annee

        # Search
        query = [EqQuery('format', 'user')]
        if search_bib == 'admins':
            any_admin = OrQuery(*[EqQuery('name', admin)
                for admin in self.get_property('admins')])
            query.append(any_admin)
        else:
            if search_bib == 'bm':
                query.append(EqQuery('stored_BM', '1'))
            elif search_bib == 'bdp':
                query.append(EqQuery('stored_BDP', '1'))
            if search_ville:
                query.append(EqQuery('user_town', search_ville))
            if search_dep:
                query.append(EqQuery('dep', search_dep))
            if search_annee:
                query.append(EqQuery('year', search_annee))

        query = AndQuery(*query)
        results = self.search(query)

        # Build the namespace
        roles = self.get_members_classified_by_role()
        members = []
        for user in results.get_documents():
            user_id = user.name
            # Find out the user role
            for role in roles:
                if user_id in roles[role]:
                    break
            else:
                role = None
            # Build the namespace for the user
            ns = {}
            ns['checkbox'] = True
            ns['id'] = user_id
            ns['img'] = None
            # Email
            href = '/users/%s' % user_id
            ns['user_id'] = user_id, href
            # Title
            ns['login_name'] = user.username
            # Role
            role = self.get_role_title(role)
            if role is None:
                if user.stored_BDP:
                    ns['role'] = u"BDP"
                elif user.stored_BM:
                    ns['role'] = u"BM"
                else:
                    ns['role'] = u""
            else:
                ns['role'] = role
            # Append
            members.append(ns)

        # Sort
        members.sort(key=itemgetter(sortby[0]), reverse=sortorder=='down')

        # Batch
        total = len(members)
        members = members[start:start+size]

        # The columns
        columns = [('user_id', u'User ID'),
                   ('login_name', u'Login'),
                   ('role', u'Role')]

        # The actions
        actions = [('permissions_del_members', self.gettext(u'Delete'),
                    'button_delete', None)]
        user = context.user
        ac = self.get_access_control()
        actions = [
            x for x in actions if ac.is_access_allowed(user, self, x[0]) ]

        namespace['batch'] = batch(context.uri, start, size, total)

        namespace['table'] = table(columns, members, sortby, sortorder,
                                   actions, self.gettext)

        handler = self.get_object('/ui/scrib/Root_permissions.xml')
        return stl(handler, namespace)


    #########################################################################
    # Debug
    #########################################################################
    xchangepassword__access__ = 'is_admin'
    def xchangepassword(self, context):
        users = self.get_object('users')
        for user in users.get_objects():
            user.set_password('a')
        # XXX écrit sur une méthode GET
        context.commit = True
        return context.come_back(u"Done", goto='/;browse_content')


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



register_object_class(Root)
