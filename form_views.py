# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Sylvain Taverne <sylvain@itaapy.com>
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

# Import from standard library
from copy import deepcopy
from decimal import Decimal as dec, InvalidOperation
from pprint import pformat
from time import time

# Import from mysql
from _mysql import OperationalError

# Import from itools
from itools.csv import CSVFile
from itools.datatypes import is_datatype, Boolean, String, Unicode
from itools.gettext import MSG
from itools.http.exceptions import Forbidden
from itools.web import BaseView, STLView, STLForm

# Import from scrib
from scrib import config
from datatypes import Checkboxes, Integer, EPCI_Statut, Decimal
from utils import get_connection, make_msg, MSG_NO_MYSQL
from utils_views import HelpView

MailResponsableBM = config.get_value('MailResponsableBM')
MailResponsableBDP = config.get_value('MailResponsableBDP')


class Form_View(STLForm):

    access = 'is_allowed_to_edit'

    def get_template(self, resource, context):
        """
        autogen_xml = 'FormXX_report1_autogen.xml'
        xml = 'FormXX_report1.xml'
        """
        template = resource.get_resource('/ui/scrib/%s' % self.autogen_xml, soft=True)
        if template is None:
            template = resource.get_resource('/ui/scrib/%s' % self.xml)
        return template


    def get_namespace(self, resource, context):
        namespace = resource.get_namespace(context)
        view = getattr(self, 'view', None)
        if context.get_form_value('view', default=view) in ['print_all', 'printable']:
            namespace['printable'] = True
        return namespace


    def action_report(self, resource, context, form):
        schema = resource.get_scrib_schema()
        fields = {}

        referer = context.request.referrer
        new_referer = deepcopy(referer)

        dependencies = resource.get_dependencies()
        sums = resource.get_sums()

        notR = [] # list of empty field
        badT = [] # list of field of bad type
        badT_missing = [] # list of field to highlight (badT_missing)
        badT_values = {} # a dict of field : value to put into namespace

        old_form_state = resource.get_form_state()

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
                        true = context.get_form_value(dependance, default='0') != '0'
                    else:
                        true = context.get_form_value(dependance, default='0') == '1'
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
            resource.update_fields(fields)

        if old_form_state == u'Exporté':
            resource.set_workflow_state('modified')
        else:
            new_form_state = resource.get_form_state()
            # 0005453: Reindex
            if new_form_state != old_form_state:
                context.server.change_resource(resource)

        new_referer, msg = make_msg(new_referer=new_referer, notR=notR,
                badT=badT, badT_missing=badT_missing, badT_values=badT_values)
        return context.come_back(MSG(msg), goto=new_referer)



class Form_Controles(STLForm):

    access = 'is_allowed_to_view'
    title = MSG(u'Contrôlez votre saisie')
    template = '/ui/scrib/Form_controles.xml'

    def get_namespace(self, resource, context):
        schema = resource.get_scrib_schema()
        controles = resource.get_controles()
        alertes = resource.get_alertes()
        namespace = resource.get_namespace(context)
        dependencies = resource.get_dependencies()
        # State
        state = resource.get_form_state()

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
        for res in resource.split_in4(restype):
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

        is_exported = resource.get_form_state() in (u'Exporté',
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
        ac = resource.get_access_control()
        namespace['is_admin'] = ac.is_admin(context.user, resource)
        return namespace



    def action_pending2submitted(self, resource, context, form):
        ac = resource.get_access_control()
        if not ac.is_allowed_to_edit(context.user, resource):
            raise Forbidden
        root = context.root
        user = context.user

        # Change state
        resource.set_property('state', 'pending')

        # Build email
        namespace = resource.get_namespace(context)
        message_pattern = u'To: %(to_addr)s\n' \
                          u'From: %(from_addr)s\n' \
                          u'Subject: %(subject)s\n' \
                          u'\n' \
                          u'%(body)s\n'
        dep = resource.get_dep()
        report_email = namespace['field11']
        if resource.is_BDP():
            to_addr = unicode(MailResponsableBDP, 'utf_8')
            subject = u'SCRIB-BDP : %s' % dep
            body = u'La Bibliothèque %s a terminé son formulaire.' % resource.name
        else:
            to_addr = unicode(MailResponsableBM, 'utf_8')
            subject = u'SCRIB-BM : %s (%s)' % (namespace['code_ua'], dep)
            body = u'La Bibliothèque %s (%s), du département %s, a terminé' \
                   u' son formulaire.'
            body = body % (resource.name, resource.get_title(), dep)
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
        resource.scrib_log(context, event='email sent', content=message)

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
        resource.scrib_log(context, event='recipe sent', content=r_message)

        return context.come_back(MSG(comeback_msg), goto=';controles_form')



    def action_submitted2exported(self, resource, context, form):
        from form import quote_namespace
        ac = resource.get_access_control()
        if not ac.is_admin(context.user, resource):
            raise Forbidden
        try:
            connection = get_connection()
            cursor = connection.cursor()
            namespace = resource.get_namespace(context)
            schema = resource.get_scrib_schema()
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
            dept = resource.get_dep()
            year = resource.parent.name[-4:]
            btype = 'bdp'
            if resource.is_BM():
                btype = 'bm'
            table = '%s%s' % (btype ,year[-2:])
            query = "delete from %s where Code_UA=%s" % (table, code_ua)
            cursor.execute(query)
            cursor.execute('commit')

            # Add into the database
            query = resource.get_export_query(namespace)
            cursor.execute(query)
            cursor.execute('commit')
            resource.set_property('state', 'public')

            cursor.close()
            connection.close()
        except OperationalError:
            context.server.log_error(context)
            context.commit = False
            return context.come_back(MSG(MSG_NO_MYSQL))

        message = MSG(u'Le rapport a été exporté')
        return context.come_back(message, goto=';controles_form')


class Form_FillReportForm(STLView):

    access = 'is_allowed_to_edit'
    title = MSG(u'Auto remplissage')
    template = '/ui/scrib/Form_fill_report.xml'

    def action(self, resource, context, form):
        schema = resource.get_scrib_schema()
        fields = {}

        t0 = time()
        ns = resource.get_namespace(context)
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

        resource.update_fields(fields)
        t = time() - t0

        message = MSG(u'Rapport auto rempli en %.2f secondes' % t)
        return context.come_back(message, goto=';controles_form')




class Form_Help(HelpView):

    access = True
    title = u'Aidez-vous !'
    template = '/ui/scrib/Form_help.xml'


class Form_Help2(HelpView):

    access = True
    title = u'Aidez-vous !'
    template = '/ui/scrib/Form_help2.xhtml'



class Form_ReportCSV(STLView):

    # XXX Est ce normal ?
    #access = Text.is_admin
    access = True
    title = MSG(u'Exportez chez vous votre rapport')
    template = '/ui/scrib/Form_report_csv.xml'

    def get_namespace(self, resource, context):
        """ Call downloadCSV """
        namespace = resource.get_namespace(context)
        #is_finished = namespace['is_finished']
        state = resource.get_workflow_state()
        is_finished = (state == 'pending')
        is_complete = namespace['is_complete']
        is_exported = resource.get_form_state() == u'Exporté'
        namespace['show'] = is_finished or is_complete or is_exported
        return namespace



class Form_DownloadCSV(BaseView):

    # XXX Est ce normal ?
    #access = 'is_admin'
    access = True

    def GET(self, resource, context):
        schema = resource.get_scrib_schema()
        response = context.response

        response.set_header('Content-Type', 'text/comma-separated-values')
        response.set_header('Content-Disposition',
                'attachment; filename="scrib.csv"')

        namespace = resource.get_namespace(context)
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
