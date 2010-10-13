# -*- coding: UTF-8 -*-
# Copyright (C) 2009-2010 Hervé Cauwelier <herve@itaapy.com>
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

# Import from ikaaro
from ikaaro.workflow import workflow


# States
EMPTY = 'private' # if first_time
DRAFT = 'private' # if not first_time
SENT = 'pending'
EXPORTED = 'public'
MODIFIED = 'modified'

# Transitions
SEND = 'request'
EXPORT = 'accept'

# Simpler that comparing publish date to modification date
workflow.add_state(MODIFIED, title=u"Modified",
        description=u"Modified after export")
