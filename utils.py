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

# Import from the Standard Library
from operator import itemgetter

# Import from mysql
from MySQLdb import connect
from MySQLdb.cursors import DictCursor

# Import from itools
from itools import get_abspath
from itools.datatypes import String, Unicode
from itools.csv import CSVFile

# Import from scrib
from scrib import config


MSG_NO_MYSQL = u"La connexion à MySql ne s'est pas faite"
MSG_NO_ADRESSE = u"La bibliothèque n'existe pas dans la base SQL : %r"


class AllBM(CSVFile):
    class_csv_guess = True
    schema = {'code': String(index='keyword'),
              'name': Unicode,
              'dep': String,
              'id': String}
    columns = ['code', 'name', 'dep', 'id']



class AllBDP(CSVFile):
    class_csv_guess = True
    # Utilise "text" comme insensible à la casse
    # Départements "2A" et "2B" mais objets "2a" et "2b"
    schema = {'code': String(index='text'),
              'name': Unicode}
    columns = ['code', 'name']



all_bm = AllBM(get_abspath(globals(), 'input_data/init_BM.txt'))
all_bdp = AllBDP(get_abspath(globals(), 'input_data/init_BDP.txt'))


SqlHost = config.get_value('SqlHost')
SqlDatabase = config.get_value('SqlDatabase')
SqlUser = config.get_value('SqlUser')
SqlPasswd = config.get_value('SqlPasswd')
SqlPort = config.get_value('SqlPort')


def get_bm(code):
    results = all_bm.search(code=code)
    if results:
        return all_bm.get_row(results[0])
    return None


def get_bdp(code):
    results = all_bdp.search(code=code)
    if results:
        return all_bdp.get_row(results[0])
    return None


def get_bdp_namespace(dep):
    departements = []
    for bib in all_bdp.get_rows():
        dep_key = bib.get_value('code')
        dep_name = bib.get_value('name').capitalize()
        departements.append({'name': '%s (%s)' % (dep_name, dep_key),
                             'value': dep_key,
                             'selected': dep_key == dep})
    departements.sort(key=itemgetter('value'))
    return departements


def get_checkbox_value(key, value):
    #len_choice = 2
    #if key == "G11":
    if key == "CV":
        len_choice = 15
    if key == "CZ":
        len_choice = 16
    elif key == "G11":
        len_choice = 7
    elif key == 'K3':
        len_choice = 4
    elif key == '13':
        len_choice = 2
    elif key == '14':
        len_choice = 4
    else:
        print 345, key, value
     
    new_values = choices = [ 'N' for item in range(len_choice)]
    values = value.split('##')
    for value in values:
        if value not in ('', None):
            i = int(value) - 1
            new_values[i] = 'O'

    value = ','.join(new_values)
    return value


def get_connection(**kw):
    return connect(db=SqlDatabase, host=SqlHost, port=int(SqlPort),
            user=SqlUser, passwd=SqlPasswd, **kw)


def get_adresse(query):
    """ Accès base adresse"""
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    if not len(results):
        #dummy = [''] * 99
        #dummy[17] = 0
        #return dummy
        raise ValueError, MSG_NO_ADRESSE % query
    results = results[0]
    adresse = []
    for val in results:
        if str(val) == 'None':
            adresse.append('')
        else:
            adresse.append(val)
    return adresse


def none2str(t):
    new = {}
    for k, v in t.items():
        if v is None:
            new[k] = ''
        else:
            new[k] = v
    return new


def bm_annexes(code_ua):
    connection = get_connection(cursorclass=DictCursor)
    cursor = connection.cursor()
    cursor.execute("select * from annexes  where code_ua = %s",
                   (code_ua,))
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    results = [none2str(d) for d in results]
    if not results:
        return {}
    return results[0]


def ua_epci(code_ua):
    connection = get_connection(cursorclass=DictCursor)
    cursor = connection.cursor()
    cursor.execute("select * from ua_epci where code_ua = %s",
                   (code_ua,))
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    results = [none2str(d) for d in results]
    if not results:
        return {}
    return results[0]


def make_msg(new_referer, notR, badT, badT_missing, badT_values):
    if notR:
        notR.sort()
        notR_missing = ['missing_' + x for x in notR]
        # convert to unicode so we can join them
        notR = [unicode(x, 'UTF-8') for x in notR]

        msg_notR = (u"Les rubriques suivantes ne sont pas "
                    u"renseignées : %s") % u', '.join(notR)

        dic = {}.fromkeys(notR_missing, '1')
        new_referer.query.clear()
        new_referer.query.update(dic)
    if badT:
        badT.sort()
        # convert to unicode so we can join them
        msg_badT = (u"Le type des rubriques suivantes n'est pas"
                    u" correct : %s" ) % u', '.join(badT)

        dic = {}.fromkeys(badT_missing, '1')
        new_referer.query.update(badT_values)
        new_referer.query.update(dic)
                
    if not (badT or notR):
        msg = u"Formulaire enregistré."
    elif badT and not notR:
        msg = msg_badT
    elif notR and not badT:
        msg = msg_notR
    else:
        msg = u'<br/>'.join([msg_notR,  msg_badT])

    return new_referer, msg


def reduce_generators(generators):
    # Migrating "reduce(lambda x,y: x+y, forms)"
    # More like linearizing
    for generator in generators:
        for item in generator:
            yield item
