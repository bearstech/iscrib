# -*- coding: UTF-8 -*-
# Copyright (C) 2004 Luis Belmar Letelier <luis@itaapy.com> 
# Copyright (C) 2006 Hervé Cauwelier <herve@itaapy.com>
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
from pprint import pformat
from copy import deepcopy
from time import time
import logging
import datetime
import socket
import smtplib
import decimal

# Import from mysql
import MySQLdb

# Import from itools
from itools.datatypes import Unicode, Boolean, String
from itools.web import get_context
from itools.web.exceptions import UserError
from itools.stl import stl
from itools.csv import CSV

# Import from itools.cms
from itools.cms.text import Text as iText
from itools.cms.workflow import WorkflowAware, workflow
from itools.cms.utils import comeback

# Import from scrib
import CultureTypes
from CultureTypes import Checkboxes, Integer, EPCI_Statut, Decimal
from scrib import config
from Handler import Handler


SMTPServer = config.SMTPServer
MailResponsableBM = config.MailResponsableBM
MailResponsableBDP = config.MailResponsableBDP

SqlHost = config.SqlHost
SqlDatabase = config.SqlDatabase
SqlUser = config.SqlUser
SqlPasswd = config.SqlPasswd
SqlPort = config.SqlPort


workflow.add_state('modified', title=u"Modifié",
        description=u"Modifié après export.")


def get_checkbox_value(key, value):

    #len_choice = 2
    #if key == "G11":
    if key == "CV":
        len_choice = 15 
    if key == "CZ":
        len_choice = 16 
    elif key == "G11":
        len_choice = 7
    elif key == 'K3':
        len_choice = 4
    elif key == '13':
        len_choice = 2
    elif key == '14':
        len_choice = 4
    else:
        print 345, key, value
     
        
    new_values = choices = [ 'N' for item in range(len_choice)]
    values = value.split('##')
    for value in values:
        if value not in ('', None):
            i = int(value) - 1 
            new_values[i] = 'O'

    value = ','.join(new_values)
    return value


def get_alertes():
    context = get_context()
    handler = context.handler
    if context.handler.is_BDP():
        from schemaBDP import alertes
    if context.handler.is_BM():
        from schemaBM import alertes 
    return alertes


def get_controles():
    context = get_context()
    handler = context.handler
    if context.handler.is_BDP():
        from schemaBDP import controles 
    if context.handler.is_BM():
        from schemaBM import controles 
    return controles 

def get_cursor():
    try: 
        connection = MySQLdb.connect(db=SqlDatabase, host=SqlHost,
                                     port=int(SqlPort), user=SqlUser,
                                     passwd=SqlPasswd)
    except MySQLdb.OperationalError: 
        raise UserError, u"La connexion à MySql ne s'est pas faite" 
    return connection.cursor()



def get_adresse(query):
    """ Accès base adresse"""
    try: 
        connection = MySQLdb.connect(db=SqlDatabase, host=SqlHost,
                                     port=int(SqlPort), user=SqlUser,
                                     passwd=SqlPasswd)
   #     connection = MySQLdb.connect(db='scrib', host='localhost', 
   #                              user='scrib' ,passwd='Scrib-2005*')
    except MySQLdb.OperationalError:
        raise UserError, u"La connexion à MySql ne s'est pas faite" 
    cursor = connection.cursor()
    cursor.execute(query)
    res = cursor.fetchall()
    
    if len(res):
        res = res[0]
        adresse = []
        for val in res:
            if str(val) == 'None':
                adresse.append('')
            else:
                adresse.append(val)
        cursor.close()
        connection.close()
    else:
        raise UserError, u"La bibliothèque n'existe pas dans la base SQL"
        
    return adresse or ''


class Form(Handler, iText, WorkflowAware):

    class_id = 'Form'
    class_icon48 = 'culture/images/form48.png'
    workflow = workflow


    # XXX deactivate archives
    def add_to_archive(self):
        pass

    def commit_revision(self):
        pass

    history_form__access__ = False
    copy_to_present__access__ = False


    def get_catalog_indexes(self):
        document = Handler.get_catalog_indexes(self)
        document['user_town'] = self.get_user_town()
        document['dep'] = self.get_dep()
        document['year'] = self.get_year()
        document['is_BDP'] = self.is_BDP()
        document['is_BM'] = self.is_BM()
        document['form_state'] = self.get_form_state()

        return document


    def get_ns_and_h(self, xml, autogen_xml, view):
        """
        autogen_xml = 'FormXX_report1_autogen.xml'
        xml = 'FormXX_report1.xml'
        """
        namespace = self.get_namespace()

        try: 
            handler = self.get_handler('/ui/culture/%s' % autogen_xml)
        except LookupError:
            handler = self.get_handler('/ui/culture/%s' % xml)

        if view == 'printable':
            namespace['printable'] = True
            context = get_context()
            context.response.set_header('Content-Type', 
                                        'text/html; charset=UTF-8')
            namespace['body'] = stl(handler, namespace)
            handler = self.get_handler('/ui/culture/printable_template.xhtml')
        elif view == 'print_all':
            namespace['printable'] = True

        namespace['submit_button'] = namespace['is_allowed_to_edit'] \
                                     and not namespace['printable']

        return stl(handler, namespace)


    ######################################################################
    # API
    def set_metadata(self, meta):
        self.set_changed()
        self.state.fields.update(meta)
   

    def is_allowed_to_view(self):
        user = get_context().user
        # Anonymous
        if user is None:
            return False
        # Admin
        if self.is_admin():
            return True
        # VoirSCRIB
        if user.name == 'VoirSCRIB':
            return True
        # Check the year
        if user.get_year() != self.parent.get_year():
            return False
        # Check the department
        if user.is_BM():
            if user.get_BM_code() != self.name:
                return False
        if user.is_BDP():
            if user.get_department() != self.name:
                return False
        return True


    def is_allowed_to_edit(self):
        user = get_context().user
        # Admin
        if self.is_admin():
            return True
        # Anonymous
        if user is None:
            return False
        # Check the year
        if user.get_year() != self.parent.get_year():
            return False
        # Check the department
        if user.is_BM():
            if user.get_BM_code() != self.name:
                return False
        if user.is_BDP():
            if user.get_department() != self.name:
                return False
        # Check the state
        return self.get_state() == 'private'


    #######################################################################
    # Namespaces
    def get_namespace(self):
        context = get_context()
        request = context.request
        schema = self.get_schema()

        namespace = {}
        # Permissions
        namespace['is_allowed_to_edit'] = self.is_allowed_to_edit()
        # Fields
        for name in schema:
            field_def = schema[name]
            type = field_def[0]
            default = field_def[1]
            value = request.get_parameter(name)
            key = name[len('field'):]
            # take the value in request first
            value = request.get_parameter(key)
            if value is None:
                # is the value is not in request, take it in fields 
                value = self.state.fields.get(name, default)
            namespace[name] = value
            # If name is 'fieldA23', add 'A23'
            if name.startswith('field'):
                namespace[key] = value
            # Booleans
            if type is Boolean:
                if namespace[name] is False:
                    namespace['%s_not' % name] = True
                else:
                    namespace['%s_not' % name] = False
            # Checkboxes 
            if type is Checkboxes:
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
            form = request.form
            # we have  _B13 in the namespace but _B13XYZ in the form 
            # so we make form_keys who remove X from _B13X 
            form_keys = form.keys()
            form_keysXYZ = [k for k in form_keys if not k[-1].isdigit()]
            form_keysXYZ = [k[:-1] for k in form_keys]
            form_keys = form_keys + form_keysXYZ
            if missing_name in form_keys:
                namespace[field_name] = 'missing_field' 
            if badT_name in form_keys:
                namespace[field_name] = 'badT_field' 

        # State
        state = self.get_property('state')
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
        namespace['is_finished'] = (state == 'pending' and self.is_admin())

        # Récupération des champs de la base ADRESSE
        dept = self.name
        champs_adr = self.base_lect(dept)
        code_ua = int(champs_adr[17])
        namespace['code_ua'] = code_ua
        # LIBELLE1
        if not namespace['field1']:
            namespace['field1'] = unicode(champs_adr[6], 'ISO-8859-1')
        # LIBELLE2
        if not namespace['field2']:
            namespace['field2'] = unicode(champs_adr[7], 'ISO-8859-1')
        # VOIE
        if not namespace['field3']:
            namespace['field3'] = unicode(champs_adr[9], 'ISO-8859-1')
        # CPBIBLIO
        if not namespace['field4']:
            namespace['field4'] = unicode(champs_adr[11], 'ISO-8859-1')
        # VILLE
        if not namespace['field5']:
            namespace['field5'] = unicode(champs_adr[18], 'ISO-8859-1')
        # CEDEXB
        if not namespace['field6']:
            namespace['field6'] = unicode(champs_adr[12], 'ISO-8859-1')
        # DIRECTEU
        if not namespace['field7']:
            namespace['field7'] = unicode(champs_adr[3], 'ISO-8859-1')
        # STDIR
        if not namespace['field8']:
            namespace['field8'] = unicode(champs_adr[19], 'ISO-8859-1')
        # TELE
        if not namespace['field9']:
            namespace['field9'] = unicode(champs_adr[14], 'ISO-8859-1')
        # FAX
        if not namespace['field10']:
            namespace['field10'] = unicode(champs_adr[13], 'ISO-8859-1')
        # MEL
        if not namespace['field11']:
            namespace['field11'] = unicode(champs_adr[2], 'ISO-8859-1')
        # WWW
        if not namespace['field12']:
            namespace['field12'] = unicode(champs_adr[15], 'ISO-8859-1')
        # INTERCOM
        if namespace.get('field13') is None:
            namespace['field13'] = unicode(champs_adr[21], 'ISO-8859-1')
        # GESTION
        if namespace.get('field14') is None:
            namespace['field14'] = unicode(champs_adr[22], 'ISO-8859-1')
        # GESTION_AUTRE
        if namespace.get('field15') is None:
            namespace['field15'] = unicode(champs_adr[23], 'ISO-8859-1')
 
        # autofill Annexes
        if self.is_BM():
            bm_annexes = self.bm_annexes(code_ua)
            for k, v in bm_annexes.items():
                key = 'field%s' % k
                if not k.startswith('J'):
                    pass
                elif not namespace[key]:
                    value = unicode(str(v), 'ISO-8859-1')
                    namespace[key] = value
       
        # autofill BM epci
        if self.is_BM():
            ua_epci = self.ua_epci(code_ua)
            for k, v in ua_epci.items():
                key = 'field%s' % k
                if not k.startswith('K'):
                    pass
                # Make the select options
                elif k.endswith('Z'):
                    kz = self.state.fields.get(key, '0')
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


    ######################################################################
    # User interface
    def get_views(self):
        return ['report_form0', 'controles_form', 'report_csv', 'print_form', 
                'help']


    def get_form_state(self):
        # State
        state = self.get_property('state')
        if state == 'private':
            if len(self.state.fields) == 0:
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


    #######################################################################
    # Control report
    controles_form__access__ = 'is_allowed_to_view'
    controles_form__label__ = u'Contrôle de la saisie'
    def controles_form(self):
        schema = self.get_schema()
        controles = get_controles()
        alertes = get_alertes()
        namespace = self.get_namespace()
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
            if stype is not String and \
                   stype is not Unicode:
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

        #namiespace['restype'] = restype
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
                # Si plusieurs termes de la somme sont égaux à NC, alors le
                # total doit être strictement supérieur à la somme des termes
                # différents de NC
                if not 'NC' in right_values:
                    pass
                elif right_values.count('NC') > 1:
                    key_type = schema['field%s' % expr1][0]

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

        is_exported = self.get_form_state() in (u'Exporté', u'Modifié après export')
        namespace['is_exportable'] = is_finished or is_exported

        #############################################################
        # Alerts
        resalt = []
        for key, text, expression in alertes:
            d = {'idalt': key,
                 'textalt': text}
            try:
                result = eval(expression, namespace)
                if key != 'G':
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
        namespace['is_admin'] = self.is_admin()

        handler = self.get_handler('/ui/culture/Form_controles.xml')
        return stl(handler, namespace) 


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
                # Empties
                Empties.append(key)
            is_mandatory = (field_type is not Unicode) and \
                            (field_type is not EPCI_Statut)
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
            if field_type is not Unicode:
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
    def pending2submitted(self):
        # Change state
        self.set_property('state', 'pending')
        context = get_context()
        root, user, request = context.root, context.user, context.request
        root.reindex_handler(self)

        # Build email
        namespace = self.get_namespace()
        message_pattern = u'To: %(to_addr)s\n' \
                          u'From: %(from_addr)s\n' \
                          u'Subject: %(subject)s\n' \
                          u'\n' \
                          u'%(body)s\n'

        dep = self.get_dep()
        report_email = namespace['field11']
        if self.is_BDP():
            to_addr = MailResponsableBDP
            subject = u'SCRIB-BDP : %s' % dep
            body = u'La Bibliothèque %s a terminé son formulaire.' % self.name
        else:
            to_addr = unicode(MailResponsableBM, 'UTF-8')
            subject = u'SCRIB-BM : %s (%s)' % (namespace['code_ua'], dep)
            subject = u'SCRIB-BM : %s (%s)' % (namespace['code_ua'], dep)
            body = u'La Bibliothèque %s (%s), du département %s, a terminé' \
                   u' son formulaire.'
            body = body % (self.name, self.get_title(), dep)

        message = message_pattern % {'to_addr': to_addr,
                                     'from_addr': report_email,
                                     'subject': subject,
                                     'body': body}

        succsess_mgs = (u'Terminé, un e-mail est envoyé à votre correspondant ' 
                        u'DLL.')
        comeback_msg = self.send_email(SMTPServer=SMTPServer, 
                                       from_addr=report_email, 
                                       to_addr=to_addr, 
                                       message=message,
                                       succsess_mgs=succsess_mgs)

        self.scrib_log(event='email sent', content=comeback_msg)

        # recipe
        r_subject = u'Accusé de réception, DLL'
        r_body = (u"Votre rapport annuel a bien été reçu par votre "
                  u"correspondant à la DLL. \n\nNous vous remercions "
                  u"de votre envoi.  Cordialement.")
        r_message = message_pattern % {'to_addr': report_email,
                                       'from_addr': to_addr,
                                       'subject': r_subject,
                                       'body': r_body}
        trash = self.send_email(SMTPServer=SMTPServer, 
                                from_addr=to_addr, 
                                to_addr=report_email, 
                                message=r_message,
                                succsess_mgs="")
        
        self.scrib_log(event='recipe sent', content=r_message)

        comeback(comeback_msg, ';controles_form')


    def scrib_log(self, event=None, content=None):
        context = get_context()
        root, user, request = context.root, context.user, context.request
        # Event Log 
        event = '\n' \
                '[Scrib event]\n' \
                'date   : %(date)s\n' \
                'uri    : %(uri)s\n' \
                'referrer: %(referrer)s\n' \
                'user   : %(user)s\n' \
                'event : %(event)s\n' \
                '\n'
        event = event % {'date': str(datetime.datetime.now()),
                         'uri': str(request.uri),
                         'referrer': str(request.referrer),
                         'user': user and user.name or None, 
                         'event': ('email sent '
                                   '\n########\n%s\n#########') % content}
        logging.getLogger().info(event)


    def send_email(self, SMTPServer=None, from_addr=None, 
                   to_addr=None, message=None, 
                   succsess_mgs=None):
        # Send email
        try:
            mail = smtplib.SMTP(SMTPServer)
        except socket.error:
            msg = u'La connexion au serveur de mail a échoué.'
        else:
            try:
                message = message.encode('latin1')
                mail.sendmail(from_addr, to_addr, message)
            except smtplib.SMTPRecipientsRefused:
                msg = u'La connexion au serveur de mail a échoué.'
            except UnicodeEncodeError:
                msg = (u"L'adresse email (%s) comporte des caractères "
                       u"non conformes. "
                       u"Le message n'a pas été envoyé") % from_addr
            else:
                msg = succsess_mgs
            #mail.quit()
        return msg


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

        for name in names:
            field_def = schema[name]
            field_type = field_def[0]
            default = field_def[1]
            value = namespace[name]
            key = name.split('field')[-1]
            chap = key[0]
            
            if not chap.isdigit():
                if value in ('', None, 'NC'):
                    value = "null"
                elif field_type is Unicode:
                    value = "'%s'" % value
                elif field_type is Integer:
                    value = str(value)
                elif field_type == Boolean:
                    if value:
                        value = "'O'"
                    else:
                        value = "'N'"
                elif field_type == Checkboxes:
                    # get the value from checkboxes
                    value = "'%s'" % get_checkbox_value(key, value)
                elif field_type == Decimal:
                    value = "'%s'" % str(value)
                elif field_type == EPCI_Statut:
                    ids = [x['id'] for x in value if x['is_selected']]
                    if ids:
                        value = ids[0]
                    else:
                        value = '0'
                values.append(value)
                
        values = ','.join(values)
        query = "insert into %s values (%s)" % (table, values)

        return query


    submitted2exported__access__ = 'is_admin'
    def submitted2exported(self):
        cursor = get_cursor()
        namespace = self.get_namespace()
        schema = self.get_schema()
        # Update dans la base ADRESSE
        query = (u'update adresse set libelle1="%(field1)s",libelle2="%(field2)s",'
                 u'voie="%(field3)s",cpbiblio="%(field4)s",ville="%(field5)s",'
                 u'cedexb="%(field6)s",directeu="%(field7)s",tele="%(field9)s",'
                 u'fax="%(field10)s",mel="%(field11)s",www="%(field12)s",'
                 u'intercom="%(field13)s",gestion="%(field14)s",'
                 u'gestion_autre="%(field15)s" where code_bib=%(code_ua)s')

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
                
        query = query % namespace
        
        # XXX charset?
        cursor.execute(query)
        cursor.execute('commit')

        # Insert dans la base BDP
        code_ua = namespace['code_ua']
        dept = self.get_dep()
        year = self.parent.name[-4:]

        # Remove from the database
        btype = 'bdp'
        if self.is_BM():
            btype = 'bm'
            
        table = '%s%s' % (btype ,year[-2:])
        
        query = "delete from %s where Code_UA=%s" % (table, code_ua)

        try:
            cursor.execute(query)
        except MySQLdb.OperationalError, message:
            message = u'Un problème est survenu durant la connexion'\
                    u' à la base de donnée %s' % message
            comeback(message, ';controles_form')
            return
        
        cursor.execute('commit')

        # Add into the database
        query = self.get_export_query(namespace)
        cursor.execute(query)
        cursor.execute('commit') 
        self.set_property('state', 'public')

        root = get_context().root
        root.reindex_handler(self)
        self.set_changed()
        
        message = u'Le rapport a été exporté'
        comeback(message, ';controles_form')


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
                if fields:
                    for field in fields:
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
    def fill_report_form(self):
        handler = self.get_handler('/ui/culture/Form_fill_report.xml')
        return handler.to_str()


    fill_report__access__ = 'is_allowed_to_edit'
    def fill_report(self):
        schema = self.get_schema()
        context = get_context()
        self.set_changed()
        
        request = context.request
        form, referer = request.form, request.referrer
        new_referer = deepcopy(referer)

        i = 0
        t0 = time()
        ns = self.get_namespace()
        for key in schema:
           i += 1
           field_type = schema[key][0]
           field_default = schema[key][1]
           is_sum = False
           if len(schema[key]) == 3:
               is_sum = schema[key][2].get('sum', False)
           keyNumber = key[len('field'):]
           if field_type is String:
               if ns[key]:
                   value = ns[key]
           elif field_type is EPCI_Statut:
               value = '4' 
           elif field_type is Unicode:
               if ns[key]:
                   value = ns[key]
               else:
                   # do not fill annexes
                   if not keyNumber.startswith('J'):
                       value = u'coué'
                   else:
                       value = u''
           elif field_type is CultureTypes.Integer:
               if is_sum:
                   value = Integer(len(is_sum) * 5)
                   e_list = ['E74X', 'E46Z', 'E67Z', 'E71Z', 'E74Y', 'E74Z']
                   g_list = ['G25Y', 'G26Y', 'G26Z']
                   if key in ['field' + x for x in e_list + g_list]:
                       value = Integer('NC')
               else:
                   value = Integer(5) 
           elif field_type is Decimal:
               value = decimal.Decimal('3.14')
               if is_sum:
                   value = value * decimal.Decimal(len(is_sum))
                   value = Decimal(value)
               else:
                   value = Decimal(value)
           elif field_type is Checkboxes:
               value = '##1' 
           elif field_type is Boolean:
               value = True 
           else: 
               value = '0' 

           self.state.fields[key] = value
           t = time() - t0

        root = context.root
        root.reindex_handler(self)
        message = u'Rapport auto remplis en %.2f secondes' % t
        comeback(message, ';controles_form')


    report__access__ = 'is_allowed_to_edit'
    def report(self):
        schema, context = self.get_schema(), get_context()
        self.set_changed()
        request = context.request
        form, referer = request.form, request.referrer
        #pprint(form)
        new_referer = deepcopy(referer)

        dependencies = self.get_dependencies()
        sums = self.get_sums()

        notR = [] # list of empty field
        badT = [] # list of field of bad type
        badT_missing = [] # list of field to highlight (badT_missing)
        badT_values = {} # a dict of field : value to put into namespace
        
        for key, value in form.items():
            if key in schema:
                #########################################
                # Take the value from the form 
                field_type = schema[key][0]
                field_default = schema[key][1]
                keyNumber = key[len('field'):]
                if isinstance(value, list):
                    if len(value) == 1:
                        value = '1'
                    else:
                        # Support checkboxes
                        value = '##'.join(value)
                # Pre-process value
                value = value.strip()

                #########################################
                # Dependance machinery XXX need to be clean up and commented
                # We need to finish comments and put it in a method
                # dependancies = {'A13': 'A11', 'A12': 'A11'}
                # dependancies.keys() == ['A13', 'A12']
                dependance = dependencies.get(key) # None if no dep

                #########################################
                # Field as the sum of other fields
                sum = key in sums

                ## Objectif : we set empty = True or False
                ## Set value to '' if dep field is False    
                # True : no dep AND no value AND no String/Unicode AND 
                # False :  
                empty = False
                if field_type is not String and \
                       field_type is not Unicode:
                    if dependance is not None :
                        # here we know if they are a dependancies
                        # and 
                        if form.get(dependance, '0') == '1':
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
                except (ValueError, UnicodeEncodeError,
                        decimal.InvalidOperation):
                    badT_missing.append('badT_%s' % keyNumber)
                    badT.append(u'%s: <b>%s</b>'
                                % (keyNumber, unicode(value, 'UTF-8')))
                    # we need the field and it's value in the
                    #query even if the type is wrong
                    badT_values[keyNumber] = value
                else:
                    self.state.fields[key] = value

        form_state = self.get_form_state()
        if form_state == u'Exporté':
            self.set_property('state', 'modified')

        new_referer, msg = self.make_msg(new_referer=new_referer, notR=notR, 
                                         badT=badT, badT_missing=badT_missing,
                                         badT_values=badT_values)
        comeback(msg, new_referer)


    def make_msg(self, new_referer, notR, badT, badT_missing, badT_values):
        if notR:
            notR.sort()
            notR_missing = ['missing_' + x for x in notR]
            # convert to unicode so we can join them
            notR = [unicode(x, 'UTF-8') for x in notR]

            msg_notR = (u"Les rubriques suivantes ne sont pas "
                        u"renseignées : %s") % u', '.join(notR)

            dic = {}.fromkeys(notR_missing, '1')
            new_referer.query.clear()
            new_referer.query.update(dic)
        if badT:
            badT.sort()
            # convert to unicode so we can join them
            msg_badT = (u"Le type des rubriques suivantes n'est pas"
                        u" correct : %s" ) % u', '.join(badT)

            dic = {}.fromkeys(badT_missing, '1')
            new_referer.query.update(badT_values)
            new_referer.query.update(dic)
                    
        if not (badT or notR):
            msg = u"Formulaire enregistré."
        elif badT and not notR:
            msg = msg_badT 
        elif notR and not badT:
            msg = msg_notR
        else:
            msg = u'<br/>'.join([msg_notR,  msg_badT])

        return new_referer, msg


    #######################################################################
    # Workflow
    def is_allowed_to_trans(self, name):
        context = get_context()
        root, user = context.root, context.user

        if user is None:
            return False

        namespace = self.get_namespace()
        is_admin = user.name in root.get_handler('admins').get_usernames()

        if is_admin:
            if name in ['request', 'accept', 'publish']:
                return namespace['is_ready']
            else:
                return True
        else:
            if name in ['request']:
                return namespace['is_ready']
            elif name in ['unrequest']:
                return True
            else:
                return False


    #######################################################################
    # Help
    help__access__ = True
    help__label__ = u'Aide'
    def help(self):
        handler = self.get_handler('/ui/culture/Form_help.xml')
        return handler.to_str()


    help2__access__ = True 
    def help2(self):
        context = get_context()
        context.response.set_header('Content-Type', 'text/html; charset=UTF-8')
        handler = self.get_handler('/ui/culture/Form_help2.xhtml')
        return handler.to_str()


    #######################################################################
    # Export
    #report_csv__access__ = Handler.is_admin
    report_csv__access__ = True
    report_csv__label__ = u'Export'
    def report_csv(self):
        """ Call downloadCSV """
        namespace = self.get_namespace()
        is_finished = namespace['is_finished']
        is_complete = namespace['is_complete']
        is_exported = self.get_form_state() == u'Exporté'
        namespace['show'] = is_finished or is_complete or is_exported
        handler = self.get_handler('/ui/culture/Form_report_csv.xml')
        return stl(handler, namespace) 


    comments__access__ = 'is_allowed_to_view'
    comments__label__ = u'Rapport Bibliothèques'
    comments__sublabel__ = u'Commentaires'
    def comments(self, view=None, **kw):
        return self.get_ns_and_h('Form_comments.xml', 
                                 'FormBM_report0_autogen.xml',
                                 view)


    #downloadCSV__access__ = Handler.is_admin
    downloadCSV__access__ = True
    def downloadCSV(self):
        schema = self.get_schema()
        context = get_context()
        response = context.response

        response.set_header('Content-Type', 'text/comma-separated-values')
        response.set_header('Content-Disposition',
                'attachment; filename="scrib.csv"')

        namespace = self.get_namespace()
        # construct the csv
        names = schema.keys()
        names.sort()
        csv = CSV()
        csv.add_row([u"Chapitre du formulaire", u"rubrique", u"valeur"])
        for name in names:
            value = namespace.get(name, '')
            if schema[name][0] is EPCI_Statut:
                label = [x['label'] for x in value if x['is_selected']]
                if label:
                    value = label[0]
                else: 
                    value = ''
            name = name[len('field'):]
            chap = name[0]
            if value is None:
                value = u"NULL"
            elif isinstance(value, bool):
                value = unicode(int(value))
            elif isinstance(value, (int, long, float, decimal.Decimal)):
                value = unicode(str(value))
            elif isinstance(value, str):
                value = unicode(str(value), 'UTF-8')
            elif isinstance(value, unicode):
                value = value.replace(u"€", u"eur")
            else:
                # CultureTypes
                value = unicode(value.__class__.encode(value), 'UTF-8')
            csv.add_row([chap, name, value])

        return csv.to_str('latin1')


#XXX do we need to register FormBM and Form ?
iText.register_handler_class(Form)
