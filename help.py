# -*- coding: UTF-8 -*-
# Copyright (C) 2005  <jdavid@favela.(none)>
# Copyright (C) 2006 J. David Ibanez <jdavid@itaapy.com>
# Copyright (C) 2006, 2008 Hervé Cauwelier <herve@itaapy.com>
# Copyright (C) 2009 Sylvain Taverne <sylvain@itaapy.com>
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
from itools.gettext import MSG
from itools.web import STLView


class HelpView(STLView):
    template = '/ui/pelleas/help/help.xml'
    access = True
    title = MSG(u'Aide générale')



class HelpAware(object):
    help = HelpView()
