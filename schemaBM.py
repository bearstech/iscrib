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
from itools.datatypes import Unicode, Boolean

# Import from Culture 
from CultureTypes import Checkboxes, Integer, Decimal, EPCI_Statut
from schema import sum2controle, checkBib

schema = {'field1': (Unicode, ''), 'field2': (Unicode, ''),
          'field30': (Unicode, ''), 'field31': (Unicode, ''),
          'field32': (Unicode, ''), 'field33': (Unicode, ''),
          'field4': (Unicode, ''),
          'field5': (Unicode, ''), 'field6': (Unicode, ''),
          'field7': (Unicode, ''), 'field8': (Unicode, ''),
          'field9': (Unicode, ''), 'field10': (Unicode, ''),
          'field11': (Unicode, ''),'field12': (Unicode, ''),
          'field13': (Checkboxes, ''), 'field14': (Checkboxes, ''),
          'field15': (Unicode, ''), 
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
          'fieldB14': (Boolean, None),
          'fieldB15': (Integer, None),
          #
          'fieldB21': (Integer, None), 'fieldB22': (Integer, None),
          'fieldB23': (Integer, None),
          #
          'fieldB31': (Boolean, '', {'depend_field' : ('fieldB32',) }),
          'fieldB32': (Unicode, ''),
          'fieldB33': (Boolean, '', {'depend_field' : ('fieldB34',) }),
          'fieldB34': (Integer, None),
          'fieldB35': (Boolean, '', {'depend_field' : ('fieldB36',) }),
          'fieldB36': (Integer, ''),
          'fieldB37X': (Integer, None), 'fieldB37Y': (Integer, None), 
          'fieldB38X': (Integer, None), 'fieldB38Y': (Integer, None), 
          'fieldB39X': (Integer, None, {'sum' : ('fieldB37X', 'fieldB38X',)}),
          'fieldB39Y': (Integer, None, {'sum' : ('fieldB37Y', 'fieldB38Y',)}),
          'fieldB40': (Boolean, '', 
                       {'depend_field' : ('fieldB41','fieldB42') }),
          #
          'fieldB41': (Boolean, ''), 'fieldB42': (Boolean, ''),
          'fieldB43': (Boolean, '', 
                       {'depend_field' : ('fieldB44','fieldB45', 
                                          'fieldB46', 'fieldB47') }),
          'fieldB44': (Boolean, ''),
          'fieldB45': (Boolean, ''), 'fieldB46': (Boolean, ''),
          'fieldB47': (Unicode, ''),
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
          'fieldC32Y': (Integer, None), 
          'fieldC33W': (Integer, None), 
          'fieldC33X' : (Decimal, None),
          'fieldC33Y': (Integer, None), 
          'fieldC34W': (Integer, None), 
          'fieldC34Y': (Integer, None), 
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
                                             'fieldC31Y', 'fieldC32Y', 
                                             'fieldC33Y', 'fieldC34Y', 
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
          'fieldD25X': (Integer,None),
          'fieldD25Y': (Integer, None),
	  'fieldD25Z': (Integer, None, {'sum': ('fieldD25X', 'fieldD25Y' )}),

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
          'fieldE71Z': (Integer, None, {'sum': ('fieldE71X', 'fieldE71Y')}),
          'fieldE72X': (Integer, None), 'fieldE72Y': (Integer, None), 
          'fieldE72Z': (Integer, None, {'sum': ('fieldE72X', 'fieldE72Y')}),
          'fieldE73X': (Integer, None), 'fieldE73Y': (Integer, None), 
          'fieldE73Z': (Integer, None, {'sum': ('fieldE73X', 'fieldE73Y')}),
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
          'fieldF11': (Boolean, ''),
          'fieldF12': (Boolean, '', {'depend_field' : ('fieldF13',),}),
          'fieldF13': (Unicode, ''),
          'fieldF14': (Boolean, '', {'depend_field' : ('fieldF15',),}),
          'fieldF15': (Unicode, ''),
          'fieldF16': (Boolean, '', {'depend_field' : 
                                            ('fieldF17', 'fieldF18', 
                                             'fieldF19', 'fieldF20',)}), 
          'fieldF17': (Boolean, ''), 'fieldF18': (Boolean, ''), 
          'fieldF19': (Boolean, ''), 'fieldF20': (Boolean, ''), 
          
          'fieldF21': (Boolean, ''),
          'fieldF22': (Boolean, ''), 'fieldF23': (Boolean, ''),
          
          # G-  ACTIVITÉS DE LA BIBLIOTHÈQUE
          #
          'fieldG11': (Checkboxes, ''),
          'fieldG12H': (Integer, ''), 'fieldG12M': (Integer, ''), 
          'fieldG13H': (Integer, ''),'fieldG13M': (Integer, ''), 
          #
          'fieldG20W': (Integer, None), 'fieldG20X': (Integer, None),
          'fieldG20Y': (Integer, None), 
          'fieldG20Z': (Integer, None), 
          'fieldG21W': (Integer, None), 'fieldG21X': (Integer, None),
          'fieldG21Y': (Integer, None), 
          'fieldG21Z': (Integer, None), 
          'fieldG22W': (Integer, None), 'fieldG22X': (Integer, None),
          'fieldG22Y': (Integer, None), 
          'fieldG22Z': (Integer, None), 
          'fieldG23W': (Integer, None), 'fieldG23X': (Integer, None),
          'fieldG23Y': (Integer, None), 
          'fieldG23Z': (Integer, None), 
          'fieldG24W': (Integer, None), 'fieldG24X': (Integer, None),
          'fieldG24Y': (Integer, None), 
          'fieldG24Z': (Integer, None), 

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
          'fieldH11': (Boolean, ''), 'fieldH12': (Boolean, ''),
          'fieldH13': (Boolean, ''), 'fieldH14': (Boolean, ''),
          'fieldH15': (Boolean, ''),
          'fieldH16': (Boolean, '', {'depend_field' : ('fieldH17',
                                                              'fieldH18',
                                                              'fieldH19',
                                                              'fieldH20',)}),
          'fieldH17': (Integer, None), 'fieldH18': (Integer, None),
          'fieldH19': (Integer, None), 'fieldH20': (Integer, None),
          'fieldH21': (Unicode, None),
          #
          'fieldH31': (Boolean, '', 
                       {'depend_field' : ('fieldH32', 'fieldH33', 'fieldH34',
                                          'fieldH35', 'fieldH36', 'fieldH37')}),
          #
          #
          'fieldH32': (Boolean, ''),
          'fieldH33': (Boolean, ''), 'fieldH34': (Boolean, ''),
          'fieldH35': (Boolean, ''), 'fieldH36': (Boolean, ''),
          'fieldH37': (Boolean, ''),
          
          'fieldH38X': (Integer, None), 'fieldH38Y': (Integer, None),
          'fieldH38Z': (Integer, None, {'sum': ('fieldH38X', 'fieldH38Y')}),
          'fieldH39' : (Boolean, None),
          'fieldH41' : (Boolean, None, {'depend_field' : ('fieldH42',)}),
          'fieldH42': (Unicode, None), 
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
          'fieldI11': (Boolean, ''), 'fieldI12': (Boolean, ''),
          'fieldI13': (Boolean, '', 
                       {'depend_field' : ('fieldI14', 'fieldI15', 'fieldI16', 
                        'fieldI17', 'fieldI18', 'fieldI19', 'fieldI20', 
                        'fieldI21')}), 
          'fieldI14': (Integer, None),
          'fieldI15': (Integer, None), 'fieldI16': (Integer, None),
          'fieldI17': (Integer, None), 'fieldI18': (Integer, None),
          'fieldI19': (Integer, None), 'fieldI20': (Integer, None),
          'fieldI21': (Integer, None),
          #
          'fieldI31': (Boolean, None),
          'fieldI32': (Boolean, None),
          'fieldI33': (Boolean, None), 
          'fieldI34': (Boolean, None),
          #
          'fieldI35': (Boolean, '', 
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
          'fieldJ1T' :(Unicode, ''), 'fieldJ1U' :(Unicode, ''),
          'fieldJ1V' :(Unicode, ''), 'fieldJ1W' :(Unicode, ''),
          'fieldJ1X' :(Unicode, ''), 'fieldJ1Y' :(Unicode, ''), 
          'fieldJ1Z' :(Unicode, ''),
          #
          #
          'fieldJ2T' :(Unicode, ''), 'fieldJ2U' :(Unicode, ''),
          'fieldJ2V' :(Unicode, ''), 'fieldJ2W' :(Unicode, ''),
          'fieldJ2X' :(Unicode, ''), 'fieldJ2Y' :(Unicode, ''), 
          'fieldJ2Z' :(Unicode, ''),
          #
          #
          'fieldJ3T' :(Unicode, ''), 'fieldJ3U' :(Unicode, ''),
          'fieldJ3V' :(Unicode, ''), 'fieldJ3W' :(Unicode, ''),
          'fieldJ3X' :(Unicode, ''), 'fieldJ3Y' :(Unicode, ''), 
          'fieldJ3Z' :(Unicode, ''),
          #
          #
          'fieldJ4T' :(Unicode, ''), 'fieldJ4U' :(Unicode, ''),
          'fieldJ4V' :(Unicode, ''), 'fieldJ4W' :(Unicode, ''),
          'fieldJ4X' :(Unicode, ''), 'fieldJ4Y' :(Unicode, ''), 
          'fieldJ4Z' :(Unicode, ''),
          #
          #
          'fieldJ5T' :(Unicode, ''), 'fieldJ5U' :(Unicode, ''),
          'fieldJ5V' :(Unicode, ''), 'fieldJ5W' :(Unicode, ''),
          'fieldJ5X' :(Unicode, ''), 'fieldJ5Y' :(Unicode, ''), 
          'fieldJ5Z' :(Unicode, ''),
          #
          #
          'fieldJ6T' :(Unicode, ''), 'fieldJ6U' :(Unicode, ''),
          'fieldJ6V' :(Unicode, ''), 'fieldJ6W' :(Unicode, ''),
          'fieldJ6X' :(Unicode, ''), 'fieldJ6Y' :(Unicode, ''), 
          'fieldJ6Z' :(Unicode, ''),
          #
          #
          'fieldJ7T' :(Unicode, ''), 'fieldJ7U' :(Unicode, ''),
          'fieldJ7V' :(Unicode, ''), 'fieldJ7W' :(Unicode, ''),
          'fieldJ7X' :(Unicode, ''), 'fieldJ7Y' :(Unicode, ''), 
          'fieldJ7Z' :(Unicode, ''),
          #
          #
          'fieldJ8T' :(Unicode, ''), 'fieldJ8U' :(Unicode, ''),
          'fieldJ8V' :(Unicode, ''), 'fieldJ8W' :(Unicode, ''),
          'fieldJ8X' :(Unicode, ''), 'fieldJ8Y' :(Unicode, ''), 
          'fieldJ8Z' :(Unicode, ''),
          #
          #
          'fieldJ9T' :(Unicode, ''), 'fieldJ9U' :(Unicode, ''),
          'fieldJ9V' :(Unicode, ''), 'fieldJ9W' :(Unicode, ''),
          'fieldJ9X' :(Unicode, ''), 'fieldJ9Y' :(Unicode, ''), 
          'fieldJ9Z' :(Unicode, ''),
          #
          #
          'fieldJ10T' :(Unicode, ''), 'fieldJ10U' :(Unicode, ''),
          'fieldJ10V' :(Unicode, ''), 'fieldJ10W' :(Unicode, ''),
          'fieldJ10X' :(Unicode, ''), 'fieldJ10Y' :(Unicode, ''), 
          'fieldJ10Z' :(Unicode, ''),
          #
          #
          'fieldJ11T' :(Unicode, ''), 'fieldJ11U' :(Unicode, ''),
          'fieldJ11V' :(Unicode, ''), 'fieldJ11W' :(Unicode, ''),
          'fieldJ11X' :(Unicode, ''), 'fieldJ11Y' :(Unicode, ''), 
          'fieldJ11Z' :(Unicode, ''),
          #
          #
          'fieldJ12T' :(Unicode, ''), 'fieldJ12U' :(Unicode, ''),
          'fieldJ12V' :(Unicode, ''), 'fieldJ12W' :(Unicode, ''),
          'fieldJ12X' :(Unicode, ''), 'fieldJ12Y' :(Unicode, ''), 
          'fieldJ12Z' :(Unicode, ''),
          #
          #
          'fieldJ13T' :(Unicode, ''), 'fieldJ13U' :(Unicode, ''),
          'fieldJ13V' :(Unicode, ''), 'fieldJ13W' :(Unicode, ''),
          'fieldJ13X' :(Unicode, ''), 'fieldJ13Y' :(Unicode, ''), 
          'fieldJ13Z' :(Unicode, ''),
          #
          'fieldJ14T' :(Unicode, ''), 'fieldJ14U' :(Unicode, ''),
          'fieldJ14V' :(Unicode, ''), 'fieldJ14W' :(Unicode, ''),
          'fieldJ14X' :(Unicode, ''), 'fieldJ14Y' :(Unicode, ''), 
          'fieldJ14Z' :(Unicode, ''),
          #
          #
          'fieldJ15T' :(Unicode, ''), 'fieldJ15U' :(Unicode, ''),
          'fieldJ15V' :(Unicode, ''), 'fieldJ15W' :(Unicode, ''),
          'fieldJ15X' :(Unicode, ''), 'fieldJ15Y' :(Unicode, ''), 
          'fieldJ15Z' :(Unicode, ''),
          #
          # K- EPCI
          'fieldK1': (Unicode, ''), 'fieldK2': (Unicode, None),
          'fieldK3': (Checkboxes, '1'), 
          'fieldK6': (Unicode, ''),
          'fieldK7': (Unicode, ''), 'fieldK8': (Unicode, ''),
          'fieldK9': (Unicode, ''), 'fieldK10': (Unicode, ''),
          'fieldK11': (Unicode, ''), 'fieldK12': (Unicode, ''),
          'fieldK13': (Unicode, ''), 'fieldK14': (Unicode, ''),
          'fieldK15': (Unicode, ''), 'fieldK16': (Unicode, ''),
          #
          #
          'fieldK17W' :(Unicode, None),
          'fieldK17X' :(Unicode, ''),
          'fieldK17Y' :(Unicode, None),
          'fieldK17Z' :(EPCI_Statut, ''),
          #
          #
          'fieldK18W' :(Unicode, None),
          'fieldK18X' :(Unicode, ''),
          'fieldK18Y' :(Unicode, None),
          'fieldK18Z' :(EPCI_Statut, ''),
          #
          #
          'fieldK19W' :(Unicode, None),
          'fieldK19X' :(Unicode, ''),
          'fieldK19Y' :(Unicode, None),
          'fieldK19Z' :(EPCI_Statut, ''),
          #
          #
          'fieldK20W' :(Unicode, None),
          'fieldK20X' :(Unicode, ''),
          'fieldK20Y' :(Unicode, None),
          'fieldK20Z' :(EPCI_Statut, ''),
          #
          #
          'fieldK21W' :(Unicode, None),
          'fieldK21X' :(Unicode, ''),
          'fieldK21Y' :(Unicode, None),
          'fieldK21Z' :(EPCI_Statut, ''),
          #
          #
          'fieldK22W' :(Unicode, None),
          'fieldK22X' :(Unicode, ''),
          'fieldK22Y' :(Unicode, None),
          'fieldK22Z' :(EPCI_Statut, ''),
          #
          #
          'fieldK23W' :(Unicode, None),
          'fieldK23X' :(Unicode, ''),
          'fieldK23Z' :(EPCI_Statut, None),
          'fieldK23Y' :(Unicode, ''),
          #
          #
          'fieldK24W' :(Unicode, None),
          'fieldK24X' :(Unicode, ''),
          'fieldK24Y' :(Unicode, None),
          'fieldK24Z' :(EPCI_Statut, ''),
          #
          #
          'fieldK25W' :(Unicode, None),
          'fieldK25X' :(Unicode, ''),
          'fieldK25Y' :(Unicode, None),
          'fieldK25Z' :(EPCI_Statut, ''),
          #
          #
          'fieldK26W' :(Unicode, None),
          'fieldK26X' :(Unicode, ''),
          'fieldK26Y' :(Unicode, None),
          'fieldK26Z' :(EPCI_Statut, ''),
          #
          #
          'fieldK27W' :(Unicode, None),
          'fieldK27X' :(Unicode, ''),
          'fieldK27Y' :(Unicode, None),
          'fieldK27Z' :(EPCI_Statut, ''),
          #
          #
          'fieldK28W' :(Unicode, None),
          'fieldK28X' :(Unicode, ''),
          'fieldK28Y' :(Unicode, None),
          'fieldK28Z' :(EPCI_Statut, ''),
          #
          #
          'fieldK29W' :(Unicode, None),
          'fieldK29X' :(Unicode, ''),
          'fieldK29Y' :(Unicode, None),
          'fieldK29Z' :(EPCI_Statut, ''),
          #
          #
          'fieldK30W' :(Unicode, None),
          'fieldK30X' :(Unicode, ''),
          'fieldK30Y' :(Unicode, None),
          'fieldK30Z' :(EPCI_Statut, ''),
          #
          #
          'fieldK31W' :(Unicode, None),
          'fieldK31X' :(Unicode, ''),
          'fieldK31Y' :(Unicode, None),
          'fieldK31Z' :(EPCI_Statut, ''),
          ## comments form
          'fieldL20': (Unicode, ''),}


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
	       ('E', u"E73Z/E46X = prix moyen d'un document patrimonial",
                  'E73Z/E46X' ),
           ('F', u"E68Z/E51Z = prix moyen d'un périodique imprimé", 
                 'int(E68Z)/int(E51Z)' ),
           ('G', u"E74Z - 5% <= A12+A24 <= E74Z + 5% = variation à +/- 5 % des dépenses documentaires", 
                 'int(E74Z) * 0.95 < A12+A24 < int(E74Z) * 1.05' ),
           ('H', u"A11/C43X = coût moyen d'un agent pour votre bibliothèque ", 
                 'int(A11)/float(C43X)' )
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


