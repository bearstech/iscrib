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
from itools.core import merge_dicts
from itools.datatypes import String, Integer

# Import from ikaaro
from ikaaro.registry import register_resource_class, register_field

# Import from scrib
from form import get_schema_pages, get_controls, FormHandler, Form
from form_views import Page_Form


class BM2009Handler(FormHandler):
    schema, pages = get_schema_pages('ui/schema-bm.csv')
    controles = get_controls('ui/controls-bm.csv')



class BM2009(Form):
    class_id = 'BM2009'
    class_handler = BM2009Handler
    class_views = ['pageA', 'pageB', 'pageC'] + Form.class_views

    # Views
    pageA = Page_Form(title=u"Identité", n='A')
    pageB = Page_Form(title=u"A-Finances", n='B')
    pageC = Page_Form(title=u"B-Locaux", n='C')


    @classmethod
    def get_metadata_schema(cls):
        return merge_dicts(Form.get_metadata_schema(),
                           code_ua=Integer,
                           id=String)


    def _get_catalog_values(self):
        values = Form._get_catalog_values(self)
        values['code_ua'] = self.get_property('code_ua')
        return values


    ######################################################################
    # Scrib API
    @staticmethod
    def is_bm():
        return True


    @staticmethod
    def is_bdp():
        return False


###########################################################################
# Register
register_resource_class(BM2009)
register_field('code_ua', Integer(is_indexed=True, is_stored=True))