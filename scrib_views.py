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
from itools.datatypes import Date, Integer, Email, Unicode
from itools.gettext import MSG
from itools.uri import get_reference, get_uri_path
from itools.stl import stl
from itools.web import BaseView, STLForm, INFO, ERROR
from itools.xml import XMLParser

# Import from ikaaro
from ikaaro.folder_views import GoToSpecificDocument
from ikaaro.forms import XHTMLBody, ReadOnlyWidget, DateWidget, RTEWidget
from ikaaro.forms import TextWidget, AutoForm
from ikaaro.resource_views import LoginView, DBResource_Edit
from ikaaro.views import IconsView
from ikaaro.website_views import ForgottenPasswordForm

# Import from scrib
from datatypes import DateLitterale, Identifiant
from form import quote_namespace
from utils import get_connection


def find_user(username, context):
    root = context.root
    results = root.search(username=username)
    if not len(results):
        results = root.search(email=username)
        if not len(results):
            message = ERROR(u"""L'utilisateur "{username}" n'existe """
                    u"pas.", username=username)
            context.message = message
            return
    return root.get_user(results.get_documents()[0].name)



class Scrib_Admin(IconsView):
    access = 'is_admin'
    title = MSG(u"Administration de Scrib")
    icon = 'settings.png'


    def get_namespace(self, resource, context):
        items = [{'icon': '/ui/icons/48x48/folder.png',
                  'title': u"BM",
                  'description': u"Rechercher une BM",
                  'url': 'bm'}]
        items.append({'icon': '/ui/icons/48x48/folder.png',
                      'title': u"BDP",
                      'description': u"Rechercher une BDP",
                      'url': 'bdp'})
        items.append({'icon': '/ui/icons/48x48/html.png',
                      'title': u"Aide générale",
                      'description': u"Modifier l'aide générale",
                      'url': 'aide/;edit'})
        for page in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'):
            items.append({'icon': '/ui/icons/48x48/html.png',
                          'title': u"Page %s" % page,
                          'description': (u"Modifier l'aide de la page %s" %
                              page),
                          'url': 'Page%s/;edit' % page})
        for name in ('edit', 'browse_users', 'add_user',
                'edit_virtual_hosts'):
            view = resource.get_view(name)
            items.append({
                'icon': resource.get_method_icon(view, size='48x48'),
                'title': view.title,
                'description': view.description,
                'url': ';%s' % name})
        return {'title': self.title,
                'batch': None,
                'items': items}



class Scrib_Login(LoginView):
    template = '/ui/scrib2009/Scrib_login.xml'


    def get_namespace(self, resource, context):
        namespace = LoginView.get_namespace(self, resource, context)
        # La page n'apparaît pas forcément sur le site_root
        site_root = context.site_root
        echeance_bm = site_root.get_property('echeance_bm')
        namespace['echeance_bm'] = DateLitterale.encode(echeance_bm)
        echeance_bdp = site_root.get_property('echeance_bdp')
        namespace['echeance_bdp'] = DateLitterale.encode(echeance_bdp)
        context.response.status = 403
        return namespace


    def action(self, resource, context, form):
        username = form['username'].strip()
        password = form['password']
        # Check the user exists
        user = find_user(username, context)
        if user is None:
            return
        # Check the password is right
        if not user.authenticate(password):
            context.message = ERROR(u"Le mot de passe est incorrect.")
            return
        # Set cookie
        user.set_auth_cookie(context, password)
        # Set context
        context.user = user
        # Come back
        referrer = context.request.referrer
        if referrer is None:
            goto = get_reference('./')
        else:
            if user.is_bm() or user.is_bdp():
                goto = get_reference('/users/%s' % user.name)
            else:
                path = get_uri_path(referrer)
                if path.endswith(';login'):
                    goto = get_reference('./')
                else:
                    goto = referrer
        return context.come_back(INFO(u"Welcome!"), goto)



class Scrib_Register(AutoForm):
    access = True
    title = MSG(u"Crééz votre compte pour l'année 2009")
    schema = {'email': Email(mandatory=True),
              'identifiant': Identifiant(mandatory=True)}
    widgets = [TextWidget('email', title=MSG(u"Adresse mél")),
               TextWidget('identifiant', title=MSG(u"Identifiant"))]
    submit_value = MSG(u"Continuer")


    def is_valid(self, resource, context, form):
        email = form['email']
        identifiant = form['identifiant']

        # Do we already have a user with that email?
        root = context.root
        results = root.search(email=email)
        if len(results):
            context.message = ERROR(u"Ce mél est déjà utilisé : essayez "
                    u"le rappel de mot de passe")
            return False

        # Is the code_ua valid?
        code_ua = int(identifiant[2:])
        form = resource.get_resource('bm/%s' % code_ua, soft=True)
        if form is None:
            context.message = ERROR(u"Cet identifiant est invalide.")
            return False

        # Do we already have a user with that code_ua?
        results = root.search(format='user', code_ua=code_ua)
        if len(results):
            # Same email already tested so it's another one with the code_ua
            context.message = ERROR(u"Cet identifiant est enregistré par un "
                    u"autre utilisateur.")
            return False

        return True


    def action(self, resource, context, form):
        if not self.is_valid(resource, context, form):
            return

        return resource.confirm.GET(resource, context)



class Scrib_ForgottenPassword(ForgottenPasswordForm):

    def action(self, resource, context, form):
        username = form['username'].strip()
        username = username

        # Get the user with the given login name
        user = find_user(username, context)
        if user is None:
            return

        # Send email of confirmation
        email = user.get_property('email')
        user.send_forgotten_password(context, email)

        handler = resource.get_resource('/ui/website/forgotten_password.xml')
        return stl(handler)



class Scrib_Confirm(STLForm):
    access = True
    title = MSG(u"Confirmation de création de compte")
    template = '/ui/scrib2009/Scrib_confirm.xml'
    schema = {'email': Email(mandatory=True),
              'identifiant': Identifiant(mandatory=True)}

    def get_namespace(self, resource, context):
        identifiant = context.get_form_value('identifiant')
        code_ua = int(identifiant[2:])
        form = resource.get_resource('bm/%s' % code_ua)
        return {'email': context.get_form_value('email'),
                'identifiant': identifiant,
                'title': form.get_title()}


    def action(self, resource, context, form):
        if not resource.register.is_valid(resource, context, form):
            return

        # Add the user
        email = form['email']
        user = resource.get_resource('/users').set_user(email, password=None)
        identifiant = form['identifiant']
        code_ua = int(identifiant[2:])
        user.set_property('username', 'BM%s' % code_ua)
        form = resource.get_resource('bm/%s' % code_ua)
        user.set_property('title', form.get_title(), language='fr')
        user.set_property('code_ua', code_ua)
        user.set_property('departement', form.get_property('departement'))
        # Set the role
        resource.set_user_role(user.name, 'members')

        # Send confirmation email
        user.send_confirmation(context, email)

        # Update "mel" field
        form.handler.set_value('A114', email)

        # Bring the user to the login form
        message = (u"<p>Un mél de confirmation vient de vous être envoyé à "
                u"l'adresse <strong>{email}</strong>.</p><p>Suivez ses "
                u"instructions pour activer votre compte.</p>".format(email=email))
        return XMLParser(message.encode('utf-8'))
        




class Scrib_Edit(DBResource_Edit):
    description = MSG(u"Paramétrer Scrib")
    icon = 'preferences.png'
    schema = merge_dicts(DBResource_Edit.schema,
            annee=Integer(mandatory=True, readonly=True),
            echeance_bm=Date(mandatory=True),
            echeance_bdp=Date(mandatory=True),
            responsable_bm=Unicode(mandatory=True),
            responsable_bdp=Unicode(mandatory=True),
            adresse=XHTMLBody,
            contacts=XHTMLBody)
    widgets = (DBResource_Edit.widgets[:3]
            + [ReadOnlyWidget('annee', readonly=True,
                    title=MSG(u"Année des données collectées")),
                DateWidget('echeance_bm',
                    title=MSG(u"Date d'échéance des BM")),
                DateWidget('echeance_bdp',
                    title=MSG(u"Date d'échéance des BDP")),
                TextWidget('responsable_bm', title=MSG(u"Mél d'envoi "
                    u"des accusés de réception au responsable BM "
                    u"(format « Nom <mél> »)")),
                TextWidget('responsable_bdp', title=MSG(u"Mél d'envoi "
                    u"des accusés de réception au responsable BDP "
                    u"(format « Nom <mél> »)")),
                RTEWidget('adresse',
                      title=MSG("Bandeau : adresse de la direction")),
                RTEWidget('contacts',
                    title=MSG("Bandeau : contacts BM et BDP"))]
             + DBResource_Edit.widgets[3:])


    def action(self, resource, context, form):
        DBResource_Edit.action(self, resource, context, form)
        if not context.edit_conflict:
            resource.set_property('echeance_bm', form['echeance_bm'])
            resource.set_property('echeance_bdp', form['echeance_bdp'])
            resource.set_property('responsable_bm', form['responsable_bm'])
            resource.set_property('responsable_bdp', form['responsable_bdp'])
            resource.set_property('adresse', form['adresse'])
            resource.set_property('contacts', form['contacts'])



class Scrib_ExportForm(STLForm):
    access = 'is_admin'
    title = MSG(u"Export")
    #icon = File.download_form__icon__
    template = '/ui/scrib2009/Scrib_export.xml'


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



class Scrib_ChangePassword(BaseView):

    def GET(self, resource, context):
        access = 'is_admin'
        users = resource.get_resource('/users')
        for user in users.get_resources():
            user.set_password('a')
        # XXX écrit sur une méthode GET
        context.commit = True
        return context.come_back(MSG(u"Done"), goto='/;browse_content')


class GoToHome(GoToSpecificDocument):
    access = 'is_authenticated'


    def get_specific_document(self, resource, context):
        return '/users/%s' % context.user.name
