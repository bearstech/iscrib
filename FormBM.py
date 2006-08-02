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

# Import from mysql
import MySQLdb
from MySQLdb.cursors import DictCursor

# Import from Culture
from scrib import config
from schemaBM import schema
from utils import get_BMs
from Form import get_adresse, Form

# Import from itools
from itools.web import get_context
from itools.stl import stl

# Import from itools.cms
from itools.cms.text import Text as iText
from itools.cms.exceptions import UserError

SqlHost = config.SqlHost
SqlDatabase = config.SqlDatabase
SqlUser = config.SqlUser
SqlPasswd = config.SqlPasswd


class FormBM(Form):
    class_id = 'Form_BM'
    class_icon48 = 'culture/images/form48.png'

    def get_catalog_indexes(self):
        document = Form.get_catalog_indexes(self)
        document['code'] = self.get_code()

        return document


    ######################################################################
    # Parsing
    def _load_state(self, resource):
        data = resource.read()
        self.state.fields = {}
        for line in data.splitlines():
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                if key in schema:
                    value = value.strip()
                    field_def = schema[key]
                    type = field_def[0]
                    default = field_def[1]
                    self.state.fields[key] = type.decode(value)


    def to_str(self, encoding='UTF-8'):
        result = []
        for key, value in self.state.fields.items():
            new_value = schema[key][0].encode(value)
            if isinstance(new_value, unicode):
                 new_value = new_value.encode('UTF-8')
            line = '%s:%s\n' % (key, new_value) 
            result.append(line)
        return ''.join(result)


    def get_subviews(self, name):
        reports = ['report_form0', 'report_form10', 'report_form11',
        'report_form1', 'report_form2', 'report_form3', 'report_form4',
        'report_form5', 'report_form6', 'report_form7', 'report_form8',
        'report_form9', 'comments']

        if name in reports:
            return reports
        return iText.get_subviews(self, name)


    def is_BDP(self):
        return False


    def is_BM(self):
        return True


    def get_year(self):
        forms = self.parent
        return forms.name.split('BM')[-1]


    def get_user_town(self):
        return get_BMs()[self.name].get('name', '')


    get_dep__access__ = True
    def get_dep(self):
        # get department number for BMs
        return get_BMs()[self.name].get('dep', '')


    def get_code(self):
        return self.name 


    def base_lect(self, insee):
        chaineSQL = "select * from adresse where "\
                    "insee is not null and code_bib='%s'" % insee
        return get_adresse(chaineSQL)


    def none2str(self, t):
        new = {} 
        for k, v in t.items():
            if v is None:
                new[k] = ''
            else:
                new[k] = v 
        return new 

    def bm_annexes(self, code_ua):
        try: 
            connection = MySQLdb.connect(db=SqlDatabase, host=SqlHost, 
                                         user=SqlUser, passwd=SqlPasswd,
                                         cursorclass=DictCursor)
        except MySQLdb.OperationalError:
            raise UserError, u"La connexion à MySql ne s'est pas faite" 

        cursor = connection.cursor()
        cursor.execute("select * from annexes04  where code_ua = %s", 
                       (code_ua,))
        res = cursor.fetchall()
        res = [self.none2str(d) for d in res]
        if not res: 
            return {}
        else:
            return res[0]


    def ua_epci(self, code_ua):
        try: 
            connection = MySQLdb.connect(db=SqlDatabase, host=SqlHost, 
                                         user=SqlUser, passwd=SqlPasswd,
                                         cursorclass=DictCursor)
        except MySQLdb.OperationalError:
            raise UserError, u"La connexion à MySql ne s'est pas faite" 

        cursor = connection.cursor()
        cursor.execute("select * from ua_epci where code_ua = %s", 
                       (code_ua,))
        res = cursor.fetchall()
        res = [self.none2str(d) for d in res]
        if not res: 
            return {}
        else:
            return res[0]


    #######################################################################
    # Edit report
    print_form__access__ = 'is_allowed_to_view'
    print_form__label__ = u'Impression du rapport '
    def print_form(self):
        context = get_context()
        context.response.set_header('Content-Type', 
                                    'text/html; charset=UTF-8')
        namespace = self.get_namespace()
        forms = ['FormBM_report%s' % i for i in range(0, 12)]
        forms = [('%s.xml' % i, '%s_autogen.xml' % i, 'print_all') 
                 for i in forms]
        # report_form10 and report_form11 must be in position 2 and 3
        forms.insert(1, forms[-2])
        forms.insert(2, forms[-1])
        forms = forms[:-2]
        forms = [self.get_ns_and_h(n, a, v) for n, a, v in forms]
        forms = reduce(lambda x,y: x+y, forms)
        namespace['body'] = forms 

        handler = self.get_handler('/ui/culture/printable_template.xhtml')
        return stl(handler, namespace)



    report_form0__access__ = 'is_allowed_to_view'
    report_form0__label__ = u'Rapport Bibliothèques'
    report_form0__sublabel__ = u'Identité'
    def report_form0(self, view=None, **kw):
        return self.get_ns_and_h('FormBM_report0.xml', 
                                 'FormBM_report0_autogen.xml',
                                 view)


    report_form1__access__ = 'is_allowed_to_view'
    report_form1__label__ = u'Rapport BM'
    report_form1__sublabel__ = u'A-Finances'
    def report_form1(self, view=None, **kw):
        return self.get_ns_and_h('FormBM_report1.xml', 
                                 'FormBM_report1_autogen.xml',
                                 view)

    report_form2__access__ = 'is_allowed_to_view'
    report_form2__label__ = u'Rapport BM'
    report_form2__sublabel__ = u'B-Locaux'
    def report_form2(self, view=None, **kw):
        return self.get_ns_and_h('FormBM_report2.xml', 
                                 'FormBM_report2_autogen.xml',
                                 view)


    report_form3__access__ = 'is_allowed_to_view'
    report_form3__label__ = u'Rapport BM'
    report_form3__sublabel__ = u'C-Personnel'
    def report_form3(self, view=None, **kw):
        return self.get_ns_and_h('FormBM_report3.xml', 
                                 'FormBM_report3_autogen.xml',
                                 view)


    report_form4__access__ = 'is_allowed_to_view'
    report_form4__label__ = u'Rapport BM'
    report_form4__sublabel__ = u'D-Collections'
    def report_form4(self, view=None, **kw):
        return self.get_ns_and_h('FormBM_report4.xml', 
                                 'FormBM_report4_autogen.xml',
                                 view)


    report_form5__access__ = 'is_allowed_to_view'
    report_form5__label__ = u'Rapport BM'
    report_form5__sublabel__ = u'E-Acquisitions'
    def report_form5(self, view=None, **kw):
        return self.get_ns_and_h('FormBM_report5.xml', 
                                 'FormBM_report5_autogen.xml',
                                 view)


    report_form6__access__ = 'is_allowed_to_view'
    report_form6__label__ = u'Rapport BM'
    report_form6__sublabel__ = u'F-Coopération et réseau'
    def report_form6(self, view=None, **kw):
        return self.get_ns_and_h('FormBM_report6.xml', 
                                 'FormBM_report6_autogen.xml',
                                 view)


    report_form7__access__ = 'is_allowed_to_view'
    report_form7__label__ = u'Rapport BM'
    report_form7__sublabel__ = u'G-Activités'
    def report_form7(self, view=None, **kw):
        return self.get_ns_and_h('FormBM_report7.xml', 
                                 'FormBM_report7_autogen.xml',
                                 view)


    report_form8__access__ = 'is_allowed_to_view'
    report_form8__label__ = u'Rapport BM'
    report_form8__sublabel__ = u'H-Services'
    def report_form8(self, view=None, **kw):
        return self.get_ns_and_h('FormBM_report8.xml', 
                                 'FormBM_report8_autogen.xml',
                                 view)


    report_form9__access__ = 'is_allowed_to_view'
    report_form9__label__ = u'Rapport BM'
    report_form9__sublabel__ = u'I-Animations, publications et formation'
    def report_form9(self, view=None, **kw):
        return self.get_ns_and_h('FormBM_report9.xml', 
                                 'FormBM_report9_autogen.xml',
                                 view)


    report_form10__access__ = 'is_allowed_to_view'
    report_form10__label__ = u'Rapport BM'
    report_form10__sublabel__ = (u'Annexes').capitalize()
    def report_form10(self, view=None, **kw):
        return self.get_ns_and_h('FormBM_report10.xml', 
                                 'FormBM_report10_autogen.xml',
                                 view)


    report_form11__access__ = 'is_allowed_to_view'
    report_form11__label__ = u'Rapport BM'
    report_form11__sublabel__ = (u'EPCI')
    def report_form11(self, view=None, **kw):
        code_ua = self.get_code()
        return self.get_ns_and_h('FormBM_report11.xml', 
                                 'FormBM_report11_autogen.xml',
                                 view)


    #######################################################################
    # Help
    
    help0__access__ = True 
    def help0(self):
        context = get_context()
        context.response.set_header('Content-Type', 'text/html; charset=UTF-8')
        handler = self.get_handler('/ui/culture/FormBM_help0.xml')
        return handler.to_str()
    
    help1__access__ = True 
    def help1(self):
        context = get_context()
        context.response.set_header('Content-Type', 'text/html; charset=UTF-8')
        handler = self.get_handler('/ui/culture/FormBM_help1.xml')
        return handler.to_str()


    help2__access__ = True 
    def help2(self):
        context = get_context()
        context.response.set_header('Content-Type', 'text/html; charset=UTF-8')
        handler = self.get_handler('/ui/culture/FormBM_help2.xml')
        return handler.to_str()


    help3__access__ = True 
    def help3(self):
        context = get_context()
        context.response.set_header('Content-Type', 'text/html; charset=UTF-8')
        handler = self.get_handler('/ui/culture/FormBM_help3.xml')
        return handler.to_str()


    help4__access__ = True 
    def help4(self):
        context = get_context()
        context.response.set_header('Content-Type', 'text/html; charset=UTF-8')
        handler = self.get_handler('/ui/culture/FormBM_help4.xml')
        return handler.to_str()


    help5__access__ = True 
    def help5(self):
        context = get_context()
        context.response.set_header('Content-Type', 'text/html; charset=UTF-8')
        handler = self.get_handler('/ui/culture/FormBM_help5.xml')
        return handler.to_str()


    help6__access__ = True 
    def help6(self):
        context = get_context()
        context.response.set_header('Content-Type', 'text/html; charset=UTF-8')
        handler = self.get_handler('/ui/culture/FormBM_help6.xml')
        return handler.to_str()


    help7__access__ = True 
    def help7(self):
        context = get_context()
        context.response.set_header('Content-Type', 'text/html; charset=UTF-8')
        handler = self.get_handler('/ui/culture/FormBM_help7.xml')
        return handler.to_str()


    help8__access__ = True 
    def help8(self):
        context = get_context()
        context.response.set_header('Content-Type', 'text/html; charset=UTF-8')
        handler = self.get_handler('/ui/culture/FormBM_help8.xml')
        return handler.to_str()


    help9__access__ = True 
    def help9(self):
        context = get_context()
        context.response.set_header('Content-Type', 'text/html; charset=UTF-8')
        handler = self.get_handler('/ui/culture/FormBM_help9.xml')
        return handler.to_str()

    help11__access__ = True 
    def help11(self):
        context = get_context()
        context.response.set_header('Content-Type', 'text/html; charset=UTF-8')
        handler = self.get_handler('/ui/culture/FormBM_help11.xml')
        return handler.to_str()


Form.register_handler_class(FormBM)
