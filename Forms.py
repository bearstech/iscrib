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
from itools.catalog.analysers import Text as TextAnalyser
from itools.web import get_context
from itools.catalog import queries
from itools.stl import stl

# Import from itools.cms
from itools.cms.utils import get_parameters
from itools.cms.widgets import Table

# Import from Culture
from Folder import bibFolder
from FormBM import FormBM
from FormBDP import FormBDP
from utils import get_deps



class Forms(bibFolder):

    class_id = 'Forms'
    class_title = u'Forms'
    class_description = u'...'
    class_icon48 = 'culture/images/form48.png'


    #########################################################################
    # User interface
    #########################################################################
    def get_views(self):
        if self.is_BM():
            return ['search_form']
        if self.is_BDP():
            return ['browse_list']


    def get_subviews(self, view):
        return []

    def is_BM(self):
        return self.name.count('BM') and True


    def is_BDP(self):
        return self.name.count('BDP') and True

    def get_year(self):
        return self.name[-4:]

    #########################################################################
    # Browse
    def _browse_namespace(self, line, object):
        line['state'] = object.get_form_state()
        line['title'] = object.get_user_town()
        line['dep'] = object.get_dep()


    browse_list__access__ = 'is_admin_or_consultant'
    def browse_list(self):
        context = get_context()
        context.set_cookie('browse', 'list')
        namespace = self.browse_namespace(16)
        handler = self.get_handler('/ui/culture/Forms_browse_list.xml')
        return stl(handler, namespace)


    search_form__access__ = 'is_admin_or_consultant'
    search_form__label__ = u'Search'
    def search_form(self):
        context = get_context()
        tablename = 'search'

        # Get the search parameters
        parameters = get_parameters(tablename, name='', dep='', code='',
                                    state='')
        states_dic = {'1': u'Vide', '2': u'En cours', '3': u'Terminé',
                      '4': u'Exporté'}

        name = parameters['name'].strip().lower()
        dep = parameters['dep'].strip()
        code = parameters['code'].strip().lower()
        state_code = parameters['state'].strip()

        name = unicode(name, 'utf8')
        dep= unicode(dep, 'utf8')
        code = unicode(code, 'utf8')
        state = states_dic.get(state_code)

        # Build the namespace
        namespace = {}
        namespace['too_long_answer'] = ''

        # The search form
        namespace['search_name'] = name

        states = []
        for state_key, state_name in states_dic.items():
            states.append({'name': state_name, 'value': state_key,
                           'selected': state_key == state_code})
        namespace['states'] = states

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

        namespace['search_dep'] = dep 
        namespace['search_code'] = code 
        namespace['search_state'] = state_code

        # Search
        if name or code or state or dep:
            # Build the query
            # The format (BM or BDP)
            if self.is_BM():
                query = queries.Equal('format', FormBM.class_id)
            else:
                query = queries.Equal('format', FormBDP.class_id)
            # The year
            year = self.get_year()
            q_year = queries.Equal('year', year)
            query = queries.And(query, q_year)
            # The name of the town
            for word, pos in TextAnalyser(name):
                q_name = queries.Equal('user_town', word)
                query = queries.And(query, q_name)
            # The department
            if dep:
                q_dep = queries.Equal('dep', dep)
                query = queries.And(query, q_dep)
            # The code UA
            if code:
                q_code = queries.Equal('code', code)
                query = queries.And(query, q_code)
            # The state
            if state_code:
                q_state = queries.Equal('form_state', state)
                query = queries.And(query, q_state)

            # Search
            root = context.root
            catalog = root.get_handler('.catalog')
            documents = catalog.search(query)
            # Get the real objects (never more than 100)
            documents = list(documents)
            answer_len = len(documents)
            if answer_len > 100:
                msg = u'Il y a %s réponses, les 100 premières sont présentées.'\
                      u'Veuillez restreindre votre recherche.'
                namespace['too_long_answer'] = msg % answer_len

            # Build objects namespace, add the path to the object from the
            # current folder.
            objects = []
            get_resource = root.resource.get_resource
            for document in documents[:100]:
                # XXX Use document.mtime_microsecond instead?
                mtime = get_resource(document.abspath).get_mtime()
                objects.append({'name': document.name,
                                'url': '%s/;report_form0' % document.name,
                                'title': document.title,
                                'state': document.form_state,
                                'date': mtime.strftime('%Y-%m-%d %H:%M')})
        else:
            objects = []

        # The table
        path = context.path
        table = Table(path.get_pathtoroot(), tablename, objects,
                      sortby='title', sortorder='up', batchstart='0',
                      batchsize='50')
        namespace['table'] = table
        namespace['batch'] = table.batch_control()

        handler = self.get_handler('/ui/culture/Forms_search.xml')
        return stl(handler, namespace)

bibFolder.register_handler_class(Forms)
