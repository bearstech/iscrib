# -*- coding: UTF-8 -*-
# Copyright (C) 2006 Luis Belmar Letelier <luis@itaapy.com>
# Copyright (C) 2006-2009 Hervé Cauwelier <herve@itaapy.com>
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
from itools.core import merge_dicts
from itools.handlers import File as FileHandler

# Import from ikaaro
from ikaaro.file import File
from ikaaro.folder import Folder
from ikaaro.registry import register_field
from ikaaro.workflow import StateForm

# Import from scrib
from datatypes import Numeric, NumDecimal
from datatypes import Unicode
from datatypes import WorkflowState
from form_views import Form_Export
from utils import SI
from workflow import workflow, EMPTY, SENT, EXPORTED, MODIFIED



class MultipleForm_StateForm(StateForm):

    def action(self, resource, context, form):
        for resource in resource.get_resources():
            resource.edit_state.action(resource, context, form)



class MultipleForm(Folder):
    class_id = 'MultipleForm'
    edit_state = MultipleForm_StateForm()


    def is_first_time(self):
        return not len(self.get_names())



class FormHandler(FileHandler):

    ######################################################################
    # Load/Save
    def new(self, encoding='UTF-8', **raw_fields):
        self._raw_fields = raw_fields


    def _load_state_from_file(self, file):
        """Load known values, the rest will be the default values.
        """
        raw_fields = {}
        for line in file.readlines():
            if ':' not in line:
                continue
            key, data = line.split(':', 1)
            raw_fields[key.strip()] = data.strip()
        self._raw_fields = raw_fields


    def to_str(self, encoding='UTF-8'):
        lines = []
        for key, value in self._raw_fields.iteritems():
            lines.append('%s:%s' % (key, value))
        return '\n'.join(lines)


    ######################################################################
    # API
    def get_value(self, name, schema):
        datatype = schema[name]
        data = self._raw_fields.get(name)
        if data is None:
            return datatype.get_default()
        try:
            value = datatype.decode(data)
        except ValueError:
            value = data
        return value


    def set_value(self, name, value, schema):
        datatype = schema[name]
        try:
            data = datatype.encode(value)
        except ValueError:
            # XXX
            data = unicode(value).encode('UTF-8')
        self._raw_fields[name] = data
        self.set_changed()



class Form(File):
    class_views = ['envoyer', 'exporter', 'imprimer', 'aide']
    class_handler = FormHandler
    workflow = workflow

    # Views
    exporter = Form_Export()


    def _get_catalog_values(self):
        return merge_dicts(File._get_catalog_values(self),
                form_state=self.get_form_state())


    ######################################################################
    # API
    def get_param_folder(self):
        """Return the folder resource where parameters are stored.
        """
        raise NotImplementedError


    def get_schema_resource(self):
        """Return the CSV schema resource.
        """
        return self.get_param_folder().get_resource('schema')


    def get_schema(self):
        """Load the schema from the CSV.
        """
        raise NotImplementedError


    def get_fields(self, schema):
        handler = self.handler
        fields = {}
        for name in schema:
            fields[name] = handler.get_value(name, schema)
        return fields


    def get_vars(self, fields):
        return merge_dicts(fields, SI=SI)


    def get_floating_vars(self, fields):
        vars = {}
        for name, value in fields.iteritems():
            if isinstance(value, Numeric):
                vars[name] = NumDecimal(value.value)
            else:
                vars[name] = value
        return vars


    def get_controls_resource(self):
        """Return the CSV controls resource.
        """
        return self.get_param_folder().get_resource('controls')


    def get_controls(self):
        """Load the controls from the CSV.
        """
        raise NotImplementedError


    def get_page_numbers(self):
        """Return the ordered list of form page numbers.
        """
        raise NotImplementedError


    def get_formpage(self, pagenum):
        """Return the FormPage resource for this number of page.
        """
        raise NotImplementedError


    def get_form(self):
        """Shortcut to find the root form in MultipleForm.
        """
        return self


    ######################################################################
    # Security
    def is_ready(self):
        raise NotImplementedError


    def get_form_state(self):
        """Translate workflow state to user-friendly state.
        """
        state = self.get_workflow_state()
        # Match the enumerate in order to search by values
        get_value = WorkflowState.get_value
        if state == EMPTY:
            if self.is_first_time():
                return get_value('vide')
            return get_value('en_cours')
        elif state == SENT:
            return get_value('envoye')
        elif state == EXPORTED:
            return get_value('exporte')
        elif state == MODIFIED:
            return get_value('modifie')
        raise NotImplementedError, state


    def is_first_time(self):
        return self.handler.timestamp is None



###########################################################################
# Register
register_field('form_state', Unicode(is_indexed=True, is_stored=True))
