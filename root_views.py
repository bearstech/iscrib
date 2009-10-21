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
from datetime import datetime

# Import from itools
from itools import uri
from itools.core import merge_dicts
from itools.datatypes import String, Boolean
from itools.gettext import MSG
from itools.xapian import PhraseQuery, AndQuery, OrQuery
from itools.datatypes import Unicode
from itools.web import BaseView, STLView, STLForm

# Import from ikaaro
from ikaaro.folder_views import Folder_BrowseContent
from ikaaro.resource_views import LoginView

# Import from scrib
from form import quote_namespace
from utils import get_connection


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
        elif user.is_bm():
            path = 'BM%s/%s' % (user.get_year(), user.get_BM_code())
            report = resource.get_resource(path)
            return uri.get_reference('%s/' % path)
        else:
            path = 'BDP%s/%s' % (user.get_year(), user.get_department())
            report = resource.get_resource(path)
            return uri.get_reference('%s/' % path)



class Root_Help(STLView):
    access = True
    title = MSG(u"Aide")
    #icon = '/ui/icons/16x16/help.png'
    template = '/ui/scrib/Form_help.xml'



class Root_ExportForm(STLForm):
    access = 'is_admin'
    title = MSG(u"Export")
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
            if container.is_bm():
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

        msg = MSG(u"Fichier exporté dans '%s'" % output_path)
        return context.come_back(msg)



class Root_PermissionsForm(Folder_BrowseContent):
    access = 'is_admin'
    title = MSG(u"Utilisateurs")
    search_template = '/ui/scrib/Root_permissions.xml'

    query_schema = merge_dicts(
        Folder_BrowseContent.query_schema,
        sort_by=String(default='login_name'),
        reverse=Boolean(default=False))

    table_actions = []
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
        return resource.search(query)


    def get_item_value(self, resource, context, item, column):
        user, item_resource = item
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



class XChangePassword(BaseView):

    def GET(self, resource, context):
        access = 'is_admin'
        users = resource.get_resource('/users')
        for user in users.get_resources():
            user.set_password('a')
        # XXX écrit sur une méthode GET
        context.commit = True
        return context.come_back(MSG(u"Done"), goto='/;browse_content')
