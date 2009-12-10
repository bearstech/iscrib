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
from itools.gettext import MSG

# Import from ikaaro
from ikaaro.registry import register_resource_class

# Import from scrib
from form import get_schema_pages, get_controls, FormHandler, Form
from form_views import Form_View


class BDP2009Handler(FormHandler):
    schema, pages = get_schema_pages('ui/scrib2009/schema-bm.csv')
    controls = get_controls('ui/scrib2009/controls-bm.csv')



class BDP2009(Form):
    class_id = 'BDP2009'
    class_handler = BDP2009Handler
    class_views = ['pageA', 'pageB', 'pageC'] + Form.class_views

    # Views
    pageA = Form_View(title=MSG(u"A-..."), n='A')
    pageB = Form_View(title=MSG(u"B-..."), n='B')
    pageC = Form_View(title=MSG(u"C-..."), n='C')


    ######################################################################
    # Scrib API
    @staticmethod
    def is_bm():
        return False


    @staticmethod
    def is_bdp():
        return True


###########################################################################
# Register
register_resource_class(BDP2009)
