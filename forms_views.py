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
from itools.xapian import PhraseQuery, AndQuery

# Import from ikaaro
from ikaaro.folder_views import Folder_BrowseContent
from ikaaro.forms import SelectWidget

# Import from scrib
from datatypes import WorkflowState
# déplacer le choix des classes en attribut de Scrib2009
from bm2009 import BM2009
from bdp2009 import BDP2009
#from utils import get_bdp_namespace


class Forms_SearchForm(Folder_BrowseContent):
    access = 'is_admin_or_VoirSCRIB'
    title = MSG(u"Search")
    context_menus = []
    query_schema = merge_dicts(
        Folder_BrowseContent.query_schema,
        sort_by=String(default='title'),
        batch_size=Integer(default=50),
        reverse=Boolean(default=False))
    table_actions = []


    def get_table_columns(self, resource, context):
        columns = [('name', MSG(u"Code")),
                   ('title', MSG(u"Ville")),
                   ('mtime', MSG(u"Date")),
                   ('form_state', MSG(u"État"))]
        if resource.is_bdp():
            columns[1] = ('title', MSG(u"Département"))
        return columns


    def get_search_namespace(self, resource, context):
        # Get the search parameters
        name = context.get_form_value('name', type=Unicode)
        dep = context.get_form_value('dep', type=Unicode)
        code = context.get_form_value('code', type=Unicode)
        state = context.get_form_value('state')
        # Build the namespace
        namespace = {}
        namespace['too_long_answer'] = ''
        # The search form
        namespace['search_name'] = name
        namespace['departements'] = get_bdp_namespace(dep)
        namespace['search_code'] = code
        widget = SelectWidget('state')
        namespace['states'] = widget.to_html(WorkflowState, state)
        namespace['is_bm'] = resource.is_bm()
        return namespace


    def get_items(self, resource, context):
        # Get the search parameters
        name = context.get_form_value('name', type=Unicode)
        dep = context.get_form_value('dep', type=Unicode)
        code = context.get_form_value('code', type=Unicode)
        state = context.get_form_value('state')
        # Build the query
        query = []
        # The format (BM or BDP)
        if resource.is_bm():
            query.append(PhraseQuery('format', BM2009.class_id))
            # The code UA
            if code:
                query.append(PhraseQuery('code', code))
        else:
            query.append(PhraseQuery('format', BDP2009.class_id))
        # The year
        query.append(PhraseQuery('year', resource.get_year()))
        # The name of the town
        if name:
            query.append(PhraseQuery('user_town', name))
        # The department
        if dep:
            # 0005862: La recherche des BM sur les départements 2A et 2B ne
            # fonctionne pas
            query.append(PhraseQuery('dep', dep.upper()))
        # The state
        if state:
            form_state = WorkflowState.get_value(state)
            query.append(PhraseQuery('form_state', form_state))
        query = AndQuery(*query)
        # Search
        root = context.root
        return root.search(query)#.get_documents()


    def get_item_value(self, resource, context, item, column):
        root = context.root
        item_brain, item_resource = item
        if column == 'name':
            form_name = item_brain.name
            if resource.is_bm():
                form_name = int(form_name)
            return form_name
        elif column == 'title':
            url = '%s/;report_form0' % item_brain.name
            return item_brain.title, url
        elif column == 'mtime':
            mtime = resource.get_mtime()
            return mtime.strftime('%d-%m-%Y %Hh%M')
        elif column == 'form_state':
            return item_brain.form_state
