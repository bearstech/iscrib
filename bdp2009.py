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
from itools.datatypes import String, Boolean
from itools.gettext import MSG

# Import from ikaaro
from ikaaro.registry import register_resource_class, register_field

# Import from scrib
from form import FormHandler, Form


class BDP2009Handler(FormHandler):
    pass



class BDP2009Form(Form):
    class_id = 'BDP2009Form'
    class_handler = BDP2009Handler
    class_title = MSG(u"Formulaire BDP")
    class_icon48 = 'scrib2009/images/form48.png'
    class_views = [] + Form.class_views

    # Views


    @classmethod
    def get_metadata_schema(cls):
        return merge_dicts(Form.get_metadata_schema(),
                departement=String)


    def _get_catalog_values(self):
        return merge_dicts(Form._get_catalog_values(self),
                is_bdp=True,
                departement=self.get_property('departement'))


    ######################################################################
    # Security
    def is_bdp(self):
        return self.parent.is_bdp()


    def get_departement(self):
        return self.get_property('departement')


###########################################################################
# Register
register_resource_class(BDP2009Form)
# TODO remove after production
register_resource_class(BDP2009Form, format='BDP2009')
register_field('is_bdp', Boolean(is_indexed=True, is_stored=True))
