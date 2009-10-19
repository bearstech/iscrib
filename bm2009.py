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
from form import get_schema_pages, get_controles, FormHandler, Form
from form_views import Page_Form
from utils import get_bm, get_adresse


class FormBMHandler(FormHandler):

    schema, pages = get_schema_pages('ui/schema-bm.csv')
    controles = get_controles('ui/controles-bm.csv')



class FormBM(Form):

    class_id = 'Form_BM'
    class_handler = FormBMHandler
    class_views = ['pageA', 'pageB', 'pageC'] + Form.class_views

    # Views
    pageA = Page_Form(title=u'Identité', n='A')
    pageB = Page_Form(title=u'A-Finances', n='B')
    pageC = Page_Form(title=u'B-Locaux', n='C')


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
