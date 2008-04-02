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
from itools.resources import base
from itools.web import get_context
from itools.web.exceptions import UserError
from itools.stl import stl
from itools.catalog.analysers import Text as TextAnalyser
from itools.catalog import queries

# Import from ikaaro
from ikaaro.users import User as iUser, UserFolder as iUserFolder
from ikaaro.group import Group as BaseGroup
from ikaaro.utils import comeback, get_parameters
from ikaaro.widgets import Table

# Import from scrib
from utils import get_deps, get_BMs
from handler import Handler



class bibGroup(Handler, BaseGroup):

    is_allowed_to_view = Handler.is_admin
    edit_metadata_form__access__ = 'is_admin'
    edit_metadata__access__ = 'is_admin'
    browse_thumbnails__access__ = False
    browse_list__access__ = 'is_admin'
    add_users_form__access__ = False


    def get_views(self):
        views = BaseGroup.get_views(self)
        return views + ['create_add_users_form']


    #######################################################################
    # Users / Add
    create_add_users_form__access__ = 'is_admin'
    create_add_users_form__label__ = u'Ajouter un administrateur Scrib'
    def create_add_users_form(self):
        context = get_context()
        root = context.root
        namespace = {}
        usernames = self.get_usernames()
        
        # Users
        users = root.get_handler('users')

        handler = self.get_handler('/ui/culture/bibGroup_create_add_users.xml')
        return stl(handler, namespace)


    create_add_users__access__ = 'is_admin'
    def create_add_users(self, username, password, password2, groups=[], **kw):
        context = get_context()
        root = context.root
        namespace = {}

        # Check the values
        if not username:
            raise UserError, self.gettext('The username is wrong, please try again.')
        if self.has_handler(username):
            raise UserError, \
                  self.gettext('There is another user with the username "%s", '
                    'please try again') % username
        if not password or password != password2:
            raise UserError, self.gettext('The password is wrong, please try again.')

        # add the user
        users = root.get_handler('users')
        users.set_user(username, password)

        # Add user in groups
        admin_group = root.get_handler('admins')
        admin_group.set_user(username)

        message = self.gettext('User added')
        comeback(message, ';browse_users')


BaseGroup.register_handler_class(bibGroup)



class bibUser(Handler, iUser):
    class_id = 'bibUser'

    def get_catalog_indexes(self):
        document = Handler.get_catalog_indexes(self)
        document['user_town'] = self.get_user_town()
        document['dep'] = self.get_department()
        document['year'] = self.get_year()
        document['is_BDP'] = self.is_BDP()
        document['is_BM'] = self.is_BM()

        return document


    def is_BM(self):
        """ patern is BMxxx"""
        return self.name.startswith('BM')


    def is_BDP(self):
        """ patern is BDPxx"""
        return self.name.startswith('BDP')


    def is_not_BDP_or_BM(self):
        return not self.is_BDP and not self.is_BM


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
    # User interface
    #######################################################################
    def get_views(self):
        root = self.get_root()
        if self.name in root.get_handler('admins').get_usernames():
            return ['edit_password_form']
        elif self.name == 'VoirSCRIB':
            return ['edit_password_form']
        return ['home', 'edit_password_form']


    def get_subviews(self, name):
        return []


    #######################################################################
    # Home
    home__access__ = True 
    home__label__ = u'Home'
    def home(self):
        namespace = {}
        root = self.get_root()
        name = self.name
        department, code = '', ''

        year = self.get_year()
        if self.is_BM():
            code = self.get_BM_code()
            report = root.get_handler('BM%s/%s' % (year, code))
        elif self.is_BDP():
            department = self.get_department()
            report = root.get_handler('BDP%s/%s' % (year, department))

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

        handler = self.get_handler('/ui/culture/User_home.xml')
        return stl(handler, namespace)


    #######################################################################
    # Password
    edit_password_form__label__ = u'Change password'


iUser.register_handler_class(bibUser)



class bibUserFolder(Handler, iUserFolder):

    is_allowed_to_view = Handler.is_admin
    browse_thumbnails__access__ = 'is_admin'
    edit_metadata_form__access__ = 'is_admin'


    #######################################################################
    # Search
    def get_views(self):
        views = iUserFolder.get_views(self)
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
    def search_form(self):
        context = get_context()
        root = context.root
        namespace = {}
        admin_names = root.get_handler('admins').get_usernames()
        admins = []
        for admin_name in admin_names:
            dic = {} 
            user = root.get_handler('users').get_handler(admin_name)
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
        names = [t[0] for t in TextAnalyser(name)]
        if names: 
            q_name =  queries.Equal('user_town', names[0])
            for subname in names:
                q_name2 = queries.Equal('user_town', subname)
                q_name = queries.And(q_name, q_name2)
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
        if year: q_year = queries.Equal('year', year)
        if dep: q_dep = queries.Equal('dep', dep)
        if name: q_name = queries.Equal('user_town', name)

        # independent of the form : q_bibUser, q_type_form
        q_bibUser = queries.Equal('format', bibUser.class_id)
        if is_BM: 
            q_type_form = queries.Equal('is_BM', str(int(is_BM)))
        if is_BDP: 
            q_type_form = queries.Equal('is_BDP', str(int(is_BDP)))


        query, objects = None, []
        if name or dep or year:
            query = q_type_form 
            query = queries.And(query, q_bibUser)
        if year: 
            query = queries.And(query, q_year)
        if name: 
            query = queries.And(query, q_name)
        if dep: 
            query = queries.And(query, q_dep)

        namespace['too_long_answer'] = '' 
        msg = u'Il y a %s réponses, les 100 premières sont présentées.'\
              u'Veuillez restreindre votre recherche.'

        # Search
        if query:
##            t = time()
            catalog = root.get_handler('.catalog')
##            t_loadC = time() - t; print 't_loadC', t_loadC

            documents = catalog.search(query)
            documents = list(documents)
##            t_search = time() - t; print 't_search', t_search

            answer_len = len(documents)
            if answer_len > 100:
                namespace['too_long_answer'] = msg % answer_len
            too_long_answer = msg % answer_len
            # Get the real objects
            objects = [ root.get_handler(x.abspath) for x in documents[:100] ]
##            t_h = time() - t; print 't_h', t_h

        # Build objects namespace, add the path to the object from the
        # current folder.
        aux = []
        root = self.get_root()
        for handler in objects:
            resource = handler.resource
            path_to_handler = self.get_pathto(handler)
            node = self
            path = []
            for name in path_to_handler:
                node = node.get_handler(name)
                path.append({'name': node.name,
                             'url': '%s/;%s' % (self.get_pathto(node),
                                                node.get_firstview())})

            if isinstance(resource, base.File):
                summary = self.gettext('%d bytes') % resource.get_size()
            elif isinstance(resource, base.Folder):
                nresources = len([ x for x in resource.get_resource_names()
                                   if not x.startswith('.') ])
                summary = str(nresources)

            mtime = resource.get_mtime()
            path_to_icon = handler.get_path_to_icon(16)
            # XXX hugly
            path_to_icon = uri.Path(str(path_to_handler) + '/').resolve(path_to_icon)
            aux.append({'oid': path_to_handler,
                        'icon': path_to_icon,
                        'type': resource.get_mimetype(),
                        'date': mtime.strftime('%Y-%m-%d %H:%M'),
                        'title': (handler.get_user_town() or 
                                  handler.get_department_name()),
                        'content_summary': summary,
                        'path': path})
        objects = aux

        # The table
        path = context.path
        table = Table(path.get_pathtoroot(), tablename, objects, sortby='oid',
                      sortorder='up', batchstart='0', batchsize='50')
        namespace['table'] = table
        namespace['batch'] = table.batch_control()

        handler = self.get_handler('/ui/culture/bibUserFolder_search.xml')
        return stl(handler, namespace)


iUserFolder.register_handler_class(bibUserFolder)
