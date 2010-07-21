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

# Import from itools
from itools.gettext import MSG

# Import from ikaaro
from ikaaro.folder import Folder
from ikaaro.registry import register_resource_class, register_document_type

# Import from iscrib
from controls import Controls
from param_views import Param_NewInstance, Param_View
from schema import Schema



class Param(Folder):
    class_id = 'Param'
    class_title = MSG(u"Form")
    class_description = MSG(u"Create a form from an ODS of parameters")
    class_icon16 = 'icons/16x16/tasks.png'
    class_icon48 = 'icons/48x48/tasks.png'
    
    schema_class = Schema
    controls_class = Controls

    # Views
    new_instance = Param_NewInstance()
    view = Param_View()


register_resource_class(Param)
register_document_type(Param)
