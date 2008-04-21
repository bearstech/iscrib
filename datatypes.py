# -*- coding: UTF-8 -*-
# Copyright (C) 2004 Luis Belmar Letelier <luis@itaapy.com>
# Copyright (C) 2006-2008 Hervé Cauwelier <herve@itaapy.com>
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
from decimal import Decimal as dec

# Import from itools
from itools.datatypes import String, Enumerate


class EPCI_Statut(Enumerate):

    @classmethod
    def get_options(cls):
        return [{'name': '0', 'label': ""},
                {'name': '1',
                 'label': u"Commune dans un EPCI sans compétence bibliothèque"},
                {'name': '2',
                 'label': u"Commune dans EPCI - bibliothèque non transférée"},
                {'name': '3',
                 'label': u"Commune dans EPCI avec compétence biblio"},
                {'name': '4',
                 'label': u"Ville-centre  d'un EPCI avec compétence biblio"},
                {'name': '5',
                 'label': u"Commune dans syndicat intercommunal"},
                {'name': '6', 'label': "Autre"},
                ]


##############################################################################
# Schema
##############################################################################

class Checkboxes(String):
    pass



class Decimal(object):

    def __init__(self, value='0'):
        if value == 'NC':
            pass
        elif isinstance(value, Decimal):
            pass
        else:
            value = dec(value)
        self.value = value


    def __str__(self):
        return str(self.value)


    def __int__(self):
        if self.value == 'NC':
            return 'NC'
        return int(self.value)


    def __float__(self):
        if self.value == 'NC':
            return 'NC'
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


    @classmethod
    def encode(cls, value):
        if value is None:
            return ''
        return str(value)


    @classmethod
    def decode(cls, value):
        value = value.strip()
        if not value:
            return None
        return Decimal(value)



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
        if self.value == 'NC':
            return 'NC'
        return self.value


    def __float__(self):
        if self.value == 'NC':
            return 'NC'
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


    @classmethod
    def encode(cls, value):
        if value is None:
            return ''
        return str(value.value)


    @classmethod
    def decode(cls, value):
        value = value.strip()
        if not value:
            return None
        return Integer(value)


class WorkflowState(Enumerate):
    options = [{'name': 'vide', 'value': u"Vide"},
               {'name': 'en_cours', 'value': u"En cours"},
               {'name': 'termine', 'value': u"Terminé"},
               {'name': 'exporte', 'value': u"Exporté"},
               {'name': 'modifie', 'value': u"Modifié après export"}]
