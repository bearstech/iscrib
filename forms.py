# -*- coding: UTF-8 -*-
# Copyright (C) 2006, 2008 Hervé Cauwelier <herve@itaapy.com>
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
from operator import itemgetter

# Import from itools
from itools.catalog import EqQuery, PhraseQuery, AndQuery
from itools.stl import stl
from itools.datatypes import Integer, Unicode

# Import from ikaaro
from ikaaro.registry import register_object_class
from ikaaro.folder import Folder
from ikaaro.widgets import table, batch
from ikaaro.forms import Select as SelectWidget

# Import from scrib
from datatypes import WorkflowState
from form_bm import FormBM
from form_bdp import FormBDP
from utils import get_bdp_namespace



class Forms(Folder):

    class_id = 'Forms'
    class_title = u'Forms'
    class_description = u'...'
    class_icon48 = 'scrib/images/form48.png'
    class_views = [['search_form']]


    #########################################################################
    # API
    #########################################################################
    def is_BM(self):
        return self.name.startswith('BM')


    def is_BDP(self):
        return self.name.startswith('BDP')


    def get_year(self):
        return self.name[-4:]


    #########################################################################
    # User interface
    #########################################################################
    search_form__access__ = 'is_admin_or_consultant'
    search_form__label__ = u'Search'
    def search_form(self, context):
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
        namespace['is_BM'] = self.is_BM()

        # The batch
        sortby = context.get_form_value('sortby', default='title')
        sortorder = context.get_form_value('sortorder', default='up')
        batchstart = context.get_form_value('batchstart', type=Integer,
                                            default=0)
        batchsize = context.get_form_value('batchsize', type=Integer,
                                           default=50)

        # Build the query
        query = []
        # The format (BM or BDP)
        if self.is_BM():
            query.append(EqQuery('format', FormBM.class_id))
            # The code UA
            if code:
                query.append(EqQuery('code', code))
        else:
            query.append(EqQuery('format', FormBDP.class_id))
        # The year
        query.append(EqQuery('year', self.get_year()))
        # The name of the town
        if name:
            query.append(PhraseQuery('user_town', name))
        # The department
        if dep:
            query.append(EqQuery('dep', dep))
        # The state
        if state:
            form_state = WorkflowState.get_value(state)
            query.append(EqQuery('form_state', form_state))
        query = AndQuery(*query)

        # Search
        root = context.root
        results = root.search(query)
        # Build objects namespace, add the path to the object from the
        # current folder.
        rows = []
        get_object = root.get_object
        for document in results.get_documents():
            mtime = get_object(document.abspath).get_mtime()
            form_name = document.name
            url = '%s/;report_form0' % form_name
            if self.is_BM():
                form_name = int(form_name)
            rows.append({'name': form_name,
                         'title': (document.title, url),
                         'form_state': document.form_state,
                         'mtime': mtime.strftime('%d-%m-%Y %Hh%M')})
        # 0005562: Tri par code_ua est alphanumérique au lieu d'être numérique
        reverse = (sortorder == 'down')
        rows.sort(key=itemgetter(sortby), reverse=reverse)
        rows = rows[batchstart:batchstart+batchsize]

        # The table
        namespace['batch'] = batch(context.uri, batchstart, batchsize,
                                   results.get_n_documents())
        columns = [('name', u"Code"),
                   ('title', u"Ville"),
                   ('mtime', u"Date"),
                   ('form_state', u"État")]
        if self.is_BDP():
            columns[1] = ('title', u"Département")
        namespace['table'] = table(columns, rows, [sortby], sortorder,
                table_with_form=True)

        template = self.get_object('/ui/scrib/Forms_search.xml')
        return stl(template, namespace)



register_object_class(Forms)
