# -*- coding: UTF-8 -*-
# Copyright (C) 2004 Luis Belmar Letelier <luis@itaapy.com>
# Copyright (C) 2006 Hervé Cauwelier <herve@itaapy.com>
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
from itools.web import get_context

# Import from ikaaro
from ikaaro.Handler import Handler as BaseHandler


class Handler(BaseHandler):

    #########################################################################
    # Security
    #########################################################################
    def is_consultant(self):
        user = get_context().user
        if user is None:
            return False
        return user.name == 'VoirSCRIB'


    def is_admin_or_consultant(self):
        user = get_context().user
        if user is None:
            return False
        return self.is_admin() or self.is_consultant()