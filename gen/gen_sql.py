# -*- coding: ISO-8859-1 -*-
# import from Python
import os

# import from itools
from itools.datatypes import String, Boolean, Unicode

# import from scrib
from datatypes import Checkboxes, Integer
from schema_bm import schema as schemaBM
from schema_bdp import schema as schemaBDP
from setup import setup
sql = setup.sql

class GenSql:
    """
    Use by the Makefile to create in the ./input_data"
    *.sql files who fill the scrib MySQL DB with the schema keys.
    this files will be called fill_bmYear_autogen.sql
    """

    def __init__(self, year, schema, type):
        """ years = ('04','05', '06', '07') """

        self.year = year
        # type is 'mb' or 'bdp'
        self.type = type

        # shema is schemaBM or schemaBDP
        self.schema = schema
        self.year_filename = 'fill_%s%s_autogen.sql' % (type, year)

        # make the documentation line
        line = 67 * '#' + '\n'
        # bash_cmd = "$ mysql -u scrib -p'Scrib-2005*' scrib <  %s"

        bash_cmd = ("$ mysql -u %(SqlUser)s -p'%(SqlPasswd)s' %(SqlDatabase)s"
                    " <  %(year_filename)s")

        bash_cmd = bash_cmd % {'SqlUser': sql.SqlUser,
                               'SqlPasswd': sql.SqlPasswd,
                               'SqlDatabase':sql.SqlDatabase,
                               'year_filename': self.year_filename}
        doc_header = '%s## %s\n%s' % (line, bash_cmd, line)

        # make the create table
        start_query = ("DROP TABLE IF EXISTS `%(type)s%(year)s`;\n"
                       "CREATE TABLE `%(type)s%(year)s` (\n"
                       "  `Code_UA` int default NULL, \n"
                       "  `dept` char(3) default NULL, \n"
                       "  `exer` int default NULL, \n") % { 'year' : year,
                                                            'type' : type}

        self.start_query = doc_header + start_query
        self.body_query = ""
        self.end_query = "\n);\n"

    def make_sql(self):
        year = self.year
        fields, queries = [], []
        keys = self.schema.keys()
        keys.sort()

        # create the body
        for field in keys:
            key_id = field[len('field'):].strip()
            if not key_id[0].isdigit():
                field_def = self.schema[field]
                field_key = field[len('field'):]
                ftype = field_def[0]
                fdefault = field_def[1]
                field_type = 'int'
                field_default = 'NULL'
                if ftype == String or ftype == Checkboxes or ftype == Unicode:
                    field_type = "varchar(100)"
                    field_default = "'%s'" % fdefault
                elif ftype == Integer:
                    field_type = 'int'
                    if fdefault == None:
                        field_default = "NULL"
                    else:
                        field_default = "'%s'" % str(fdefault)
                elif ftype == Boolean:
                    field_type = "char(1)"
                    field_default = "NULL"
                sql_field = "  `%s` %s default %s " % (field_key, field_type,
                                                     field_default)
                fields.append(sql_field)

        self.body_query = ',\n'.join(fields)

        # create the all query
        query = self.start_query + self.body_query + self.end_query

        # create the year.sql file
        path = os.getcwd()
        file_abs_path = '%s/input_data/%s' % (path, self.year_filename)
        print 'autogen SQL tables   ./input_data/%s' % self.year_filename
        open(file_abs_path, 'w').write(query)


create_DB = u"""
# installation  $ mysql -u root < create_scrib.SQL
# ou alors
#  $ mysql -u root
#  mysql> source create_scrib.SQL;

use mysql;
delete from mysql.user where user='%(SqlUser)s' and host='%(SqlHost)s';
delete from db where user='%(SqlUser)s' and host='%(SqlHost)s';

# Base de données: `%(SqlDatabase)s`
DROP DATABASE IF EXISTS %(SqlDatabase)s;
CREATE DATABASE  %(SqlDatabase)s;
USE  %(SqlDatabase)s;
GRANT ALL PRIVILEGES ON %(SqlDatabase)s.* to '%(SqlDatabase)s'@'%(SqlHost)s' identified by '%(SqlPasswd)s';

FLUSH PRIVILEGES;
"""

create_DB = create_DB % {'SqlUser':sql.SqlUser,
                         'SqlHost':sql.SqlHost,
                         'SqlDatabase':sql.SqlDatabase,
                         'SqlPasswd':sql.SqlPasswd}

# create the DB
path = os.getcwd()
file_abs_path = '%s/input_data/create_scrib.SQL' % path
print '\nCreate the init SQL DB   ./input_data/create_scrib.SQL'
open(file_abs_path, 'w').write(create_DB.encode('latin1'))
print ''


schemas = {
    'bm' : schemaBM,
    'bdp' : schemaBDP
    }
for type, schema in schemas.items():
  for year in ('04','05', '06', '07'):
      genSql = GenSql(year, schema, type)
      genSql.make_sql()
print ''
