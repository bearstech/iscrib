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
from itools.core import get_abspath, merge_dicts
from itools.csv import CSVFile
from itools.datatypes import String, Boolean
from itools.gettext import MSG
from itools.handlers import File as FileHandler

# Import from ikaaro
from ikaaro.file import File
from ikaaro.registry import register_field
from ikaaro.text import Text
from ikaaro.webpage import WebPage_View
from ikaaro.workflow import workflow

# Import from scrib
from datatypes import Numeric, NumInteger, NumDecimal, NumTime, NumShortTime
from datatypes import NumDate, NumShortDate, NumDigit, Unicode, EnumBoolean
from datatypes import WorkflowState, make_enumerate
from form_views import Send_View
from utils import SI
from workflow import EMPTY, SENT, EXPORTED, MODIFIED


dt_mapping = {
    'boolean': EnumBoolean,
    'dec': NumDecimal,
    'digit': NumDigit,
    'hh:mm': NumShortTime,
    'hhh:mm': NumTime,
    'int': NumInteger,
    'jj/mm/aaaa': NumDate,
    'mm/aaaa': NumShortDate,
    'str': Unicode,
    'text': Text}


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



def get_schema_pages(path):
    path = get_abspath(path)
    handler = CSVFile(path)
    rows = handler.get_rows()
    # Skip header
    rows.next()

    schema = {}
    pages = {}
    for (name, title, form, page_number, dt_name, format, vocabulary,
            is_mandatory, fixed, sum, dependances, abrege, init) in rows:
        # The name
        name = name.strip()
        if name == '':
            continue
        if name[0] == '#':
            name = name[1:]
        # The datatype
        dt_name = dt_name.strip().lower()
        if dt_name == 'enum':
            datatype = make_enumerate(vocabulary)
        else:
            datatype = dt_mapping.get(dt_name)
        if datatype is None:
            raise NotImplementedError, (dt_name, path)
        # The page number
        page_number = page_number.replace('-', '')
        # allow multiple page numbers
        page_numbers = []
        for page in page_number.split(','):
            assert page.isalpha()
            page_fields = pages.setdefault(page, set())
            page_fields.add(name)
            page_numbers.append(page)
        # Mandatory
        is_mandatory = (not is_mandatory or is_mandatory.upper() == 'OUI')
        # Sum
        sum = sum.strip()
        # Add to the schema
        page_numbers = tuple(page_numbers)
        schema[name] = datatype(format=format, pages=page_numbers,
                is_mandatory=is_mandatory, sum=sum, abrege=abrege)
    return schema, pages



def get_controls(path):
    path = get_abspath(path)
    handler = CSVFile(path)
    rows = handler.get_rows()
    # Skip header
    rows.next()
    return list(rows)



class FormHandler(FileHandler):
    schema = {}
    pages = {}


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
    class_icon48 = 'scrib/images/form48.png'
    class_views = ['envoyer', 'exporter', 'imprimer', 'aide']
    class_handler = FormHandler
    workflow = workflow

    # Views
    envoyer = Send_View()
    exporter = WebPage_View(template='../../aide', title=MSG(u"Exporter"))
    imprimer = WebPage_View(template='../../aide', title=MSG(u"Imprimer"))
    aide = WebPage_View(template='../../aide', title=MSG(u"Aide"))


    @classmethod
    def get_metadata_schema(cls):
        return merge_dicts(File.get_metadata_schema(),
                           departement=String)



    def _get_catalog_values(self):
        values = File._get_catalog_values(self)
        values['is_bm'] = self.is_bm()
        values['is_bdp'] = self.is_bdp()
        values['departement'] = self.get_property('departement')
        values['form_state'] = self.get_form_state()
        return values


    ######################################################################
    # Scrib API
    @staticmethod
    def is_bm():
        raise NotImplementedError


    @staticmethod
    def is_bdp():
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


    def get_namespace(self, context):
        # TODO
        return {'is_ready': False}



###########################################################################
# Register
register_field('is_bm', Boolean(is_indexed=True, is_stored=True))
register_field('is_bdp', Boolean(is_indexed=True, is_stored=True))
register_field('departement', Unicode(is_indexed=True, is_stored=True))
register_field('form_state', Unicode(is_indexed=True, is_stored=True))
