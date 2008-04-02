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

# Import from itools
from itools.web import get_context
from itools.stl import stl

# Import from itools.cms
from itools.cms.text import Text as iText

# Import from Culture
from schemaBDP import schema
from Form import get_adresse, Form
from utils import get_deps



class FormBDP(Form):
    class_id = 'FormBDP'
    class_icon48 = 'culture/images/form48.png'

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
        reports = ['report_form0', 'report_form1', 'report_form2', 
                   'report_form3', 'report_form4', 'report_form5',
                   'report_form6', 'report_form7', 'report_form8',
                   'report_form9', 'comments']
        
        if name in reports:
            return reports
        return iText.get_subviews(self, name)


    def get_schema(self):
        from schemaBDP import schema

        return schema


    def is_BDP(self):
        return True


    def is_BM(self):
        return False 


    def get_year(self):
        return self.parent.name.split('BDP')[-1]


    def get_dep(self):
        return self.name


    def get_user_town(self):
        return get_deps()[self.name].get('name', '')


    def base_lect(self, dept):
        chaineSQL = "select * from adresse where type_adr='3' and  " \
                    "code_ua is not null and dept='%s'" % dept
        return get_adresse(chaineSQL)


    #######################################################################
    # Edit report
    print_form__access__ = 'is_allowed_to_view'
    print_form__label__ = u'Impression du formulaire '
    def print_form(self):
        context = get_context()
        context.response.set_header('Content-Type', 
                                    'text/html; charset=UTF-8')
        namespace = self.get_namespace()
        forms = ['FormBDP_report%s' % i for i in range(0, 10)]
        forms = [('%s.xml' % i, '%s_autogen.xml' % i, 'print_all') 
                 for i in forms]
        forms = [self.get_ns_and_h(n, a, v) for n, a, v in forms]
        forms = reduce(lambda x,y: x+y, forms)
        namespace['body'] = forms 

        handler = self.get_handler('/ui/culture/printable_template.xhtml')
        return stl(handler, namespace)


    report_form0__access__ = 'is_allowed_to_view'
    report_form0__label__ = u'Rapport Bibliothèques'
    report_form0__sublabel__ = u'Identité'
    def report_form0(self, view=None, **kw):
        return self.get_ns_and_h('FormBDP_report0.xml', 
                                 'FormBDP_report0_autogen.xml',
                                 view)


    report_form1__access__ = 'is_allowed_to_view'
    report_form1__label__ = u'Rapport BDP'
    report_form1__sublabel__ = u'A-Finances'
    def report_form1(self, view=None, **kw):
        return self.get_ns_and_h('FormBDP_report1.xml', 
                                 'FormBDP_report1_autogen.xml',
                                 view)


    report_form2__access__ = 'is_allowed_to_view'
    report_form2__label__ = u'Rapport BDP'
    report_form2__sublabel__ = u'B-Locaux'
    def report_form2(self, view=None, **kw):
        return self.get_ns_and_h('FormBDP_report2.xml', 
                                 'FormBDP_report2_autogen.xml',
                                 view)


    report_form3__access__ = 'is_allowed_to_view'
    report_form3__label__ = u'Rapport BDP'
    report_form3__sublabel__ = u'C-Personnel'
    def report_form3(self, view=None, **kw):
        return self.get_ns_and_h('FormBDP_report3.xml', 
                                 'FormBDP_report3_autogen.xml',
                                 view)


    report_form4__access__ = 'is_allowed_to_view'
    report_form4__label__ = u'Rapport BDP'
    report_form4__sublabel__ = u'D-Collections'
    def report_form4(self, view=None, **kw):
        return self.get_ns_and_h('FormBDP_report4.xml', 
                                 'FormBDP_report4_autogen.xml',
                                 view)


    report_form5__access__ = 'is_allowed_to_view'
    report_form5__label__ = u'Rapport BDP'
    report_form5__sublabel__ = u'E-Acquisitions'
    def report_form5(self, view=None, **kw):
        return self.get_ns_and_h('FormBDP_report5.xml', 
                                 'FormBDP_report5_autogen.xml',
                                 view)


    report_form6__access__ = 'is_allowed_to_view'
    report_form6__label__ = u'Rapport BDP'
    report_form6__sublabel__ = u'F-Réseau tous public'
    def report_form6(self, view=None, **kw):
        return self.get_ns_and_h('FormBDP_report6.xml', 
                                 'FormBDP_report6_autogen.xml',
                                 view)


    report_form7__access__ = 'is_allowed_to_view'
    report_form7__label__ = u'Rapport BDP'
    report_form7__sublabel__ = u'G-Réseau spécifique'
    def report_form7(self, view=None, **kw):
        return self.get_ns_and_h('FormBDP_report7.xml', 
                                 'FormBDP_report7_autogen.xml',
                                 view)


    report_form8__access__ = 'is_allowed_to_view'
    report_form8__label__ = u'Rapport BDP'
    report_form8__sublabel__ = u'H-Services'
    def report_form8(self, view=None, **kw):
        return self.get_ns_and_h('FormBDP_report8.xml', 
                                 'FormBDP_report8_autogen.xml',
                                 view)


    report_form9__access__ = 'is_allowed_to_view'
    report_form9__label__ = u'Rapport BDP'
    report_form9__sublabel__ = u'I-Action Culturelle'
    def report_form9(self, view=None, **kw):
        return self.get_ns_and_h('FormBDP_report9.xml', 
                                 'FormBDP_report9_autogen.xml',
                                 view)


    #######################################################################
    # Help
    help_menu__access__ = True 
    def help_menu(self):
        context = get_context()
        context.response.set_header('Content-Type', 'text/html; charset=UTF-8')
        handler = self.get_handler('/ui/culture/FormBDP_help_menu.xml')
        return handler.to_str()


    help1__access__ = True 
    def help1(self):
        context = get_context()
        context.response.set_header('Content-Type', 'text/html; charset=UTF-8')
        handler = self.get_handler('/ui/culture/FormBDP_help1.xml')
        return handler.to_str()


    help2__access__ = True 
    def help2(self):
        context = get_context()
        context.response.set_header('Content-Type', 'text/html; charset=UTF-8')
        handler = self.get_handler('/ui/culture/FormBDP_help2.xml')
        return handler.to_str()


    help3__access__ = True 
    def help3(self):
        context = get_context()
        context.response.set_header('Content-Type', 'text/html; charset=UTF-8')
        handler = self.get_handler('/ui/culture/FormBDP_help3.xml')
        return handler.to_str()


    help4__access__ = True 
    def help4(self):
        context = get_context()
        context.response.set_header('Content-Type', 'text/html; charset=UTF-8')
        handler = self.get_handler('/ui/culture/FormBDP_help4.xml')
        return handler.to_str()


    help5__access__ = True 
    def help5(self):
        context = get_context()
        context.response.set_header('Content-Type', 'text/html; charset=UTF-8')
        handler = self.get_handler('/ui/culture/FormBDP_help5.xml')
        return handler.to_str()


    help6__access__ = True 
    def help6(self):
        context = get_context()
        context.response.set_header('Content-Type', 'text/html; charset=UTF-8')
        handler = self.get_handler('/ui/culture/FormBDP_help6.xml')
        return handler.to_str()


    help7__access__ = True 
    def help7(self):
        context = get_context()
        context.response.set_header('Content-Type', 'text/html; charset=UTF-8')
        handler = self.get_handler('/ui/culture/FormBDP_help7.xml')
        return handler.to_str()


    help8__access__ = True 
    def help8(self):
        context = get_context()
        context.response.set_header('Content-Type', 'text/html; charset=UTF-8')
        handler = self.get_handler('/ui/culture/FormBDP_help8.xml')
        return handler.to_str()


    help9__access__ = True 
    def help9(self):
        context = get_context()
        context.response.set_header('Content-Type', 'text/html; charset=UTF-8')
        handler = self.get_handler('/ui/culture/FormBDP_help9.xml')
        return handler.to_str()


Form.register_handler_class(FormBDP)
