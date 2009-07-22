# -*- coding: UTF-8 -*-
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

# Import from the Standard Library
from os import getcwd
from os.path import join
from datetime import datetime, date
from time import time
from operator import itemgetter

# Import from itools
from itools import uri
from itools.core import merge_dicts
from itools.datatypes import String, Boolean
from itools.gettext import MSG
from itools.xapian import PhraseQuery, AndQuery, OrQuery
from itools.datatypes import Unicode
from itools.web import BaseView, STLView, STLForm

# Import from ikaaro
from ikaaro.views import SearchForm
from ikaaro.user import crypt_password
from ikaaro.resource_views import LoginView

# Import from scrib
from form import quote_namespace
from form_bm import FormBM
from form_bdp import FormBDP
from forms import Forms
from user import ScribUser
from utils import all_bm, all_bdp, get_bm, get_connection


class Root_Login(LoginView):

    template = '/ui/scrib/Root_login.xml'

    def get_namespace(self, resource, context):
        namespace = {}
        here = context.resource
        site_root = here.get_site_root()
        namespace['action'] = '%s/;login' % here.get_pathto(site_root)
        namespace['username'] = context.get_form_value('username')
        return namespace


    def action(self, resource, context, form):
        goto = LoginView.action(self, resource, context, form)
        user = context.user
        if user is None:
            return goto
        if user.name == 'VoirSCRIB' or user.is_admin(user, resource):
            return uri.get_reference('./')
        elif user.is_BM():
            path = 'BM%s/%s' % (user.get_year(), user.get_BM_code())
            report = resource.get_resource(path)
            return uri.get_reference('%s/' % path)
        else:
            path = 'BDP%s/%s' % (user.get_year(), user.get_department())
            report = resource.get_resource(path)
            return uri.get_reference('%s/' % path)



class NewReportsForm(STLForm):

    access = 'is_admin'
    title = u'Ajouter'
    subtitle = u'Rapport'
    #icon = BaseRoot.new_resource_form__icon__
    template = '/ui/scrib/Root_new_reports.xml'

    def get_namespace(self, resource, context):
        namespace = {}
        today = date.today()
        ### BDP form
        years = [
          {'value': x,
           'is_disabled': resource.get_resource('BDP'+str(x), soft=True) is not None,
           'is_selected': False}
                  for x in range(today.year - 2, today.year + 4) ]
        # Select one
        for i in [2, 3, 4, 5, 1, 0]:
            if years[i]['is_disabled'] is False:
                years[i]['is_selected'] = True
                break
        namespace['years'] = years
        ### BM form
        years = [
          {'value': x,
           'is_disabled': resource.get_resource('BM'+str(x), soft=True) is not None,
           'is_selected': False}
                  for x in range(today.year - 2, today.year + 4) ]
        # Select one
        for i in [2, 3, 4, 5, 1, 0]:
            if years[i]['is_disabled'] is False:
                years[i]['is_selected'] = True
                break
        namespace['BMyears'] = years
        return namespace


    def action_new_BM_reports(self, resource, context, form):
        """ """
        # Add reports container
        year = context.get_form_value('year')
        report_name = 'BM' + str(year)
        # Add reports and users, one per department
        reports = Forms.make_resource(Forms, resource, report_name)
        users = resource.get_resource('users')

        bm_len =  all_bm.get_nrows()
        bib_municipales = list(all_bm.get_rows())
        # so we sort by integers values
        bib_municipales.sort(key=itemgetter(0))

        t = time()
        for i, bib in enumerate(bib_municipales):
            code = bib.get_value('code')
            name = bib.get_value('name')
            dep = bib.get_value('dep')
            # Add report
            FormBM.make_resource(FormBM, reports, code, **{'title': name})
            # Add user
            username = 'BM%s' % code
            if users.get_resource(username, soft=True) is None:
                ScribUser.make_resource(ScribUser, users, username,
                                      username=username,
                                      password=crypt_password(username))
            if i % 10 == 0:
                print '%s/%s' % (i, bm_len), dep, code, username
        report_m = int(time() - t)
        print 'users and reports set ', report_m
        secondes = int(time() - t)
        minutes = secondes // 60
        message = (u"Les rapports des BM pour l'année {year} ont été "
                   u"ajoutés, ainsi que les utilisateurs associés : "
                   u"BMxxxx:BMxxxx, BMyyyy:BMyyyy, etc. "
                   u"en {temps} {unite}")
        message.format(year=year, temps=minutes or secondes,
                       unite=minutes and u'minutes' or u'secondes')
        return context.come_back(MSG(message), goto=';browse_content')


    def action_new_BDP_reports(self, resource, context, form):
        """ patern for BDP users is BDPxx_Year"""
        # Add reports container
        year = context.get_form_value('year')
        name = 'BDP' + str(year)
        reports = Forms.make_resource(Forms, resource, name)
        # Add reports and users, one per department
        users = resource.get_resource('users')
        for bib in all_bdp.get_rows():
            name = bib.get_value('code')
            title = bib.get_value('name')
            # Add report
            FormBDP.make_resource(FormBDP, reports, name, **{'title': title})
            # Add user
            username = 'BDP%s' % name
            if users.get_resource(username, soft=True) is None:
                ScribUser.make_resource(ScribUser, users, username,
                                      username=username,
                                      password=crypt_password(username))

        message = MSG(
                   u"Les rapports des BDP pour l'année %s ont été "
                   u"ajoutés, et leurs utilisateurs associés BDPxx:BDPxx, "
                   u"BDPyy:BDPyy, etc." % year)
        return context.come_back(message, goto=';browse_content')


class Root_CreerVoirSCRIB(BaseView):

    access = 'is_admin'
    title = u"Créer VoirSCRIB"

    def GET(self, resource, context):
        username = 'VoirSCRIB'
        password = 'BMBDP'

        users = resource.get_resource('users')
        if users.get_resource(username, soft=True) is not None:
            return context.come_back(MSG(u"Le compte VoirSCRIB existe déjà."))

        ScribUser.make_resource(ScribUser, users, username, username=username,
                              password=crypt_password(password))

        # Était un GET
        context.commit = True

        return context.come_back(MSG(u"Compte VoirSCRIB créé."))


class Root_HELP(STLView):

    access = True
    title = u'Aide'
    #icon = '/ui/icons/16x16/help.png'
    template = '/ui/scrib/Form_help.xml'


class Root_ExportForm(STLForm):

    access = 'is_admin'
    title = u"Export"
    #icon = File.download_form__icon__
    template = '/ui/scrib/Root_export.xml'


    def action(self, resource, context, form):

        __cache__ = {}

        def get_form_and_namespace(container, name):
            if name not in __cache__:
                form = container.get_resource(name)
                schema = form.get_scrib_schema()
                namespace = form.get_namespace(context)
                quote_namespace(namespace, schema)
                __cache__[name] = (form, namespace)

            return __cache__[name]


        def export_adr(container, output, context):
            """Ajout ALP - 27 nov 2007
            """
            folder = container.handler
            names = [o.name for o in container.search_resources(state='public')]

            # Adresses déjà exportées
            if container.is_BM():
                query = ("SELECT code_bib FROM adresse08 "
                         "WHERE insee is not null")
            else:
                query = ("SELECT dept FROM adresse08 "
                         "WHERE type_adr='3' and code_ua is not null")
            connexion = get_connection()
            cursor = connexion.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            adresses_connues = []
            for result in results:
                try:
                    value = str(int(result[0]))
                except ValueError:
                    # Corse
                    value = str(result[0])
                adresses_connues.append(value)
            cursor.close()
            connexion.close()

            for name in names:
                form, namespace = get_form_and_namespace(container, name)
                namespace['myname'] = name
                if name in adresses_connues:
                    query = (u'UPDATE adresse08 SET libelle1="%(field1)s",'
                             u'libelle2="%(field2)s",local="%(field30)s",'
                             u'voie_num="%(field31)s",voie_type="%(field32)s",'
                             u'voie_nom="%(field33)s",cpbiblio="%(field4)s",'
                             u'ville="%(field5)s",cedexb="%(field6)s",'
                             u'directeu="%(field7)s",st_dir="%(field8)s",'
                             u'tele="%(field9)s",fax="%(field10)s",'
                             u'mel="%(field11)s",www="%(field12)s",'
                             u'intercom="%(field13)s",gestion="%(field14)s",'
                             u'gestion_autre="%(field15)s" '
                             u'where code_bib=%(myname)s;\n')
                else:
                    # N'est pas censé être utilisé dans 99 % des cas
                    query = (u'INSERT INTO adresse08 (insee,type_adr,mel,'
                             u'directeu,region,dept,libelle1,libelle2,local,'
                             u'cpbiblio,cedexb,fax,tele,www,code_bib,'
                             u'code_ua,ville,st_dir,type,intercom,gestion,'
                             u'gestion_autre,voie_num,voie_type,voie_nom,'
                             u'commune,minitel) VALUES ("%(insee)s",'
                             u'"%(type_adr)s","%(field11)s","%(field7)s",'
                             u'"%(region)s","%(dept)s","%(field1)s",'
                             u'"%(field2)s","%(field30)s","%(field4)s",'
                             u'"%(field6)s","%(field10)s","%(field9)s",'
                             u'"%(field12)s","%(myname)s","%(code_ua)s",'
                             u'"%(field5)s","%(field8)s","%(type)s",'
                             u'"%(field13)s","%(field14)s","%(field15)s",'
                             u'"%(field31)s","%(field32)s","%(field33)s",'
                             u'"%(commune)s","%(minitel)s");\n')
                query = query % namespace
                output.write(query.encode('latin1') + '\n')


        def export_bib(container, ouput, context):
            """ (bm|bdp)08
            """
            folder = container.handler
            names = [o.name for o in container.search_resources(state='public')]
            if len(names) == 0:
                output.write(u'-- aucune bibliothèque exportée'.encode('latin1'))
                return

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
        # 0006036 ne pas effacer cette table, on ne la gère pas
        #output.write('DELETE FROM adresse08;\n')
        output.write('DELETE FROM bm08;\n')
        output.write('DELETE FROM bdp08;\n')
        output.write('\n')

        BM2008 = resource.get_resource('BM2008')
        BDP2008 = resource.get_resource('BDP2008')
        output.write('-- ADRESSE\n')
        output.write('\n')
        export_adr(BM2008, output, context)
        export_adr(BDP2008, output, context)

        output.write('-- BM2008\n')
        output.write('\n')
        export_bib(BM2008, output, context)

        output.write('\n')
        output.write('-- BDP2008\n')
        output.write('\n')
        export_bib(BDP2008, output, context)

        output.close()

        return context.come_back(u"Fichier exporté dans '%s'" % output_path)


#########################################################################
# New User

class Root_NewBmForm(STLForm):

    access = 'is_admin'
    title = u"Nouvelle BM"

    template = '/ui/scrib/Root_new_bm.xml'

    def action(self, resource, context, form):
        code_bib = context.get_form_value('code_bib')
        codes = []

        for code in code_bib.split():
            if not all_bm.search(code=code):
                return context.come_back(u"Le code_bib $code n'est pas "
                        u"dans le fichier input_data/init_BM.txt installé.",
                        code=repr(code))
            codes.append(int(code))

        users = resource.get_resource('users')
        bm2008 = resource.get_resource('BM2008')

        for code in codes:
            name = str(code)
            # Add report
            bib = get_bm(name)
            ville = bib.get_value('name')
            if bm2008.has_resource(name, soft=True) is None:
                FormBM.make_resource(FormBM, bm2008, name, **{'title': ville})
            # Add user
            username = 'BM%s' % code
            if not users.has_resource(username):
                ScribUser.make_resoruce(ScribUser, users, username,
                                      username=username,
                                      password=crypt_password(username))

        message = (u"Formulaire et utilisateur ajoutés : "
                   u"code_bib={code_bib} ville={ville} dept={dept} "
                   u"code_insee={code_insee} login={login} password={password}")
        message.format(code_bib=code, ville=ville, dept=bib.get_value('dep'),
                       code_insee=bib.get_value('id'), login=username,
                       password=username)
        return context.come_back(message, goto=';new_bm_form')



class Root_PermissionsForm(SearchForm):

    title = u"Utilisateurs"
    search_template = '/ui/scrib/Root_permissions.xml'

    # XXX Get values from the request
    #sortby = context.get_form_values('sortby', default=['login_name'])
    #sortorder = context.get_form_value('sortorder', default='up')
    #start = context.get_form_value('batchstart', type=Integer, default=0)
    #size = 20
    access = 'is_admin' # XXX Acls ?

    query_schema = merge_dicts(
        SearchForm.query_schema,
        sort_by=String(default='login_name'),
        reverse=Boolean(default=False))

    table_columns = [('user_id', u'User ID'),
                     ('login_name', u'Login'),
                     ('role', u'Role')]


    def get_search_namespace(self, resource, context):
        namespace = {}


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
        return namespace


    def get_items(self, resource, context):
        search_bib = context.get_form_value('bib')
        search_ville = context.get_form_value('ville', type=Unicode)
        search_dep = context.get_form_value('dep', default='').upper()
        search_annee = context.get_form_value('annee')
        query = [PhraseQuery('format', 'user')]
        if search_bib == 'admins':
            any_admin = OrQuery(*[PhraseQuery('name', admin)
                for admin in self.get_property('admins')])
            query.append(any_admin)
        else:
            if search_bib == 'bm':
                query.append(PhraseQuery('stored_BM', True))
            elif search_bib == 'bdp':
                query.append(PhraseQuery('stored_BDP', True))
            if search_ville:
                query.append(PhraseQuery('user_town', search_ville))
            if search_dep:
                query.append(PhraseQuery('dep', search_dep))
            if search_annee:
                query.append(PhraseQuery('year', search_annee))

        query = AndQuery(*query)
        return resource.search(query).get_documents()


    def get_item_value(self, resource, context, item, column):
        user = item
        if column == 'user_id':
            href = '/users/%s' % user.name
            return user.name, href
        elif column == 'login_name':
            return user.username
        elif column == 'role':
            # Find out the user role
            user_id = user.name
            roles = resource.get_members_classified_by_role()
            for role in roles:
                if user_id in roles[role]:
                    break
            else:
                role = None
            role = resource.get_role_title(role)
            if role is None:
                if user.stored_BDP:
                    return u"BDP"
                elif user.stored_BM:
                    return u"BM"
                else:
                    return u""
            else:
                return role
        raise ValueError, u'Unknow column'


    def sort_and_batch(self, resource, context, results):
        # XXX
        return results


#########################################################################
# XXX Migrate to 060
# Debug
#########################################################################
#xchangepassword__access__ = 'is_admin'
#def xchangepassword(self, context):
#    users = self.get_resource('users')
#    for user in users.get_resources():
#        user.set_password('a')
#    # XXX écrit sur une méthode GET
#    context.commit = True
#    return context.come_back(u"Done", goto='/;browse_content')
