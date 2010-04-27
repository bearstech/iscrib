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
from itools.core import merge_dicts, freeze
from itools.datatypes import Boolean
from itools.gettext import MSG
from itools.uri import resolve_uri

# Import from ikaaro
from ikaaro.registry import register_resource_class, register_field

# Import from scrib
from base2009 import get_schema_pages, get_controls
from base2009 import Base2009Handler, Base2009Form
from base2009_views import Base2009Form_Edit
from bm2009_pageb_views import BM2009Form_PageB_View
from bm2009_views import BM2009Form_View, BM2009Form_Send, BM2009Form_Print
from form import Form


class BM2009Handler(Base2009Handler):
    schema, pages = get_schema_pages('ui/scrib2009/bm/schema.csv')
    controls = get_controls('ui/scrib2009/bm/controls.csv')



class BM2009Form(Base2009Form):
    class_id = 'BM2009Form'
    class_handler = BM2009Handler
    class_title = MSG(u"Formulaire BM")
    class_views = ['pageA'] + Form.class_views

    # Views
    pageA = BM2009Form_View(title=MSG(u"Saisie du rapport"), n='A')
    pageB = BM2009Form_PageB_View(n='B')
    pageC = BM2009Form_View(n='C')
    pageD = BM2009Form_View(n='D')
    pageE = BM2009Form_View(n='E')
    pageF = BM2009Form_View(n='F')
    pageG = BM2009Form_View(n='G')
    pageH = BM2009Form_View(n='H')
    pageI = BM2009Form_View(n='I')
    envoyer = BM2009Form_Send()
    imprimer = BM2009Form_Print()
    edit = Base2009Form_Edit()

    def _get_catalog_values(self):
        return merge_dicts(Base2009Form._get_catalog_values(self),
                is_bm=True)


    ######################################################################
    # Security
    def is_ready(self):
        if not Base2009Form.is_ready(self):
            return False
        for form in self.get_pageb().get_resources():
            for name, datatype in form.get_invalid_fields():
                if datatype.is_mandatory:
                    return False
            for control in form.get_failed_controls():
                if control['level'] == '2':
                    return False
        return True


    ######################################################################
    # API
    def get_pageb(self, make=False):
        from bm2009_pageb import MultipleForm_PageB

        name = '%s-pageb' % self.get_code_ua()
        pageb = self.parent.get_resource(name, soft=True)
        if pageb is None:
            if make is False:
                metadata = MultipleForm_PageB.build_metadata()
                metadata.uri = resolve_uri(self.metadata.uri,
                        '%s.metadata' % name)
                metadata.database = self.metadata.database
                pageb = MultipleForm_PageB(metadata)
                pageb.name = name
                pageb.parent = self.parent
            else:
                pageb = MultipleForm_PageB.make_resource(MultipleForm_PageB,
                        self.parent, name,
                        title={'fr': self.get_title()})
        return pageb


    def is_first_time(self):
        if not Base2009Form.is_first_time(self):
            return False
        pageb = self.get_pageb()
        return pageb.is_first_time()


    def get_invalid_fields(self, pages=freeze([]), exclude=freeze(['B'])):
        return Base2009Form.get_invalid_fields(self, pages=pages,
                exclude=exclude)


    def get_failed_controls(self, pages=freeze([]), exclude=freeze(['B'])):
        return Base2009Form.get_failed_controls(self, pages=pages,
                exclude=exclude)

    
    def get_export_query(self, table, pages=freeze([]),
            exclude=freeze(['B'])):
        return Base2009Form.get_export_query(self, table, pages=pages,
                exclude=exclude)



###########################################################################
# Register
register_resource_class(BM2009Form)
register_field('is_bm', Boolean(is_indexed=True, is_stored=True))
