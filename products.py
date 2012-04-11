# -*- coding: UTF-8 -*-
# Copyright (C) 2012 Sylvain Taverne <sylvain@itaapy.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Import from itools
from itools.core import merge_dicts
from itools.datatypes import Integer
from itools.gettext import MSG

# Import from ikaaro
from ikaaro.buttons import PublishButton, RemoveButton, RetireButton
from ikaaro.folder import Folder

# Import from itws
from itws.feed_views import FieldsTableFeed_View
from itws.shop import Product as BaseProduct
from itws.views import FieldsAutomaticEditView, FieldsAdvance_NewInstance


class Product(BaseProduct):

    class_id = 'iscrib-product'
    class_title = MSG(u"Produit")
    class_views = ['view', 'edit']

    class_schema = merge_dicts(
        BaseProduct.class_schema,
        nb_users=Integer(source='metadata', title=MSG(u'Nb users')))

    # Views
    _fields = BaseProduct._fields + ['nb_users']
    new_instance = FieldsAdvance_NewInstance(fields=_fields, access='is_admin')
    edit = FieldsAutomaticEditView(edit_fields=_fields)


class Products_View(FieldsTableFeed_View):

    search_cls = Product
    search_fields = []
    search_class_id = 'iscrib-product'
    table_fields = ['checkbox', 'name', 'reference', 'title', 'description',
                    'nb_users', 'workflow_state']
    table_actions = [RemoveButton, PublishButton, RetireButton]



class Products(Folder):

    class_id = 'iscrib-products'
    class_title = MSG(u'Products')

    def get_document_types(self):
        return [Product]

    # Views
    view  = Products_View()
