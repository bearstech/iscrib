# -*- coding: UTF-8 -*-
# Copyright (C) 2005  <jdavid@favela.(none)>
# Copyright (C) 2006 J. David Ibanez <jdavid@itaapy.com>
# Copyright (C) 2006 luis <luis@lucifer.localdomain>
# Copyright (C) 2006-2008 Hervé Cauwelier <herve@itaapy.com>
# Copyright (C) 2008 Henry Obein <henry@itaapy.com>
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
from itools.csv import CSVFile
from itools.datatypes import Enumerate, String
from itools.gettext import MSG

# Import from ikaaro
from ikaaro.registry import register_resource_class
from ikaaro.text import CSV

# Import from scrib
from datatypes import Unicode
from schema2009 import PageNumber


class ControlLevel(Enumerate):
    options = [
        {'name': '0', 'value': u"Informatif"},
        {'name': '1', 'value': u"Avertissement"},
        {'name': '2', 'value': u"Bloquant"}]



class Controls2009Handler(CSVFile):
    schema = {'number': String(mandatory=True, title=MSG(u"Numéro")),
              'title': Unicode(mandatory=True, title=MSG(u"Titre")),
              'expr': String(mandatory=True, title=MSG(u"Expression")),
              'level': ControlLevel(mandatory=True, title=MSG(u"Niveau")),
              'page': PageNumber(mandatory=True, title=MSG(u"Page"))}
    columns = ['number', 'title', 'expr', 'level', 'page']


    def get_controls(self):
        return list(self.get_rows())



class Controls2009(CSV):
    class_id = 'Controls2009'
    class_title = MSG(u"Contrôles 2009")
    class_handler = Controls2009Handler



register_resource_class(Controls2009)
