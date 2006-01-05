# -*- coding: ISO-8859-1 -*-

# Import from Python 
from pprint import pprint, pformat

# Import from itools
from itools.handlers import IO

# Import from Culture 
from CultureTypes import Checkboxes, Integer, Decimal, EPCI_Statut
from schema import sum2controle, checkBib

schema = {'field1': (IO.Unicode, ''), 'field2': (IO.Unicode, ''),
          'field3': (IO.Unicode, ''), 'field4': (IO.Unicode, ''),
          'field5': (IO.Unicode, ''), 'field6': (IO.Unicode, ''),
          'field7': (IO.Unicode, ''), 'field8': (IO.Unicode, ''),
          'field9': (IO.Unicode, ''), 'field10': (IO.Unicode, ''),
          'field11': (IO.Unicode, ''),'field12': (IO.Unicode, ''),
          'field13': (Checkboxes, ''), 'field14': (Checkboxes, ''),
          'field15': (IO.Unicode, ''),
          ## A.1 DÉPENSES PROPRES A LA BIBLIOTHÈQUE
          'fieldA11': (Integer, None), 'fieldA12': (Integer, None),
          'fieldA13': (Integer, None), 'fieldA14': (Integer, None),
          'fieldA15': (Integer, None), 
          'fieldA16': (Integer, None, {'sum' : ('fieldA11', 'fieldA12', 
                                                'fieldA13', 'fieldA14',
                                                'fieldA15')}),
          #
          'fieldA21': (Integer, None), 'fieldA22': (Integer, None),
          'fieldA23': (Integer, None), 'fieldA24': (Integer, None),
          'fieldA25': (Integer, None, {'sum' : ('fieldA21', 'fieldA22', 
                                                'fieldA23', 'fieldA24',)}),
          #
          'fieldA31': (Integer, None), 'fieldA32': (Integer, None),
          'fieldA33': (Integer, None), 'fieldA34': (Integer, None),
          ## B  LOCAUX - VÉHICULES - ÉQUIPEMENT INFORMATIQUE 
          'fieldB11X': (Integer, None), 'fieldB11Y': (Integer, None),
          'fieldB11Z': (Integer, None, {'sum':('fieldB11X', 'fieldB11Y')}), 
          'fieldB12X': (Integer, None), 'fieldB12Y': (Integer, None), 
          'fieldB12Z': (Integer, None, {'sum':('fieldB12X', 'fieldB12Y')}), 
          'fieldB13X': (Integer, None), 'fieldB13Y': (Integer, None),
          'fieldB13Z': (Integer, None, {'sum':('fieldB13X', 'fieldB13Y')}), 
          'fieldB14': (IO.Boolean, None),
          'fieldB15': (Integer, None),
          #
          'fieldB21': (Integer, None), 'fieldB22': (Integer, None),
          'fieldB23': (Integer, None),
          #
          'fieldB31': (IO.Boolean, '', {'depend_field' : ('fieldB32',) }),
          'fieldB32': (IO.Unicode, ''),
          'fieldB33': (IO.Boolean, '', {'depend_field' : ('fieldB34',) }),
          'fieldB34': (Integer, None),
          'fieldB35': (IO.Boolean, '', {'depend_field' : ('fieldB36',) }),
          'fieldB36': (Integer, ''),
          'fieldB37X': (Integer, None), 'fieldB37Y': (Integer, None), 
          'fieldB38X': (Integer, None), 'fieldB38Y': (Integer, None), 
          'fieldB39X': (Integer, None, {'sum' : ('fieldB37X', 'fieldB38X',)}),
          'fieldB39Y': (Integer, None, {'sum' : ('fieldB37Y', 'fieldB38Y',)}),
          'fieldB40': (IO.Boolean, '', 
                       {'depend_field' : ('fieldB41','fieldB42') }),
          #
          'fieldB41': (IO.Boolean, ''), 'fieldB42': (IO.Boolean, ''),
          'fieldB43': (IO.Boolean, '', 
                       {'depend_field' : ('fieldB44','fieldB45', 
                                          'fieldB46', 'fieldB47') }),
          'fieldB44': (IO.Boolean, ''),
          'fieldB45': (IO.Boolean, ''), 'fieldB46': (IO.Boolean, ''),
          'fieldB47': (IO.Unicode, ''),
          # C  PERSONNEL EN POSTE AU 31 DECEMBRE 2003
          'fieldC11W': (Integer, None), 
          'fieldC11X': (Decimal, None),
          'fieldC11Y': (Integer, None), 
          'fieldCZ': (Checkboxes, ''),
          'fieldC12W': (Integer, None), 
          'fieldC12X' : (Decimal, None),
          'fieldC12Y': (Integer, None), 
          'fieldC13W': (Integer, None), 
          'fieldC13X' : (Decimal, None),
          'fieldC13Y': (Integer, None), 
          'fieldC14W': (Integer, None), 
          'fieldC14X' : (Decimal, None),
          'fieldC14Y': (Integer, None), 
          'fieldC15W': (Integer, None), 
          'fieldC15X' : (Decimal, None),
          'fieldC15Y': (Integer, None), 
          'fieldC16W': (Integer, None), 
          'fieldC16X' : (Decimal, None),
          'fieldC16Y': (Integer, None), 
          'fieldC17W': (Integer, None), 
          'fieldC17X' : (Decimal, None),
          'fieldC17Y': (Integer, None), 
          #
          'fieldC21W': (Integer, None), 
          'fieldC21X' : (Decimal, None),
          'fieldC21Y': (Integer, None), 
          'fieldC22W': (Integer, None), 
          'fieldC22X' : (Decimal, None),
          'fieldC22Y': (Integer, None), 
          'fieldC23W': (Integer, None), 
          'fieldC23X' : (Decimal, None),
          'fieldC23Y': (Integer, None), 
          #
          'fieldC31W': (Integer, None), 
          'fieldC31X' : (Decimal, None),
          'fieldC31Y': (Integer, None), 
          'fieldC32W': (Integer, None), 
          'fieldC32X' : (Decimal, None),
          'fieldC33W': (Integer, None), 
          'fieldC33X' : (Decimal, None),
          'fieldC33Y': (Integer, None), 
          'fieldC34W': (Integer, None), 
          'fieldC34X' : (Decimal, None),
          #
          'fieldC41W': (Integer, None),
          'fieldC41Y': (Integer, None),
          'fieldC42W': (Integer, None),
          'fieldC42Y': (Integer, None),
          'fieldC43W' : (Integer, None, {'sum' : 
                                            (
                                             'fieldC11W', 'fieldC12W', 
                                             'fieldC13W', 'fieldC14W',
                                             'fieldC15W', 'fieldC16W',
                                             'fieldC17W', 'fieldC21W',
                                             'fieldC22W', 'fieldC23W',
                                             'fieldC31W', 'fieldC32W', 
                                             'fieldC33W', 'fieldC34W',
                                             'fieldC41W', 'fieldC42W', 
                                             )}), 
          'fieldC43X' : (Decimal, None, {'sum' : 
                                            (
                                             'fieldC11X', 'fieldC12X', 
                                             'fieldC13X', 'fieldC14X',
                                             'fieldC15X', 'fieldC16X',
                                             'fieldC17X', 'fieldC21X',
                                             'fieldC22X', 'fieldC23X',
                                             'fieldC31X', 'fieldC32X', 
                                             'fieldC33X', 'fieldC34X',
                                             )}), 
          'fieldC43Y' : (Integer, None, {'sum' : 
                                            (
                                             'fieldC11Y', 'fieldC12Y', 
                                             'fieldC13Y', 'fieldC14Y',
                                             'fieldC15Y', 'fieldC16Y',
                                             'fieldC17Y', 'fieldC21Y',
                                             'fieldC22Y', 'fieldC23Y',
                                             'fieldC31Y', 'fieldC33Y', 
                                             'fieldC41Y', 'fieldC42Y', 
                                             )}), 
          #
          'fieldC51': (Integer, None),
          # D- Collections
          'fieldD11X': (Integer, None), 'fieldD11Y': (Integer, None), 
          'fieldD11Z': (Integer, None, {'sum': ('fieldD11X', 'fieldD11Y')}),
          'fieldD12X': (Integer, None), 'fieldD12Y': (Integer, None), 
          'fieldD12Z': (Integer, None, {'sum': ('fieldD12X', 'fieldD12Y')}),
          'fieldD13X': (Integer, None), 'fieldD13Y': (Integer, None), 
          'fieldD13Z': (Integer, None, {'sum': ('fieldD13X', 'fieldD13Y')}),
          'fieldD14X': (Integer, None), 'fieldD14Y': (Integer, None), 
          'fieldD14Z': (Integer, None, {'sum': ('fieldD14X', 'fieldD14Y')}),
          'fieldD15X': (Integer, None), 'fieldD15Y': (Integer, None), 
          'fieldD15Z': (Integer, None, {'sum': ('fieldD15X', 'fieldD15Y')}),
          'fieldD16X': (Integer, None), 'fieldD16Y': (Integer, None), 
          'fieldD16Z': (Integer, None, {'sum': ('fieldD16X', 'fieldD16Y')}),
          'fieldD17X': (Integer, None), 'fieldD17Y': (Integer, None), 
          'fieldD17Z': (Integer, None, {'sum': ('fieldD17X', 'fieldD17Y')}),
          'fieldD18X': (Integer, None), 'fieldD18Y': (Integer, None), 
          'fieldD18Z': (Integer, None, {'sum': ('fieldD18X', 'fieldD18Y')}),
          #
          'fieldD19': (Integer, None), 'fieldD20': (Integer, None),
          'fieldD21': (Integer, None), 'fieldD22': (Integer, None),
          'fieldD23': (Integer, None), 'fieldD24': (Integer, None),
          'fieldD25X': (Integer, None, {'sum': (
                                                'fieldD11X', 'fieldD12X',
                                                'fieldD13X', 'fieldD14X',
                                                'fieldD15X', 'fieldD16X',
                                                'fieldD17X', 'fieldD18X',
                                                )}),
          'fieldD25Y': (Integer, None, {'sum': (
                                                'fieldD11Y', 'fieldD12Y',
                                                'fieldD13Y', 'fieldD14Y',
                                                'fieldD15Y', 'fieldD16Y',
                                                'fieldD17Y', 'fieldD18Y',
                                                )}),
          'fieldD25Z': (Integer, None, {'sum': (
                                                'fieldD11Z', 'fieldD12Z',
                                                'fieldD13Z', 'fieldD14Z',
                                                'fieldD15Z', 'fieldD16Z',
                                                'fieldD17Z', 'fieldD18Z',
                                                'fieldD19', 'fieldD20',
                                                'fieldD21', 'fieldD22', 
                                                'fieldD23', 'fieldD24'
                                                )}),
          #
          'fieldD31': (Integer, None), 'fieldD32': (Integer, None),
          'fieldD33': (Integer, None), 'fieldD34': (Integer, None),
          'fieldD35': (Integer, None), 'fieldD36': (Integer, None),
          'fieldD37': (Integer, None, {'sum': (
                                               'fieldD31', 'fieldD32',
                                               'fieldD33', 'fieldD34',
                                               'fieldD35', 'fieldD36',
                                               )}),
          #
          'fieldD41': (Integer, None), 'fieldD42': (Integer, None),
          'fieldD43': (Integer, None), 'fieldD44': (Integer, None),
          #'fieldD45': (Integer, None), 'fieldD46': (Integer, None),
          #'fieldD47': (Integer, None), 
          # E- ACQUISITIONS ET ÉLIMINATIONS DE L'ANNÉE
          #
          'fieldE11X': (Integer, None), 'fieldE11Y': (Integer, None), 
          'fieldE11Z': (Integer, None, {'sum': ('fieldE11X', 'fieldE11Y')}),
          'fieldE12X': (Integer, None), 'fieldE12Y': (Integer, None), 
          'fieldE12Z': (Integer, None, {'sum': ('fieldE12X', 'fieldE12Y')}),
          'fieldE13X': (Integer, None), 'fieldE13Y': (Integer, None), 
          'fieldE13Z': (Integer, None, {'sum': ('fieldE13X', 'fieldE13Y')}),
          'fieldE14X': (Integer, None), 'fieldE14Y': (Integer, None), 
          'fieldE14Z': (Integer, None, {'sum': ('fieldE14X', 'fieldE14Y')}),
          'fieldE15X': (Integer, None), 'fieldE15Y': (Integer, None), 
          'fieldE15Z': (Integer, None, {'sum': ('fieldE15X', 'fieldE15Y')}),
          'fieldE16X': (Integer, None), 'fieldE16Y': (Integer, None), 
          'fieldE16Z': (Integer, None, {'sum': ('fieldE16X', 'fieldE16Y')}),
          'fieldE17X': (Integer, None), 'fieldE17Y': (Integer, None), 
          'fieldE17Z': (Integer, None, {'sum': ('fieldE17X', 'fieldE17Y')}),
          #
          'fieldE21X': (Integer, None), 'fieldE21Y': (Integer, None), 
          'fieldE21Z': (Integer, None, {'sum': ('fieldE21X', 'fieldE21Y')}),
          'fieldE22X': (Integer, None), 'fieldE22Y': (Integer, None), 
          'fieldE22Z': (Integer, None, {'sum': ('fieldE22X', 'fieldE22Y')}),
          'fieldE23X': (Integer, None), 'fieldE23Y': (Integer, None), 
          'fieldE23Z': (Integer, None, {'sum': ('fieldE23X', 'fieldE23Y')}),
          'fieldE24X': (Integer, None), 'fieldE24Y': (Integer, None), 
          'fieldE24Z': (Integer, None, {'sum': ('fieldE24X', 'fieldE24Y')}),
          'fieldE25X': (Integer, None), 'fieldE25Y': (Integer, None), 
          'fieldE25Z': (Integer, None, {'sum': ('fieldE25X', 'fieldE25Y')}),
          'fieldE26X': (Integer, None), 'fieldE26Y': (Integer, None), 
          'fieldE26Z': (Integer, None, {'sum': ('fieldE26X', 'fieldE26Y')}),
          'fieldE27X': (Integer, None), 'fieldE27Y': (Integer, None), 
          'fieldE27Z': (Integer, None, {'sum': ('fieldE27X', 'fieldE27Y')}),
          #
          'fieldE31X': (Integer, None), 'fieldE31Y': (Integer, None), 
          'fieldE31Z': (Integer, None, {'sum': ('fieldE31X', 'fieldE31Y')}),
          'fieldE32X': (Integer, None), 'fieldE32Y': (Integer, None), 
          'fieldE32Z': (Integer, None, {'sum': ('fieldE32X', 'fieldE32Y')}),
          'fieldE33X': (Integer, None), 'fieldE33Y': (Integer, None), 
          'fieldE33Z': (Integer, None, {'sum': ('fieldE33X', 'fieldE33Y')}),
          'fieldE34X': (Integer, None), 'fieldE34Y': (Integer, None), 
          'fieldE34Z': (Integer, None, {'sum': ('fieldE34X', 'fieldE34Y')}),
          'fieldE35X': (Integer, None), 'fieldE35Y': (Integer, None), 
          'fieldE35Z': (Integer, None, {'sum': ('fieldE35X', 'fieldE35Y')}),
          'fieldE36X': (Integer, None), 'fieldE36Y': (Integer, None), 
          'fieldE36Z': (Integer, None, {'sum': ('fieldE36X', 'fieldE36Y')}),
          'fieldE37X': (Integer, None), 'fieldE37Y': (Integer, None), 
          'fieldE37Z': (Integer, None, {'sum': ('fieldE37X', 'fieldE37Y')}),
          'fieldE38X': (Integer, None), 'fieldE38Y': (Integer, None), 
          'fieldE38Z': (Integer, None, {'sum': ('fieldE38X', 'fieldE38Y')}),
          #
          'fieldE41X': (Integer, None), 'fieldE41Y': (Integer, None), 
          'fieldE41Z': (Integer, None, {'sum': ('fieldE41X', 'fieldE41Y')}),
          'fieldE42X': (Integer, None), 'fieldE42Y': (Integer, None), 
          'fieldE42Z': (Integer, None, {'sum': ('fieldE42X', 'fieldE42Y')}),
          'fieldE43X': (Integer, None), 'fieldE43Y': (Integer, None), 
          'fieldE43Z': (Integer, None, {'sum': ('fieldE43X', 'fieldE43Y')}),
          'fieldE44X': (Integer, None), 'fieldE44Y': (Integer, None), 
          'fieldE44Z': (Integer, None, {'sum': ('fieldE44X', 'fieldE44Y')}),
          'fieldE45X': (Integer, None), 'fieldE45Y': (Integer, None), 
          'fieldE45Z': (Integer, None, {'sum': ('fieldE45X', 'fieldE45Y')}),

          'fieldE46X': (Integer, None, {'sum': (
                                                'fieldE41X', 'fieldE42X',
                                                'fieldE43X', 'fieldE44X',
                                                'fieldE45X',
                                                )}), 

          'fieldE46Y': (Integer, None, {'sum': (
                                                'fieldE41Y', 'fieldE42Y',
                                                'fieldE43Y', 'fieldE44Y',
                                                'fieldE45Y',
                                                )}), 
          'fieldE46Z': (Integer, None, {'sum': ('fieldE46X', 'fieldE46Y')}),
          #
          'fieldE51X': (Integer, None), 'fieldE51Y': (Integer, None), 
          'fieldE51Z': (Integer, None, {'sum': ('fieldE51X', 'fieldE51Y')}),
          'fieldE52X': (Integer, None), 'fieldE52Y': (Integer, None), 
          'fieldE52Z': (Integer, None, {'sum': ('fieldE52X', 'fieldE52Y')}),
          'fieldE53X': (Integer, None), 'fieldE53Y': (Integer, None), 
          'fieldE53Z': (Integer, None, {'sum': ('fieldE53X', 'fieldE53Y')}),
          #
          'fieldE61X': (Integer, None), 'fieldE61Y': (Integer, None), 
          'fieldE61Z': (Integer, None, {'sum': ('fieldE61X', 'fieldE61Y')}),
          'fieldE62X': (Integer, None), 'fieldE62Y': (Integer, None), 
          'fieldE62Z': (Integer, None, {'sum': ('fieldE62X', 'fieldE62Y')}),
          'fieldE63X': (Integer, None), 'fieldE63Y': (Integer, None), 
          'fieldE63Z': (Integer, None, {'sum': ('fieldE63X', 'fieldE63Y')}),
          'fieldE64X': (Integer, None), 'fieldE64Y': (Integer, None), 
          'fieldE64Z': (Integer, None, {'sum': ('fieldE64X', 'fieldE64Y')}),
          'fieldE65X': (Integer, None), 'fieldE65Y': (Integer, None), 
          'fieldE65Z': (Integer, None, {'sum': ('fieldE65X', 'fieldE65Y')}),
          'fieldE66X': (Integer, None), 'fieldE66Y': (Integer, None), 
          'fieldE66Z': (Integer, None, {'sum': ('fieldE66X', 'fieldE66Y')}),

          'fieldE67X': (Integer, None, {'sum': (
                                                'fieldE61X', 'fieldE62X',
                                                'fieldE63X', 'fieldE64X',
                                                'fieldE65X',
                                                )}), 
          'fieldE67Y': (Integer, None, {'sum': (
                                                'fieldE61Y', 'fieldE62Y',
                                                'fieldE63Y', 'fieldE64Y',
                                                'fieldE65Y',
                                                )}), 

          'fieldE67Z': (Integer, None, {'sum': ('fieldE67X', 'fieldE67Y')}),
          'fieldE68X': (Integer, None), 'fieldE68Y': (Integer, None), 
          'fieldE68Z': (Integer, None, {'sum': ('fieldE68X', 'fieldE68Y')}),
          'fieldE69X': (Integer, None), 'fieldE69Y': (Integer, None), 
          'fieldE69Z': (Integer, None, {'sum': ('fieldE69X', 'fieldE69Y')}),
          #
          'fieldE70X': (Integer, None), 'fieldE70Y': (Integer, None), 
          'fieldE70Z': (Integer, None, {'sum': ('fieldE70X', 'fieldE70Y')}),
          'fieldE71X': (Integer, None, {'sum': (
                                                'fieldE68X', 'fieldE69X',
                                                'fieldE70X', 
                                                )}), 
          'fieldE71Y': (Integer, None, {'sum': (
                                                'fieldE68Y', 'fieldE69Y',
                                                'fieldE70Y', 
                                                )}), 
          'fieldE71Z': (Integer, None, {'sum': ('fieldE71X', 'fieldE11Y')}),
          'fieldE72X': (Integer, None), 'fieldE72Y': (Integer, None), 
          'fieldE72Z': (Integer, None, {'sum': ('fieldE71X', 'fieldE11Y')}),
          'fieldE73X': (Integer, None), 'fieldE73Y': (Integer, None), 
          'fieldE73Z': (Integer, None, {'sum': ('fieldE71X', 'fieldE71Y')}),
          'fieldE74X': (Integer, None, {'sum': (
                                                'fieldE67X', 'fieldE71X',
                                                'fieldE72X', 'fieldE73X', 
                                                )}), 
          'fieldE74Y': (Integer, None, {'sum': (
                                                'fieldE67Y', 'fieldE71Y',
                                                'fieldE72Y', 'fieldE73Y', 
                                                )}), 
          'fieldE74Z': (Integer, None, {'sum': ('fieldE74X', 'fieldE74Y')}),
          # F- 6 COOPÉRATION ET RÉSEAU 
          #
          'fieldF11': (IO.Boolean, ''),
          'fieldF12': (IO.Boolean, '', {'depend_field' : ('fieldF13',),}),
          'fieldF13': (IO.Unicode, ''),
          'fieldF14': (IO.Boolean, '', {'depend_field' : ('fieldF15',),}),
          'fieldF15': (IO.Unicode, ''),
          'fieldF16': (IO.Boolean, '', {'depend_field' : 
                                            ('fieldF17', 'fieldF18', 
                                             'fieldF19', 'fieldF20',)}), 
          'fieldF17': (IO.Boolean, ''), 'fieldF18': (IO.Boolean, ''), 
          'fieldF19': (IO.Boolean, ''), 'fieldF20': (IO.Boolean, ''), 
          
          'fieldF21': (IO.Boolean, ''),
          'fieldF22': (IO.Boolean, ''), 'fieldF23': (IO.Boolean, ''),
          
          # G-  ACTIVITÉS DE LA BIBLIOTHÈQUE
          #
          'fieldG11': (Checkboxes, ''),
          'fieldG12H': (Integer, ''), 'fieldG12M': (Integer, ''), 
          'fieldG13H': (Integer, ''),'fieldG13M': (Integer, ''), 
          #
          'fieldG20W': (Integer, None), 'fieldG20X': (Integer, None),
          'fieldG20Y': (Integer, None), 
          'fieldG20Z': (Integer, None, {'sum': ('fieldG20W', 'fieldG20X')}),
          'fieldG21W': (Integer, None), 'fieldG21X': (Integer, None),
          'fieldG21Y': (Integer, None), 
          'fieldG21Z': (Integer, None, {'sum': ('fieldG21W', 'fieldG21X')}),
          'fieldG22W': (Integer, None), 'fieldG22X': (Integer, None),
          'fieldG22Y': (Integer, None), 
          'fieldG22Z': (Integer, None, {'sum': ('fieldG22W', 'fieldG22X')}),
          'fieldG23W': (Integer, None), 'fieldG23X': (Integer, None),
          'fieldG23Y': (Integer, None), 
          'fieldG23Z': (Integer, None, {'sum': ('fieldG23W', 'fieldG23X')}),
          'fieldG24W': (Integer, None), 'fieldG24X': (Integer, None),
          'fieldG24Y': (Integer, None), 
          'fieldG24Z': (Integer, None, {'sum': ('fieldG24W', 'fieldG24X')}),

          'fieldG25W': (Integer, None, {'sum': (
                                                'fieldG22W', 'fieldG23W', 
                                                'fieldG24W', 
                                                )}), 
          'fieldG25X': (Integer, None, {'sum': (
                                                'fieldG22X', 'fieldG23X', 
                                                'fieldG24X', 
                                                )}), 
          'fieldG25Y': (Integer, None, {'sum': ('fieldG25W', 'fieldG25X')}), 
          'fieldG25Z': (Integer, None, {'sum': (
                                                'fieldG20Z', 'fieldG21Z',
                                                'fieldG22Z', 'fieldG23Z', 
                                                'fieldG24Z', 
                                                )}), 
          #
          'fieldG26Y': (Integer, None, {'sum': ('fieldG20Y', 'fieldG21Y', 
                                                'fieldG25Y')}), 
          'fieldG26Z': (Integer, None, {'sum': ('fieldG20Z', 'fieldG21Z', 
                                                'fieldG25Z')}), 
          'fieldG27Y': (Integer, None), 'fieldG27Z': (Integer, None),
          #
          'fieldG28': (Integer, None), 'fieldG29': (Integer, None),
          'fieldG30': (Integer, None), 'fieldG31': (Integer, None),
          'fieldG32': (Integer, None), 'fieldG33': (Integer, None),
          #
          'fieldG41X': (Integer, None), 'fieldG41Y': (Integer, None), 
          'fieldG41Z': (Integer, None, {'sum': ('fieldG41X', 'fieldG41Y')}),
          'fieldG42X': (Integer, None), 'fieldG42Y': (Integer, None), 
          'fieldG42Z': (Integer, None, {'sum': ('fieldG42X', 'fieldG42Y')}),
          'fieldG43X': (Integer, None), 'fieldG43Y': (Integer, None), 
          'fieldG43Z': (Integer, None, {'sum': ('fieldG43X', 'fieldG43Y')}),
          'fieldG44X': (Integer, None), 'fieldG44Y': (Integer, None), 
          'fieldG44Z': (Integer, None, {'sum': ('fieldG44X', 'fieldG44Y')}),
          'fieldG45X': (Integer, None), 'fieldG45Y': (Integer, None), 
          'fieldG45Z': (Integer, None, {'sum': ('fieldG45X', 'fieldG45Y')}),
          #
          'fieldG47X': (Integer, None), 'fieldG47Y': (Integer, None), 
          'fieldG47Z': (Integer, None, {'sum': ('fieldG47X', 'fieldG47Y')}),

          'fieldG48X': (Integer, None, {'sum': (
                                                'fieldG41X', 'fieldG42X',
                                                'fieldG43X', 'fieldG44X', 
                                                'fieldG45X', 
                                                'fieldG47X', 
                                                )}), 
          'fieldG48Y': (Integer, None, {'sum': (
                                                'fieldG41Y', 'fieldG42Y',
                                                'fieldG43Y', 'fieldG44Y', 
                                                'fieldG45Y', 
                                                'fieldG47Y', 
                                                )}), 
          'fieldG48Z': (Integer, None),
          #
          'fieldG49': (Integer, None),
          'fieldG50': (Integer, None), 
          'fieldG51': (Integer, None),
          'fieldG51': (Integer, None, {'sum': ('fieldG49', 'fieldG50')}), 
          # H- SERVICES OFFERTS PAR LA BIBLIOTHÈQUE 
          #
          'fieldH11': (IO.Boolean, ''), 'fieldH12': (IO.Boolean, ''),
          'fieldH13': (IO.Boolean, ''), 'fieldH14': (IO.Boolean, ''),
          'fieldH15': (IO.Boolean, ''),
          'fieldH16': (IO.Boolean, '', {'depend_field' : ('fieldH17',
                                                              'fieldH18',
                                                              'fieldH19',
                                                              'fieldH20',)}),
          'fieldH17': (Integer, None), 'fieldH18': (Integer, None),
          'fieldH19': (Integer, None), 'fieldH20': (Integer, None),
          'fieldH21': (IO.Unicode, None),
          #
          'fieldH31': (IO.Boolean, '', 
                       {'depend_field' : ('fieldH32', 'fieldH33', 'fieldH34',
                                          'fieldH35', 'fieldH36', 'fieldH37')}),
          #
          #
          'fieldH32': (IO.Boolean, ''),
          'fieldH33': (IO.Boolean, ''), 'fieldH34': (IO.Boolean, ''),
          'fieldH35': (IO.Boolean, ''), 'fieldH36': (IO.Boolean, ''),
          'fieldH37': (IO.Boolean, ''),
          
          'fieldH38X': (Integer, None), 'fieldH38Y': (Integer, None),
          'fieldH38Z': (Integer, None, {'sum': ('fieldH38X', 'fieldH38Y')}),
          'fieldH39' : (IO.Boolean, None),
          'fieldH41' : (IO.Boolean, None, {'depend_field' : ('fieldH42',)}),
          'fieldH42': (IO.Unicode, None), 
          #
          'fieldH52Y': (Integer, None), 'fieldH52Z': (Integer, None),
          'fieldH53Y': (Integer, None), 'fieldH53Z': (Integer, None),
          'fieldH54Y': (Integer, None), 'fieldH54Z': (Integer, None),
          'fieldH55Y': (Integer, None), 'fieldH55Z': (Integer, None),
          'fieldH56Y': (Integer, None), 'fieldH56Z': (Integer, None),
          'fieldH57Y': (Integer, None), 'fieldH57Z': (Integer, None),
          'fieldH58Y': (Integer, None), 'fieldH58Z': (Integer, None),
          'fieldH59Y': (Integer, None), 'fieldH59Z': (Integer, None),
          'fieldH60Y': (Integer, None), 'fieldH60Z': (Integer, None),
          'fieldH61Y': (Integer, None), 'fieldH61Z': (Integer, None),
          'fieldH62Y': (Integer, None), 'fieldH62Z': (Integer, None),
          'fieldH63Y': (Integer, None, {'sum': ('fieldH52Y',
                                                'fieldH53Y', 'fieldH54Y', 
                                                'fieldH55Y', 'fieldH56Y', 
                                                'fieldH57Y', 'fieldH58Y', 
                                                'fieldH59Y', 'fieldH60Y', 
                                                'fieldH61Y', 'fieldH62Y', 
                                                )}), 
          'fieldH63Z': (Integer, None, {'sum': ('fieldH52Z',
                                                'fieldH53Z', 'fieldH54Z', 
                                                'fieldH55Z', 'fieldH56Z', 
                                                'fieldH57Z', 'fieldH58Z', 
                                                'fieldH59Z', 'fieldH60Z', 
                                                'fieldH61Z', 'fieldH62Z', 
                                                )}), 
          # I-  ANIMATIONS, PUBLICATIONS ET FORMATION
          #
          'fieldI11': (IO.Boolean, ''), 'fieldI12': (IO.Boolean, ''),
          'fieldI13': (IO.Boolean, '', 
                       {'depend_field' : ('fieldI14', 'fieldI15', 'fieldI16', 
                        'fieldI17', 'fieldI18', 'fieldI19', 'fieldI20', 
                        'fieldI21')}), 
          'fieldI14': (Integer, None),
          'fieldI15': (Integer, None), 'fieldI16': (Integer, None),
          'fieldI17': (Integer, None), 'fieldI18': (Integer, None),
          'fieldI19': (Integer, None), 'fieldI20': (Integer, None),
          'fieldI21': (Integer, None),
          #
          'fieldI31': (IO.Boolean, None),
          'fieldI32': (IO.Boolean, None),
          'fieldI33': (IO.Boolean, None), 
          'fieldI34': (IO.Boolean, None),
          #
          'fieldI35': (IO.Boolean, '', 
                       {'depend_field' : ('fieldI36', 'fieldI37',
                                          'fieldI38', 'fieldI39')}),
          'fieldI36': (Integer, None), 'fieldI37': (Integer, None), 
          'fieldI38': (Integer, None), 'fieldI39': (Integer, None), 
          #
          'fieldI41': (Integer, None),
          #
          'fieldI42Y': (Integer, None), 'fieldI42Z': (Integer, None),
          'fieldI43Y': (Integer, None), 'fieldI43Z': (Integer, None),
          'fieldI44Y': (Integer, None, {'sum': ('fieldI42Y', 'fieldI43Y')}),
          'fieldI44Z': (Integer, None, {'sum': ('fieldI42Z', 'fieldI43Z')}),
          'fieldI45Y': (Integer, None), 'fieldI45Z': (Integer, None),
          'fieldI46Y': (Integer, None), 'fieldI46Z': (Integer, None),

          'fieldI47Y': (Integer, None, {'sum': ('fieldI45Y', 'fieldI46Y')}),
          'fieldI47Z': (Integer, None, {'sum': ('fieldI45Z', 'fieldI46Z')}),
          'fieldI48Y': (Integer, None), 'fieldI48Z': (Integer, None),
          # J- Annex 
          #
          'fieldJ1T' :(IO.Unicode, ''), 'fieldJ1U' :(IO.Unicode, ''),
          'fieldJ1V' :(IO.Unicode, ''), 'fieldJ1W' :(IO.Unicode, ''),
          'fieldJ1X' :(IO.Unicode, ''), 'fieldJ1Y' :(IO.Unicode, ''), 
          'fieldJ1Z' :(IO.Unicode, ''),
          #
          #
          'fieldJ2T' :(IO.Unicode, ''), 'fieldJ2U' :(IO.Unicode, ''),
          'fieldJ2V' :(IO.Unicode, ''), 'fieldJ2W' :(IO.Unicode, ''),
          'fieldJ2X' :(IO.Unicode, ''), 'fieldJ2Y' :(IO.Unicode, ''), 
          'fieldJ2Z' :(IO.Unicode, ''),
          #
          #
          'fieldJ3T' :(IO.Unicode, ''), 'fieldJ3U' :(IO.Unicode, ''),
          'fieldJ3V' :(IO.Unicode, ''), 'fieldJ3W' :(IO.Unicode, ''),
          'fieldJ3X' :(IO.Unicode, ''), 'fieldJ3Y' :(IO.Unicode, ''), 
          'fieldJ3Z' :(IO.Unicode, ''),
          #
          #
          'fieldJ4T' :(IO.Unicode, ''), 'fieldJ4U' :(IO.Unicode, ''),
          'fieldJ4V' :(IO.Unicode, ''), 'fieldJ4W' :(IO.Unicode, ''),
          'fieldJ4X' :(IO.Unicode, ''), 'fieldJ4Y' :(IO.Unicode, ''), 
          'fieldJ4Z' :(IO.Unicode, ''),
          #
          #
          'fieldJ5T' :(IO.Unicode, ''), 'fieldJ5U' :(IO.Unicode, ''),
          'fieldJ5V' :(IO.Unicode, ''), 'fieldJ5W' :(IO.Unicode, ''),
          'fieldJ5X' :(IO.Unicode, ''), 'fieldJ5Y' :(IO.Unicode, ''), 
          'fieldJ5Z' :(IO.Unicode, ''),
          #
          #
          'fieldJ6T' :(IO.Unicode, ''), 'fieldJ6U' :(IO.Unicode, ''),
          'fieldJ6V' :(IO.Unicode, ''), 'fieldJ6W' :(IO.Unicode, ''),
          'fieldJ6X' :(IO.Unicode, ''), 'fieldJ6Y' :(IO.Unicode, ''), 
          'fieldJ6Z' :(IO.Unicode, ''),
          #
          #
          'fieldJ7T' :(IO.Unicode, ''), 'fieldJ7U' :(IO.Unicode, ''),
          'fieldJ7V' :(IO.Unicode, ''), 'fieldJ7W' :(IO.Unicode, ''),
          'fieldJ7X' :(IO.Unicode, ''), 'fieldJ7Y' :(IO.Unicode, ''), 
          'fieldJ7Z' :(IO.Unicode, ''),
          #
          #
          'fieldJ8T' :(IO.Unicode, ''), 'fieldJ8U' :(IO.Unicode, ''),
          'fieldJ8V' :(IO.Unicode, ''), 'fieldJ8W' :(IO.Unicode, ''),
          'fieldJ8X' :(IO.Unicode, ''), 'fieldJ8Y' :(IO.Unicode, ''), 
          'fieldJ8Z' :(IO.Unicode, ''),
          #
          #
          'fieldJ9T' :(IO.Unicode, ''), 'fieldJ9U' :(IO.Unicode, ''),
          'fieldJ9V' :(IO.Unicode, ''), 'fieldJ9W' :(IO.Unicode, ''),
          'fieldJ9X' :(IO.Unicode, ''), 'fieldJ9Y' :(IO.Unicode, ''), 
          'fieldJ9Z' :(IO.Unicode, ''),
          #
          #
          'fieldJ10T' :(IO.Unicode, ''), 'fieldJ10U' :(IO.Unicode, ''),
          'fieldJ10V' :(IO.Unicode, ''), 'fieldJ10W' :(IO.Unicode, ''),
          'fieldJ10X' :(IO.Unicode, ''), 'fieldJ10Y' :(IO.Unicode, ''), 
          'fieldJ10Z' :(IO.Unicode, ''),
          #
          #
          'fieldJ11T' :(IO.Unicode, ''), 'fieldJ11U' :(IO.Unicode, ''),
          'fieldJ11V' :(IO.Unicode, ''), 'fieldJ11W' :(IO.Unicode, ''),
          'fieldJ11X' :(IO.Unicode, ''), 'fieldJ11Y' :(IO.Unicode, ''), 
          'fieldJ11Z' :(IO.Unicode, ''),
          #
          #
          'fieldJ12T' :(IO.Unicode, ''), 'fieldJ12U' :(IO.Unicode, ''),
          'fieldJ12V' :(IO.Unicode, ''), 'fieldJ12W' :(IO.Unicode, ''),
          'fieldJ12X' :(IO.Unicode, ''), 'fieldJ12Y' :(IO.Unicode, ''), 
          'fieldJ12Z' :(IO.Unicode, ''),
          #
          #
          'fieldJ13T' :(IO.Unicode, ''), 'fieldJ13U' :(IO.Unicode, ''),
          'fieldJ13V' :(IO.Unicode, ''), 'fieldJ13W' :(IO.Unicode, ''),
          'fieldJ13X' :(IO.Unicode, ''), 'fieldJ13Y' :(IO.Unicode, ''), 
          'fieldJ13Z' :(IO.Unicode, ''),
          #
          'fieldJ14T' :(IO.Unicode, ''), 'fieldJ14U' :(IO.Unicode, ''),
          'fieldJ14V' :(IO.Unicode, ''), 'fieldJ14W' :(IO.Unicode, ''),
          'fieldJ14X' :(IO.Unicode, ''), 'fieldJ14Y' :(IO.Unicode, ''), 
          'fieldJ14Z' :(IO.Unicode, ''),
          #
          #
          'fieldJ15T' :(IO.Unicode, ''), 'fieldJ15U' :(IO.Unicode, ''),
          'fieldJ15V' :(IO.Unicode, ''), 'fieldJ15W' :(IO.Unicode, ''),
          'fieldJ15X' :(IO.Unicode, ''), 'fieldJ15Y' :(IO.Unicode, ''), 
          'fieldJ15Z' :(IO.Unicode, ''),
          #
          # K- EPCI
          'fieldK1': (IO.Unicode, ''), 'fieldK2': (IO.Unicode, None),
          'fieldK3': (Checkboxes, '1'), 
          'fieldK6': (IO.Unicode, ''),
          'fieldK7': (IO.Unicode, ''), 'fieldK8': (IO.Unicode, ''),
          'fieldK9': (IO.Unicode, ''), 'fieldK10': (IO.Unicode, ''),
          'fieldK11': (IO.Unicode, ''), 'fieldK12': (IO.Unicode, ''),
          'fieldK13': (IO.Unicode, ''), 'fieldK14': (IO.Unicode, ''),
          'fieldK15': (IO.Unicode, ''), 'fieldK16': (IO.Unicode, ''),
          #
          #
          'fieldK17W' :(IO.Unicode, None),
          'fieldK17X' :(IO.Unicode, ''),
          'fieldK17Y' :(IO.Unicode, None),
          'fieldK17Z' :(EPCI_Statut, ''),
          #
          #
          'fieldK18W' :(IO.Unicode, None),
          'fieldK18X' :(IO.Unicode, ''),
          'fieldK18Y' :(IO.Unicode, None),
          'fieldK18Z' :(EPCI_Statut, ''),
          #
          #
          'fieldK19W' :(IO.Unicode, None),
          'fieldK19X' :(IO.Unicode, ''),
          'fieldK19Y' :(IO.Unicode, None),
          'fieldK19Z' :(EPCI_Statut, ''),
          #
          #
          'fieldK20W' :(IO.Unicode, None),
          'fieldK20X' :(IO.Unicode, ''),
          'fieldK20Y' :(IO.Unicode, None),
          'fieldK20Z' :(EPCI_Statut, ''),
          #
          #
          'fieldK21W' :(IO.Unicode, None),
          'fieldK21X' :(IO.Unicode, ''),
          'fieldK21Y' :(IO.Unicode, None),
          'fieldK21Z' :(EPCI_Statut, ''),
          #
          #
          'fieldK22W' :(IO.Unicode, None),
          'fieldK22X' :(IO.Unicode, ''),
          'fieldK22Y' :(IO.Unicode, None),
          'fieldK22Z' :(EPCI_Statut, ''),
          #
          #
          'fieldK23W' :(IO.Unicode, None),
          'fieldK23X' :(IO.Unicode, ''),
          'fieldK23Z' :(EPCI_Statut, None),
          'fieldK23Y' :(IO.Unicode, ''),
          #
          #
          'fieldK24W' :(IO.Unicode, None),
          'fieldK24X' :(IO.Unicode, ''),
          'fieldK24Y' :(IO.Unicode, None),
          'fieldK24Z' :(EPCI_Statut, ''),
          #
          #
          'fieldK25W' :(IO.Unicode, None),
          'fieldK25X' :(IO.Unicode, ''),
          'fieldK25Y' :(IO.Unicode, None),
          'fieldK25Z' :(EPCI_Statut, ''),
          #
          #
          'fieldK26W' :(IO.Unicode, None),
          'fieldK26X' :(IO.Unicode, ''),
          'fieldK26Y' :(IO.Unicode, None),
          'fieldK26Z' :(EPCI_Statut, ''),
          #
          #
          'fieldK27W' :(IO.Unicode, None),
          'fieldK27X' :(IO.Unicode, ''),
          'fieldK27Y' :(IO.Unicode, None),
          'fieldK27Z' :(EPCI_Statut, ''),
          #
          #
          'fieldK28W' :(IO.Unicode, None),
          'fieldK28X' :(IO.Unicode, ''),
          'fieldK28Y' :(IO.Unicode, None),
          'fieldK28Z' :(EPCI_Statut, ''),
          #
          #
          'fieldK29W' :(IO.Unicode, None),
          'fieldK29X' :(IO.Unicode, ''),
          'fieldK29Y' :(IO.Unicode, None),
          'fieldK29Z' :(EPCI_Statut, ''),
          #
          #
          'fieldK30W' :(IO.Unicode, None),
          'fieldK30X' :(IO.Unicode, ''),
          'fieldK30Y' :(IO.Unicode, None),
          'fieldK30Z' :(EPCI_Statut, ''),
          #
          #
          'fieldK31W' :(IO.Unicode, None),
          'fieldK31X' :(IO.Unicode, ''),
          'fieldK31Y' :(IO.Unicode, None),
          'fieldK31Z' :(EPCI_Statut, ''),
          }


##############################################################################
# Alerts
##############################################################################
alertes_txt = """
E61Z/E11Z = prix moyen d'un livre
E62Z/E12Z = prix moyen d'un phonogramme
E63Z/E13Z = prix moyen d'un vidéogramme
E64Z/E14Z = prix moyen d'un cédérom
E73Z/E46X = prix moyen d'un document patrimonial
E69Z/E51Z = prix moyen d'un périodique imprimé
E74Z - 5% <= A12+A24 <= E74Z + 5 %
A11/C43X = coût moyen d'un emploi
"""

# for key, text, expression in alertes:
alertes = [('A', u"E61Z/E11Z = prix moyen d'un livre", 'E61Z / E11Z' ),
           ('B', u"E62Z/E12Z = prix moyen d'un phonogramme", 'E62Z / E12Z' ),
           ('C', u"E63Z/E13Z = prix moyen d'un vidéogramme", 'E63Z/E13Z' ),
           ('D', u"E64Z/E14Z = prix moyen d'un cédérom", 'E64Z/E14Z' ),
	         ('E', (u"E73Z/E46X = prix moyen d'un document patrimonial"),
                  'E73Z/E46X' ),
           ('F', u"E68Z/E51Z = prix moyen d'un périodique imprimé", 
                 'int(E68Z)/int(E51Z)' ),
           ('G', u"E74Z - 5% <= A12+A24 <= E74Z + 5% = variation à +/- 5 % des dépenses documentaires", 
                 'int(E74Z) * 0.95 < A12+A24 < int(E74Z) * 1.05' ),
            ]

##############################################################################
# Controles 
##############################################################################

controles = [
 ('a_name', u'B21 [%s]  < %s ', 'B21', '9', 'B21 < 9', ['B21'], []),
 ('a_name', u'B22 [%s]  < %s ', 'B22', '9', 'B22 < 9', ['B22'], []),
 ]

controles = controles + sum2controle(schema=schema)
sort_controles = [(x[2], x) for x in controles]
sort_controles.sort()
controles = [t[-1] for t in sort_controles]

#pprint(controles)


##############################################################################
# Check that all keys are in schema
##############################################################################

def checkBM():
    checkBib(bib_type='BM', max=30, schema=schema)

if __name__ == '__main__':
    checkBM()    


