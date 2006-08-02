# -*- coding: UTF-8 -*-
# Copyright (C) 2004 Luis Belmar Letelier <luis@itaapy.com>
# Copyright (C) 2006 Hervé Cauwelier <herve@itaapy.com>
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

# Import from itools
from itools import get_abspath


path = get_abspath(globals(), 'input_data/init_BM.txt')
file = open(path)
bib_municipales = [ x.strip().split(';') for x in file.readlines() ]
print 'len', len(bib_municipales)
bib_municipales.sort()
bibs = {}
for x in bib_municipales:
    bibs[x[0]] = {'name': unicode(x[1], 'iso8859-1'),
                  'dep':x[2], 
                  'id':x[3],
                  'code': x[0]}

def get_BMs():
    return bibs


def get_deps():
    path = get_abspath(globals(), 'input_data/init_BDP.txt')
    file = open(path)
    depts = [ x.strip().split(';') for x in file.readlines() ]
    depts.sort()
    departements = {}
    for x in depts:
        departements[x[0]] = { 'name': unicode(x[1], 'iso8859-1'), 
                               'code': x[0]} 
    return departements

