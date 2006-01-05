# -*- coding: ISO-8859-1 -*-

# Import from python
from decimal import Decimal as pythonDecimal

# Import from itools
from itools.handlers import IO


class Enumerate(IO.String):

    def get_namespace(cls, value):
        options = cls.get_options()
        for option in options:
            option['is_selected'] = option['id'] == value
        return options
    get_namespace = classmethod(get_namespace)



class EPCI_Statut(Enumerate):

    def get_options(cls):
        return [{'id': '0', 'label': ""},
                {'id': '1', 
                 'label': u"Commune dans un EPCI sans compétence bibliothèque"},
                {'id': '2', 
                 'label': u"Commune dans EPCI - bibliothèque non transférée"},
                {'id': '3', 
                 'label': u"Commune dans EPCI avec compétence biblio"},
                {'id': '4', 
                 'label': u"Ville-centre  d'un EPCI avec compétence biblio"},
                {'id': '5', 
                 'label': u"Commune dans syndicat intercommunal"},
                {'id': '6', 'label': "Autre"},
                ]
    get_options = classmethod(get_options)


##############################################################################
# Schema
##############################################################################

class Checkboxes(IO.String):
    pass 



class Decimal(object):

    def __init__(self, value='0'):
        if value == 'NC':
            pass
        elif isinstance(value, Decimal):
            pass
        else:
            value = pythonDecimal(value)
        self.value = value


    def __str__(self):
        return str(self.value)


    def __int__(self):
        return self.value


    def __float__(self):
        return float(self.value)


    def __add__(self, value):
        if isinstance(value, Decimal):
            value = value.value
        if self.value == 'NC' or value == 'NC':
            return Decimal('NC')
        return Decimal(self.value + value)


    def __div__(self, value):
        if isinstance(value, Integer) or isinstance(value, Decimal):
            value = value.value
        if self.value == 'NC' or value == 'NC':
            return Decimal('NC')
        return Decimal(self.value / value)


    def __cmp__(self, x):
        if isinstance(x, Integer) or isinstance(x, Decimal):
            if self.value == 'NC' or x.value == 'NC':
                return 0
            return cmp(self.value, x.value)
        return cmp(self.value, x)


    def encode(cls, value):
        if value is None:
            return ''
        return str(value)
    encode = classmethod(encode)


    def decode(cls, value):
        value = value.strip()
        if not value:
            return None
        return Decimal(value)
    decode = classmethod(decode)



class Integer(object):

    def __init__(self, value=0):
        if value == 'NC':
            pass
        elif isinstance(value, int):
            pass
        elif isinstance(value, str):
            value = int(str(value))
        else:
            value = int(value)
        self.value = value


    def __str__(self):
        return str(self.value)


    def __int__(self):
        return self.value


    def __float__(self):
        return float(self.value)


    def __add__(self, value):
        if isinstance(value, Integer):
            value = value.value
        if self.value == 'NC' or value == 'NC':
            return Integer('NC')
        return Integer(self.value + value)


    def __div__(self, value):
        if isinstance(value, Integer):
            value = value.value
        if self.value == 'NC' or value == 'NC':
            return Integer('NC')
        return Integer(self.value / value)


    def __cmp__(self, x):
        if isinstance(x, Integer):
            if self.value == 'NC' or x.value == 'NC':
                return 0
            return cmp(self.value, x.value)
        return cmp(self.value, x)


    def encode(cls, value):
        if value is None:
            return ''
        return str(value.value)
    encode = classmethod(encode)


    def decode(cls, value):
        value = value.strip()
        if not value:
            return None
        return Integer(value)
    decode = classmethod(decode)
