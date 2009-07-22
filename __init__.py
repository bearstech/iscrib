# -*- coding: UTF-8 -*-
# Copyright (C) 2006, 2008 Hervé Cauwelier <herve@itaapy.com>
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
from os.path import exists

# Import from itools
from itools.core import get_abspath, get_version
from itools.handlers import ConfigFile

# Import from ikaaro
from ikaaro.skins import register_skin

# Import from pelleas
import skin


# Give a version
__version__ = get_version()

# Read the configuration (TODO move to instance's config.conf)
config_path = get_abspath('Setup.conf')
if not exists(config_path):
    raise ("copiez le fichier 'Setup.conf' (pas 'setup.conf') "
           "du répertoire scrib ici.")
config = ConfigFile(config_path)

# Register root
from root import Root
