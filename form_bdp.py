# -*- coding: UTF-8 -*-
# Copyright (C) 2006 Luis Belmar Letelier <luis@itaapy.com>
# Copyright (C) 2006, 2008 Hervé Cauwelier <herve@itaapy.com>
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
from itools.stl import stl

# Import from ikaaro
from ikaaro.registry import register_object_class

# Import from scrib
from schema_bdp import schema, alertes, controles
from form import FormHandler, Form
from utils import get_bdp, get_adresse, reduce_generators



class FormBDPHandler(FormHandler):
    def _load_state_from_file(self, file):
        return FormHandler._load_state_from_file(self, file, schema)


    def to_str(self, encoding='UTF-8'):
        return FormHandler.to_str(self, schema, encoding)



class FormBDP(Form):
    class_id = 'FormBDP'
    class_handler = FormBDPHandler
    class_views = [['report_form0', 'report_form1', 'report_form2',
                    'report_form3', 'report_form4', 'report_form5',
                    'report_form6', 'report_form7', 'report_form8',
                    'report_form9', 'comments']] + Form.class_views


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
        return True


    @staticmethod
    def is_BM():
        return False


    @staticmethod
    def base_lect(dept):
        chaineSQL = ("select * from adresse where type_adr='3' and "
                     "code_ua is not null and dept='%s'" % dept)
        return get_adresse(chaineSQL)


    def get_year(self):
        return self.parent.name.split('BDP')[-1]


    def get_dep(self):
        return self.name


    def get_user_town(self):
        return get_bdp(self.name).get_value('name')


    ######################################################################
    # User interface
    #######################################################################

    #######################################################################
    # Edit report
    print_form__access__ = 'is_allowed_to_view_form'
    print_form__label__ = u'Impression du formulaire '
    def print_form(self, context):
        context.response.set_header('Content-Type',
                                    'text/html; charset=UTF-8')
        namespace = self.get_namespace(context)
        forms = ['FormBDP_report%s' % i for i in range(0, 10)]
        forms.append('Form_comments')
        forms = [('%s.xml' % i, '%s_autogen.xml' % i, 'print_all')
                 for i in forms]
        forms = [self.get_ns_and_h(context, n, a, v) for n, a, v in forms]
        namespace['body'] = reduce_generators(forms)
        namespace['title'] = self.get_title()
        namespace['styles'] = context.root.get_skin().get_styles(context)

        template = self.get_object('/ui/scrib/printable_template.xhtml')
        return stl(template, namespace)


    report_form0__access__ = 'is_allowed_to_view_form'
    report_form0__label__ = u'Rapport Bibliothèques'
    report_form0__sublabel__ = u'Identité'
    def report_form0(self, context, view=None):
        return self.get_ns_and_h(context,
                                 'FormBDP_report0.xml',
                                 'FormBDP_report0_autogen.xml',
                                 view)


    report_form1__access__ = 'is_allowed_to_view_form'
    report_form1__sublabel__ = u'A-Finances'
    def report_form1(self, context, view=None):
        return self.get_ns_and_h(context,
                                 'FormBDP_report1.xml',
                                 'FormBDP_report1_autogen.xml',
                                 view)


    report_form2__access__ = 'is_allowed_to_view_form'
    report_form2__sublabel__ = u'B-Locaux'
    def report_form2(self, context, view=None):
        return self.get_ns_and_h(context,
                                 'FormBDP_report2.xml',
                                 'FormBDP_report2_autogen.xml',
                                 view)


    report_form3__access__ = 'is_allowed_to_view_form'
    report_form3__sublabel__ = u'C-Personnel'
    def report_form3(self, context, view=None):
        return self.get_ns_and_h(context,
                                 'FormBDP_report3.xml',
                                 'FormBDP_report3_autogen.xml',
                                 view)


    report_form4__access__ = 'is_allowed_to_view_form'
    report_form4__sublabel__ = u'D-Collections'
    def report_form4(self, context, view=None):
        return self.get_ns_and_h(context,
                                 'FormBDP_report4.xml',
                                 'FormBDP_report4_autogen.xml',
                                 view)


    report_form5__access__ = 'is_allowed_to_view_form'
    report_form5__sublabel__ = u'E-Acquisitions'
    def report_form5(self, context, view=None):
        return self.get_ns_and_h(context,
                                 'FormBDP_report5.xml',
                                 'FormBDP_report5_autogen.xml',
                                 view)


    report_form6__access__ = 'is_allowed_to_view_form'
    report_form6__sublabel__ = u'F-Réseau tous public'
    def report_form6(self, context, view=None):
        return self.get_ns_and_h(context,
                                 'FormBDP_report6.xml',
                                 'FormBDP_report6_autogen.xml',
                                 view)


    report_form7__access__ = 'is_allowed_to_view_form'
    report_form7__sublabel__ = u'G-Réseau spécifique'
    def report_form7(self, context, view=None):
        return self.get_ns_and_h(context,
                                 'FormBDP_report7.xml',
                                 'FormBDP_report7_autogen.xml',
                                 view)


    report_form8__access__ = 'is_allowed_to_view_form'
    report_form8__sublabel__ = u'H-Services'
    def report_form8(self, context, view=None):
        return self.get_ns_and_h(context,
                                 'FormBDP_report8.xml',
                                 'FormBDP_report8_autogen.xml',
                                 view)


    report_form9__access__ = 'is_allowed_to_view_form'
    report_form9__sublabel__ = u'I-Action Culturelle'
    def report_form9(self, context, view=None):
        return self.get_ns_and_h(context,
                                 'FormBDP_report9.xml',
                                 'FormBDP_report9_autogen.xml',
                                 view)


    #######################################################################
    # Help
    help_menu__access__ = True
    def help_menu(self, context):
        context.response.set_header('Content-Type', 'text/html; charset=UTF-8')
        template = self.get_object('/ui/scrib/FormBDP_help_menu.xml')
        return template.to_str()


    help0__access__ = True
    def help0(self, context):
        context.response.set_header('Content-Type', 'text/html; charset=UTF-8')
        handler = self.get_handler('/ui/culture/FormBDP_help0.xml')
        return handler.to_str()


    help1__access__ = True
    def help1(self, context):
        context.response.set_header('Content-Type', 'text/html; charset=UTF-8')
        template = self.get_object('/ui/scrib/FormBDP_help1.xml')
        return template.to_str()


    help2__access__ = True
    def help2(self, context):
        context.response.set_header('Content-Type', 'text/html; charset=UTF-8')
        template = self.get_object('/ui/scrib/FormBDP_help2.xml')
        return template.to_str()


    help3__access__ = True
    def help3(self, context):
        context.response.set_header('Content-Type', 'text/html; charset=UTF-8')
        template = self.get_object('/ui/scrib/FormBDP_help3.xml')
        return template.to_str()


    help4__access__ = True
    def help4(self, context):
        context.response.set_header('Content-Type', 'text/html; charset=UTF-8')
        template = self.get_object('/ui/scrib/FormBDP_help4.xml')
        return template.to_str()


    help5__access__ = True
    def help5(self, context):
        context.response.set_header('Content-Type', 'text/html; charset=UTF-8')
        template = self.get_object('/ui/scrib/FormBDP_help5.xml')
        return template.to_str()


    help6__access__ = True
    def help6(self, context):
        context.response.set_header('Content-Type', 'text/html; charset=UTF-8')
        template = self.get_object('/ui/scrib/FormBDP_help6.xml')
        return template.to_str()


    help7__access__ = True
    def help7(self, context):
        context.response.set_header('Content-Type', 'text/html; charset=UTF-8')
        template = self.get_object('/ui/scrib/FormBDP_help7.xml')
        return template.to_str()


    help8__access__ = True
    def help8(self, context):
        context.response.set_header('Content-Type', 'text/html; charset=UTF-8')
        template = self.get_object('/ui/scrib/FormBDP_help8.xml')
        return template.to_str()


    help9__access__ = True
    def help9(self, context):
        context.response.set_header('Content-Type', 'text/html; charset=UTF-8')
        template = self.get_object('/ui/scrib/FormBDP_help9.xml')
        return template.to_str()



register_object_class(FormBDP)
