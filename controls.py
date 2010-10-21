# -*- coding: UTF-8 -*-
# Copyright (C) 2005  <jdavid@favela.(none)>
# Copyright (C) 2006 J. David Ibanez <jdavid@itaapy.com>
# Copyright (C) 2006 luis <luis@lucifer.localdomain>
# Copyright (C) 2006-2008, 2010 Hervé Cauwelier <herve@itaapy.com>
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
from itools.csv import Table as TableFile
from itools.datatypes import Enumerate
from itools.gettext import MSG
from itools.web import ERROR

# Import from ikaaro
from ikaaro.table import Table

# Import from iscrib
from datatypes import Unicode
from utils import SI
from schema import Variable


ERR_EMPTY_TITLE = ERROR(u'In controls, line {line}, title is missing.')
ERR_EMPTY_EXPRESSION = ERROR(u'In controls, line {line}, expression is '
        u'missing.')
ERR_BAD_EXPRESSION = ERROR(u'In controls, line {line}, syntax error in '
        u'expression: {err}')
ERR_BAD_LEVEL = ERROR(u'In controls, line {line}, unexpected level '
        u'"{level}".')
ERR_EMPTY_VARIABLE = ERROR(u'In controls, line {line}, variable is missing.')


class ZeroDict(dict):

    def __getitem__(self, key):
        try:
            value = super(ZeroDict, self).__getitem__(key)
        except KeyError:
            value = 0
        return value



class Expression(Unicode):

    @staticmethod
    def decode(data):
        # Risque d'espaces insécables autour des guillemets
        # Ni upper() ni lower() !
        return Unicode.decode(data).replace(u' ', u' ').strip()


    @staticmethod
    def is_valid(value):
        vars = ZeroDict()
        vars['SI'] = SI
        try:
            eval(value, vars)
        except ZeroDivisionError:
            pass
        except Exception, err:
            # Let error raise with message
            raise
        return True



class ControlLevel(Enumerate):
    options = [
        {'name': '0', 'value': u"Informative"},
        {'name': '1', 'value': u"Warning"},
        {'name': '2', 'value': u"Error"}]


    @staticmethod
    def decode(data):
        return Enumerate.decode(data).strip()



class ControlsHandler(TableFile):
    record_properties = {'number': Unicode(mandatory=True,
            title=MSG(u"Number")),
        'title': Unicode(mandatory=True, title=MSG(u"Title")),
        'expression': Expression(mandatory=True, title=MSG(u"Expression")),
        'level': ControlLevel(mandatory=True, title=MSG(u"Level")),
        'variable': Variable(mandatory=True, title=MSG(u"Main Variable"))}



class Controls(Table):
    class_id = 'Controls'
    class_title = MSG(u"Controls")
    class_handler = ControlsHandler
    class_icon16 = 'icons/16x16/excel.png'
    class_icon48 = 'icons/48x48/excel.png'

    # To import from CSV
    columns = ['number', 'title', 'expression', 'level', 'variable']


    def _load_from_csv(self, body, columns):
        handler = self.handler
        handler.update_from_csv(body, columns)
        # Consistency check
        get_record_value = handler.get_record_value
        for lineno, record in enumerate(handler.get_records()):
            # Starting from 0 + header
            lineno += 2
            title = get_record_value(record, 'title').strip()
            if not title:
                raise ValueError, ERR_EMPTY_TITLE(line=lineno)
            expression = get_record_value(record, 'expression')
            if not expression:
                raise ValueError, ERR_EMPTY_EXPRESSION(line=lineno)
            try:
                Expression.is_valid(expression)
            except Exception, err:
                raise ValueError, ERR_BAD_EXPRESSION(line=lineno,
                        err=err)
            level = get_record_value(record, 'level')
            if not ControlLevel.is_valid(level):
                raise ValueError, ERR_BAD_LEVEL(line=lineno,
                        level=level)
            variable = get_record_value(record, 'variable')
            if not variable:
                raise ValueError, ERR_EMPTY_VARIABLE(line=lineno)


    def init_resource(self, body=None, filename=None, extension=None, **kw):
        super(Controls, self).init_resource(filename=filename,
                extension=extension, **kw)
        self._load_from_csv(body, self.columns)
