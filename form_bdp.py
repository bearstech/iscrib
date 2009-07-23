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

# Import from ikaaro
from ikaaro.registry import register_resource_class

# Import from scrib
from schema_bdp import schema, alertes, controles
from form import FormHandler, Form
from form_views import Form_View
from form_bdp_views import Form_BDP_PrintForm
from utils import get_bdp, get_adresse
from utils_views import HelpView


class FormBDPHandler(FormHandler):

    def _load_state_from_file(self, file):
        return FormHandler._load_state_from_file(self, file, schema)


    def to_str(self, encoding='UTF-8'):
        return FormHandler.to_str(self, schema, encoding)



class FormBDP(Form):

    class_id = 'FormBDP'
    class_handler = FormBDPHandler
    class_views = ['report_form0', 'report_form1', 'report_form2',
                   'report_form3', 'report_form4', 'report_form5',
                   'report_form6', 'report_form7', 'report_form8',
                   'report_form9', 'comments'] + Form.class_views

    print_form = Form_BDP_PrintForm()

    ######################################################################
    # Form API
    @staticmethod
    def get_scrib_schema():
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
        chaineSQL = ("select * from adresse08 where type_adr='3' and "
                     "code_ua is not null and dept='%s'" % dept)
        return get_adresse(chaineSQL)


    def get_year(self):
        return int(self.parent.name.split('BDP')[-1])


    def get_dep(self):
        return self.name


    def get_user_town(self):
        return get_bdp(self.name).get_value('name')




    #title=u'Renseignez votre rapport',

    report_form0 = Form_View(access='is_allowed_to_view',
                             title=u'Identité',
                             xml='FormBDP_report0.xml',
                             autogen_xml='FormBDP_report0_autogen.xml')

    report_form1 = Form_View(access='is_allowed_to_view',
                             title=u'A-Finances',
                             xml='FormBDP_report1.xml',
                             autogen_xml='FormBDP_report1_autogen.xml')


    report_form2 = Form_View(access='is_allowed_to_view',
                             title=u'B-Locaux',
                             xml='FormBDP_report2.xml',
                             autogen_xml='FormBDP_report2_autogen.xml')


    report_form3 = Form_View(access='is_allowed_to_view',
                             title=u'C-Personnel',
                             xml='FormBDP_report3.xml',
                             autogen_xml='FormBDP_report3_autogen.xml')


    report_form4 = Form_View(access='is_allowed_to_view',
                             title=u'D-Collections',
                             xml='FormBDP_report4.xml',
                             autogen_xml='FormBDP_report4_autogen.xml')


    report_form5 = Form_View(access='is_allowed_to_view',
                             title=u'E-Acquisitions',
                             xml='FormBDP_report5.xml',
                             autogen_xml='FormBDP_report5_autogen.xml')


    report_form6 = Form_View(access='is_allowed_to_view',
                             title=u'F-Réseau tous public',
                             xml='FormBDP_report6.xml',
                             autogen_xml='FormBDP_report6_autogen.xml')


    report_form7 = Form_View(access='is_allowed_to_view',
                             title=u'G-Réseau spécifique',
                             xml='FormBDP_report7.xml',
                             autogen_xml='FormBDP_report7_autogen.xml')


    report_form8 = Form_View(access='is_allowed_to_view',
                             title=u'H-Services',
                             xml='FormBDP_report8.xml',
                             autogen_xml='FormBDP_report8_autogen.xml')


    report_form9 = Form_View(access='is_allowed_to_view',
                             title=u'I-Action Culturelle',
                             xml='FormBDP_report9.xml',
                             autogen_xml='FormBDP_report9_autogen.xml')



    #######################################################################
    # Help
    help_menu = HelpView(access=True, template='/ui/scrib/FormBDP_help_menu.xml')
    help0 = HelpView(access=True, template='/ui/scrib/FormBDP_help0.xml')
    help1 = HelpView(access=True, template='/ui/scrib/FormBDP_help1.xml')
    help2 = HelpView(access=True, template='/ui/scrib/FormBDP_help2.xml')
    help3 = HelpView(access=True, template='/ui/scrib/FormBDP_help3.xml')
    help4 = HelpView(access=True, template='/ui/scrib/FormBDP_help4.xml')
    help5 = HelpView(access=True, template='/ui/scrib/FormBDP_help5.xml')
    help6 = HelpView(access=True, template='/ui/scrib/FormBDP_help6.xml')
    help7 = HelpView(access=True, template='/ui/scrib/FormBDP_help7.xml')
    help8 = HelpView(access=True, template='/ui/scrib/FormBDP_help8.xml')
    help9 = HelpView(access=True, template='/ui/scrib/FormBDP_help9.xml')



register_resource_class(FormBDP)
