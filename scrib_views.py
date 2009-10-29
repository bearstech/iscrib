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
from itools.core import merge_dicts
from itools.datatypes import Date, Integer
from itools.gettext import MSG
from itools.uri import get_reference
from itools.web import BaseView, STLView, STLForm

# Import from ikaaro
from ikaaro.forms import ReadOnlyWidget, DateWidget
from ikaaro.resource_views import LoginView, DBResource_Edit

# Import from scrib
from datatypes import DateLitterale
from form import quote_namespace
from utils import get_connection


class Scrib_Login(LoginView):
    template = '/ui/scrib/Scrib_login.xml'


    def get_namespace(self, resource, context):
        namespace = LoginView.get_namespace(self, resource, context)
        echeance_bm = resource.get_property('echeance_bm')
        namespace['echeance_bm'] = DateLitterale.encode(echeance_bm)
        echeance_bdp = resource.get_property('echeance_bdp')
        namespace['echeance_bdp'] = DateLitterale.encode(echeance_bdp)
        return namespace


    def action(self, resource, context, form):
        goto = LoginView.action(self, resource, context, form)
        user = context.user
        if user is None:
            return goto
        elif user.is_bm() or user.is_bdp():
            return get_reference('/users/%s' % user.name)
        return goto



class  Scrib_Edit(DBResource_Edit):
    schema = merge_dicts(DBResource_Edit.schema,
                         annee=Integer(mandatory=True, readonly=True),
                         echeance_bm=Date(mandatory=True),
                         echeance_bdp=Date(mandatory=True))
    widgets = (DBResource_Edit.widgets[:3]
               + [ReadOnlyWidget('annee', readonly=True,
                      title=MSG(u"Année des données collectées")),
                  DateWidget('echeance_bm',
                      title=MSG(u"Date d'échéance des BM")),
                  DateWidget('echeance_bdp',
                      title=MSG(u"Date d'échéance des BDP"))]
               + DBResource_Edit.widgets[3:])


    def action(self, resource, context, form):
        DBResource_Edit.action(self, resource, context, form)
        if not context.edit_conflict:
            resource.set_property('echeance_bm', form['echeance_bm'])
            resource.set_property('echeance_bdp', form['echeance_bdp'])



class Scrib_ExportForm(STLForm):
    access = 'is_admin'
    title = MSG(u"Export")
    #icon = File.download_form__icon__
    template = '/ui/scrib/Scrib_export.xml'


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



class Scrib_Help(STLView):
    access = True
    title = MSG(u"Aide")
    #icon = '/ui/icons/16x16/help.png'
    template = '/ui/scrib/Form_help.xml'



class Scrib_ChangePassword(BaseView):

    def GET(self, resource, context):
        access = 'is_admin'
        users = resource.get_resource('/users')
        for user in users.get_resources():
            user.set_password('a')
        # XXX écrit sur une méthode GET
        context.commit = True
        return context.come_back(MSG(u"Done"), goto='/;browse_content')
