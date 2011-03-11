# -*- coding: UTF-8 -*-
# Copyright (C) 2010 Hervé Cauwelier <herve@itaapy.com>
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

# Import from the Standard Library

# Import from itools
from itools.gettext import MSG

# Import from ikaaro
from ikaaro.buttons import BrowseButton, Button

# Import from iscrib


class Create(Button):
    access = True
    title = None
    css = 'button-create'



class ExportODSButton(BrowseButton):
    access = 'is_allowed_to_edit'
    name = 'export'
    title = MSG(u"Export This List in ODS Format")



class ExportXLSButton(ExportODSButton):
    name = 'export_xls'
    title = MSG(u"Export This List in XLS Format")



class AddUsers(Button):
    access = 'is_allowed_to_edit'
    name = "add_users"
    title = MSG(u"Add Users")
