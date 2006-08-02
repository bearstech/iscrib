# -*- coding: UTF-8 -*-
# Copyright (C) 2004 Juan David Ibáñez Palomar <jdavid@itaapy.com>
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

# Import from the Standard Library
import os

# Import from itools
from itools import get_abspath, get_version

# Import from itools.cms
from itools.cms.skins import register_skin

# Import from scrib
from Culture import Root


class Configuration(object):
    pass


# Read the configuration 
path = get_abspath(globals(), 'Setup.conf')
config = Configuration()

for line in open(path, 'r').readlines():
    key, value = line.split('=')
    key = key.strip()
    if not key:
        raise ValueError, 'One line has no left value' 
    value = value.strip()
    if not value:
        raise ValueError, "No value for the key '%s' in Setup.conf file" % key
    setattr(config, key, value)


# Register interface
path = get_abspath(globals(), 'ui')
register_skin('culture', path)


__version__ = get_version(globals())
