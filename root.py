# -*- coding: UTF-8 -*-
# Copyright (C) 2004 Luis Belmar Letelier <luis@itaapy.com>
# Copyright (C) 2006 Hervé Cauwelier <herve@itaapy.com>
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
from itools.datatypes import Unicode
from itools.web import get_context
from itools.stl import stl

# Import from ikaaro
from ikaaro.root import Root as BaseRoot
from ikaaro.registry import register_object_class

# Import from scrib
from Form import get_cursor
from form_bm import FormBM
from form_bdp import FormBDP
from forms import Forms
from user import bibUser
from utils import get_deps, get_BMs


class Root(BaseRoot):

    class_id = 'Culture'
    class_version = '20060802'
    class_title = u"SCRIB"


    _catalog_fields = BaseRoot._catalog_fields \
                      + [('user_town', 'text', True, False),
                         ('dep', 'keyword', True, True),
                         ('year', 'keyword', True, False),
                         ('is_BDP', 'bool', True, False),
                         ('is_BM', 'bool', True, False),
                         ('form_state', 'keyword', True, True),
                         ('code', 'keyword', True, False)]


    login_form__access__ = True
    def login_form(self, context):
        namespace = {'referer': context.get_form_value('referer', default=''),
                     'username': context.get_form_value('username', default='')}

        handler = self.get_handler('/ui/culture/SiteRoot_login.xml')
        return stl(handler, namespace)


    _get_handler = BaseRoot._get_handler


    def before_traverse(self, context):
        BaseRoot.before_traverse(self, context)
        # Set french as default language, whatever the browser config is
        accept = context.request.accept_language
        accept.set('fr', 1.5)


    #########################################################################
    # Security
    #########################################################################
    browse_list__access__ = 'is_admin'


    def is_consultant(self, user, object):
        if user is None:
            return False
        return user.name == 'VoirSCRIB'


    def is_admin_or_consultant(self, user, object):
        if user is None:
            return False
        return self.is_admin() or self.is_consultant()


    def is_allowed_to_view_form(self, user, object):
        # Anonymous
        if user is None:
            return False
        # Admin
        if self.is_admin():
            return True
        # VoirSCRIB
        if user.name == 'VoirSCRIB':
            return True
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


    def is_allowed_to_edit_form(self, user, object):
        # Admin
        if self.is_admin():
            return True
        # Anonymous
        if user is None:
            return False
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
    def get_skin_name(self):
        return 'scrib'


    def get_skin(self):
        return self.get_handler('ui/scrib')


    def get_available_languages(self):
        return ['fr']


    def get_default_language(self):
        return 'fr'


    def get_views(self):
        user = get_context().user
        if user is None:
            return ['login_form', 'help']

        if user.is_admin():
            return ['browse_thumbnails', 'new_reports_form', 'export_form',
                    'edit_metadata_form', 'help', 'catalog_form']

        if user.name == 'VoirSCRIB':
            return ['browse_thumbnails', 'help']

        return []


    def get_subviews(self, name):
        if name in ['browse_thumbnails', 'browse_list']:
            return ['browse_thumbnails', 'browse_list']
        elif name in ['new_reports_form', 'new_bm_form']:
            return ['new_reports_form', 'new_bm_form']
        return []


    #########################################################################
    # Login
    def login(self, context):
        goto = BaseRoot.login(self, context)
        user = context.user
        if user is None:
            return goto
        if user.is_admin() or user.name == 'VoirSCRIB':
            return uri.get_reference(';%s' % self.get_firstview())
        elif user.is_BM():
            path = 'BM%s/%s' % (user.get_year(), user.get_BM_code())
            report = self.get_handler(path)
            return uri.get_reference('%s/;%s' % (path, report.get_firstview()))
        else:
            path = 'BDP%s/%s' % (user.get_year(), user.get_department())
            report = self.get_handler(path)
            return uri.get_reference('%s/;%s' % (path, report.get_firstview()))


    #########################################################################
    # New reports
    new_reports_form__access__ = 'is_admin'
    new_reports_form__label__ = u'Ajouter'
    new_reports_form__sublabel__ = u'Rapport'
    def new_reports_form(self, context):
        namespace = {}
        today = date.today()
        ### BDP form
        years = [ {'value': x, 
                   'is_disabled': self.has_handler('BDP'+str(x)),
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
                   'is_disabled': self.has_handler('BM'+str(x)),
                   'is_selected': False}
                  for x in range(today.year - 2, today.year + 4) ]
        # Select one
        for i in [2, 3, 4, 5, 1, 0]:
            if years[i]['is_disabled'] is False:
                years[i]['is_selected'] = True
                break
        namespace['BMyears'] = years
        handler = self.get_handler('/ui/culture/Culture_new_reports.xml')
        return stl(handler, namespace)


    new_BM_reports__access__ = 'is_admin'
    def new_BM_reports(self, context):
        """ """
        # Add reports container
        year = context.get_form_value('year')
        report_name = 'BM' + str(year)
        # Add reports and users, one per department
        reports = Forms()
        self.set_object(report_name, reports)
        reports = self.get_handler(report_name)
        t = time()

        users = self.get_handler('users')
        report_c = int(time() -t); print 'get users, deep copy', report_c 

        BMs = get_BMs()
        BMs_len =  len(BMs)
        bib_municipals = BMs.items()
        # so we sort by integers values
        bib_municipals.sort(key=itemgetter(0))
        form = FormBM()
        i = 0
        for code, bib in bib_municipals: 
            name, dep = bib['name'], bib['dep']
            # Add report
            reports.set_object(code, form, **{'dc:title': name})
            # Add user
            #username = 'user%s_%s' % (code, year)
            username = 'BM%s' % code
            if not users.has_handler(username):
                users.set_object(username, bibUser())
                user = users.get_handler(username)
                user.set_password('BM%s' % code)
                del user
            print '%s/%s' % (i, BMs_len), dep, code, username
            i += 1
        report_m = int(time() -t); print 'users and reperts set ', report_m 
        secondes = int(time() - t)
        minutes = secondes / 60 
        message = u"Les rapports des BM pour l'année %(year)s ont été " \
                  u"ajoutés, ainsi que les utilisateurs associés : " \
                  u"BMxxx:BMxxx, BMyy:BMyy, etc. " \
                  u"En %(temp)s %(unite)s"
        message = message % {'year': year, 'temp': minutes or secondes,
                'unite': minutes and 'minutes' or 'secondes' }
        return context.come_back(message, goto=';browse_thumbnails')


    new_BDP_reports__access__ = 'is_admin'
    def new_BDP_reports(self, context):
        """ patern for BDP users is BDPxx_Year"""
        # Add reports container
        year = context.get_form_value('year')
        name = 'BDP' + str(year)
        self.set_object(name, Forms())
        # Add reports and users, one per department
        reports = self.get_handler(name)
        users = self.get_handler('users')
        form = FormBDP()
        for name, dic in get_deps().items():
            title = dic['name']
            # Add report
            reports.set_object(name, form, **{'dc:title': title})
            # Add user
            username = 'BDP%s' % name
            if not users.has_handler(username):
                users.set_object(username, bibUser())
                user = users.get_handler(username)
                user.set_password('BDP%s' % name)
                del user

        message = u"Les rapports des BDP pour l'année %s ont été ajoutés. " \
                  u"Et aussi ses utilisateurs associés (BDP01:BDP01, " \
                  u"BDP02:BDP02, etc.)." % year
        return context.come_back(message, goto=';browse_thumbnails')


    #########################################################################
    # Help
    help__access__ = True
    help__label__ = u'Aide'
    def help(self, context):
        handler = self.get_handler('/ui/culture/Form_help.xml')
        return handler.to_str()


    #########################################################################
    # Export
    export_form__access__ = 'is_admin'
    export_form__label__ = u"Exporter"
    def export_form(self, context):
        handler = self.get_handler('/ui/culture/Culture_export.xml')
        return handler.to_str()


    export__access__ = 'is_admin'
    def export(self, context):

        def export_bib(container, ouput):
            cursor = get_cursor()
            names = [name for name in container.get_handler_names()
                    if name.isdigit() and (
                        container.get_handler('.%s.metadata' % name).get_property('state') == 'public')]

            # adresse
            keys = ', '.join(names)
            if container.is_BM():
                query = "select * from adresse where insee is not null and code_bib in (%s)" % keys
            else:
                query = "select * from adresse where type='3' and code_ua is not null and dept in (%s)" % keys
            cursor.execute(query)
            resultset = cursor.fetchall()
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

            # (bm|bdp)05
            for name in names:
                handler = container.get_handler(name)
                schema = handler.get_schema()
                namespace = handler.get_namespace()
                # XXX copy/paste
                for key, value in namespace.items():
                    field_def = schema.get(key)
                    if field_def is not None:
                        ftype = field_def[0]
                        if ftype is Unicode:
                            if value is not None:
                                value = value.replace(u"€", u"eur")
                                value = value.replace(u'"', u'\\"')
                                value = value.replace(u"&quot;", u'\\"')
                                value = value.replace(u"'", u"\\'")
                            namespace[key] = value
                # XXX end
                query = handler.get_export_query(namespace)
                output.write(query.encode('latin1') + '\n')
                del namespace
                del handler

            output.write('\n')


        output_path = join(getcwd(), 'exportscrib.sql')
        output = open(output_path, 'w')
        output.write(u'-- Généré le %s\n'.encode('latin1') % datetime.now())
        output.write('\n')

        output.write(u'-- Réinitialisation'.encode('latin1'))
        output.write('\n')
        output.write('DELETE FROM adresse;\n')
        output.write('DELETE FROM bm05;\n')
        output.write('DELETE FROM bdp05;\n')
        output.write('\n')

        output.write('-- BM2005\n')
        output.write('\n')
        BM2005 = self.get_handler('BM2005')
        export_bib(BM2005, output)

        output.write('\n')
        output.write('-- BDP2005\n')
        output.write('\n')
        BDP2005 = self.get_handler('BDP2005')
        export_bib(BDP2005, output)

        output.close()

        return context.come_back(u"Fichier exporté dans '$output_path'",
                output_path=output_path)


    #########################################################################
    # New User
    new_bm_form__access__ = 'is_admin'
    new_bm_form__sublabel__ = u"Nouvelle BM"
    def new_bm_form(self, context):
        handler = self.get_handler('/ui/culture/Culture_new_bm.xml')
        return handler.to_str()


    new_bm__access__ = 'is_admin'
    def new_bm(self, context):
        code_bib = context.get_form_value('code_bib')
        bms = get_BMs()
        codes = []
        
        for code in code_bib.split():
            if code not in bms:
                return context.come_back(u"Le code_bib $code n'est pas "
                        u"dans le fichier input_data/init_BM.txt installé.",
                        code=repr(code))
            codes.append(int(code))

        users = self.get_handler('users')
        bm2005 = self.get_handler('BM2005')

        for code in codes:
            name = unicode(code)

            # Add report
            ville = bms[name]['name']
            if not bm2005.has_handler(name):
                bm2005.set_object(name, FormBM(), **{'dc:title': ville})

            # Add user
            username = 'BM%s' % code
            if not users.has_handler(username):
                users.set_object(username, bibUser())
                user = users.get_handler(username)
                user.set_password(username)

        message = (u"Formulaire et utilisateur ajoutés : "
                u"code_bib=%s ville=%s dept=%s code_insee=%s login=%s password=%s")
        message = message % (code, ville, bms[name]['dep'],
                bms[name]['id'], username, username)

        return context.come_back(message, goto=';new_bm_form')


    #########################################################################
    # Upgrade
    #########################################################################



register_object_class(Root)
