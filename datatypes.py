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
from itools.datatypes.primitive import enumerate_get_namespace
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



class Numeric(object):
    """All arithmetical operations."""
    default = ''


    ########################################################################
    # DataType API
    @classmethod
    def get_default(cls):
        return cls.decode(cls.default)


    @classmethod
    def is_valid(cls, data):
        try:
            cls(data)
        except Exception:
            return False
        return True


    @classmethod
    def decode(cls, data):
        if isinstance(data, Numeric):
            return data
        elif data is None or str(data).upper() == 'NC':
            return cls('NC')
        return cls(data)


    @classmethod
    def encode(cls, value):
        if isinstance(value, Numeric):
            value = value.value
        if value is None:
            return 'NC'
        return str(value)


    @classmethod
    def encode_sql(cls, value):
        if isinstance(value, cls):
            if value.value is None or value.value == '':
                return 'null'
        return cls.encode(value)


    ########################################################################
    # Numeric API
    def __init__(self, **kw):
        object.__init__(self)
        for key, value in kw.iteritems():
            setattr(self, key, value)


    def __str__(self):
        return self.encode(self.value)


    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, vars(self))


    def __int__(self):
        return int(self.value)


    def __float__(self):
        return float(self.value)


    def __add__(self, right):
        if self.value is None:
            # NC + right = NC
            return self.__class__('NC')
        if isinstance(right, Numeric):
            right = right.value
            if right is None:
                # left + NC = NC
                return self.__class__('NC')
        # 0008535 pas de "elif" pour réévaluer right.value
        if right == '':
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
        if right == '':
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
        if right == '':
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
        if right == '':
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
        elif str(right).upper() == 'NC' or right is None:
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
            return str(right).upper() != 'NC' and right is not None
        elif str(right).upper() == 'NC' or right is None:
            # <type> != NC
            return True
        # <type> != <type>
        return left != right


    def __cmp__(self, right):
        # Toutes les combinaisons ont été épuisées
        raise NotImplementedError


    def __bool__(self):
        # FIXME seulement dans Python 3 ?
        raise NotImplementedError


    def __nonzero__(self):
        return bool(self.value)


    def __len__(self):
        raise NotImplementedError



class NumDecimal(Numeric):

    def __init__(self, value=None, **kw):
        Numeric.__init__(self, **kw)
        if value is not None:
            if str(value).upper() == 'NC':
                value = None
            elif type(value) is dec or value == '':
                pass
            else:
                point = value
                if type(value) is str:
                    point = value.replace(',', '.')
                try:
                    value = dec(str(point))
                except InvalidOperation:
                    pass
        self.value = value


    @staticmethod
    def is_valid(data):
        if data.upper() == 'NC':
            return True
        try:
            dec(str(data))
        except InvalidOperation:
            return False
        return True


    def get_sql_schema(self):
        return "decimal(%s) default 0.0" % self.representation



class NumInteger(Numeric):

    def __init__(self, value=None, **kw):
        Numeric.__init__(self, **kw)
        if value is not None:
            if str(value).upper() == 'NC':
                value = None
            elif type(value) is int or value == '':
                pass
            else:
                try:
                    value = int(value)
                except ValueError:
                    pass
        self.value = value


    @staticmethod
    def is_valid(data):
        if data.upper() == 'NC':
            return True
        try:
            int(data)
        except ValueError:
            return False
        return True


    def get_sql_schema(self):
        return "int(%s) default 0" % self.representation



class NumTime(Numeric):

    def __init__(self, value=None, **kw):
        Numeric.__init__(self, **kw)
        if value is not None:
            if str(value).upper() == 'NC':
                value = None
            elif type(value) is int or value == '':
                pass
            elif ':' in value:
                hours, minutes = value.split(':')
                value = int(hours) * 60 + int(minutes)
            else:
                value = int(value)
        self.value = value


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
    def is_valid(data):
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
        return "char(6) default '000:00'"



class NumShortTime(NumTime):

    @staticmethod
    def encode(value):
        data = NumTime.encode(value)
        if data == '' or data == 'NC':
            return data

        return data[1:]


    def get_sql_schema(self):
        return "char(5) default '00:00'"



class NumDate(DataType):

    def __init__(self, value=None, **kw):
        DataType.__init__(self, **kw)
        if value is not None:
            if str(value).upper() == 'NC':
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
                d, m, y = [int(x) for x in parts]
                # 2-digit year
                if y < 10:
                    y += 2000
                elif y < 100:
                    y += 1900
                value = date(y, m, d)
        self.value = value


    # XXX remove?
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
    def is_valid(data):
        if data.upper() == 'NC':
            return True
        if data.count('/') not in (1, 2):
            return False
        try:
            parts = [int(x) for x in data.split('/')]
        except ValueError:
            return False
        # NumShortDate
        if len(parts) == 2:
            parts.insert(0, 1)
        d, m, y = parts
        try:
            date(y, m, d)
        except ValueError:
            return False
        return True


    def get_sql_schema(self):
        return "char(10) default null"



class NumShortDate(NumDate):

    @staticmethod
    def encode(value):
        data = NumDate.encode(value)
        if data == '' or data == 'NC':
            return data

        return data[3:]


    def get_sql_schema(self):
        return "char(7) default null"



class NumDigit(Numeric):

    def __init__(self, value=None, **kw):
        Numeric.__init__(self, **kw)
        if value is not None:
            if str(value).upper() == 'NC':
                value = None
            else:
                pass
        self.value = value


    # FIXME should be classmethod
    def is_valid(self, data):
        representation = int(self.representation)
        return data.isdigit() if len(data) == representation else data == ''


    def get_sql_schema(self):
        return "char(%s) default null" % self.representation



class Unicode(BaseUnicode):
    default = ''


    @staticmethod
    def is_valid(data):
        try:
            unicode(data, 'utf8')
        except Exception:
            return False
        return True


    @classmethod
    def get_sql_schema(cls):
        return "varchar(%s) default null" % cls.representation


    @classmethod
    def encode_sql(cls, value):
        if value is None:
            return 'null'
        return '"%s"' % cls.encode(value).replace('"', r'\"')



class Text(Unicode):

    @staticmethod
    def decode(data):
        data = Unicode.decode(data)
        # Restaure les retours chariot
        return data.replace(u'\\r\\n', u'\r\n')


    @staticmethod
    def encode(value):
        value = Unicode.encode(value)
        # Stocke tout sur une ligne
        return value.replace('\r\n', '\\r\\n')



class EnumBoolean(Enumerate):
    default = ''
    options = [
        {'name': '1', 'value': u"Oui"},
        {'name': '2', 'value': u"Non"},
    ]


    @staticmethod
    def decode(data):
        if data == '1':
            return True
        elif data == '2':
            return False
        return data


    @staticmethod
    def encode(value):
        if value is True:
            return '1'
        elif value is False:
            return '2'
        return value


    @classmethod
    def get_sql_schema(cls):
        return "tinyint default null"


    @classmethod
    def encode_sql(cls, value):
        if value is None or value == '':
            return 'null'
        return cls.encode(value)



class EnumCV(Enumerate):
    default = ''
    counter = 1

    @classmethod
    def get_options(cls):
        yield {'name': str(cls.counter), 'value': unicode(cls.counter)}
        cls.counter += 1
        if cls.counter == 6:
            cls.counter = 7


    @classmethod
    def is_valid(cls, name):
        return name.isdigit()


    @classmethod
    def get_value(cls, name, default=None):
        return unicode(name)


    @classmethod
    def get_namespace(cls, name):
        options = list(cls.get_options())
        return enumerate_get_namespace(options, name)


    @classmethod
    def reset(cls):
        cls.counter = 1



class SqlEnumerate(Enumerate):
    default = ''


    @classmethod
    def get_sql_schema(cls):
        return "varchar(20) default null"


    @classmethod
    def encode_sql(cls, value):
        if value is None or value == '':
            return 'null'
        return "'%s'" % cls.encode(value)



class Departements(Enumerate):
    """Ce sont les codes Insee, pas les codes postaux.
    """
    options = [
        # 0008124 '1' -> '01'
        {'name': '01', 'value': "Ain"},
        {'name': '02', 'value': "Aisne"},
        {'name': '03', 'value': "Allier"},
        {'name': '04', 'value': "Alpes-de-Haute-Provence"},
        {'name': '05', 'value': "Hautes-Alpes"},
        {'name': '06', 'value': "Alpes maritimes"},
        {'name': '07', 'value': "Ardèche"},
        {'name': '08', 'value': "Ardennes"},
        {'name': '09', 'value': "Ariège"},
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
        {'name': '985', 'value': "Mayotte"},
        {'name': '988', 'value': "Nouvelle-Calédonie"}]


    @staticmethod
    def decode(data):
        if len(data) == 1:
            # "1" -> "01"
            return '0' + data
        return data



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



class Identifiant(DataType):

    @staticmethod
    def encode(value):
        if value is None:
            return ''
        return '%s%s' % value


    @staticmethod
    def decode(data):
        if data[:2] == 'BM':
            # ('BM', code_ua)
            return data[:2], int(data[2:])
        # ('BDP', departement)
        departement = data[3:]
        if len(departement) == 1:
            # "1" -> "01"
            departement = '0' + departement
        return data[:3], departement


    @staticmethod
    def is_valid(value):
        categorie, code_ua = value
        return categorie in ('BM', 'BDP')
