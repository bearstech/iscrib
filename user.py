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

# Import from itools
from itools import uri
from itools import vfs
from itools.stl import stl
from itools.catalog import (KeywordField, TextField, BoolField, EqQuery,
        AndQuery)

# Import from ikaaro
from ikaaro.file import File
from ikaaro.folder import Folder
from ikaaro.users import User, UserFolder
from ikaaro.utils import get_parameters
from ikaaro.registry import register_object_class
from ikaaro.widgets import table

# Import from scrib
from utils import get_deps, get_BMs



class ScribUser(User):
    class_views = [['home'], ['edit_password_form']]

    def get_catalog_fields(self):
        fields = User.get_catalog_fields(self)
        fields['user_town'] = TextField('user_town')
        fields['dep'] = KeywordField('dep', is_stored=True)
        fields['year'] = KeywordField('year')
        fields['is_BDP'] = BoolField('is_BDP')
        fields['is_BM'] = BoolField('is_BM')
        return fields


    def get_catalog_values(self):
        values = User.get_catalog_values(self)
        values['user_town'] = self.get_user_town()
        values['dep'] = self.get_dep()
        values['year'] = self.get_year()
        values['is_BDP'] = self.is_BDP()
        values['is_BM'] = self.is_BM()
        return values


    def is_BM(self):
        """ patern is BMxxx"""
        return self.name.startswith('BM')


    def is_BDP(self):
        """ patern is BDPxx"""
        return self.name.startswith('BDP')


    def is_not_BDP_or_BM(self):
        return not self.is_BDP() and not self.is_BM()


    def get_department_name(self):
        name = self.name
        dep = self.get_department()
        dep_name = get_deps().get(dep)
        if dep_name:
            dep_name = dep_name.get('name') 
        return dep_name


    def get_department(self):
        name = self.name
        dep = ''
        if self.is_BDP():
           dep = name.split('BDP')[-1]
        elif self.is_BM():
            code = self.get_BM_code()
            if code:
                # Cf. #2617
                bib = get_BMs().get(code)
                if bib:
                    dep = bib.get('dep', '')
                else:
                    print "bib", code, "n'existe pas"
        return dep


    def get_BM_code(self):
        """ patern is BMxxx"""
        name = self.name
        if self.is_BM():
           return name.split('BM')[-1]
        else:
            return None


    def get_user_town(self):
        title = ''
        if self.is_BM():
            code = self.get_BM_code()
            if code:
                # Cf. #2617
                bib = get_BMs().get(code)
                if bib:
                    title = bib.get('name', '')
                else:
                    print "bib", code, "n'existe pas"
        return title 


    def get_year(self):
        name = self.name
        if self.is_BDP():
           # XXX just for 2005 ;)
           return '2005'
        elif self.is_BM():
           return '2005'
        return None


    #######################################################################
    # Security
    #######################################################################
    def is_self(self, user, object):
        if user is None:
            return False
        return self.name == user.name


    #######################################################################
    # Home
    home__access__ = 'is_self'
    home__label__ = u'Home'
    def home(self, context):
        namespace = {}
        root = self.get_root()
        name = self.name
        department, code = '', ''

        year = self.get_year()
        if self.is_BM():
            code = self.get_BM_code()
            report = root.get_object('BM%s/%s' % (year, code))
        elif self.is_BDP():
            department = self.get_department()
            report = root.get_object('BDP%s/%s' % (year, department))

        namespace['report_url'] = '%s/;%s' % (self.get_pathto(report),
                                              report.get_firstview())

        # The year
        namespace['year'] = year
        # The department or the BM Code
        departments = get_deps()
        namespace['dep'] = ''
        if department:
            dep_name = departments[department].get('name', '')
            namespace['dep'] = dep_name 
        elif code:
            bib = get_BMs().get(code)
            if bib:
                namespace['dep'] = bib.get('name', '')

        template = self.get_object('/ui/scrib/User_home.xml')
        return stl(template, namespace)


    #######################################################################
    # Password
    edit_password_form__label__ = u'Change password'


register_object_class(ScribUser)



class ScribUserFolder(UserFolder):

    is_allowed_to_view = UserFolder.is_admin
    browse_thumbnails__access__ = 'is_admin'
    edit_metadata_form__access__ = 'is_admin'


    #######################################################################
    # Search
    def get_views(self):
        views = UserFolder.get_views(self)
        if 'browse_thumbnails' in views:
            views.remove('browse_thumbnails')
        if 'new_user_form' in views:
            views.remove('new_user_form')
        if 'search_form' in views:
            views.remove('search_form')
        views.insert(0, 'search_form')
        return views 


    search_form__access__ = 'is_admin'
    search_form__label__ = u'Search'
    def search_form(self, context):
        root = context.root
        namespace = {}
        admin_names = root.get_members_classified_by_role()['admins']
        admins = []
        user_folder = root.get_object('users')
        for admin_name in admin_names:
            dic = {} 
            user = user_folder.get_object(admin_name)
            dic['name'] = user.get_property('title') or user.name
            dic['url'] = str(self.get_pathto(user))
            admins.append(dic)
        namespace['admins'] = admins
        tablename = 'search'

        # Search parameters
        parameters = get_parameters(tablename, name='', year='', dep='', 
                                    bib='BM')

        name = parameters['name'].strip().lower()
        year = parameters['year'].strip().lower()
        dep = parameters['dep'].strip().lower()
        name = unicode(name, 'utf8')
        year = unicode(year, 'utf8')
        dep= unicode(dep, 'utf8')
        namespace['search_year'] = year 

        # make possible the search in 'bellegarde-sur-valserine'
        # by the Complex search on 'bellegarde', 'sur', 'valserine'
        names = [t[0] for t in TextField.split(name)]
        if names: 
            q_name =  EqQuery('user_town', names[0])
            for subname in names:
                q_name2 = EqQuery('user_town', subname)
                q_name = AndQuery(q_name, q_name2)
        namespace['search_name'] = name

        # departements
        namespace['search_dep'] = dep 
        departements = [] 
        for dep_key, dep_dic in get_deps().items():
            dep_name = dep_dic['name'].capitalize()
            departements.append({'name': '%s (%s)' % (dep_name, dep_key), 
                                 'value': dep_key, 
                                 'selected': dep_key == dep})
        departements = [(d['value'], d) for d in departements] 
        departements.sort()
        departements = [d[-1] for d in departements] 
        namespace['departements'] = departements

        bib = parameters['bib']
        bib_types = [{'name': x, 'value': x, 'checked': x==bib} 
                     for x in ['BM', 'BDP']] 
        namespace['bib_types'] = bib_types

        is_BDP, is_BM = False, False
        if bib == 'BM':
            is_BM = True
        namespace['is_BM'] = is_BM
        if bib == 'BDP':
            is_BDP = True
        
        # Search
        if year:
            q_year = EqQuery('year', year)
        if dep:
            q_dep = EqQuery('dep', dep)
        if name:
            q_name = EqQuery('user_town', name)

        # independent of the form : q_scribuser, q_type_form
        q_scribuser = EqQuery('format', ScribUser.class_id)
        if is_BM: 
            q_type_form = EqQuery('is_BM', str(int(is_BM)))
        if is_BDP: 
            q_type_form = EqQuery('is_BDP', str(int(is_BDP)))


        query, objects = None, []
        if name or dep or year:
            query = q_type_form 
            query = AndQuery(query, q_scribuser)
        if year: 
            query = AndQuery(query, q_year)
        if name: 
            query = AndQuery(query, q_name)
        if dep: 
            query = AndQuery(query, q_dep)

        namespace['too_long_answer'] = '' 
        msg = u'Il y a %s réponses, les 100 premières sont présentées.'\
              u'Veuillez restreindre votre recherche.'

        # Search
        if query:
            results = root.search(query)
            answer_len = results.get_n_documents()
            if answer_len > 100:
                namespace['too_long_answer'] = msg % answer_len
            too_long_answer = msg % answer_len
            # Get the real objects
            documents = results.get_documents(size=100)
            objects = [ root.get_object(x.abspath) for x in documents ]
##            t_h = time() - t; print 't_h', t_h

        # Build objects namespace, add the path to the object from the
        # current folder.
        aux = []
        for object in objects:
            path_to_object = self.get_pathto(object)
            node = self
            path = []
            for name in path_to_object:
                node = node.get_object(name)
                path.append({'name': node.name,
                             'url': '%s/;%s' % (self.get_pathto(node),
                                                node.get_firstview())})

            if isinstance(object, File):
                summary = self.gettext(u'%d bytes') % vfs.get_size(object.uri)
            elif isinstance(object, Folder):
                nobjects = len([ x for x in object.get_names()
                                   if not x.endswith('.metadata') ])
                summary = str(nobjects)

            mtime = object.get_mtime()
            path_to_icon = object.get_path_to_icon(16)
            # XXX ugly
            path_to_icon = uri.Path(str(path_to_object) + '/').resolve(path_to_icon)
            aux.append({'oid': path_to_object,
                        'icon': path_to_icon,
                        'type': object.handler.get_mimetype(),
                        'date': mtime.strftime('%Y-%m-%d %H:%M'),
                        'title': (object.get_user_town() or 
                                  object.get_department_name()),
                        'content_summary': summary,
                        'path': path})
        objects = aux

        # The table
        path = context.path
        namespace['table'] = table(path.get_pathtoroot(), tablename, objects,
                sortby='oid', sortorder='up', batchstart='0', batchsize='50')

        template = self.get_object('/ui/scrib/ScribUserFolder_search.xml')
        return stl(template, namespace)


register_object_class(ScribUserFolder)
