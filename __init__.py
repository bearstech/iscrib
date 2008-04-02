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
from os import path
import sys

# Import from itools
from itools import get_abspath, get_version

# Import from ikaaro
from ikaaro.skins import register_skin


class Configuration(object):
    pass


# Read the configuration 
config_path = path.join(os.getcwd(), 'Setup.conf')
try:
    config_file = open(config_path, 'r')
except IOError:
    print "copiez le fichier 'Setup.conf' (pas 'setup.conf') du répertoire scrib ici."
    sys.exit(1)
config = Configuration()

for line in config_file.readlines():
    line = line.strip()
    if not line or line.startswith('#'):
        continue
    key, value = line.split('=', 1)
    key = key.strip()
    if not key:
        raise ValueError, 'One line has no left value' 
    value = value.strip()
    if not value:
        raise ValueError, "No value for the key '%s' in Setup.conf file" % key
    setattr(config, key, value)

config_file.close()

# Register interface
path = get_abspath(globals(), 'ui')
register_skin('scrib', path)


# Register Root
from root import Root

__version__ = get_version(globals())
