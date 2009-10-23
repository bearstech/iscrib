# -*- coding: UTF-8 -*-
# Copyright (C) 2007-2008 Hervé Cauwelier <herve@itaapy.com>
# Copyright (C) 2008 Henry Obein <henry@itaapy.com>
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

# Import from itools
from itools.core import get_abspath

# Import from ikaaro
from ikaaro.skins import Skin, register_skin, map

# Import from scrib
from widgets import UITable


class ScribSkin(Skin):

    def get_styles(self, context):
        styles = [
            # BackOffice style
            '/ui/bo.css',
            # Calendar JS Widget (http://dynarch.com/mishoo/calendar.epl)
            '/ui/js_calendar/calendar-aruni.css',
            # Table
            '/ui/table/style.css',
            # Aruni
            '/ui/aruni/style.css',
            # Scrib
            '/ui/scrib/style.css']
        # Dynamic styles
        for style in context.styles:
            styles.append(style)
        return styles



#############################################################################
# Register
map[UITable.class_mimetypes[0]] = UITable
path = get_abspath('ui')
register_skin('scrib', ScribSkin(path))
