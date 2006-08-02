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
import datetime
from time import time
import tempfile

# Import from itools
from itools.resources import base, get_resource
from itools.datatypes import Unicode, String, DateTime
from itools.web import get_context
from itools.stl import stl
from itools.handlers.transactions import get_transaction

# Import from itools.cms
from itools.cms.Root import Root as iRoot
from itools.cms.Metadata import Metadata, Record
from itools.cms.utils import comeback

# Import from culture
from FormBM import FormBM
from FormBDP import FormBDP
from Forms import Forms
from User import bibUser
from Folder import bibFolder
from utils import get_deps, get_BMs


class Root(bibFolder, iRoot):

    class_id = 'Culture'
    class_version = '20060802'


    _catalog_fields = iRoot._catalog_fields \
                      + [('user_town', 'text', True, False),
                         ('dep', 'keyword', True, False),
                         ('year', 'keyword', True, False),
                         ('is_BDP', 'bool', True, False),
                         ('is_BM', 'bool', True, False),
                         ('form_state', 'keyword', True, True),
                         ('code', 'keyword', True, False)]


    login_form__access__ = True
    login_form__label__ = u'Login'
    def login_form(self):
        request = get_context().request
        namespace = {'referer': request.form.get('referer', ''),
                     'username': request.form.get('username', '')}

        handler = self.get_handler('/ui/culture/SiteRoot_login.xml')
        return stl(handler, namespace)


    def get_skeleton(self, username=None, password=None):
        skeleton = iRoot.get_skeleton(self, username, password)
        # Skip reviewers
        del skeleton['reviewers']
        return skeleton


    _get_handler = iRoot._get_handler


    def before_traverse(self):
        # Set french as default language, whatever the browser config is
        context = get_context()
        accept = context.request.accept_language
        accept.set('fr', 1.5)


    #########################################################################
    # Security declarations
    #########################################################################
    browse_list__access__ = 'is_admin'


    #########################################################################
    # User interface
    #########################################################################
    def get_skin_name(self):
        return 'culture'


    def get_skin(self):
        return self.get_handler('ui/culture')


    def get_themes(self):
        return ['culture']


    def get_available_languages(self):
        return ['fr']


    def get_default_language(self):
        return 'fr'


    def get_views(self):
        user = get_context().user
        if user is None:
            return ['login_form', 'help']

        if user.is_admin():
            return ['browse_thumbnails', 'new_reports_form',
                    'edit_metadata_form', 'help', 'catalog_form']

        if user.name == 'VoirSCRIB':
            return ['browse_thumbnails', 'help']

        return []


    def get_subviews(self, name):
        if name in ['browse_thumbnails', 'browse_list']:
            return ['browse_thumbnails', 'browse_list']
        return []


    #########################################################################
    # Login
    def login(self, username, password, referer=None, **kw):
        iRoot.login(self, username, password, referer)
        context = get_context()
        user = context.user
        if user.is_admin() or user.name == 'VoirSCRIB':
            context.redirect(';%s' % self.get_firstview())
        elif user.is_BM():
            path = 'BM%s/%s' % (user.get_year(), user.get_BM_code())
            report = self.get_handler(path)
            context.redirect('%s/;%s' % (path, report.get_firstview()))
        else:
            path = 'BDP%s/%s' % (user.get_year(), user.get_department())
            report = self.get_handler(path)
            context.redirect('%s/;%s' % (path, report.get_firstview()))


    #########################################################################
    # New reports
    new_reports_form__access__ = 'is_admin'
    new_reports_form__label__ = u'Ajouter'
    def new_reports_form(self):
        namespace = {}
        today = datetime.date.today()
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
    def new_BM_reports(self, year, **kw):
        """ """
        # Add reports container
        report_name = 'BM' + str(year)
        # Add reports and users, one per department
        reports = Forms()
        self.set_handler(report_name, reports)
        reports = self.get_handler(report_name)
        t = time()

        users = self.get_handler('users')
        report_c = int(time() -t); print 'get users, deep copy', report_c 

        BMs_len =  len(get_BMs())
        bib_municipals = get_BMs().items()
        # so we sort by integers values
        bib_municipals = [(int(k), v) for k, v in bib_municipals]
        bib_municipals.sort()
        bib_municipals = [b[-1] for b in bib_municipals]
        form = FormBM()
        i = 0
        #for bib in bib_municipals[:200]: 
        for bib in bib_municipals: 
            name, dep, code = (bib['name'], bib['dep'], bib['code'])
            # Add report
            reports.set_handler(code, form, title=name)
            # Add user
            #username = 'user%s_%s' % (code, year)
            username = 'BM%s' % (code,)
            password = 'BM%s' % code
            users.set_handler(username, bibUser(password=password))
            if i % 200 == 0:
                get_transaction().commit()
                print "#200", '%s/%s' % (i, BMs_len), dep, code, username
            else:
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
        comeback(message, 'browse_thumbnails')


    new_BDP_reports__access__ = 'is_admin'
    def new_BDP_reports(self, year, **kw):
        """ patern for BDP users is BDPxx_Year"""
        # Add reports container
        name = 'BDP' + str(year)
        self.set_handler(name, Forms())
        # Add reports and users, one per department
        reports = self.get_handler(name)
        users = self.get_handler('users')
        for name, title in get_deps().items():
            # Add report
            reports.set_handler(name, FormBDP(), title=title)
            # Add user
            username = 'BDP%s' % (name,)
            if not users.has_handler(username):
                password = 'BDP%s' % name
                users.set_handler(username, bibUser(password=password))

        message = u"Les rapports des BDP pour l'année %s ont été ajoutés. " \
                  u"Et aussi ses utilisateurs associés (BDP01:BDP01, " \
                  u"BDP02:BDP02, etc.)." % year
        comeback(message, 'browse_thumbnails')


    #########################################################################
    # Help
    help__access__ = True
    help__label__ = u'Aide'
    def help(self):
        handler = self.get_handler('/ui/culture/Form_help.xml')
        return handler.to_str()


    #########################################################################
    # Upgrade
    #########################################################################
    def update_metadata(self, metadata):
        # Update metadata
        trans = {(None, 'title'): (('dc', 'title'), Unicode),
                 (None, 'description'): (('dc', 'description'), Unicode),
                 (None, 'language'): (('dc', 'language'), String),
                 (None, 'user_theme'): (('ikaaro', 'user_theme'), String),
                 (None, 'date'): (('dc', 'date'), DateTime),
                 (None, 'wf_transition'): (('ikaaro', 'wf_transition'), Record)
                 }

        properties = metadata.properties

        has_changed = False
        for key in properties:
            if key in trans:
                new_key, type = trans[key]
                metadata.prefixes.add(new_key[0])
                value = properties[key]
                # Transform property
                if isinstance(value, dict):
                    properties[new_key] = {}
                    for language, value in value.items():
                        value = type.decode(value)
                        properties[new_key][language] = value
                elif isinstance(value, list):
                    properties[new_key] = []
                    for value in value:
                        properties[new_key].append({})
                        for key2, value2 in value.items():
                            if key2 in trans:
                                new_key2, type2 = trans[key2]
                                metadata.prefixes.add(new_key2[0])
                                value2 = type2.decode(value2)
                                properties[new_key][-1][new_key2] = value2
                            else:
                                properties[new_key][-1][key2] = value2
                else:
                    value = type.decode(value)
                    properties[new_key] = value


                # Remove old propertye
                del properties[key]
                has_changed = True

        if has_changed:
            metadata.save()


    def update_20050509(self):
        # Move settings to metadata
        settings = self.get_handler('.settings')
        if settings.state.join is True:
            self.set_property('ikaaro:website_is_open', True)
        self.set_property('ikaaro:website_languages',
                          tuple(settings.state.languages))
        self.metadata.save_state()

        self.resource.del_resource('.settings')


    def update_20050728(self):
        resource = self.resource
        object = resource._get_object().aq_base
        delattr(object, '__before_publishing_traverse__')
        delattr(object, '__browser_default__')
        resource.get_transaction().commit()


    def update_20051020(self):
        root = self.resource
        for resource in root.get_resources():
            if resource.name.endswith('.metadata'):
                print resource.name
                metadata = Metadata(resource)
                self.update_metadata(metadata)
            elif isinstance(resource, base.Folder):
                for resource_name in resource.get_resource_names():
                    if resource_name.endswith('.metadata'):
                        print '%s/%s' % (resource.name, resource_name)
                        metadata = Metadata(resource.get_resource(resource_name))
                        self.update_metadata(metadata)
                

    def update_20060505(self):
        users = self.get_handler('users')
        users.set_handler('VoirSCRIB', bibUser(password='BMBDP'))
        users.save()


    def update_20060728(self):
        self.update_20050509()


    def update_20060801(self):
        self.update_20050728()
        iRoot.update_20051025(self)


    def update_20060802(self):
        iRoot.update_20060205(self)


    xexport__access__ = True
    def xexport(self):
        tmp_path = tempfile.mkdtemp()
        tmp_folder = get_resource(tmp_path)

        root_resource = self.resource
        for name in root_resource.get_resource_names():
            resource = root_resource.get_resource(name)
            tmp_folder.set_resource(name, resource)

        return 'Exported: %s' % tmp_path


iRoot.register_handler_class(Root)
