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

# Import from itools
from itools.catalog import KeywordField
from itools.stl import stl

# Import from ikaaro
from ikaaro.registry import register_object_class

# Import from scrib
from schema_bm import schema, alertes, controles
from form import FormHandler, Form
from utils import get_bm, get_adresse


class FormBMHandler(FormHandler):
    def _load_state_from_file(self, file):
        return FormHandler._load_state_from_file(self, file, schema)


    def to_str(self, encoding='UTF-8'):
        return FormHandler.to_str(self, schema, encoding)



class FormBM(Form):
    class_id = 'Form_BM'
    class_handler = FormBMHandler
    class_views = [['report_form0'], ['report_form10'], ['report_form11'],
                   ['report_form1'], ['report_form2'], ['report_form3'],
                   ['report_form4'], ['report_form5'], ['report_form6'],
                   ['report_form7'], ['report_form8'], ['report_form9'],
                   ['comments']] + Form.class_views


    ######################################################################
    # Form API
    @staticmethod
    def get_schema():
        return schema


    @staticmethod
    def get_alertes():
        return alertes


    @staticmethod
    def get_controles():
        return controles


    @staticmethod
    def is_BDP():
        return False


    @staticmethod
    def is_BM():
        return True


    @staticmethod
    def base_lect(insee):
        chaineSQL = ("select * from adresse where "
                     "insee is not null and code_bib='%s'" % insee)
        return get_adresse(chaineSQL)


    def get_year(self):
        return self.parent.name.split('BM')[-1]


    def get_dep(self):
        # get department number for BMs
        dep = ''
        bib = get_bm(self.name)
        if bib:
            dep = bib.get_value('dep')
        return dep


    def get_user_town(self):
        title = ''
        bib = get_bm(self.name)
        if bib:
            title = bib.get_value('name')
        return title


    def get_code(self):
        return self.name


    ######################################################################
    # Catalog API
    def get_catalog_fields(self):
        fields = Form.get_catalog_fields(self)
        fields += [KeywordField('code')]
        return fields

    
    def get_catalog_values(self):
        values = Form.get_catalog_values(self)
        values['code'] = self.get_code()
        return values


    #######################################################################
    # Edit report
    print_form__access__ = 'is_allowed_to_view_form'
    print_form__label__ = u'Impression du rapport '
    def print_form(self, context):
        context.response.set_header('Content-Type',
                                    'text/html; charset=UTF-8')
        namespace = self.get_namespace(context)
        forms = ['FormBM_report%s' % i for i in range(0, 12)]
        forms = [('%s.xml' % i, '%s_autogen.xml' % i, 'print_all')
                 for i in forms]
        # report_form10 and report_form11 must be in position 2 and 3
        forms.insert(1, forms[-2])
        forms.insert(2, forms[-1])
        forms = forms[:-2]
        forms = [self.get_ns_and_h(context, n, a, v) for n, a, v in forms]
        forms = reduce(lambda x,y: x+y, forms)
        namespace['body'] = forms

        template = self.get_object('/ui/scrib/printable_template.xhtml')
        return stl(template, namespace)



    report_form0__access__ = 'is_allowed_to_view_form'
    report_form0__label__ = u'Identité'
    def report_form0(self, context, view=None):
        return self.get_ns_and_h(context,
                                 'FormBM_report0.xml',
                                 'FormBM_report0_autogen.xml',
                                 view)


    report_form1__access__ = 'is_allowed_to_view_form'
    report_form1__label__ = u'A-Finances'
    def report_form1(self, context, view=None):
        return self.get_ns_and_h(context,
                                 'FormBM_report1.xml',
                                 'FormBM_report1_autogen.xml',
                                 view)

    report_form2__access__ = 'is_allowed_to_view_form'
    report_form2__label__ = u'B-Locaux'
    def report_form2(self, context, view=None):
        return self.get_ns_and_h(context,
                                 'FormBM_report2.xml',
                                 'FormBM_report2_autogen.xml',
                                 view)


    report_form3__access__ = 'is_allowed_to_view_form'
    report_form3__label__ = u'C-Personnel'
    def report_form3(self, context, view=None):
        return self.get_ns_and_h(context,
                                 'FormBM_report3.xml',
                                 'FormBM_report3_autogen.xml',
                                 view)


    report_form4__access__ = 'is_allowed_to_view_form'
    report_form4__label__ = u'D-Collections'
    def report_form4(self, context, view=None):
        return self.get_ns_and_h(context,
                                 'FormBM_report4.xml',
                                 'FormBM_report4_autogen.xml',
                                 view)


    report_form5__access__ = 'is_allowed_to_view_form'
    report_form5__label__ = u'E-Acquisitions'
    def report_form5(self, context, view=None):
        return self.get_ns_and_h(context,
                                 'FormBM_report5.xml',
                                 'FormBM_report5_autogen.xml',
                                 view)


    report_form6__access__ = 'is_allowed_to_view_form'
    report_form6__label__ = u'F-Coopération et réseau'
    def report_form6(self, context, view=None):
        return self.get_ns_and_h(context,
                                 'FormBM_report6.xml',
                                 'FormBM_report6_autogen.xml',
                                 view)


    report_form7__access__ = 'is_allowed_to_view_form'
    report_form7__label__ = u'G-Activités'
    def report_form7(self, context, view=None):
        return self.get_ns_and_h(context,
                                 'FormBM_report7.xml',
                                 'FormBM_report7_autogen.xml',
                                 view)


    report_form8__access__ = 'is_allowed_to_view_form'
    report_form8__label__ = u'H-Services'
    def report_form8(self, context, view=None):
        return self.get_ns_and_h(context,
                                 'FormBM_report8.xml',
                                 'FormBM_report8_autogen.xml',
                                 view)


    report_form9__access__ = 'is_allowed_to_view_form'
    report_form9__label__ = u'I-Animations, publications et formation'
    def report_form9(self, context, view=None):
        return self.get_ns_and_h(context,
                                 'FormBM_report9.xml',
                                 'FormBM_report9_autogen.xml',
                                 view)


    report_form10__access__ = 'is_allowed_to_view_form'
    report_form10__label__ = u'Annexes'
    def report_form10(self, context, view=None):
        return self.get_ns_and_h(context,
                                 'FormBM_report10.xml',
                                 'FormBM_report10_autogen.xml',
                                 view)


    report_form11__access__ = 'is_allowed_to_view_form'
    report_form11__label__ = u'EPCI'
    def report_form11(self, context, view=None):
        code_ua = self.get_code()
        return self.get_ns_and_h(context,
                                 'FormBM_report11.xml',
                                 'FormBM_report11_autogen.xml',
                                 view)


    #######################################################################
    # Help
    help0__access__ = True
    def help0(self, context):
        context.response.set_header('Content-Type', 'text/html; charset=UTF-8')
        template = self.get_object('/ui/scrib/FormBM_help0.xml')
        return template.to_str()
    
    help1__access__ = True
    def help1(self, context):
        context.response.set_header('Content-Type', 'text/html; charset=UTF-8')
        template = self.get_object('/ui/scrib/FormBM_help1.xml')
        return template.to_str()


    help2__access__ = True
    def help2(self, context):
        context.response.set_header('Content-Type', 'text/html; charset=UTF-8')
        template = self.get_object('/ui/scrib/FormBM_help2.xml')
        return template.to_str()


    help3__access__ = True
    def help3(self, context):
        context.response.set_header('Content-Type', 'text/html; charset=UTF-8')
        template = self.get_object('/ui/scrib/FormBM_help3.xml')
        return template.to_str()


    help4__access__ = True
    def help4(self, context):
        context.response.set_header('Content-Type', 'text/html; charset=UTF-8')
        template = self.get_object('/ui/scrib/FormBM_help4.xml')
        return template.to_str()


    help5__access__ = True
    def help5(self, context):
        context.response.set_header('Content-Type', 'text/html; charset=UTF-8')
        template = self.get_object('/ui/scrib/FormBM_help5.xml')
        return template.to_str()


    help6__access__ = True
    def help6(self, context):
        context.response.set_header('Content-Type', 'text/html; charset=UTF-8')
        template = self.get_object('/ui/scrib/FormBM_help6.xml')
        return template.to_str()


    help7__access__ = True
    def help7(self, context):
        context.response.set_header('Content-Type', 'text/html; charset=UTF-8')
        template = self.get_object('/ui/scrib/FormBM_help7.xml')
        return template.to_str()


    help8__access__ = True
    def help8(self, context):
        context.response.set_header('Content-Type', 'text/html; charset=UTF-8')
        template = self.get_object('/ui/scrib/FormBM_help8.xml')
        return template.to_str()


    help9__access__ = True
    def help9(self, context):
        context.response.set_header('Content-Type', 'text/html; charset=UTF-8')
        template = self.get_object('/ui/scrib/FormBM_help9.xml')
        return template.to_str()

    help11__access__ = True
    def help11(self, context):
        context.response.set_header('Content-Type', 'text/html; charset=UTF-8')
        template = self.get_object('/ui/scrib/FormBM_help11.xml')
        return template.to_str()


register_object_class(FormBM)
