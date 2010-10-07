# -*- coding: UTF-8 -*-
# Copyright (C) 2010 Sylvain Taverne <sylvain@itaapy.com>
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

# Import from ikaaro
from ikaaro.resource_views import DBResource_Edit
from ikaaro.workflow import state_widget, WorkflowAware, StateEnumerate


class AutomaticEditView(DBResource_Edit):
    base_schema = DBResource_Edit.schema

    def _get_schema(self, resource, context):
        schema = merge_dicts(DBResource_Edit.schema, resource.edit_schema)
        if isinstance(resource, WorkflowAware):
            schema['state'] = StateEnumerate(resource=resource,
                    context=context)
        return schema


    def _get_widgets(self, resource, context):
        widgets = self.widgets + resource.edit_widgets
        # Add state widget in bottom
        if isinstance(resource, WorkflowAware):
            widgets.append(state_widget)
        return widgets


    def get_value(self, resource, context, name, datatype):
        if name == 'state':
            return resource.get_workflow_state()
        return DBResource_Edit.get_value(self, resource, context, name,
                datatype)


    def set_value(self, resource, context, name, form):
        schema = self.get_schema(resource, context)
        datatype = schema[name]
        if getattr(datatype, 'ignore', False) is True:
            return False
        return DBResource_Edit.set_value(self, resource, context, name, form)
