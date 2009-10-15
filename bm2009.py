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
from itools.datatypes import String

# Import from ikaaro
from ikaaro.registry import register_resource_class, register_field

# Import from scrib
from schema_bm import schema, alertes, controles
from form import FormHandler, Form
from form_views import Form_View
from form_bm_views import FormBM_PrintForm
from utils import get_bm, get_adresse
from utils_views import HelpView


class FormBMHandler(FormHandler):

    schema, pages = get_schema_pages('ui/schema-bm.csv')
    controles = get_controles('ui/controles-bm.csv')



class FormBM(Form):

    class_id = 'Form_BM'
    class_handler = FormBMHandler
    class_views = ['page0', 'page10', 'page11', 'page1', 'page2', 'page3',
                   'page4', 'page5', 'page6', 'page7', 'page8', 'page9',
                   'comments'] + Form.class_views

    # Views
    page0 = Page_Form(title=u'Identité', n=0)
    page1 = Page_Form(title=u'A-Finances', n=1)
    page2 = Page_Form(title=u'B-Locaux', n=2)
    page3 = Page_Form(title=u'C-Personnel', n=3)
    page4 = Page_Form(title=u'D-Collections', n=4)
    page5 = Page_Form(title=u'E-Acquisitions', n=5)
    page6 = Page_Form(title=u'F-Coopération et réseau', n=6)
    page7 = Page_Form(title=u'G-Activités', n=7)
    page8 = Page_Form(title=u'H-Services', n=8)
    page9 = Page_Form(title=u'I-Animations, publications et formation', n=9)
    page10 = Page_Form(title=u'Annexes', n=10)
    page11 = Page_Form(title=u'K-EPCI', n=11)
    help0 = HelpView(template='/ui/scrib/FormBM_help0.xml')
    help1 = HelpView(template='/ui/scrib/FormBM_help1.xml')
    help2 = HelpView(template='/ui/scrib/FormBM_help2.xml')
    help3 = HelpView(template='/ui/scrib/FormBM_help3.xml')
    help4 = HelpView(template='/ui/scrib/FormBM_help4.xml')
    help5 = HelpView(template='/ui/scrib/FormBM_help5.xml')
    help6 = HelpView(template='/ui/scrib/FormBM_help6.xml')
    help7 = HelpView(template='/ui/scrib/FormBM_help7.xml')
    help8 = HelpView(template='/ui/scrib/FormBM_help8.xml')
    help9 = HelpView(template='/ui/scrib/FormBM_help9.xml')
    help11 = HelpView(template='/ui/scrib/FormBM_help11.xml')
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

register_resource_class(FormBM)
register_field('code', String(is_indexed=True))
