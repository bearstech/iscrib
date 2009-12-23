# -*- coding: UTF-8 -*-
# Copyright (C) 2006 Luis Belmar Letelier <luis@itaapy.com>
# Copyright (C) 2008 Hervé Cauwelier <herve@itaapy.com>
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

# Import from mysql
from MySQLdb import connect
from MySQLdb.cursors import DictCursor

# Import from itools
from itools.core import merge_dicts
from itools.datatypes import Integer, String

# Import from ikaaro
from ikaaro.config import ServerConfig


class ScribServerConfig(ServerConfig):
    schema = merge_dicts(ServerConfig.schema, **{
            'sql-host': String,
            'sql-port': Integer,
            'sql-db': String,
            'sql-user': String,
            'sql-passwd': String})



def get_config(context=None, target=None):
    if target is None:
        target = context.server.target
    return ScribServerConfig('%s/config.conf' % target)



def get_connection(context=None, target=None):
    config = get_config(context=context, target=target)
    kw = {}
    for arg in ('host', 'port', 'db', 'user', 'passwd'):
        value = config.get_value('sql-%s' % arg)
        if value is None:
            raise ValueError, "%s: sql-%s undefined" % (config.uri, arg)
        kw[arg] = value
    return connect(**kw)



def get_adresse(code_ua, table, context=None, target=None):
    connection = get_connection(context=context, target=target)
    cursor = connection.cursor(DictCursor)
    cursor.execute('select * from %s where code_ua=%s' % (table, code_ua))
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    if not len(results):
        raise KeyError, "pas de code_ua '%s' dans '%s'" % (code_ua, table)
    adresse = results[0]
    for key, value in adresse.iteritems():
        if value is None:
            adresse[key] = ''
    return adresse



def SI(condition, iftrue, iffalse=True):
    if condition:
        value = iftrue
    else:
        value = iffalse
    return value



def parse_control(title):
    # FIXME documenter...
    generator = enumerate(title)
    end = 0
    for start, char in generator:
        if char == '[':
            yield False, title[end:start+1]
            for end, char2 in generator:
                if char2 == ']':
                    yield True, title[start+1:end]
                    break
    yield False, title[end:]
