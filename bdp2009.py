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
from itools.datatypes import Boolean
from itools.gettext import MSG

# Import from ikaaro
from ikaaro.registry import register_resource_class, register_field

# Import from scrib
from base2009 import Base2009Form
from base2009_views import Base2009Form_Edit
from base2009_views import Base2009Form_New
from bdp2009_views import BDP2009Form_View, BDP2009Form_Send
from bdp2009_views import BDP2009Form_Print
from datatypes import Departements
from form import Form


class BDP2009Form(Base2009Form):
    class_id = 'BDP2009Form'
    class_version = '20090123'
    class_title = MSG(u"Formulaire BDP")
    class_views = ['page0'] + Form.class_views

    # Views
    page0 = BDP2009Form_View(title=MSG(u"Saisie du rapport"), pagenum='0')
    envoyer = BDP2009Form_Send()
    imprimer = BDP2009Form_Print()
    edit = Base2009Form_Edit()
    new_instance = Base2009Form_New()


    def __getattr__(self, name):
        print "BDP2009Form.__getattr__", name
        pagenum = name[-1]
        assert pagenum in self.get_page_numbers()
        view = BDP2009Form_View(pagenum=pagenum)
        # XXX marche pas
        self.__dict__[name] = view
        return view


    def _get_catalog_values(self):
        return merge_dicts(Base2009Form._get_catalog_values(self),
                is_bdp=True)


    ######################################################################
    # Security
    def update_20090123(self):
        """0008687: BDP : l'en-tête du formulaire fait aparaître le nom de la
        ville où se situe la BDP au lieu du département.
        """
        departement = self.get_property('departement')
        title = Departements.get_value(departement)
        self.set_property('title', title)



###########################################################################
# Register
register_resource_class(BDP2009Form)
register_field('is_bdp', Boolean(is_indexed=True, is_stored=True))
