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
from itools.datatypes import String, Boolean, Integer
from itools.gettext import MSG

# Import from ikaaro
from ikaaro.registry import register_resource_class, register_field

# Import from scrib
from bdp2009_views import BDP2009Form_View
from bm2009 import get_schema_pages, get_controls, BM2009Handler
from bm2009_views import BM2009Form_Print, BM2009Form_Edit
from form import Form


class BDP2009Handler(BM2009Handler):
    schema, pages = get_schema_pages('ui/scrib2009/bdp/schema.csv')
    controls = get_controls('ui/scrib2009/bdp/controls.csv')



class BDP2009Form(Form):
    class_id = 'BDP2009Form'
    class_handler = BDP2009Handler
    class_title = MSG(u"Formulaire BDP")
    class_icon48 = 'scrib2009/images/form48.png'
    class_views = ['page0'] + Form.class_views

    # Views
    Page0 = BDP2009Form_View(title=MSG(u"Saisie du rapport"), n='0')
    PageA = BDP2009Form_View(n='A')
    PageB = BDP2009Form_View(n='B')
    PageC = BDP2009Form_View(n='C')
    PageD = BDP2009Form_View(n='D')
    PageE = BDP2009Form_View(n='E')
    PageF = BDP2009Form_View(n='F')
    PageG = BDP2009Form_View(n='G')
    PageH = BDP2009Form_View(n='H')
    PageI = BDP2009Form_View(n='I')
    PageL = BDP2009Form_View(n='L')
    imprimer = BM2009Form_Print()
    edit = BM2009Form_Edit()


    @classmethod
    def get_metadata_schema(cls):
        return merge_dicts(Form.get_metadata_schema(),
                departement=String,
                # Utilisé pour la recherche, pas la sécurité
                code_ua=Integer,
                is_first_time=Boolean(default=True))


    def _get_catalog_values(self):
        return merge_dicts(Form._get_catalog_values(self),
                is_bdp=True,
                departement=self.get_property('departement'),
                # Utilisé pour la recherche, pas la sécurité
                code_ua=self.get_property('code_ua'))


    ######################################################################
    # Security
    def is_bdp(self):
        return self.parent.is_bdp()


    def is_ready(self):
        # TODO
        return False


    def get_departement(self):
        return self.get_property('departement')


###########################################################################
# Register
register_resource_class(BDP2009Form)
register_field('is_bdp', Boolean(is_indexed=True, is_stored=True))
