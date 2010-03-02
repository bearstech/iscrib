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
from itools.csv import CSVFile
from itools.datatypes import Integer, String, Unicode
from itools.web import ERROR

# Import from ikaaro
from ikaaro.config import ServerConfig


class ProgressMeter(object):
    last_percent = 0

    def __init__(self, max):
        self.max = max


    def show(self, i):
        percent = i * 100 / self.max
        if percent % 10 == 0 and percent != self.last_percent:
            print "  %s %%" % percent
            self.last_percent = percent



class UsersCSV(CSVFile):
    skip_header = True
    schema = {'annee': Unicode,
              'code_ua': Integer,
              'categorie': String(is_indexed=True),
              'nom': Unicode,
              'departement': String, # Corse « 2A » et « 2B »
              'id': String} # Corse « 2A004 »
    columns = ['annee', 'code_ua', 'categorie', 'nom', 'departement', 'id']



class ScribServerConfig(ServerConfig):
    schema = merge_dicts(ServerConfig.schema, **{
            'sql-host': String,
            'sql-port': Integer,
            'sql-db': String,
            'sql-user': String,
            'sql-passwd': String})



def get_config(context=None, target=None):
    assert context or target
    if target is None:
        target = context.server.target
    return ScribServerConfig('%s/config.conf' % target)



def get_connection(context=None, target=None):
    assert context or target
    config = get_config(context=context, target=target)
    kw = {}
    for arg in ('host', 'port', 'db', 'user', 'passwd'):
        value = config.get_value('sql-%s' % arg)
        if value is None:
            raise ValueError, "%s: sql-%s undefined" % (config.uri, arg)
        kw[arg] = value
    connection = connect(**kw)
    encoding = config.get_value('sql-encoding', default='latin1')
    connection.scrib_encoding = encoding
    return connection



def execute(query, context):
    try:
        connection = get_connection(context)
        cursor = connection.cursor()
        cursor.execute(query)
        # 2014 "Commands out of sync; you can't run this command now"
        cursor.close()
        cursor = connection.cursor()
        cursor.execute('commit')
    except Exception, e:
        context.commit = False
        context.message = ERROR(unicode(str(e), 'utf8'))
        print "query", query
        print "*" * 78
        raise
    finally:
        cursor.close()
        connection.close()



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
    encoding = connection.scrib_encoding
    for new, old in [('A101', 'libelle1'), ('A102', 'libelle2'),
            ('A103', 'local'), ('A104', 'voie_num'), ('A105', 'voie_type'),
            ('A106', 'voie_nom'), ('A107', 'CPBIBLIO'), ('A108', 'ville'),
            ('A109', 'CEDEXB'), ('A110', 'DIRECTEU'), ('A111', 'st_dir'),
            ('A112', 'TELE'), ('A113', 'FAX'), ('A115', 'WWW')]:
        adresse[new] = unicode(adresse.pop(old), encoding).encode('utf8')
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
