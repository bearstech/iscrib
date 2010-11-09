# -*- coding: UTF-8 -*-
# Copyright (C) 2006 Luis Belmar Letelier <luis@itaapy.com>
# Copyright (C) 2006, 2008-2010 Hervé Cauwelier <herve@itaapy.com>
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
from itools.gettext import MSG


def quote_integer(data):
    data = unicode(data, 'utf8')
    # FIXME restore unicode
    return data.replace('"', '\\"').replace("'", "\\'")


def quote_string(data):
    data = unicode(data, 'utf8')
    # FIXME restore unicode
    return '"%s"' % data.replace('"', '\\"').replace("'", "\\'")



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
                return u"null"
        return quote_integer(cls.encode(value))


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


    @classmethod
    def sum(cls, formula, schema, fields):
        sum = cls.decode(0)
        for term in formula.split('+'):
            term = term.strip()
            data = fields.get(term)
            if not data:
                return None
            if str(data).upper() == 'NC':
                return 'NC'
            datatype = schema[term]
            try:
                value = datatype.decode(data)
            except Exception:
                return None
            sum += value
        return sum



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


    def round(self, digits=2):
        value = self.value
        if value is None or type(value) is str:
            return value
        places = dec('10') ** -digits
        return value.quantize(places)


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



class NumDate(Numeric):

    def __init__(self, value=None, **kw):
        Numeric.__init__(self, **kw)
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


    @classmethod
    def encode_sql(cls, value):
        if isinstance(value, cls):
            if value.value is None or value.value == '':
                return u"null"
        return quote_string(cls.encode(value))



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
            return u"null"
        return quote_string(cls.encode(value))



class Text(Unicode):

    @staticmethod
    def decode(data, encoding='UTF-8'):
        value = Unicode.decode(data, encoding=encoding)
        # Restaure les retours chariot
        # FIXME restore unicode
        return value.replace(u'\\r\\n', u'\r\n')


    @staticmethod
    def encode(value, encoding='UTF-8'):
        value = Unicode.encode(value, encoding=encoding)
        # Stocke tout sur une ligne
        # FIXME restore unicode
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
            return u"null"
        return quote_integer(cls.encode(value))



class SqlEnumerate(Enumerate):
    default = ''


    @classmethod
    def get_sql_schema(cls):
        return "varchar(20) default null"


    @classmethod
    def encode_sql(cls, value):
        if value is None or value == '':
            return u"null"
        return quote_string(cls.encode(value))


    @classmethod
    def get_values(cls, value):
        return (cls.get_value(value, value) for value in value)



class EnumCV(SqlEnumerate):
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



class Subscription(Enumerate):
    options = [
            {'name': 'restricted',
                'value': MSG(u"Restricted (users must be subscribed)")},
            {'name': 'open',
                'value': MSG(u"Open (accounts are created on demand)")}]


class Nil(DataType):

    @staticmethod
    def encode(value):
        return value
