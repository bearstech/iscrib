# -*- coding: UTF-8 -*-
# Copyright (C) 2006 Luis Belmar Letelier <luis@itaapy.com>
# Copyright (C) 2006-2008 Hervé Cauwelier <herve@itaapy.com>
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
import datetime
import logging

# Import from itools
from itools.datatypes import is_datatype, Unicode, Boolean, String
from itools.handlers import File

# Import from ikaaro
from ikaaro.registry import register_field
from ikaaro.text import Text
from ikaaro.workflow import workflow

# Import from scrib
from datatypes import Checkboxes, Integer, EPCI_Statut, Decimal
from utils import get_checkbox_value, bm_annexes, ua_epci
from form_views import Form_DownloadCSV, Form_Help, Form_Help2
from form_views import Form_Controles, Form_View, Form_ReportCSV


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



class FormHandler(File):

    def new(self):
        self.fields = {}


    def _load_state_from_file(self, file, schema):
        data = file.read()
        fields = {}
        for line in data.splitlines():
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                if key in schema:
                    value = value.strip()
                    field_def = schema[key]
                    type = field_def[0]
                    default = field_def[1]
                    fields[key] = type.decode(value)
        self.fields = fields


    def to_str(self, schema, encoding='UTF-8'):
        result = []
        for key, value in self.fields.items():
            new_value = schema[key][0].encode(value)
            if isinstance(new_value, unicode):
                 new_value = new_value.encode('UTF-8')
            line = '%s:%s\n' % (key, new_value)
            result.append(line)
        return ''.join(result)



class Form(Text):

    class_id = 'Form'
    class_icon48 = 'scrib/images/form48.png'
    class_views = ['controles_form', 'report_csv', 'print_form', 'help']
    class_handler = FormHandler
    workflow = workflow

    # Views
    controles_form = Form_Controles()
    report_csv = Form_ReportCSV()
    help = Form_Help()
    help2 = Form_Help2()
    downloadCSV = Form_DownloadCSV()
    comments = Form_View(access='is_allowed_to_view',
                         title=u'Commentaires',
                         xml='Form_comments.xml',
                         autogen_xml='FormBM_report0_autogen.xml')


    ######################################################################
    # Form API
    def update_fields(self, fields):
        self.handler.fields.update(fields)
        self.handler.set_changed()


    @staticmethod
    def get_scrib_schema():
        raise NotImplementedError


    @staticmethod
    def is_BM():
        raise NotImplementedError


    @staticmethod
    def is_BDP():
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


    ######################################################################
    # Catalog API
    def _get_catalog_values(self):
        values = Text._get_catalog_values(self)
        values['user_town'] = self.get_user_town()
        values['dep'] = self.get_dep()
        values['year'] = self.get_year()
        values['is_BDP'] = self.is_BDP()
        values['is_BM'] = self.is_BM()
        values['form_state'] = self.get_form_state()
        return values


    def get_sets(self, namespace):
        """
        All_fields =  All_mandatorie +  All_optional
        All_fields = optional_nonEmpties + mandatory_nonEmpties + Empties
        return :
                 (All_fields, All_mandatorie, All_optional,
                  optional_nonEmpties, mandatory_nonEmpties, Empties)

        Take dependencies into account: if they
        for fieldXX put from mandatory_nonEmpties to optional_nonEmpties
        if fieldXX has dependencies whitch valeus are not False
        """
        All_fields, All_mandatorie, All_optional = [], [], []
        optional_nonEmpties, mandatory_nonEmpties, Empties = [], [], []

        schema = self.get_scrib_schema()
        dependencies = self.get_dependencies()
        # All_fields
        All_fields = schema.keys()
        for key in schema.keys():
            field_def = schema[key]
            field_type = field_def[0]
            value = namespace[key]
            if value in ('', None):
                empty = False
                # Empties
                Empties.append(key)
            is_mandatory = (not is_datatype(field_type, (Unicode,
                                                         EPCI_Statut,
                                                         String))
                                and (key != 'fieldK0')
                                and (key not in ['fieldK%s' % i
                                         for i in range(40,47)]))
            dependence_id = dependencies.get(key)
            if dependence_id is not None:
                dependence_value = namespace.get(dependence_id, False)
                is_mandatory = is_mandatory and dependence_value
            if is_mandatory:
                # All_mandatorie
                All_mandatorie.append(key)
                if value not in ('', None):
                    # mandatory_nonEmpties
                    mandatory_nonEmpties.append(key)
            else:
                # All_optional
                All_optional.append(key)
                if value not in ('', None):
                    # optional_nonEmpties
                    optional_nonEmpties.append(key)

        return (All_fields, All_mandatorie, All_optional,
                optional_nonEmpties, mandatory_nonEmpties, Empties)


    def get_total_good_fields(self, namespace):
        mendatories = []
        optionals = []
        empties = []
        schema = self.get_scrib_schema()
        dependencies = self.get_dependencies()

        for key in schema.keys():
            field_def = schema[key]
            field_type = field_def[0]
            value = namespace[key]
            if value in ('', None):
                empties.append(key)
            # XXX check if Checkbox and Decimal and ... are needed here
            if not is_datatype(field_type, Unicode):
                if value not in ('', None):
                    mendatories.append(key)
            else:
                optionals.append(key)

        return mendatories, optionals, empties


    def split_in4(self, restype):
        i_max = len(restype) + 3
        l_max = len(restype)
        res0 = [restype[i] for i in [0+j*4 for j in range(i_max)] if i < l_max]
        res1 = [restype[i] for i in [1+j*4 for j in range(i_max)] if i < l_max]
        res2 = [restype[i] for i in [2+j*4 for j in range(i_max)] if i < l_max]
        res3 = [restype[i] for i in [3+j*4 for j in range(i_max)] if i < l_max]
        return (res0, res1, res2, res3)


    def scrib_log(self, context, event=None, content=None):
        user = context.user
        # Event Log
        event = '\n' \
                '[Scrib event]\n' \
                'date   : %(date)s\n' \
                'uri    : %(uri)s\n' \
                'referrer: %(referrer)s\n' \
                'user   : %(user)s\n' \
                'event : %(event)s\n' \
                '\n'
        if isinstance(content, unicode):
            content = content.encode('utf_8')
        event = event % {'date': str(datetime.datetime.now()),
                         'uri': str(context.uri),
                         'referrer': str(context.request.referrer),
                         'user': user and user.name or None,
                         'event': ('email sent '
                                   '\n########\n%s\n#########') % content}
        logging.getLogger().info(event)


    def get_export_query(self, namespace):
        schema = self.get_scrib_schema()
        code_ua = namespace['code_ua']
        dept = self.get_dep()
        year = self.parent.name[-4:]
        btype = self.is_BM() and 'bm' or 'bdp'
        table = '%s%s' % (btype ,year[-2:])

        values = ["'%s'" % item for item in [code_ua, dept, year]]
        names = schema.keys()
        names.sort()
        keys = ['Code_UA', 'dept', 'exer']

        for name in names:
            field_def = schema[name]
            field_type = field_def[0]
            default = field_def[1]
            value = namespace[name]
            key = name.split('field')[-1]
            chap = key[0]

            if not chap.isdigit():
                keys.append(key)
                if value in ('', None, 'NC'):
                    value = "null"
                elif is_datatype(field_type, Unicode):
                    value = "'%s'" % value
                elif is_datatype(field_type, Integer):
                    value = str(value)
                elif is_datatype(field_type, Boolean):
                    if value:
                        value = "'O'"
                    else:
                        value = "'N'"
                elif is_datatype(field_type, Checkboxes):
                    # get the value from checkboxes
                    value = "'%s'" % get_checkbox_value(key, value)
                elif is_datatype(field_type, Decimal):
                    value = "'%s'" % str(value)
                elif is_datatype(field_type, EPCI_Statut):
                    # 0006036: Export général ne marche pas
                    if isinstance(value, str):
                        pass
                    else:
                        ids = [x['name'] for x in value if x['selected']]
                        if ids:
                            value = ids[0]
                        else:
                            value = '0'
                values.append(value)

        keys = ','.join(keys)
        values = ','.join(values)
        query = "INSERT INTO %s (%s) VALUES (%s);" % (table, keys, values)

        return query


    def get_dependencies(self):
        """
        {'fieldB32': 'fieldB31',
         'fieldB34': 'fieldB33',
         'fieldB36': 'fieldB35',
         'fieldB41': 'fieldB40',
         'fieldB42': 'fieldB40',
        """
        schema = self.get_scrib_schema()
        dependencies = {}
        for field_id in schema.keys():
            field_def = schema[field_id]
            dep_or_sum = len(field_def) == 3
            if dep_or_sum:
                fields = field_def[2].get('depend_field')
                if fields is None:
                    continue
                # 0006009: rubriques B41 et H38Z
                if not isinstance(fields, tuple):
                    raise TypeError, ("""champ "%s": la propriété"""
                                      """"depend_field" n'est pas un"""
                                      """ tuple""" % field_id)
                for field in fields:
                    # 0006009: rubriques B41 et H38Z
                    if field.count('field') > 1:
                        raise ValueError, ("""champ "%s": il manque une"""
                                           """ virgule dans "%s\"""" % (
                                               field_id, field))
                    dependencies[field] = field_id
        return dependencies


    def get_sums(self):
        schema = self.get_scrib_schema()
        sums = {}
        for field_id in schema.keys():
            field_def = schema[field_id]
            dep_or_sum = len(field_def) == 3
            if dep_or_sum:
                fields = field_def[2].get('sum')
                sums[field_id] = fields
        return sums



    def get_namespace(self, context):
        schema = self.get_scrib_schema()
        fields = self.handler.fields

        namespace = {}
        # Permissions
        user = context.user
        ac = self.get_access_control()
        namespace['is_allowed_to_edit'] = ac.is_allowed_to_edit(user, self)
        # Fields
        for name in schema:
            field_def = schema[name]
            type = field_def[0]
            default = field_def[1]
            key = name[len('field'):]
            # take the value in request first
            value = context.get_form_value(key)
            if value is None:
                # is the value is not in query string, take it in fields
                value = fields.get(name, default)
            namespace[name] = value
            # If name is 'fieldA23', add 'A23'
            if name.startswith('field'):
                namespace[key] = value
            # Booleans
            if is_datatype(type, Boolean):
                if namespace[name] is False:
                    namespace['%s_not' % name] = True
                else:
                    namespace['%s_not' % name] = False
            # Checkboxes
            elif is_datatype(type, Checkboxes):
                values = value.split('##')
                for i in range(1, 30, 1):
                    namespace['%s_%s' % (name, i)] = str(i) in values

            # for the names :fieldA21X, fieldA21Y, we call A21 field_name
            if not name[-1].isdigit(): # fieldA21X
                field_name = name.split('field')[-1][:-1]
            else: # fieldA21
                field_name = name.split('field')[-1]

            # From A21 we get _A21 and for A21X we get _A21 too
            field_name = '_' + field_name
            # From fieldA21 we get missing_A21
            missing_name = 'missing' + field_name
            # From fieldA21 we get badT_A21
            badT_name = 'badT' + field_name

            # Missing
            namespace[field_name] = None
            # we have  _B13 in the namespace but _B13XYZ in the form
            # so we make form_keys who remove X from _B13X
            form_keys = context.get_form_keys()
            form_keysXYZ = [k for k in form_keys if not k[-1].isdigit()]
            form_keysXYZ = [k[:-1] for k in form_keys]
            form_keys = form_keys + form_keysXYZ
            if missing_name in form_keys:
                namespace[field_name] = 'missing_field'
            if badT_name in form_keys:
                namespace[field_name] = 'badT_field'

        # State
        state = self.get_workflow_state()
        namespace['is_vide'] = self.get_form_state() == u'Vide'

        (All_fields, All_mandatorie, All_optional, optional_nonEmpties,
         mandatory_nonEmpties, Empties) = self.get_sets(namespace)

        namespace['All_fields'] = len(All_fields)
        namespace['All_mandatorie'] = len(All_mandatorie)
        namespace['All_optional'] = len(All_optional)
        namespace['optional_nonEmpties'] = len(optional_nonEmpties)
        namespace['mandatory_nonEmpties'] = len(mandatory_nonEmpties)
        namespace['mandatory_Empties'] = (len(All_mandatorie) -
                                          len(mandatory_nonEmpties))
        # from sets import Set
        # print Set(All_mandatorie).difference(Set(mandatory_nonEmpties))
        namespace['Empties'] =  len(Empties)

        is_ready = namespace['mandatory_Empties'] == 0
        namespace['is_ready'] = is_ready
        namespace['is_complete'] = state == 'private' and is_ready
        is_admin = ac.is_admin(user, self)
        namespace['is_finished'] = (state == 'pending' and is_admin)

        # Récupération des champs de la base ADRESSE
        dept = self.name
        champs_adr = self.base_lect(dept)
        namespace['insee'] = unicode(champs_adr[0], 'ISO-8859-1')
        namespace['type_adr'] = int(champs_adr[1])
        namespace['region'] = unicode(champs_adr[4], 'ISO-8859-1')
        namespace['dept'] = dept
        namespace['type'] = unicode(champs_adr[10], 'ISO-8859-1')
        namespace['commune'] = unicode(champs_adr[27], 'ISO-8859-1')
        namespace['minitel'] = unicode(champs_adr[28], 'ISO-8859-1')
        code_ua = int(champs_adr[17])
        namespace['code_ua'] = code_ua

        for field_name, champ_index in [('field1', 6), # LIBELLE1
                                        ('field2', 7), # LIBELLE2
                                        #('field3', 9), # VOIE
                                        ('field30', 8), # COMPLEMENT ADRESSE
                                        ('field31', 24), # Numéro VOIE
                                        ('field32', 25), # type de VOIE
                                        ('field33', 26), # NOM VOIE
                                        ('field4', 11), # CPBIBLIO
                                        ('field5', 18), # VILLE
                                        ('field6', 12), # CEDEXB
                                        ('field7', 3), # DIRECTEU
                                        ('field8', 19), # STDIR
                                        ('field9', 14), # TELE
                                        ('field10', 13), # FAX
                                        ('field11', 2), # MEL
                                        ('field12', 15), # WWW
                                        ('field13', 21), # INTERCOM
                                        ('field14', 22), # GESTION
                                        ('field15', 23)]: # GESTION_AUTRE
            if field_name in schema and not field_name in fields:
                # Prend la valeur par défaut dans la table adresse
                value = unicode(champs_adr[champ_index], 'ISO-8859-1')
                namespace[field_name] = value
                field_def = schema[field_name]
                type = field_def[0]
                if type is Checkboxes:
                    for i in range(1, 10):
                        namespace['%s_%s' % (field_name, i)] = (
                                unicode(i) == value)

        # autofill Annexes
        if self.is_BM():
            annexes = bm_annexes(code_ua)
            for k, v in annexes.items():
                key = 'field%s' % k
                if not k.startswith('J'):
                    pass
                elif not namespace[key]:
                    value = unicode(str(v), 'ISO-8859-1')
                    namespace[key] = value
        # autofill BM epci
        if self.is_BM():
            epci = ua_epci(code_ua)
            for k, v in epci.items():
                key = 'field%s' % k
                if not k.startswith('K'):
                    pass
                # Make the select options
                elif k.endswith('Z'):
                    kz = fields.get(key, '0')
                    if kz != '0':
                        namespace[key] = EPCI_Statut.get_namespace(kz)
                    else:
                        namespace[key] = EPCI_Statut.get_namespace(v)
                elif not namespace[key]:
                    if isinstance(v, float):
                        value = unicode(str(int(v)), 'ISO-8859-1')
                    else:
                        value = unicode(str(v), 'ISO-8859-1')
                    namespace[key] = value
        # get namespace
        sums = self.get_sums()
        for k, v in sums.items():
            if v:
                empty_or_NC = [i for i in v if namespace[i] in ('', None, 'NC')]
                # no sum if a value manualy set
                if namespace[k] and namespace[k] not in (0, '', None, 'NC'):
                    pass
                # no sum if an empty or NC
                elif empty_or_NC:
                    pass
                # automatic sum
                else:
                    res = [namespace[i] for i in v if namespace[i]]
                    key_type = schema[k][0]
                    if key_type is Decimal:
                        rr = Decimal('0')
                    elif key_type is Integer:
                        rr = Integer(0)
                    for i in res:
                        rr = i + rr
                    namespace[k] = rr

        namespace['printable'] = False
        namespace['submit_button'] = namespace['is_allowed_to_edit'] \
                                     and not namespace['printable']
        return namespace



register_field('is_BDP', Boolean)
register_field('is_BM', Boolean)
register_field('form_state', Unicode(is_indexed=True, is_stored=True))
