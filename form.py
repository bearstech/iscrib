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
from itools.gettext import MSG
from itools.handlers import File as FileHandler

# Import from ikaaro
from ikaaro.file import File
from ikaaro.folder import Folder
from ikaaro.registry import register_field
from ikaaro.workflow import WorkflowAware

# Import from scrib
from datatypes import Numeric, NumDecimal
from datatypes import Unicode
from datatypes import WorkflowState
from form_views import Todo_View, Form_Help
from utils import SI
from workflow import workflow, EMPTY, SENT, EXPORTED, MODIFIED


def quote_namespace(namespace, schema):
    for key, value in namespace.items():
        field_def = schema.get(key)
        if field_def is not None:
            ftype = field_def[0]
            if ftype is Unicode:
                   if value is not None:
                       value = value.replace(u"€", u"eur")
                       value = value.replace(u'"', u'\\"')
                       value = value.replace(u"&quot;", u'\\"')
                       value = value.replace(u"'", u"\\'")
                   namespace[key] = value



class FormHandler(FileHandler):
    schema = {}
    pages = {}
    controls = []


    ######################################################################
    # Load/Save
    def new(self, **kw):
        """Preload with all known keys, fill the gaps with defaults.
        """
        fields = {}
        for key, datatype in self.schema.iteritems():
            try:
                data = kw[key]
            except KeyError:
                data = datatype.get_default()
            value = datatype.decode(data)
            fields[key] = value
        self.fields = fields


    def _load_state_from_file(self, file):
        """Load known values, the rest will be the default values.
        """
        kw = {}
        for line in file.readlines():
            if ':' not in line:
                continue
            key, data = line.split(':', 1)
            kw[key.strip()] = data.strip()
        self.new(**kw)


    def to_str(self, encoding='UTF-8'):
        fields = self.fields
        lines = []
        for key, value in fields.iteritems():
            datatype = self.schema[key]
            lines.append('%s:%s' % (key, datatype.encode(value)))
        return '\n'.join(lines)


    ######################################################################
    # API
    def get_value(self, name):
        return self.fields[name]


    def set_value(self, name, value):
        self.fields[name] = value
        self.set_changed()


    @classmethod
    def sum(cls, datatype, formula, **kw):
        sum = datatype(0)
        for term in formula.split('+'):
            term = term.strip()
            try:
                data = kw[term]
            except KeyError:
                return None
            if data.upper() == 'NC':
                return 'NC'
            dt = cls.schema[term]
            try:
                value = dt.decode(data)
            except Exception:
                return None
            sum += value
        return sum



class Form(File):
    class_id = 'Form'
    class_handler = FormHandler
    class_views = ['envoyer', 'exporter', 'imprimer', 'aide']
    class_handler = FormHandler
    workflow = workflow

    # Views
    envoyer = Todo_View(title=MSG(u"Contrôle de saisie"))
    exporter = Todo_View(title=MSG(u"Import du rapport"))
    imprimer = Todo_View(title=MSG(u"Impression du rapport"))
    aide = Form_Help()


    def _get_catalog_values(self):
        return merge_dicts(File._get_catalog_values(self),
                form_state=self.get_form_state())


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


    def get_vars(self):
        return merge_dicts(self.handler.fields,
                           SI=SI)


    def get_floating_vars(self):
        vars = {}
        for name, value in self.handler.fields.iteritems():
            if isinstance(value, Numeric):
                vars[name] = NumDecimal(value.value)
            else:
                vars[name] = value
        return vars


    def is_first_time(self):
        return self.handler.timestamp is None


    def is_ready(self):
        schema = self.handler.schema
        for name, value in self.handler.fields.iteritems():
            datatype = schema[name]
            if datatype.is_mandatory and not value:
                return False
        return True



class MultipleForm(WorkflowAware, Folder):
    class_id = 'MultipleForm'
    workflow = workflow


    def is_first_time(self):
        return not len(self.get_names())


    def is_ready(self):
        for form in self.get_resources():
            if not form.is_ready():
                return False
        return True



###########################################################################
# Register
register_field('form_state', Unicode(is_indexed=True, is_stored=True))
