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


# Import from ikaaro
from ikaaro.registry import register_resource_class

# Import from scrib
from schema_bm import schema, alertes, controles
from form import FormHandler, Form
from form_views import Form_View
from form_bm_views import FormBM_PrintForm
from utils import get_bm, get_adresse
from utils_views import HelpView



class FormBMHandler(FormHandler):
    def _load_state_from_file(self, file):
        return FormHandler._load_state_from_file(self, file, schema)


    def to_str(self, encoding='UTF-8'):
        return FormHandler.to_str(self, schema, encoding)



class FormBM(Form):

    class_id = 'Form_BM'
    class_handler = FormBMHandler
    class_views = ['report_form0', 'report_form10', 'report_form11',
                   'report_form1', 'report_form2', 'report_form3',
                   'report_form4', 'report_form5', 'report_form6',
                   'report_form7', 'report_form8', 'report_form9',
                   'comments'] + Form.class_views

    print_form = FormBM_PrintForm()

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
        return False


    @staticmethod
    def is_BM():
        return True


    @staticmethod
    def base_lect(insee):
        chaineSQL = ("select * from adresse08 where "
                     "insee is not null and code_bib='%s'" % insee)
        return get_adresse(chaineSQL)


    def get_year(self):
        return int(self.parent.name.split('BM')[-1])


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
    def _get_catalog_values(self):
        values = Form._get_catalog_values(self)
        values['code'] = self.get_code()
        return values


    #######################################################################
    # Edit report

    report_form0 = Form_View(access='is_allowed_to_view',
                             title=u'Identité',
                             xml='FormBM_report0.xml',
                             autogen_xml='FormBM_report0_autogen.xml')

    report_form1 = Form_View(access='is_allowed_to_view',
                             title=u'A-Finances',
                             xml='FormBM_report1.xml',
                             autogen_xml='FormBM_report1_autogen.xml')

    report_form2 = Form_View(access='is_allowed_to_view',
                             title=u'B-Locaux',
                             xml='FormBM_report2.xml',
                             autogen_xml='FormBM_report2_autogen.xml')

    report_form3 = Form_View(access='is_allowed_to_view',
                             title=u'C-Personnel',
                             xml='FormBM_report3.xml',
                             autogen_xml='FormBM_report3_autogen.xml')

    report_form4 = Form_View(access='is_allowed_to_view',
                             title=u'D-Collections',
                             xml='FormBM_report4.xml',
                             autogen_xml='FormBM_report4_autogen.xml')

    report_form5 = Form_View(access='is_allowed_to_view',
                             title=u'E-Acquisitions',
                             xml='FormBM_report5.xml',
                             autogen_xml='FormBM_report5_autogen.xml')

    report_form6 = Form_View(access='is_allowed_to_view',
                             title=u'F-Coopération et réseau',
                             xml='FormBM_report6.xml',
                             autogen_xml='FormBM_report6_autogen.xml')

    report_form7 = Form_View(access='is_allowed_to_view',
                             title=u'G-Activités',
                             xml='FormBM_report7.xml',
                             autogen_xml='FormBM_report7_autogen.xml')

    report_form8 = Form_View(access='is_allowed_to_view',
                             title=u'H-Services',
                             xml='FormBM_report8.xml',
                             autogen_xml='FormBM_report8_autogen.xml')

    report_form9 = Form_View(access='is_allowed_to_view',
                             title=u'I-Animations, publications et formation',
                             xml='FormBM_report9.xml',
                             autogen_xml='FormBM_report9_autogen.xml')

    report_form10 = Form_View(access='is_allowed_to_view',
                             title=u'Annexes',
                             xml='FormBM_report10.xml',
                             autogen_xml='FormBM_report10_autogen.xml')

    report_form11 = Form_View(access='is_allowed_to_view',
                             title=u'K-EPCI',
                             xml='FormBM_report10.xml',
                             autogen_xml='FormBM_report10_autogen.xml')


    help0 = HelpView(access=True, template='/ui/scrib/FormBM_help0.xml')
    help1 = HelpView(access=True, template='/ui/scrib/FormBM_help1.xml')
    help2 = HelpView(access=True, template='/ui/scrib/FormBM_help2.xml')
    help3 = HelpView(access=True, template='/ui/scrib/FormBM_help3.xml')
    help4 = HelpView(access=True, template='/ui/scrib/FormBM_help4.xml')
    help5 = HelpView(access=True, template='/ui/scrib/FormBM_help5.xml')
    help6 = HelpView(access=True, template='/ui/scrib/FormBM_help6.xml')
    help7 = HelpView(access=True, template='/ui/scrib/FormBM_help7.xml')
    help8 = HelpView(access=True, template='/ui/scrib/FormBM_help8.xml')
    help9 = HelpView(access=True, template='/ui/scrib/FormBM_help9.xml')
    help11 = HelpView(access=True, template='/ui/scrib/FormBM_help11.xml')

register_resource_class(FormBM)

# XXX to migrate
#
#    def get_catalog_fields(self):
#        fields = Form.get_catalog_fields(self)
#        fields += [KeywordField('code')]
#        return fields
#
#
