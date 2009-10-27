# -*- coding: UTF-8 -*-
# Copyright (C) 2006 Luis Belmar Letelier <luis@itaapy.com>
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

# Import from python
from datetime import date
from decimal import Decimal as dec, InvalidOperation

# Import from itools
from itools.datatypes import DataType, Unicode as BaseUnicode, Enumerate
from itools.handlers import checkid


class DateLitterale(DataType):
    weekdays = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi',
                'dimanche']
    # begin at index 1
    months = ['', 'janvier', 'février', 'mars', 'avril', 'mai', 'juin',
              'juillet', 'août', 'septembre', 'octobre', 'novembre',
              'décembre']


    @classmethod
    def encode(cls, value):
        if not value:
            return ''
        return (value.strftime("# %d & %Y")
                     .replace('#', cls.weekdays[value.weekday()])
                     .replace('&', cls.months[value.month]))



class Numeric(DataType):
    """All arithmetical operations."""
    default = '0'


    @classmethod
    def get_default(cls):
        return cls.decode(cls.default)


    def __new__(cls, *args, **kw):
        return object.__new__(cls)


    def __init__(self, **kw):
        object.__init__(self)
        for key, value in kw.iteritems():
            setattr(self, key, value)


    def __int__(self):
        return int(self.value)


    def __float__(self):
        return float(self.value)


    def __str__(self):
        return self.encode(self.value)


    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.value)


    def __add__(self, right):
        if self.value is None:
            # NC + right = NC
            return self.__class__('NC')
        if isinstance(right, Numeric):
            right = right.value
            if right is None:
                # left + NC = NC
                return self.__class__('NC')
        elif right == '':
            right = 0
        left = dec(str(self.value))
        right = dec(str(right))
        # <type> + <type>
        return self.__class__(left + right)

    __radd__ = __add__


    def __sub__(self, right):
        if self.value is None:
            # NC - right = NC
            return self.__class__('NC')
        if isinstance(right, Numeric):
            right = right.value
            if right is None:
                # left - NC = NC
                return self.__class__('NC')
        elif right == '':
            right = 0
        left = dec(str(self.value))
        right = dec(str(right))
        # <type> - <type>
        return self.__class__(left - right)


    def __rsub__(self, left):
        if self.value is None:
            # left - NC = NC
            return self.__class__('NC')
        if isinstance(left, Numeric):
            left = left.value
            if left is None:
                # NC - right = NC
                return self.__class__('NC')
        elif left == '':
            left = 0
        left = dec(str(left))
        right = dec(str(self.value))
        # <type> - <type>
        return self.__class__(left - right)



    def __mul__(self, right):
        if self.value is None:
            # NC * right = NC
            return self.__class__('NC')
        if isinstance(right, Numeric):
            right = right.value
            if right is None:
                # left * NC = NC
                return self.__class__('NC')
        elif right == '':
            right = 0
        left = dec(str(self.value))
        right = dec(str(right))
        # <type> * <type>
        return self.__class__(left * right)

    __rmul__ = __mul__


    def __div__(self, right):
        if self.value is None:
            # NC / right = NC
            return self.__class__('NC')
        if isinstance(right, Numeric):
            right = right.value
            if right is None:
                # left / NC = NC
                return self.__class__('NC')
        elif right == '':
            right = 0
        if right == 0:
            # Pas de division par zéro !
            return self.__class__(0)
        left = dec(str(self.value))
        right = dec(str(right))
        # <type> / <type>
        return self.__class__(left / right)


    def __rdiv__(self, left):
        if self.value is None:
            # left / NC = NC
            return self.__class__('NC')
        if isinstance(left, Numeric):
            left = left.value
            if left is None:
                # NC / right = NC
                return self.__class__('NC')
        elif left == '':
            left = 0
        if left == 0:
            # Pas de division par zéro !
            return self.__class__(0)
        left = dec(str(left))
        right = dec(str(self.value))
        # <type> / <type>
        return self.__class__(left / right)


    def __gt__(self, right):
        left = self.value
        if isinstance(right, Numeric):
            right = right.value
        if right is 'NC' or right is None:
            # left > NC
            return True
        elif left is None:
            # NC > right
            return True
        # <type> > <type>
        return left > right


    def __ge__(self, right):
        left = self.value
        if isinstance(right, Numeric):
            right = right.value
        if right is 'NC' or right is None:
            # left >= NC
            return True
        elif left is None:
            # NC >= right
            return True
        # <type> >= <type>
        return left >= right


    def __lt__(self, right):
        left = self.value
        if isinstance(right, Numeric):
            right = right.value
        if right is 'NC' or right is None:
            # left < NC
            return True
        elif left is None:
            # NC < right
            return True
        # <type> < <type>
        return left < right


    def __le__(self, right):
        left = self.value
        if isinstance(right, Numeric):
            right = right.value
        if right is 'NC' or right is None:
            # left <= NC
            return True
        elif left is None:
            # NC <= right
            return True
        # <type> <= <type>
        return left <= right


    def __eq__(self, right):
        left = self.value
        if isinstance(right, Numeric):
            right = right.value
        if left is None:
            # NC == right
            return True
        elif right == 'NC' or right is None:
            # <type> == NC
            return True
        # <type> == <type>
        return left == right


    def __ne__(self, right):
        left = self.value
        if isinstance(right, Numeric):
            right = right.value
        if left is None:
            # NC != right
            return right != 'NC' and right is not None
        elif right == 'NC' or right is None:
            # <type> != NC
            return True
        # <type> != <type>
        return left != right


    def __cmp__(self, right):
        # Toutes les combinaisons ont été épuisées
        raise NotImplementedError


    @classmethod
    def decode(cls, data):
        if isinstance(data, Numeric):
            return data
        elif data is None or str(data).upper() == 'NC':
            return cls('NC')
        return cls(data)


    @staticmethod
    def encode(value):
        if isinstance(value, Numeric):
            value = value.value
        if value is None:
            return 'NC'
        return str(value)



class NumDecimal(Numeric):

    def __init__(self, value=None, **kw):
        Numeric.__init__(self, **kw)
        if value is not None:
            if value == 'NC':
                value = None
            elif type(value) is dec:
                pass
            elif value == '':
                value = dec(0)
            else:
                if type(value) is str:
                    value = value.replace(',', '.')
                value = dec(str(value))
        self.value = value


    @staticmethod
    def is_valid(data, repr):
        if data.upper() == 'NC':
            return True
        try:
            dec(str(data))
        except InvalidOperation:
            return False

        return True


    def get_sql_schema(self):
        # ASSUME precision == 2
        repr = self.repr - 3
        return "DECIMAL(%s,2) default 0.0" % repr


    @classmethod
    def encode_sql(cls, value):
        if isinstance(value, NumDecimal):
            if value.value is None:
                return 'NULL'
        return cls.encode(value)



class NumInteger(Numeric):

    def __init__(self, value=None, **kw):
        Numeric.__init__(self, **kw)
        if value is not None:
            if value == 'NC':
                value = None
            elif type(value) is int:
                pass
            elif value == '':
                value = 0
            else:
                if type(value) is str:
                    value = ''.join([x for x in value if x.isdigit()])
                value = int(value)
        self.value = value


    @staticmethod
    def is_valid(data, repr):
        if data.upper() == 'NC':
            return True
        try:
            int(data)
        except ValueError:
            return False

        return True


    def get_sql_schema(self):
        return "INT(%s) default 0" % self.repr


    @classmethod
    def encode_sql(cls, value):
        if isinstance(value, NumInteger):
            if value.value is None:
                return 'NULL'
        return cls.encode(value)



class NumTime(Numeric):

    def __init__(self, value=None, **kw):
        Numeric.__init__(self, **kw)
        if value is not None:
            if value == 'NC':
                value = None
            elif type(value) is int:
                pass
            elif value == '':
                value = 0
            else:
                value = int(value)
        self.value = value


    @classmethod
    def decode(cls, data):
        if data is None or str(data).upper() == 'NC':
            return cls('NC')
        data = str(data).strip()
        if data == '':
            return ''
        elif ':' in data:
            hours, minutes = data.split(':')
        else:
            hours = int(data)
            minutes = 0

        return cls(int(hours) * 60 + int(minutes))


    @staticmethod
    def encode(value):
        if isinstance(value, NumTime):
            value = value.value
        if value is None:
            return 'NC'
        elif value == '':
            return ''

        return '%03d:%02d' % (value / 60, value % 60)


    @staticmethod
    def is_valid(data, repr):
        if data == '' or data.upper() == 'NC':
            return True
        if data.count(':') > 1:
            return False
        for x in data.split(':'):
            try:
                int(x)
            except ValueError:
                return False

        return True


    def get_sql_schema(self):
        return "CHAR(6) default '000:00'"


    @classmethod
    def encode_sql(cls, value):
        if isinstance(value, NumTime):
            if value.value is None:
                return 'NULL'
        return "'%s'" % cls.encode(value)



class NumShortTime(NumTime):

    @staticmethod
    def encode(value):
        data = NumTime.encode(value)
        if data == '' or data == 'NC':
            return data

        return data[1:]


    def get_sql_schema(self):
        return "CHAR(5) default '00:00'"



class NumDate(DataType):

    def __init__(self, value=None, **kw):
        DataType.__init__(self, **kw)
        if value is not None:
            if value == 'NC':
                value = None
            elif type(value) is date:
                pass
            elif value == '':
                pass
            else:
                parts = value.split('/')
                if len(parts) == 2:
                    # Support ShortDate
                    parts.insert(0, 1)
                j, m, a = parts
                value = date(int(a), int(m), int(j))
        self.value = value


    def __str__(self):
        return self.encode(self.value)


    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.value)


    def __cmp__(self, right):
        left = self.value
        if isinstance(right, Numeric):
            right = right.value
        if right is 'NC' or right is None:
            if left is None:
                # NC == NC
                return 0
            # left (!NC) > NC
            return 1
        elif left is None:
            # NC < right (!NC)
            return -1
        # cmp(left (!NC), right (!NC)
        return cmp(left, right)


    @classmethod
    def decode(cls, data):
        if data is None or str(data).upper() == 'NC':
            return cls('NC')
        parts = data.split('/')
        if len(parts) == 3:
            pass
        elif len(parts) == 2:
            parts.insert(0, '1')
        else:
            return data
        for i in range(3):
            try:
                parts[i] = int(parts[i])
            except ValueError:
                return data
        j, m, a = parts
        if a < 10:
            a += 2000
        if a < 100:
            a += 1900

        try:
            value = cls(date(a, m, j))
        except ValueError:
            value = data
        return value


    @staticmethod
    def encode(value):
        if isinstance(value, NumDate):
            value = value.value
        if value is None:
            return 'NC'
        elif type(value) is str:
            return value

        return value.strftime('%d/%m/%Y')


    @staticmethod
    def is_valid(data, repr):
        if data.upper() == 'NC':
            return True
        if data.count('/') != 2:
            return False
        for x in data.split('/'):
            try:
                int(x)
            except ValueError:
                return False
        j, m, a = data.split('/')
        try:
            date(int(a), int(m), int(j))
        except ValueError:
            return False

        return True


    def get_sql_schema(self):
        return "CHAR(10) NOT NULL default ''"


    @classmethod
    def encode_sql(cls, value):
        return "'%s'" % cls.encode(value)



class NumShortDate(NumDate):

    @staticmethod
    def encode(value):
        data = NumDate.encode(value)
        if data == '' or data == 'NC':
            return data

        return data[3:]


    @staticmethod
    def is_valid(data, repr):
        if data.upper() == 'NC':
            return True
        if data.count('/') != 1:
            return False
        for x in data.split('/'):
            try:
                int(x)
            except ValueError:
                return False
        m, a = data.split('/')
        try:
            date(int(a), int(m), 1)
        except ValueError:
            return False

        return True


    def get_sql_schema(self):
        return "CHAR(7) NOT NULL default ''"



class Unicode(BaseUnicode):
    default = ''


    @staticmethod
    def is_valid(value, repr):
        try:
            unicode(value, 'utf8')
        except UnicodeDecodeError:
            return False
        return True


    def get_sql_schema(self):
        return "VARCHAR(%s) NOT NULL default ''" % self.repr


    @classmethod
    def encode_sql(cls, value):
        return '"%s"' % cls.encode(value).replace('"', r'\"')



class Text(Unicode):

    @staticmethod
    def decode(data):
        data = Unicode.decode(data)
        return data.replace(u'\\r\\n', u'\r\n')


    @staticmethod
    def encode(value):
        value = Unicode.encode(value)
        return value.replace('\r\n', '\\r\\n')



class EnumBoolean(Enumerate):
    options = [
        {'name': '1', 'value': u"Oui"},
        {'name': '2', 'value': u"Non"},
    ]


    @staticmethod
    def is_valid(value, repr):
        return value in (True, False, '1', '2')


    @staticmethod
    def decode(data):
        if type(data) is bool:
            return data
        # 0001892: '0' est l'ancienne représentation de False
        elif data in (None, '', '0', '2'):
            return False
        elif data == '1':
            return True
        raise ValueError, str(data)



    @staticmethod
    def encode(value):
        if value in (True, '1'):
            return '1'
        elif value in (False, None, '', '0', '2'):
            return '2'
        raise ValueError, str(value)


    def get_sql_schema(self):
        return "TINYINT NOT NULL default 0"


    @classmethod
    def encode_sql(cls, value):
        if value is None:
            value = False
        return cls.encode(value)



class Digit(DataType):

    @staticmethod
    def encode(value):
        if value is None:
            return 'NC'
        return ''.join([x for x in value if x.isdigit()])


    @staticmethod
    def decode(data):
        if data is None or str(data).upper() == 'NC':
            return None
        return ''.join([x for x in data if x.isdigit()])


    @staticmethod
    def is_valid(data, repr):
        return data.isdigit() if len(data) == repr else data == ''


    def get_sql_schema(self):
        return "CHAR(%s) NOT NULL default ''" % self.repr


    @classmethod
    def encode_sql(cls, value):
        return "'%s'" % cls.encode(value)



class SqlEnumerate(Enumerate):

    @classmethod
    def is_valid(cls, data, repr):
        return data in [x['name'] for x in cls.options]


    def get_sql_schema(self):
        return "INT(3) default NULL"


    @classmethod
    def encode_sql(cls, value):
        if value is None or value == '':
            return 'NULL'
        return cls.encode(value)



class Departements(Enumerate):
    options = [
        {'name': '1', 'value': "Ain"},
        {'name': '2', 'value': "Aisne"},
        {'name': '3', 'value': "Allier"},
        {'name': '4', 'value': "Alpes-de-Haute-Provence"},
        {'name': '5', 'value': "Hautes-Alpes"},
        {'name': '6', 'value': "Alpes maritimes"},
        {'name': '7', 'value': "Ardèche"},
        {'name': '8', 'value': "Ardennes"},
        {'name': '9', 'value': "Ariège"},
        {'name': '10', 'value': "Aube"},
        {'name': '11', 'value': "Aude"},
        {'name': '12', 'value': "Aveyron"},
        {'name': '13', 'value': "Bouches-du-Rhône"},
        {'name': '14', 'value': "Calvados"},
        {'name': '15', 'value': "Cantal"},
        {'name': '16', 'value': "Charente"},
        {'name': '17', 'value': "Charente-Maritime"},
        {'name': '18', 'value': "Cher"},
        {'name': '19', 'value': "Corrèze"},
        {'name': '2A', 'value': "Corse-du-Sud"},
        {'name': '2B', 'value': "Haute-Corse"},
        {'name': '21', 'value': "Côte-d'Or"},
        {'name': '22', 'value': "Côtes-d'Armor"},
        {'name': '23', 'value': "Creuse"},
        {'name': '24', 'value': "Dordogne"},
        {'name': '25', 'value': "Doubs"},
        {'name': '26', 'value': "Drôme"},
        {'name': '27', 'value': "Eure"},
        {'name': '28', 'value': "Eure-et-Loir"},
        {'name': '29', 'value': "Finistère"},
        {'name': '30', 'value': "Gard"},
        {'name': '31', 'value': "Haute-Garonne"},
        {'name': '32', 'value': "Gers"},
        {'name': '33', 'value': "Gironde"},
        {'name': '34', 'value': "Hérault"},
        {'name': '35', 'value': "Ille-et-Vilaine"},
        {'name': '36', 'value': "Indre"},
        {'name': '37', 'value': "Indre-et-Loire"},
        {'name': '38', 'value': "Isère"},
        {'name': '39', 'value': "Jura"},
        {'name': '40', 'value': "Landes"},
        {'name': '41', 'value': "Loir-et-Cher"},
        {'name': '42', 'value': "Loire"},
        {'name': '43', 'value': "Haute-Loire"},
        {'name': '44', 'value': "Loire-Atlantique"},
        {'name': '45', 'value': "Loiret"},
        {'name': '46', 'value': "Lot"},
        {'name': '47', 'value': "Lot-et-Garonne"},
        {'name': '48', 'value': "Lozère"},
        {'name': '49', 'value': "Maine-et-Loire"},
        {'name': '50', 'value': "Manche"},
        {'name': '51', 'value': "Marne"},
        {'name': '52', 'value': "Haute-Marne"},
        {'name': '53', 'value': "Mayenne"},
        {'name': '54', 'value': "Meurthe-et-Moselle"},
        {'name': '55', 'value': "Meuse"},
        {'name': '56', 'value': "Morbihan"},
        {'name': '57', 'value': "Moselle"},
        {'name': '58', 'value': "Nièvre"},
        {'name': '59', 'value': "Nord"},
        {'name': '60', 'value': "Oise"},
        {'name': '61', 'value': "Orne"},
        {'name': '62', 'value': "Pas-de-Calais"},
        {'name': '63', 'value': "Puy-de-Dôme"},
        {'name': '64', 'value': "Pyrénées-Atlantiques"},
        {'name': '65', 'value': "Hautes-Pyrénées"},
        {'name': '66', 'value': "Pyrénées-Orientales"},
        {'name': '67', 'value': "Bas-Rhin"},
        {'name': '68', 'value': "Haut-Rhin"},
        {'name': '69', 'value': "Rhône"},
        {'name': '70', 'value': "Haute-Saône"},
        {'name': '71', 'value': "Saône-et-Loire"},
        {'name': '72', 'value': "Sarthe"},
        {'name': '73', 'value': "Savoie"},
        {'name': '74', 'value': "Haute-Savoie"},
        {'name': '75', 'value': "Paris"},
        {'name': '76', 'value': "Seine-Maritime"},
        {'name': '77', 'value': "Seine-et-Marne"},
        {'name': '78', 'value': "Yvelines"},
        {'name': '79', 'value': "Deux-Sèvres"},
        {'name': '80', 'value': "Somme"},
        {'name': '81', 'value': "Tarn"},
        {'name': '82', 'value': "Tarn-et-Garonne"},
        {'name': '83', 'value': "Var"},
        {'name': '84', 'value': "Vaucluse"},
        {'name': '85', 'value': "Vendée"},
        {'name': '86', 'value': "Vienne"},
        {'name': '87', 'value': "Haute-Vienne"},
        {'name': '88', 'value': "Vosges"},
        {'name': '89', 'value': "Yonne"},
        {'name': '90', 'value': "Territoire de Belfort"},
        {'name': '91', 'value': "Essonne"},
        {'name': '92', 'value': "Hauts-de-Seine"},
        {'name': '93', 'value': "Seine-Saint-Denis"},
        {'name': '94', 'value': "Val-de-Marne"},
        {'name': '95', 'value': "Val-d'Oise"},
        {'name': '971', 'value': "Guadeloupe"},
        {'name': '972', 'value': "Martinique"},
        {'name': '973', 'value': "Guyane"},
        {'name': '974', 'value': "La Réunion"},
        {'name': '975', 'value': "Saint-Pierre-et-Miquelon"},
        # FIXME 976
        {'name': '985', 'value': "Mayotte"},
        {'name': '988', 'value': "Nouvelle-Calédonie"}]



class WorkflowState(Enumerate):
    options = [
        {'name': 'vide', 'value': u"Vide"},
        {'name': 'en_cours', 'value': u"En cours"},
        {'name': 'envoye', 'value': u"Envoyé"},
        {'name': 'exporte', 'value': u"Exporté"},
        {'name': 'modifie', 'value': u"Modifié après export"}]



def make_enumerate(raw):
    options = []
    for value in raw.strip().split('/'):
        value = unicode(value.strip(), 'utf8')
        options.append({'name': checkid(value),
                        'value': value})
    return SqlEnumerate(options=options)
