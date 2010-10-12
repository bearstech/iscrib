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
from itools.core import merge_dicts

# Import from ikaaro
from ikaaro.access import is_admin
from ikaaro.skins import Skin as BaseSkin

# Import from iscrib


class Skin(BaseSkin):

    def build_namespace(self, context):
        resource = context.resource
        website_title = resource.get_site_root().get_title()
        new_resource_allowed = is_admin(context.user, resource)
        return merge_dicts(BaseSkin.build_namespace(self, context),
                  website_title=website_title,
                  new_resource_allowed=new_resource_allowed)
