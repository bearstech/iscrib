# -*- coding: ISO-8859-1 -*-

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

