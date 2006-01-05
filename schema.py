# -*- coding: ISO-8859-1 -*-

# Import from Python 
from pprint import pprint, pformat

##############################################################################
# Controles 
##############################################################################


def sum2controle(schema=None):
    """
    strucutre of controles : key, text, expr1, expr2, expr3
    with 'A16 = A11+A12+A13+A14+A15'
    we make :
    ('a_name_whatever we want2', 
     u"A16 [%s]  = A11+A12+A13+A14+A15 [%s]",
     'A16',
     'A11+A12+A13+A14+A15',
     'A16 == A11+A12+A13+A14+A15')
    
    strucutre of controles : key, text, expr1, expr2, expr3
    """ 

    all_sums = []
    for key, value in schema.items():
        if len(value) != 3:
            pass
        else:
            key_type, default, kw = value
            sums = kw.get('sum', None)
            if not sums:
                pass
            else:
                key = key.split('field')[-1]
                sums = [x.split('field')[-1] for x in sums]
                all_sums.append((key, key_type, default, sums))
    
    all_sums_controles = []
    for key, key_type, default, sums in all_sums:
        res = []
        sums_string = ' + '.join(sums)
        res.append('sum')
        text = u'%s [%%s] = %s [%%s]' % (key, sums_string)
        res.append(text)
        res.append(key)
        res.append(sums_string)
        res.append('%s == %s' %  (key, sums_string))
        res.append([key])
        res.append(sums)
        res = tuple(res)
        all_sums_controles.append(res)
    return all_sums_controles


##############################################################################
# Check that all keys are in schema
##############################################################################

def checkBib(bib_type='BM', max=30, schema=None):
    Bibkeys = schema.keys()
    accu = ''
    for i in range(max):
      FormBib = ('Form%s_report%s_autogen.xml' % (bib_type, i), 
                'Form%s_report%s.xml' % (bib_type, i))
      try:
          accu += open('ui/%s' % FormBib[0]).read()
          print 'in try', FormBib[0]
      except:
          accu += open('ui/%s' % FormBib[1]).read()
          print 'in except', FormBib[1]
    lines = accu.split('\n') 

    xmlBib = []
    for line in lines:
       m = re.search(r'name="(.*?)"', line)
       if m: 
           f = m.groups()
           for it in f:
               xmlBib.append(it)

    xmlBib = sets.Set(xmlBib)
    Bibkeys = sets.Set(Bibkeys)
    intersec = Bibkeys.intersection(xmlBib) 
    print '\n#### in xml but not in schema'
    pprint (list(xmlBib.difference(intersec)))
    print '\n#### in schema but not in xml'
    pprint (list(Bibkeys.difference(intersec)))


