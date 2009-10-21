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

# Import from the Standard Library

# Import from itools
from itools.core import get_abspath
from itools.csv import CSVFile
from itools.datatypes import Unicode, Boolean
from itools.handlers import File as FileHandler

# Import from ikaaro
from ikaaro.file import File
from ikaaro.registry import register_field
from ikaaro.text import Text
from ikaaro.workflow import workflow

# Import from scrib
from datatypes import Integer, Decimal, Time, ShortTime, Date, ShortDate
from datatypes import Digit
from help import HelpAware


workflow.add_state('modified', title=u"Modifié",
        description=u"Modifié après export.")



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
    for (name, title, form, page_number, type, repr, vocabulary,
            is_mandatory, fixed, somme, dependances, abrege, init) in rows:
        # The name
        name = name.strip()
        if name == '':
            # Ligne vide
            continue
        if name[0] == '#':
            name = name[1:]
        # The type and representation
        type = type.strip().lower()
        if type == 'text':
            repr = int(repr)
            type = Text
        elif type == 'str':
            repr = int(repr)
            type = Unicode
        elif type == 'int':
            repr = int(repr)
            type = Integer
        elif type == 'HHH:MM':
            type = Time
        elif type == 'hh:mm':
            type = ShortTime
        elif type == 'jj/mm/aaaa':
            type = Date
        elif type == 'mm/aaaa':
            type = ShortDate
        elif type == 'boolean':
            type = Boolean
        elif type == 'dec':
            repr = sum([ int(x) for x in repr.split(',') ]) + 1
            type = Decimal
        elif type == 'digit':
            repr = int(repr)
            type = Digit
        else:
            raise ValueError, "Type '%s' not supported in '%s'" % (type, path)
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
        is_mandatory = (is_mandatory.upper() == 'OUI')
        # Sum
        somme = somme.strip()
        # Add to the schema
        page_numbers = tuple(page_numbers)
        schema[name] = type(repr=repr, pages=page_numbers,
                                    is_mandatory=is_mandatory, somme=somme,
                                    abrege=abrege)

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
        fields = {}
        for key in kw:
            if key in self.schema:
                datatype = self.schema[key]
                try:
                    value = datatype.decode(kw[key])
                except ValueError:
                    raise ValueError, "%s: %s" % (key, kw[key])
                if value is not None:
                    fields[key] = value
        self.fields = fields


    def _load_state_from_file(self, file):
        fields = {}
        for line in file.readlines():
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                if key in self.schema:
                    value = value.strip()
                    datatype = self.schema[key]
                    try:
                        fields[key] = datatype.decode(value)
                    except:
                        raise ValueError, "key '%s' value '%s'" % (key,
                                                                   value)
        self.fields = fields


    def to_str(self, encoding='UTF-8'):
        fields = self.fields
        lines = []
        for key in fields:
            value = fields[key]
            datatype = self.schema[key]
            lines.append('%s:%s' % (key, datatype.encode(value)))
        return '\n'.join(lines)


    ######################################################################
    # API (private)
    def _get_value(self, name):
        datatype = self.schema[name]
        return self.fields.get(name, datatype.decode(datatype.default))


    def _set_value(self, name, value):
        self.set_changed()
        self.fields[name] = value


    @classmethod
    def somme(cls, datatype, formule, **kw):
        value = 0

        for terme in formule.split('+'):
            terme = terme.strip()
            try:
                valeur = kw[terme]
            except KeyError:
                return None
            if valeur.upper() == 'NC':
                return 'NC'
            elif valeur == '':
                valeur = 0
            dt = cls.schema[terme]
            try:
                valeur = dt.decode(valeur)
            except ValueError:
                return None
            value += valeur

        return datatype.encode(value)



class Form(HelpAware, File):
    class_id = 'Form'
    class_handler = FormHandler
    class_icon48 = 'scrib/images/form48.png'
    class_views = ['controles', 'report_csv', 'print_form', 'help']
    class_handler = FormHandler
    workflow = workflow

    # Views


    #def _get_catalog_values(self):
    #    values = File._get_catalog_values(self)
    #    #values['user_town'] = self.get_user_town()
    #    values['is_bm'] = self.is_bm()
    #    values['is_bdp'] = self.is_bdp()
    #    values['departement'] = self.get_property('departement')
    #    values['form_state'] = self.get_form_state()
    #    return values


    ######################################################################
    # Scrib API
    @staticmethod
    def is_bm():
        raise NotImplementedError


    @staticmethod
    def is_bdp():
        raise NotImplementedError


    def get_form_state(self):
        # State
        state = self.get_workflow_state()
        if state == 'private':
            if len(self.handler.fields) == 0:
                state = u'Vide'
            else:
                state = u'En cours'
        elif state == 'pending':
            state = u'Terminé'
        elif state == 'public':
            state = u'Exporté'
        elif state == 'modified':
            state = u'Modifié après export'
        return state


    def get_namespace(self, context):
        # TODO
        return {'is_ready': False}



###########################################################################
# Register
#register_field('is_bm', Boolean(is_stored=True))
#register_field('is_bdp', Boolean(is_stored=True))
#register_field('departement', Unicode(is_indexed=True, is_stored=True))
#register_field('form_state', Unicode(is_indexed=True, is_stored=True))
