# -*- coding: ISO-8859-1 -*-
# Copyright (C) 2004 Juan David Ibáñez Palomar <jdavid@itaapy.com>
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
import logging
import logging.config

# Import from itools
from itools import get_abspath
from itools.handlers import get_handler

# Import from iKaaro
from Products.ikaaro import ui

# Import from Culture
from Culture import Culture


def initialize(context):
    Culture.register_in_zope(context)


# Register interface
path = get_abspath(globals(), 'ui')
ui.register_skin('culture', path)

# Found the python used by Zope for generate xml
import os 
gen_path = get_abspath(globals(), 'input_data')
proces, python_line, python_cmd = [], '', ''
proces = os.popen('ps auxwww | grep python').read().split('\n')
pid = os.getpid()
python_line = [l for l in proces if l.count(str(pid))]
if python_line:
    python_cmd = python_line[0].split(':')[-1]
if python_cmd:
    python_cmd = python_cmd.split()[1]
if not python_cmd:
    python_cmd = 'python'
open('%s/where_is_python.txt' % gen_path, 'w').write(python_cmd)


#############################################################################
# Logging facilities
#############################################################################
filename = get_abspath(globals(), 'logging.conf')
logging.config.fileConfig(filename)

