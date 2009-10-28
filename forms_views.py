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

# Import from itools
from itools.core import merge_dicts
from itools.datatypes import Boolean, Integer, String, Unicode
from itools.gettext import MSG
from itools.xapian import PhraseQuery, StartQuery, AndQuery

# Import from ikaaro
from ikaaro.folder_views import Folder_BrowseContent
from ikaaro.forms import TextWidget, SelectWidget

# Import from scrib
from datatypes import Departements, WorkflowState


class Forms_SearchForm(Folder_BrowseContent):
    access = 'is_admin_or_voir_scrib'
    title = MSG(u"Rechercher un formulaire")
    context_menus = []
    query_schema = merge_dicts(Folder_BrowseContent.query_schema,
                               sort_by=String(default='title'),
                               batch_size=Integer(default=50),
                               reverse=Boolean(default=False))
    # Search form
    search_template = '/ui/scrib/Forms_search.xml'
    search_schema = {
        'search_title': Unicode,
        'search_dep': Departements,
        'search_code_ua': Integer,
        'search_state': WorkflowState}
    # Table
    table_actions = []


    def get_table_columns(self, resource, context):
        columns = [('code_ua', MSG(u"Code ua")),
                   ('title', MSG(u"Ville")),
                   ('mtime', MSG(u"Date")),
                   ('form_state', MSG(u"État"))]
        if resource.is_bdp():
            columns[1] = ('title', MSG(u"Département"))
        return columns


    def get_search_namespace(self, resource, context):
        # Get the search parameters
        title = context.query['search_title']
        dep = context.query['search_dep']
        code_ua = context.query['search_code_ua']
        state = context.query['search_state']
        # Build the namespace
        namespace = {}
        namespace['too_long_answer'] = ''
        # The search form
        search_title = TextWidget('search_title', size=30)
        namespace['search_title'] = search_title.to_html(Unicode, title)
        search_dep = SelectWidget('search_dep')
        namespace['search_dep'] = search_dep.to_html(Departements, dep)
        search_code_ua = TextWidget('search_code_ua', size=6)
        namespace['search_code_ua'] = search_code_ua.to_html(Unicode,
                                                             code_ua)
        search_state = SelectWidget('search_state')
        namespace['search_state'] = search_state.to_html(WorkflowState,
                                                         state)
        namespace['is_bm'] = resource.is_bm()
        return namespace


    def get_items(self, resource, context):
        # Get the search parameters
        title = context.query['search_title']
        dep = context.query['search_dep']
        code_ua = context.query['search_code_ua']
        state = context.query['search_state']
        # Build the query
        abspath = str(resource.get_canonical_path())
        query = [PhraseQuery('parent_path', abspath)]
        # The format (BM or BDP)
        if resource.is_bm():
            query.append(PhraseQuery('is_bm', True))
            # The code UA
            if code_ua:
                query.append(PhraseQuery('code_ua', code_ua))
        else:
            query.append(PhraseQuery('is_bdp', True))
        # The department
        if dep:
            query.append(PhraseQuery('departement', dep))
        # The state
        if state:
            form_state = WorkflowState.get_value(state)
            query.append(PhraseQuery('form_state', form_state))
        # The city
        if title:
            query.append(StartQuery('title', title))
        query = AndQuery(*query)
        # Search
        return context.root.search(query)


    def get_item_value(self, resource, context, item, column):
        root = context.root
        item_brain, item_resource = item
        if column == 'code_ua':
            form_name = item_brain.code_ua
            if item_brain.is_bm:
                form_name = int(form_name)
            return form_name
        elif column == 'title':
            url = '%s/;pageA' % item_brain.name
            return (item_brain.title, url)
        elif column == 'mtime':
            mtime = item_brain.mtime
            return mtime.strftime('%d-%m-%Y %Hh%M')
        elif column == 'form_state':
            return item_brain.form_state
        raise NotImplementedError, column
