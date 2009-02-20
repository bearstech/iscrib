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
from copy import deepcopy
from decimal import Decimal as dec, InvalidOperation
from pprint import pformat
from time import time
import datetime
import logging

# Import from mysql
from MySQLdb import OperationalError

# Import from itools
from itools.catalog import KeywordField, TextField, BoolField
from itools.datatypes import is_datatype, Unicode, Boolean, String
from itools.stl import stl
from itools.csv import CSVFile
from itools.handlers import File

# Import from ikaaro
from ikaaro.text import Text
from ikaaro.workflow import workflow

# Import from scrib
from scrib import config
from datatypes import Checkboxes, Integer, EPCI_Statut, Decimal
from utils import (get_checkbox_value, get_connection, MSG_NO_MYSQL, make_msg,
        bm_annexes, ua_epci)


MailResponsableBM = config.get_value('MailResponsableBM')
MailResponsableBDP = config.get_value('MailResponsableBDP')

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
    class_views = [['controles_form'], ['report_csv'], ['print_form'],
                   ['help']]
    class_handler = FormHandler
    workflow = workflow


    ######################################################################
    # Form API
    def update_fields(self, fields):
        self.handler.fields.update(fields)
        self.handler.set_changed()


    @staticmethod
    def get_schema():
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
    def get_catalog_fields(self):
        fields = Text.get_catalog_fields(self)
        fields += [TextField('user_town'),
                   KeywordField('dep', is_stored=True),
                   KeywordField('year'),
                   BoolField('is_BDP'),
                   BoolField('is_BM'),
                   KeywordField('form_state', is_stored=True)]
        return fields


    def get_catalog_values(self):
        values = Text.get_catalog_values(self)
        values['user_town'] = self.get_user_town()
        values['dep'] = self.get_dep()
        values['year'] = self.get_year()
        values['is_BDP'] = self.is_BDP()
        values['is_BM'] = self.is_BM()
        values['form_state'] = self.get_form_state()
        return values


    #######################################################################
    # Namespaces
    def get_namespace(self, context):
        schema = self.get_schema()
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
        return namespace


    def get_ns_and_h(self, context, xml, autogen_xml, view):
        """
        autogen_xml = 'FormXX_report1_autogen.xml'
        xml = 'FormXX_report1.xml'
        """
        namespace = self.get_namespace(context)

        try:
            template = self.get_object('/ui/scrib/%s' % autogen_xml)
        except LookupError:
            template = self.get_object('/ui/scrib/%s' % xml)

        if view == 'printable':
            namespace['printable'] = True
            context.response.set_header('Content-Type',
                                        'text/html; charset=UTF-8')
            namespace['body'] = stl(template, namespace)
            template = self.get_object('/ui/scrib/printable_template.xhtml')
        elif view == 'print_all':
            namespace['printable'] = True

        namespace['submit_button'] = namespace['is_allowed_to_edit'] \
                                     and not namespace['printable']

        return stl(template, namespace)


    ######################################################################
    # User interface
    #######################################################################

    #######################################################################
    # Control report
    controles_form__access__ = 'is_allowed_to_view'
    controles_form__label__ = u'Contrôlez votre saisie'
    def controles_form(self, context):
        schema = self.get_schema()
        controles = self.get_controles()
        alertes = self.get_alertes()
        namespace = self.get_namespace(context)
        dependencies = self.get_dependencies()
        # State
        state = self.get_form_state()

        #############################################################
        # Vérification des champs renseignés
        restype = []
        j = 0
        for name in schema:
            field_def = schema[name]
            stype = field_def[0]
            default = field_def[1]
            empty = False
            if (stype is not String and stype is not EPCI_Statut
                    and stype is not Unicode
                    and name not in ['fieldK%s' % i for i in range(40,47)]):
                if namespace[name] in ('', None):
                    dependance = dependencies.get(name)
                    if dependance is not None:
                        if namespace.get(dependance, False) == True:
                            empty = True
                    else:
                        empty = True
            if empty:
                j += 1
                restype.append({'chp': name[len('field'):],
                                'num': j,
                                'type': u'Non renseigné',
                                })

        restype_for_sort = [(x['type'], x['chp'], x) for x in restype]
        restype_for_sort.sort()
        restype = [x[-1] for x in restype_for_sort]

        #namespace['restype'] = restype
        i = 0
        for res in self.split_in4(restype):
            namespace['restype%s' % i] = res
            i += 1

        #############################################################
        # Controls
        res = []
        i = 0

        for controle in controles:
            key, text, expr1, expr2, expr3, left_args, right_args = controle
            try:
                x1 = eval(expr1, namespace)
            except (TypeError, ZeroDivisionError):
                x1 = '?'
            try:
                x2 = eval(expr2, namespace)
            except (TypeError, ZeroDivisionError):
                x2 = '?'
            try:
                x3 = eval(expr3, namespace)
            except (TypeError, ZeroDivisionError):
                x3 = '?'

            left_values = []
            for arg in left_args:
                left_values.append(eval(arg , namespace))

            right_values = []
            for arg in right_args:
                right_values.append(eval(arg , namespace))

            empty = None in left_values or None in right_values
            fail = x3 is False

            if not key is 'sum':
                if str(x1) == 'NC' and str(x2) == 'NC':
                    fail = False
                    empty = False
                elif str(x1) is None  and str(x2) == 'NC':
                    empty = True
                    fail = False
            else:
                # 0006009: une somme en dépendance d'un champ désactivé
                field_name = 'field%s' % expr1
                if (field_name in dependencies
                        and namespace[dependencies[field_name]] is False):
                    empty = False
                    fail = False
                # Si plusieurs termes de la somme sont égaux à NC, alors le
                # total doit être strictement supérieur à la somme des termes
                # différents de NC
                elif not 'NC' in right_values:
                    pass
                elif right_values.count('NC') > 1:
                    key_type = schema[field_name][0]

                    if key_type is Integer:
                        sum_of_not_NC = Integer(0)
                    elif key_type is Decimal:
                        sum_of_not_NC = Decimal(0)
                    for real_val in [x for x in right_values
                            if x not in ['NC', None]]:
                        sum_of_not_NC += real_val

                    if sum_of_not_NC:
                        fail = ( x1 <= sum_of_not_NC ) and (str(x1) != 'NC')
                    else:
                        fail = not ( x1 == 'NC')
                # Si un seul des termes de la somme est égal à NC, alors le
                # total doit être égal à NC
                elif right_values.count('NC') == 1:
                    fail = not (x1 == 'NC')

            if empty or fail:
                i += 1
                trans = {'None': 'Rien',
                         'False': 'Faux',
                         'True' : 'Vrai',
                         '?' : 'Incomplet'
                         }
                x1 = trans.get(str(x1), x1)
                x2 = trans.get(str(x2), x2)
                res.append({'id': key,
                            'expr1': str(expr1),
                            'num': str(i),
                            'text': text % (x1, x2),
                            'empty': empty,
                            'fail': fail })

        namespace['res2'] = [r for ii, r in enumerate(res) if ii%2]
        namespace['res1'] = [r for ii, r in enumerate(res) if not ii%2]
        namespace['ppres1'] = pformat(namespace['res1'])
        namespace['ppres2'] = pformat(namespace['res2'])

        # clasify controles by report
        sec2form = {'A': ';report_form1', 'B': ';report_form2',
                    'C': ';report_form3', 'D': ';report_form4',
                    'E': ';report_form5', 'F': ';report_form6',
                    'G': ';report_form7', 'H': ';report_form8',
                    'I': ';report_form9',}
        titles = sec2form.keys()
        titles.sort()

        blocks = []
        for key in titles:
            lines = [d for d in res if d['expr1'].startswith(key)]
            if lines:
                block = {'section_title': key,
                         'section_url': sec2form[key],
                         'lines': lines}
                blocks.append(block)

        namespace['controle_blocks2'] = [r for i, r in enumerate(blocks) if i%2]
        namespace['controle_blocks1'] = [r for i, r in enumerate(blocks)
                                         if not i%2]

        # ControlesFailed
        failedControles = [control for control in res if control.get('fail')]
        ControlesFailed = len(failedControles) and True or False

        # add ControlesFailed
        is_complete = namespace['is_complete']
        namespace['is_complete'] =  is_complete and not ControlesFailed
        #disable control for testing #namespace['is_complete'] = True
        # add ControlesFailed
        is_finished = namespace['is_finished']

        namespace['is_finished'] =  is_finished and not ControlesFailed
        #disable control for testing
        #namespace['is_finished'] = True

        is_exported = self.get_form_state() in (u'Exporté',
                                                u'Modifié après export')
        namespace['is_exportable'] = is_finished or is_exported

        #############################################################
        # Alerts
        resalt = []
        for key, text, expression in alertes:
            d = {'idalt': key,
                 'textalt': text}
            try:
                result = eval(expression, namespace)
                if key != 'G' and key != 'K':
                    d['resultat'] = "%.2f" % result
                else:
                    trans = { True: 'Oui', False: 'Non' }
                    d['resultat'] = trans.get(result == 0, '?')
            except (TypeError, ZeroDivisionError):
                d['resultat'] = '?'

            resalt.append(d)
        namespace['resalt'] = resalt

        #############################################################
        # Actions
        namespace['allGood'] = len([ x for x in restype
                                     if x['type'] != u'OK' ]) == 0

        namespace['state'] = state
        namespace['total'] = len(schema)
        ac = self.get_access_control()
        namespace['is_admin'] = ac.is_admin(context.user, self)

        template = self.get_object('/ui/scrib/Form_controles.xml')
        return stl(template, namespace)


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

        schema = self.get_schema()
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

        return  (All_fields, All_mandatorie, All_optional,
                 optional_nonEmpties, mandatory_nonEmpties, Empties)


    def get_total_good_fields(self, namespace):
        mendatories = []
        optionals = []
        empties = []
        schema = self.get_schema()
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


    pending2submitted__access__ = 'is_allowed_to_edit'
    def pending2submitted(self, context):
        root = context.root
        user = context.user

        # Change state
        self.set_property('state', 'pending')

        # Build email
        namespace = self.get_namespace(context)
        message_pattern = u'To: %(to_addr)s\n' \
                          u'From: %(from_addr)s\n' \
                          u'Subject: %(subject)s\n' \
                          u'\n' \
                          u'%(body)s\n'
        dep = self.get_dep()
        report_email = namespace['field11']
        if self.is_BDP():
            to_addr = unicode(MailResponsableBDP, 'utf_8')
            subject = u'SCRIB-BDP : %s' % dep
            body = u'La Bibliothèque %s a terminé son formulaire.' % self.name
        else:
            to_addr = unicode(MailResponsableBM, 'utf_8')
            subject = u'SCRIB-BM : %s (%s)' % (namespace['code_ua'], dep)
            body = u'La Bibliothèque %s (%s), du département %s, a terminé' \
                   u' son formulaire.'
            body = body % (self.name, self.get_title(), dep)
        message = message_pattern % {'to_addr': to_addr,
                                     'from_addr': report_email,
                                     'subject': subject,
                                     'body': body}
        comeback_msg = (u'Terminé, un e-mail est envoyé à votre '
                        u'correspondant DLL.')
        try:
            root.send_email(to_addr, subject, from_addr=report_email,
                    text=body, subject_with_host=False)
        except Exception, e:
            context.server.log_error(context)
            comeback_msg = u"%r %s" % (Exception, e)
        self.scrib_log(context, event='email sent', content=message)

        # Recipient
        r_subject = u'Accusé de réception, DLL'
        r_body = (u"Votre rapport annuel a bien été reçu par votre "
                  u"correspondant à la DLL.\n\nNous vous remercions "
                  u"de votre envoi.\n\nCordialement.")
        r_message = message_pattern % {'to_addr': report_email,
                                       'from_addr': to_addr,
                                       'subject': r_subject,
                                       'body': r_body}
        try:
            root.send_email(report_email, r_subject, from_addr=to_addr,
                    text=r_body, subject_with_host=False)
        except:
            context.server.log_error(context)
        self.scrib_log(context, event='recipe sent', content=r_message)

        return context.come_back(comeback_msg, goto=';controles_form')


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
        schema = self.get_schema()
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


    submitted2exported__access__ = 'is_admin'
    def submitted2exported(self, context):
        try:
            connection = get_connection()
            cursor = connection.cursor()
            namespace = self.get_namespace(context)
            schema = self.get_schema()
            quote_namespace(namespace, schema)
            # Update dans la base ADRESSE
            query = (u'update adresse08 set libelle1="%(field1)s",'
                     u'libelle2="%(field2)s",local="%(field30)s",'
                     u'voie_num="%(field31)s",voie_type="%(field32)s",'
                     u'voie_nom="%(field33)s",cpbiblio="%(field4)s",'
                     u'ville="%(field5)s",cedexb="%(field6)s",'
                     u'directeu="%(field7)s",st_dir="%(field8)s",'
                     u'tele="%(field9)s",fax="%(field10)s",'
                     u'mel="%(field11)s",www="%(field12)s",'
                     u'intercom="%(field13)s",gestion="%(field14)s",'
                     u'gestion_autre="%(field15)s" '
                     u'where code_bib=%(code_ua)s')
            query = query % namespace

            # XXX charset?
            cursor.execute(query)
            cursor.execute('commit')

            # Remove from the database
            code_ua = namespace['code_ua']
            dept = self.get_dep()
            year = self.parent.name[-4:]
            btype = 'bdp'
            if self.is_BM():
                btype = 'bm'
            table = '%s%s' % (btype ,year[-2:])
            query = "delete from %s where Code_UA=%s" % (table, code_ua)
            cursor.execute(query)
            cursor.execute('commit')

            # Add into the database
            query = self.get_export_query(namespace)
            cursor.execute(query)
            cursor.execute('commit')
            self.set_property('state', 'public')

            cursor.close()
            connection.close()
        except OperationalError:
            context.server.log_error(context)
            context.commit = False
            return context.come_back(MSG_NO_MYSQL)

        message = u'Le rapport a été exporté'
        return context.come_back(message, goto=';controles_form')


    def get_dependencies(self):
        """
        {'fieldB32': 'fieldB31',
         'fieldB34': 'fieldB33',
         'fieldB36': 'fieldB35',
         'fieldB41': 'fieldB40',
         'fieldB42': 'fieldB40',
        """
        schema = self.get_schema()
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
        schema = self.get_schema()
        sums = {}
        for field_id in schema.keys():
            field_def = schema[field_id]
            dep_or_sum = len(field_def) == 3
            if dep_or_sum:
                fields = field_def[2].get('sum')
                sums[field_id] = fields
        return sums


    fill_report_form__access__ = True
    fill_report_form__label__ = u'Auto remplissage'
    def fill_report_form(self, context):
        template = self.get_object('/ui/scrib/Form_fill_report.xml')
        return template.to_str()


    fill_report__access__ = 'is_allowed_to_edit'
    def fill_report(self, context):
        schema = self.get_schema()
        fields = {}

        t0 = time()
        ns = self.get_namespace(context)
        for key in schema:
            field_type = schema[key][0]
            field_default = schema[key][1]
            is_sum = False
            if len(schema[key]) == 3:
                is_sum = schema[key][2].get('sum', False)
            keyNumber = key[len('field'):]
            if is_datatype(field_type, String):
                if ns[key]:
                    value = ns[key]
            elif is_datatype(field_type, EPCI_Statut):
                value = '4'
            elif is_datatype(field_type, Unicode):
                if ns[key]:
                    value = ns[key]
                else:
                    # do not fill annexes
                    if not keyNumber.startswith('J'):
                        value = u'coué'
                    else:
                        value = u''
            elif is_datatype(field_type, Integer):
                if is_sum:
                    value = Integer(len(is_sum) * 5)
                    e_list = ['E74X', 'E46Z', 'E67Z', 'E71Z', 'E74Y', 'E74Z']
                    g_list = ['G25Y', 'G26Y', 'G26Z']
                    if key in ['field' + x for x in e_list + g_list]:
                        value = Integer('NC')
                else:
                    value = Integer(5)
            elif is_datatype(field_type, Decimal):
                value = dec('3.14')
                if is_sum:
                    value = value * dec(len(is_sum))
                    value = Decimal(value)
                else:
                    value = Decimal(value)
            elif is_datatype(field_type, Checkboxes):
                value = '##1'
            elif is_datatype(field_type, Boolean):
                value = True
            else:
                value = '0'

            fields[key] = value

        self.update_fields(fields)
        t = time() - t0

        message = u'Rapport auto rempli en %.2f secondes' % t
        return context.come_back(message, goto=';controles_form')


    report__access__ = 'is_allowed_to_edit'
    def report(self, context):
        schema = self.get_schema()
        fields = {}

        referer = context.request.referrer
        new_referer = deepcopy(referer)

        dependencies = self.get_dependencies()
        sums = self.get_sums()

        notR = [] # list of empty field
        badT = [] # list of field of bad type
        badT_missing = [] # list of field to highlight (badT_missing)
        badT_values = {} # a dict of field : value to put into namespace

        old_form_state = self.get_form_state()

        for key in context.get_form_keys():
            if key not in schema:
                continue
            field_type = schema[key][0]
            field_default = schema[key][1]
            #########################################
            # Take the value from the form
            # Support checkboxes
            if is_datatype(field_type, Checkboxes):
                values = context.get_form_values(key)
                value = '##'.join(values)
            else:
                value = context.get_form_value(key)
            value = value.strip()
            keyNumber = key[len('field'):]

            #########################################
            # Dependance machinery XXX need to be clean up and commented
            # We need to finish comments and put it in a method
            # dependancies = {'A13': 'A11', 'A12': 'A11'}
            # dependancies.keys() == ['A13', 'A12']
            # None if no dep
            dependance = dependencies.get(key)

            #########################################
            # Field as the sum of other fields
            sum = key in sums

            ## Objectif : we set empty = True or False
            ## Set value to '' if dep field is False
            # True : no dep AND no value AND no String/Unicode AND
            # False :
            empty = False
            if not is_datatype(field_type, (String, Unicode)):
                if dependance is not None:
                    # here we know if they are a dependancies
                    # and
                    dependance_type = schema[dependance][0]
                    if is_datatype(dependance_type, Checkboxes):
                        true = context.get_form_value(dependance, '0') != '0'
                    else:
                        true = context.get_form_value(dependance, '0') == '1'
                    if true:
                        if not value:
                            empty = True
                    # clean value if dependance False
                    else:
                        if value:
                            value = ''
                elif not sum:
                    empty = not str(value)

            if key in ['fieldK%sY' % i for i in range(17, 31)]:
                empty = False
            if key in ['fieldK%s' % i for i in range(40, 46)]:
                empty = False
            #########################################
            # fill badT_missing and badT  lists
            if empty:
                notR.append(keyNumber)

            # Encode and store
            field_def = schema[key]
            type = field_def[0]
            default = field_def[1]
            # check for forbiden caracters, 8bits like "é"
            # use unicode instead
            try:
                value = type.decode(value)
            except (ValueError, UnicodeEncodeError, InvalidOperation):
                badT_missing.append('badT_%s' % keyNumber)
                badT.append(u'%s: <b>%s</b>'
                            % (keyNumber, unicode(value, 'UTF-8')))
                # we need the field and it's value in the
                #query even if the type is wrong
                badT_values[keyNumber] = value
            else:
                fields[key] = value

        # 0000320: pb calcul total et champ vide
        for key, terms in sums.items():
            if not terms:
                continue
            # no sum if an empty or NC
            empty_or_NC = [term for term in terms
                                if fields.get(term) in ('', None, 'NC')]
            if empty_or_NC:
                continue
            # no sum if a value manualy set
            if key in fields and fields.get(key) not in (0, '', None, 'NC'):
                continue
            # automatic sum
            key_type = schema[key][0]
            # Initialisation du type du total
            total = Decimal('0') if key_type is Decimal else Integer(0)
            for term in terms:
                total = fields[term] + total
            fields[key] = total

        if fields:
            self.update_fields(fields)

        if old_form_state == u'Exporté':
            self.set_workflow_state('modified')
        else:
            new_form_state = self.get_form_state()
            # 0005453: Reindex
            if new_form_state != old_form_state:
                context.server.change_object(self)

        new_referer, msg = make_msg(new_referer=new_referer, notR=notR,
                badT=badT, badT_missing=badT_missing, badT_values=badT_values)
        return context.come_back(msg, goto=new_referer)


    #######################################################################
    # Help
    help__access__ = True
    help__label__ = u'Aidez-vous !'
    def help(self, context):
        template = self.get_object('/ui/scrib/Form_help.xml')
        return template.to_str()


    help2__access__ = True
    def help2(self, context):
        context.response.set_header('Content-Type', 'text/html; charset=UTF-8')
        template = self.get_object('/ui/scrib/Form_help2.xhtml')
        return template.to_str()


    #######################################################################
    # Export
    #report_csv__access__ = Text.is_admin
    report_csv__access__ = True
    report_csv__label__ = u'Exportez chez vous votre rapport'
    def report_csv(self, context):
        """ Call downloadCSV """
        namespace = self.get_namespace(context)
        #is_finished = namespace['is_finished']
        state = self.get_workflow_state()
        is_finished = (state == 'pending')
        is_complete = namespace['is_complete']
        is_exported = self.get_form_state() == u'Exporté'
        namespace['show'] = is_finished or is_complete or is_exported
        template = self.get_object('/ui/scrib/Form_report_csv.xml')
        return stl(template, namespace)


    comments__access__ = 'is_allowed_to_view'
    comments__sublabel__ = u'Commentaires'
    def comments(self, context, view=None):
        return self.get_ns_and_h(context,
                                 'Form_comments.xml',
                                 'FormBM_report0_autogen.xml',
                                 view)


    #downloadCSV__access__ = 'is_admin'
    downloadCSV__access__ = True
    def downloadCSV(self, context):
        schema = self.get_schema()
        response = context.response

        response.set_header('Content-Type', 'text/comma-separated-values')
        response.set_header('Content-Disposition',
                'attachment; filename="scrib.csv"')

        namespace = self.get_namespace(context)
        # construct the csv
        names = schema.keys()
        names.sort()
        csv = CSVFile()
        csv.add_row(["Chapitre du formulaire", "rubrique", "valeur"])
        for name in names:
            value = namespace.get(name, '')
            if schema[name][0] is EPCI_Statut:
                label = [x['label'] for x in value if x['selected']]
                if label:
                    value = label[0]
                else:
                    value = ''
            name = name[len('field'):]
            chap = name[0]
            if value is None:
                value = "NULL"
            elif isinstance(value, bool):
                value = str(int(value))
            elif isinstance(value, (int, long, float, dec)):
                value = str(value)
            elif isinstance(value, unicode):
                value = value.encode('cp1252')
            else:
                # Culture Types
                value = value.__class__.encode(value)
            if not isinstance(value, str):
                raise "value", str(type(value))
            csv.add_row([chap, name, value])

        return csv.to_str(separator=';')
