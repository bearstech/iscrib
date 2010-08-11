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
from itools.csv import Property
from itools.datatypes import DateTime, Unicode

# Import from ikaaro
from ikaaro import messages
from ikaaro.autoform import title_widget, description_widget, subject_widget
from ikaaro.autoform import timestamp_widget
from ikaaro.resource_views import DBResource_Edit
from ikaaro.workflow import state_widget, WorkflowAware, StateEnumerate


class AutomaticEditView(DBResource_Edit):

    base_schema = {'title': Unicode(multilingual=True),
                   'timestamp': DateTime(readonly=True, ignore=True)}

    # Add timestamp_widget in get_widgets method
    base_widgets = [title_widget]


    def get_schema(self, resource, context):
        schema = {}
        if isinstance(resource, WorkflowAware):
            schema['state'] = StateEnumerate(resource=resource,
                                             context=context)
        if getattr(resource, 'edit_show_meta', False) is True:
            schema['description'] = Unicode(multilingual=True)
            schema['subject'] = Unicode(multilingual=True)
        return merge_dicts(self.base_schema, schema, resource.edit_schema)


    def get_widgets(self, resource, context):
        widgets = []
        if getattr(resource, 'edit_show_meta', False) is True:
            widgets.extend([description_widget, subject_widget])
        widgets = self.base_widgets + widgets + resource.edit_widgets
        # Add state widget in bottom
        if isinstance(resource, WorkflowAware):
            widgets.append(state_widget)
        # Add timestamp_widget
        widgets.append(timestamp_widget)
        return widgets


    def get_value(self, resource, context, name, datatype):
        if name == 'state':
            return resource.get_workflow_state()
        return DBResource_Edit.get_value(self, resource, context, name,
                                         datatype)


    def action(self, resource, context, form):
        self.check_edit_conflict(resource, context, form)
        # Check edit conflict
        if context.edit_conflict:
            return
        # Save changes
        language = resource.get_content_language(context)
        for key, datatype in self.get_schema(resource, context).items():
            if getattr(datatype, 'ignore', False) is True:
                continue
            elif getattr(datatype, 'multilingual', False) is True:
                p_value = Property(form[key], lang=language)
                resource.set_property(key, p_value)
            else:
                resource.set_property(key, form[key])
        # Ok
        context.message = messages.MSG_CHANGES_SAVED
