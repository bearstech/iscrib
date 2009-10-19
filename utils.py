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

# Import from itools
from itools.csv import CSVFile
from itools.datatypes import String, Unicode, Integer

# Import from ikaaro
from ikaaro.server import get_config


MSG_NO_MYSQL = u"La connexion à MySql ne s'est pas faite"
MSG_NO_ADRESSE = u"La bibliothèque n'existe pas dans la base SQL : %r"


def get_config_data(context):
    server = context.server
    target = server.target
    return get_config(target)



def get_connection(context, **kw):
    config = get_config_data(context)
    host = config.get_value('sql_host')
    db = config.get_value('sql_database')
    user = config.get_value('sql_user')
    passwd = config.get_value('sql_passwd')
    port = config.get_value('sql_port', type=Integer)
    return connect(db=db, host=host, port=port, user=user, passwd=passwd)


def SI(condition, iftrue, iffalse=True):
    if condition:
        value = iftrue
    else:
        value = iffalse
    return value



def parse_control(title):
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



class UsersCSV(CSVFile):

    schema = {'annee': Unicode,
              'code': Integer,
              'categorie': String(is_indexed=True),
              'nomecole': Unicode,
              'departement': String, # Corse 2A et 2B
              'id': Integer,
              'mel': String,
              'utilisateur': String,
              'motdepasse': String}
    columns = ['annee', 'code', 'categorie', 'nomecole', 'departement', 'id',
               'utilisateur', 'motdepasse']
    skip_header = True
