# -*- coding: ISO-8859-1 -*-
# Import from python
from pprint import pprint

# Import from Culture
#from schema import schema
from GenFormsTemplates import GenForms


######################################################################## 
# Form BDP 1
######################################################################## 

f1 = GenForms(encoding='latin1', filename='FormBDP_report1_autogen.xml', no_generation=True)
f1.main_header()
f1.add_h1(title=u'A- �L�MENTS FINANCIERS ( en euros, sans d�cimales)', 
          help_file='help1')
# A1
f1.add_h2(title=u'A.1 D�PENSES PROPRES A LA BDP')
data = u"""
Pour le personnel : salaires et charges,  A11
Pour les acquisitions de tous documents et abonnements A12
Pour la reliure et l'�quipement des documents A13
Pour la maintenance informatique A14
Pour l'animation (communication, impression, d�fraiement) A15
Pour la formation A16
TOTAL (A11� A16) A17"""
body, trach = f1.raw_text2lines(data=data)
f1.table(body)

# A2
f1.add_h2(title=u"""A.2 D�PENSES D'INVESTISSEMENT POUR LA BDP (hors documents)
                    : construction, �quipement, informatisation""")
data = u"""
Pour les b�timents de la BDP, centrale et annexes (construction, agrandissement, r�novation) A21
Pour le mobilier et le mat�riel (y compris achat de v�hicules) A22
Pour l'informatique (logiciel et mat�riel) A23
TOTAL (A21� A23) A24 """
body, trach = f1.raw_text2lines(data=data)
f1.table(body)

# A3
f1.add_h2(title=u"A.3 RECETTES PROPRES A LA BIBLIOTH�QUE")
data = u"""
Montant total des droits d'inscription (pr�ts directs, cotisations des communes) per�us dans l'ann�e sur budget d�partemental (hors association) A31
Montant total des autres recettes (inscription aux formations, droits de location) A32"""
body, trach = f1.raw_text2lines(data=data)
f1.table(body)
f1.main_footer()

######################################################################## 
# Form BDP 2
######################################################################## 

f2 = GenForms(encoding='latin1', filename='FormBDP_report2_autogen.xml', no_generation=True)
f2.main_header()
f2.add_h1(title=(u'B  LOCAUX - V�HICULES - �QUIPEMENT INFORMATIQUE'),
          help_file='help2')
# B1
f2.add_h2(title=(u'B.1 LOCAUX : BDP et r�seau (surface en m� SHON- '
                 u'hors oeuvre nette)'))

data = u"""
##XYZ##Centrale X##Annexes Y##Total Z
Surface de la BDP (services publics et int�rieurs confondus)   B11
Nombre de b�timents de la BDP ouverts � tous publics          B12
Nombre de m� ouverts � tous publics                           B13
"""
body, xyz_labels = f2.raw_text2lines(data=data)
f2.table(body, xyz_labels)

data = u"""
##Z##Total Z
Surface totaledes biblioth�ques du r�seau tous publics        B14
"""
body, xyz_labels = f2.raw_text2lines(data=data)
f2.table(body, xyz_labels)

f2.add_h2(title=u"B. 2 V�HICULES DE LA BDP")
data = u"""
Nombre total de bus : bibliobus ou m�diabus (musibus, artobus, etc.) B21
Dont nombre de bus faisant du pr�t direct                            B22 
Autres v�hicules (fourgonnettes, voitures l�g�res)                   B23
"""
body, xyz_labels = f2.raw_text2lines(data=data)
f2.table(body, xyz_labels)

f2.add_h2(title=u"B.3 �QUIPEMENT INFORMATIQUE (BDP et annexes)")
data = u"""
La BDP est-t-elle �quip�e d'un logiciel de gestion ?                       B31
Si oui, pr�ciser lequel:                                                              B32 
La BDP constitue-t-elle son catalogue � partir de notices import�e         B33
Si oui, quelle est la proportion des notices import�es dans votre catalogue ? (en %)  B34
pr�ciser les sources :                                                                B35
"""
body, xyz_labels = f2.raw_text2lines(data=data)
f2.table(body, xyz_labels)

f2.add_th_comment(title=u"Nombre de postes informatiques")
data = u"""##XY##Professionnels X##Publics Y
Sans acc�s internet           B36
Avec acc�s internet           B37
Total                         B38
"""
body, xyz_labels = f2.raw_text2lines(data=data)
f2.table(body, xyz_labels)

f2.add_th_comment(title=u"Dans les b�timents ouverts tous publics, l'acc�s public � internet est-il ?")
data = u"""
Enti�rement gratuit                            B39
Payant, m�me partiellement                     B40
"""
body, xyz_labels = f2.raw_text2lines(data=data)
f2.table(body, xyz_labels)

f2.main_footer()

######################################################################## 
# Form BDP 3
######################################################################## 

f3 = GenForms(encoding='latin1', filename='FormBDP_report3_autogen.xml', no_generation=True)
f3.main_header()
f3.add_h1(title=(u'C - PERSONNEL EN POSTE AU 31 D�CEMBRE 2005'),
          help_file='help3')
# B1
f3.add_h2(title=u'C.1 FONCTION PUBLIQUE : FILI�RE CULTURELLE')

data = u"""
##STUVWXYZ##Nb de personnes##Nb d'emplois d'ETP (1)##Nb de personnes ayant suivi une formation dans l'ann�e##Responsable de la biblioth�que ?(2)##Nb de personnes##Nb d'emplois d'ETP (1)##Nb de personnes ayant suivi une formation dans l'ann�e##Nb de responsables par statut
Conservateurs                         C11
Biblioth�caires                       C12
Assistants qualifi�s de conservation  C13
Assistants de conservation            C14
Agents qualifi�s du patrimoine        C15
Agents du patrimoine                  C16
"""
body, xyz_labels = f3.raw_text2lines(data=data)
f3.table(body, xyz_labels)
f3.add_th_comment(title=u"(1)ETP : Equivalent temps plein.")
f3.add_th_comment(title=u"(2) cocher la case correspondante")
f3.add_th_comment(title=u"(3) PERSONNELS OUBENEVOLES QUALIFIES : personnes ayant suivi des formations (exemple : ABF, BDP, etc)")

f3.add_h2(title=u'C.2 FONCTION PUBLIQUE : AUTRE FILI�RE')
f3.add_th_comment(title=u"Personnels d'autres fili�res (administrative, technique, sociale...)")
data = u"""
##STUVWXYZ##Nb de personnes##Nb d'emplois d'ETP (1)##Nb de personnes ayant suivi une formation dans l'ann�e##Responsable de la biblioth�que ?(2)##Nb de personnes##Nb d'emplois d'ETP (1)##Nb de personnes ayant suivi une formation dans l'ann�e##Nb de responsables par statut
Cat. A    C21
Cat. B    C22
Cat. C    C23
"""
body, xyz_labels = f3.raw_text2lines(data=data)
f3.table(body, xyz_labels)
f3.add_th_comment(title=u"(1)ETP : Equivalent temps plein.")
f3.add_th_comment(title=u"(2) cocher la case correspondante")
f3.add_th_comment(title=u"(3) PERSONNELS OUBENEVOLES QUALIFIES : personnes ayant suivi des formations (exemple : ABF, BDP, etc)")

f3.add_h2(title=u'C.3 AUTRES PERSONNELS REMUNER�S')
data = u"""
##STUVWXYZ##Nb de personnes##Nb d'emplois d'ETP (1)##Nb de personnes ayant suivi une formation dans l'ann�e##Responsable de la biblioth�que ?(2)##Nb de personnes##Nb d'emplois d'ETP (1)##Nb de personnes ayant suivi une formation dans l'ann�e##Nb de responsables par statut
Agents non titulaires/emplois non aid�s par l'Etat (contractuels,vacataires...) C31
dont personnels qualifi�s (3)                                                   C32
Agents non titulaires/ emplois aid�s par l'Etat ( C.E.S., C.E.C., C.EJ...)      C33
dont personnels qualifi�s                                                       C34
"""
body, xyz_labels = f3.raw_text2lines(data=data)
f3.table(body, xyz_labels)

f3.add_th_comment(title=u"(1)ETP : Equivalent temps plein.")
f3.add_th_comment(title=u"(2) cocher la case correspondante")
f3.add_th_comment(title=u"(3) PERSONNELS OUBENEVOLES QUALIFIES : personnes ayant suivi des formations (exemple : ABF, BDP, etc)")
f3.add_h2(title=u'C.4 B�N�VOLES')
data = u"""
##STUVWXYZ##Nb de personnes##Nb d'emplois d'ETP (1)##Nb de personnes ayant suivi une formation dans l'ann�e##Responsable de la biblioth�que ?(2)##Nb de personnes##Nb d'emplois d'ETP (1)##Nb de personnes ayant suivi une formation dans l'ann�e##Nb de responsables par statut
B�n�voles qualifi�s (3)    C41
B�n�voles non form�s       C42
TOTAL (C11 � C42)          C43
"""
body, xyz_labels = f3.raw_text2lines(data=data)
f3.table(body, xyz_labels)
f3.add_th_comment(title=u"(1)ETP : Equivalent temps plein.")
f3.add_th_comment(title=u"(2) cocher la case correspondante")
f3.add_th_comment(title=u"(3) PERSONNELS OUBENEVOLES QUALIFIES : personnes ayant suivi des formations (exemple : ABF, BDP, etc)")
f3.add_h2(title=u"C.5 NOMBRE TOTAL DE PERSONNES AYANT SUIVI UNE FIA (formation initiale d'application) ")

data = u"""
##Z##Nb de responsables par statut Z
DANS L'ANN�E :          C51
"""
body, xyz_labels = f3.raw_text2lines(data=data)
f3.table(body, xyz_labels)

# f3 is no more genarated
f3.main_footer()


######################################################################## 
# Form BDP 4
########################################################################

f4 = GenForms(encoding='latin1', filename='FormBDP_report4_autogen.xml', no_generation=True)
f4.main_header()
f4.add_h1(title=(u'D - COLLECTIONS au 31.12.(cf. notice explicative)'),
          help_file='help4')

f4.add_h2(title=u'D. 1/ D. 2  LIVRES ET AUTRES DOCUMENTS (hors p�riodiques)')

data = u"""
##XYZ##BDP X##R�seau public Y##Total Z
Livres adultes                            D11
Livres enfants                            D12
TOTAL des livres (D11+D12)                D13
Phonogrammes adultes (tous supports)      D14
Phonogrammes enfants (tous supports)      D15
TOTAL des phonogrammes (D14 + D15)        D16
Vid�ogrammes adultes (tous supports)      D17
Vid�ogrammes enfants (tous supports)      D18
TOTAL des vid�ogrammes (D17 + D18)        D19
C�d�roms adultes                          D20
C�d�roms enfants                          D21
TOTAL des c�d�roms (D20 = D21)            D22
Autres documents                          D23
Bases de donn�es                          D24
"""
body, xyz_labels = f4.raw_text2lines(data=data)
f4.table(body, xyz_labels)

f4.add_h2(title=u'D.3 P�RIODIQUES')
data = u"""
Nombre de titres de p�riodiques conserv�s (titres morts ou courants) D31
Nombre d'unit�s mat�rielles                                          D32
"""
body, trach = f4.raw_text2lines(data=data)
f4.table(body)
f4.main_footer()



######################################################################## 
# Form BDP 5
########################################################################

f5 = GenForms(encoding='latin1',
              filename='FormBDP_report5_autogen.xml',
              no_generation=True )
f5.main_header()
f5.add_h1(title=(u"E- ACQUISITIONS ET �LIMINATIONS DE L'ANN�E(cf. notice explicative)"),
          help_file='help5')

f5.add_h2(title=u"E. 1 / 2 NOMBRE DE DOCUMENTS ACHET�S  (hors p�riodiques)")
data = u"""
##XYZ##BDP X##R�seau public Y##Total Z
Livres adultes                         E11
Livres enfants                         E12
TOTAL des livres (E11+E12)             E13
Phonogrammes adultes (tous supports)   E14
Phonogrammes enfants (tous supports)   E15
TOTAL des phonogrammes (E14 + E15)     E16
Vid�ogrammes adultes (tous supports)   E17
Vid�ogrammes enfants (tous supports)   E18
TOTAL des vid�ogrammes (E17 + E18)     E19
C�d�roms adultes                       E20
C�d�roms enfants                       E21
TOTAL des c�d�roms (E20 + E21)         E22
Autres documents                       E23
"""
body, xyz_labels = f5.raw_text2lines(data=data)
f5.table(body, xyz_labels)

f5.add_h2(title=u"E. 3 / 4  NOMBRE DE DOCUMENTS ENTR�S PAR DONS, LEGS   (hors p�riodiques )")
data = u"""
##XYZ##BDP X##R�seau public Y##Total Z
Livres adultes                         E31
Livres enfants                         E32
TOTAL des livres (E31+E32)             E33
Phonogrammes adultes (tous supports)   E34
Phonogrammes enfants (tous supports)   E35
TOTAL des phonogrammes                 E36
Vid�ogrammes adultes (tous supports)   E37
Vid�ogrammes enfants (tous supports)   E38
TOTAL des vid�ogrammes                 E39
C�d�roms adultes                       E40
C�d�roms enfants                       E41
TOTAL des c�d�roms                     E42
Autres documents                       E43
"""
body, xyz_labels = f5.raw_text2lines(data=data)
f5.table(body, xyz_labels)

f5.add_h2(title=u"E. 5 / 6  NOMBRE DE DOCUMENTS RETIR�S DE L'INVENTAIRE (hors p�riodiques et documents patrimoniaux)")
data = u"""
##XYZ##BDP X##R�seau public Y##Total Z
Livres adultes                          E51
Livres enfants                          E52
TOTAL des livres (E31+E32)              E53
Phonogrammes adultes (tous supports)    E54
Phonogrammes enfants (tous supports)    E55
TOTAL des phonogrammes (E54 + E55)      E56
Vid�ogrammes adultes (tous supports)    E57
Vid�ogrammes enfants (tous supports)    E58
TOTAL des vid�ogrammes (E57 + E58)      E59
C�d�roms adultes                        E60
C�d�roms enfants                        E61
TOTAL des c�d�roms (E60 + E61)          E62
Autres documents                        E63
"""
body, xyz_labels = f5.raw_text2lines(data=data)
f5.table(body, xyz_labels)

f5.add_h2(title=u"E. 7  NOMBRE DE P�RIODIQUES ACQUIS (ACH�TS, DONS, LEGS?)")
data = u"""
##XYZ##BDP X##R�seau public Y##Total Z
Nombre d'abonnements en cours ( payants et gratuits, support imprim� ou microforme)  E71
Nombre de fascicules                                                                 E72
Nombre d'abonnements en cours sur c�d�roms ou en ligne                               E73
"""
body, xyz_labels = f5.raw_text2lines(data=data)
f5.table(body, xyz_labels)


f5.add_h2(title=u"E. 8  NOMBRE DE P�RIODIQUES RETIR�S DE L'INVENTAIREE.")
data = u"""
##XYZ##BDP X##R�seau public Y##Total Z
Nombre d'abonnements supprim�s                       E81
Nombre de fascicules retir�s                         E82
"""
body, xyz_labels = f5.raw_text2lines(data=data)
f5.table(body, xyz_labels)


f5.add_h2(title=u"E. 8 / 9  D�PENSES D'ACQUISITION(en euros, sans  d�cimale)")
data = u"""
##XYZ##BDP X##R�seau public Y##Total Z
Livres adultes                          E83
Livres enfants                          E84
TOTAL des livres (E83 + E84 )           E85
Phonogrammes adultes                    E86
Phonogrammes enfants                    E87
TOTAL des phonogrammes (E86 + E87)      E88
Vid�ogrammes adultes                    E89
Vid�ogrammes enfants                    E90
TOTAL des vid�ogrammes (E89 + E90)      E91
C�d�roms adultes                        E92
C�d�roms enfants                        E93
TOTAL des c�d�roms (E92 + E93)          E94
Autres documents                        E95
P�riodiques imprim�s                    E96
P�riodiques sur c�d�roms ou en ligne    E97
TOTAL                                   E98
"""
body, xyz_labels = f5.raw_text2lines(data=data)
f5.table(body, xyz_labels)

f5.main_footer()

######################################################################## 
# Form BDP 6
########################################################################

f6 = GenForms(encoding='latin1', filename='FormBDP_report6_autogen.xml', no_generation=True)
f6.main_header()
f6.add_h1(title=(u"F-  R�SEAU TOUS PUBLICS"),
          help_file='help6')

f6.add_h2(title=u"F.1 / 2 DESSERTE DU R�SEAU TOUS PUBLICS (cf. notice explicative)")
data = u"""
##WXY##Nombre de points W##Nombre de commune X##Population desservie Y
Biblioth�ques municipales niveau 1            F11
Biblioth�ques municipales niveau 2            F12
Biblioth�ques relais niveau 3                 F13
Point-lecture                                 F14
Autres d�p�ts tous publics                    F15
TOTAL (F11 � F15)                             F16
Arr�ts bibliobus-m�diabus pr�t direct         F17
TOTAL (F16 + F17)                             F18
"""
body, xyz_labels = f6.raw_text2lines(data=data)
f6.table(body, xyz_labels)
f6.add_th_comment(title=u"Dont :")
data = u"""
##XY##Nombre de commune X##Population desservie Y
communes de + 10 000 habitants                       F19
groupements de communes de + 10 000 habitants        F20
"""
body, xyz_labels = f6.raw_text2lines(data=data)
f6.table(body, xyz_labels)

data = u"""
##XY##Nombre de commune X##Population desservie Y
communes desservies par plusieurs modes de desserte (ex BM + pr�t direct)  F21
"""
body, xyz_labels = f6.raw_text2lines(data=data)
f6.table(body, xyz_labels)

f6.add_h2(title=u"F. 3 D�P�TS DE LA BDP")
data = u"""
##YZ##Nombre de documents d�pos�s dans l'ann�e Y##Nombre de documents en d�p�t au 31.12. Z
Imprim�s adultes                            F31
Imprim�s enfants                            F32
TOTAL ( F31 + F32)                          F33
Phonogrammes                                F34
Vid�ogrammes                                F35
C�d�roms                                    F36
Autres documents                            F37
TOTAL (F33 � F37 )                          F38
"""
body, xyz_labels = f6.raw_text2lines(data=data)
f6.table(body, xyz_labels)

f6.add_h2(title=u"F. 4 BIBLIOTH�QUES AYANT FOURNI DES STATISTIQUES")
data = u"""
##WXY##Nombre de points W##Nombre de communes  X##Population desservie Y
Biblioth�ques niveau 1                                 F41
Biblioth�ques niveau 2                                 F42 
Biblioth�ques-relais niveau 3                          F43 
Points-lecture                                         F44
D�p�ts tous publics                                    F45  
TOTAL (F41 � F45  )                                    F46
"""
body, xyz_labels = f6.raw_text2lines(data=data)
f6.table(body, xyz_labels)

f6.add_h2(title=u"F. 5 ACTIVIT�S DU R�SEAU TOUS PUBLICS : INSCRITS")
f6.add_th_comment(title=u"Nombre d'inscrits enfants")
data = u"""
##WXYZ##BDP/Annexes ouvertes � tous publics W##Bibliobus de pr�ts direct X##R�seau public Y##Total Z
0-14 ans                                F51
"""
body, xyz_labels = f6.raw_text2lines(data=data)
f6.table(body, xyz_labels)
f6.add_th_comment(title=u"Nombre d'inscrits adultes")
data = u"""
##WXYZ##BDP/Annexes ouvertes � tous publics W##Bibliobus de pr�ts direct X##R�seau public Y##Total Z
15-24 ans                             F52
25-59 ans                             F53
60 ans et +                           F54
TOTAL Adultes                         F55
TOTAL DES INSCRITS (F51 + F55)        F56
"""
body, xyz_labels = f6.raw_text2lines(data=data)
f6.table(body, xyz_labels)

f6.add_h2(title=u"F. 6 ACTIVIT�S DU R�SEAU TOUS PUBLICS : NOMBRE DE PR�TS (1)")
data = u"""
##WXYZ##BDP/Annexes ouvertes � tous publics W##Bibliobus de pr�ts direct X##R�seau public Y##Total Z
Pr�ts de livres adultes                       F61
Pr�ts de livres enfants                       F62
TOTAL (F61+F62)                               F63
Pr�ts de p�riodiques                          F64
Pr�ts de phonogrammes                         F65
Pr�ts de vid�ogrammes                         F66
Pr�ts de disques optiques num�riques          F67
Pr�ts d'autres documents                      F68
TOTAL DES PR�TS (F63 � F68)                   F69
"""
body, xyz_labels = f6.raw_text2lines(data=data)
f6.table(body, xyz_labels)

f6.main_footer()


######################################################################## 
# Form BDP 7
########################################################################

f7 = GenForms(encoding='latin1', filename='FormBDP_report7_autogen.xml', no_generation=True)
f7.main_header()
f7.add_h1(title=(u"G-  R�SEAU SP�CIFIQUE (cf. notice explicative)"),
          help_file='help7')

f7.add_h2(title=u"G.1 / 2 D�P�TS DANS LES COLLECTIVIT�S (Public sp�cifique)")
data = u"""
##VWXYZ##Nb de collectivit�s V##Nb de documents d�pos�s dans l'ann�e W##Nb de documents X##Nb d'inscrits Y##Nb de pr�ts
Ecoles                                     G11
Coll�ges                                   G12
Lyc�es                                     G13
Prisons                                    G14
H�pitaux                                   G15
Maisons de retraite                        G16
Comit� d'entreprise                        G17
Petite enfance (cr�che, PMI)               G18
Centres sociaux, foyers ruraux             G19
Centres de vacances et de loisirs          G20
Autres                                     G21
TOTAL (G11 � G21)                          G22
"""
body, xyz_labels = f7.raw_text2lines(data=data)
f7.table(body, xyz_labels)

f7.add_h2(title=u"G. 3 / 4 PR�T DIRECT (Public sp�cifique)")
data = u"""
##XYZ##Nb de lieux de stationnement X##Nb d'inscrits Y##Nb de pr�ts Z
Ecoles                                     G31
Coll�ges                                   G32
Lyc�es                                     G33
Prisons                                    G34
H�pitaux                                   G35
Maisons de retraite                        G36
Comit� d'entreprise                        G37
Petite enfance (cr�che, PMI)               G38
Centres sociaux, foyers ruraux             G39
Centres de vacances et de loisirs          G40
Autres                                     G41
TOTAL (G31 � G41)                          G42
"""
body, xyz_labels = f7.raw_text2lines(data=data)
f7.table(body, xyz_labels)
f7.main_footer()

######################################################################## 
# Form BDP 8
########################################################################

f8 = GenForms(encoding='latin1', filename='FormBDP_report8_autogen.xml', no_generation=True)
f8.main_header()
f8.add_h1(title=(u"H. SERVICES (cf. notice explicative)"),
          help_file='help8')
f8.add_h2(title=u"H. 1 SERVICES � DISTANCE POUR LES BIBLIOTH�QUES DU R�SEAU")
data = u"""
La biblioth�que a-t-elle un site Web?:    H11
"""
body, xyz_labels = f8.raw_text2lines(data=data)
f8.table(body, xyz_labels)
f8.add_th_comment(title=u"Si oui : adresse URL � pr�ciser en 1�re page")
data = u"""
Ce site donne-t-il acc�s au catalogue de la biblioth�que?   H12

"""
body, xyz_labels = f8.raw_text2lines(data=data)
f8.table(body, xyz_labels)
f8.add_th_comment(title=u"Quels services sont offerts aux biblioth�ques du r�seau sur le site web? (cocher les cases)")
data = u"""
consultation du catalogue                      H13
R�servation en ligne                           H14
Consultation du compte lecteur                 H15
Autres (pr�ciser)                              H16
"""
body, xyz_labels = f8.raw_text2lines(data=data)
f8.table(body, xyz_labels)
data = u"""
Nb de sessions/an (� distance)        H17
Nb de pages vues/an (� distance)      H18
"""
body, xyz_labels = f8.raw_text2lines(data=data)
f8.table(body, xyz_labels)

f8.add_h2(title=u"H. 2 COOP�RATION, R�SEAU")
data = u"""
La BDP organise-t-elle un catalogue collectif d�partemental ?    H21
Si oui, pr�ciser le nb de biblioth�ques participantes                       H22
La BDP utilise-t-elle un logiciel pour l'�valuation de son r�seau ?  H23
Si oui, pr�ciser lequel                                                     H24 
La BDP appartient-elle � un r�seau documentaire autre que le r�seau qu'elle d�ssert ?  H25
Si oui, pr�ciser lequel                                                     H26 
La BDP a-t-elle men�e des actions internationales ?         H27

"""
body, xyz_labels = f8.raw_text2lines(data=data)
f8.table(body, xyz_labels)


f8.add_th_comment(title=u"Si oui, cocher les cases correspondantes")
data = u"""
Voyage d'�tude, expertise � l'�tranger   H28
Don de livres                            H29
"""
body, xyz_labels = f8.raw_text2lines(data=data)
f8.table(body, xyz_labels)

f8.add_h2(title=u"H. 3 SUBVENTIONS D�PARTEMENTALES AUX COLLECTIVIT�S DANS L'ANN�E")
data = u"""##VWXYZ##Subventions du conseil  g�n�ral V##Nb de communes aid�es inf. � 10000h W##Montant des aides vers�es X##Nombre de communes aid�es sup. � 10000h Y##Montant des aides vers�es Z
Construction                                    H31
Am�nagement                                     H32
Informatisation                                 H33
Equipement multimedia                           H34
"""
body, xyz_labels = f8.raw_text2lines(data=data)
f8.table(body, xyz_labels)

data = u"""##VWXYZ##Subventions du conseil  g�n�ral V##Nb de communes aid�es inf. � 10000h W##Montant des aides vers�es X##Nombre de communes aid�es sup. � 10000h Y##Montant des aides vers�es Z
 Acquisition de documents : Imprim�s          H35
 Acquisition de documents : Phonogrammes      H36
 Acquisition de documents : Multmedia         H37
Animation                                     H38
Emplois                                       H39
"""
body, xyz_labels = f8.raw_text2lines(data=data)
f8.table(body, xyz_labels)

f8.add_h2(title=u"H. 4 CONSEILS DE LA BDP AUX COLLECTIVIT�S DANS L'ANN�E")
data = u"""##XYZ##Conseils, aides et assistance BDP X##Nombre de communes aid�es inf. � 10000h Y##Nombre de communes aid�es sup. � 10000h Z
Construction                                  H41
Am�nagement                                   H42
Informatisation                               H43
Equipement multimedia                         H44
"""
body, xyz_labels = f8.raw_text2lines(data=data)
f8.table(body, xyz_labels)

data = u"""##XYZ##Conseils, aides et assistance BDP X##Nombre de communes aid�es inf. � 10000h Y##Nombre de communes aid�es sup. � 10000h Z 
 Acquisition de documents : Imprim�s          H45
 Acquisition de documents : Phonogrammes      H46
 Acquisition de documents : Multmedia         H47
"""
body, xyz_labels = f8.raw_text2lines(data=data)
f8.table(body, xyz_labels)

data = u"""##XYZ##Conseils, aides et assistance BDP X##Nombre de communes aid�es inf. � 10000h Y##Nombre de communes aid�es sup. � 10000h Z 
Animation                      H48
Emplois                        H49
"""
body, xyz_labels = f8.raw_text2lines(data=data)
f8.table(body, xyz_labels)

f8.add_h2(title=u"H. 5 - SERVICES AU R�SEAU (r�seau public et sp�cifique)")
f8.add_h2(title=u"Services particuliers au r�seau")
f8.add_th_comment(title=u"La BDP offre-t-elle ces services ?")

data = u"""
R�servation                      H51
"""
body, xyz_labels = f8.raw_text2lines(data=data)
f8.table(body, xyz_labels)
f8.add_th_comment(title=u"Si oui")
data = u"""
Nb de demandes re�ues                   H52
Nb de demandes satisfaites              H53
"""
body, xyz_labels = f8.raw_text2lines(data=data)
f8.table(body, xyz_labels)

data = u"""
Portage de documents par navette          H54
Pr�t Inter Biblioth�ques                  H55
"""
body, xyz_labels = f8.raw_text2lines(data=data)
f8.table(body, xyz_labels)

f8.add_th_comment(title=u"Si oui")
data = u"""
Nb de demandes re�ues                   H56
Nb de demandes satisfaites              H57
"""
body, xyz_labels = f8.raw_text2lines(data=data)
f8.table(body, xyz_labels)

data = u"""
Pr�t d'expositions                                                    H58
Pr�t de valises th�matiques                                           H59
Pr�t de mat�riel d'animation                                          H60  
Groupements d'achats (mat�riel, documents)                            H61
Comit�s de lecture, offices en consultation pour les biblioth�ques du r�seau   H62
Autre                                                      H63
Si oui, pr�ciser                                           H74
"""
body, xyz_labels = f8.raw_text2lines(data=data)
f8.table(body, xyz_labels)

f8.add_h2(title=u"Formations pour les partenaires du r�seau dans l'ann�e")
data = u"""
Nombre de th�mes formations diff�rents propos�s            H64
"""
body, xyz_labels = f8.raw_text2lines(data=data)
f8.table(body, xyz_labels)

f8.add_th_comment(title=u"Formations organis�es par la BDP")
data = u"""##YZ##Nombre de participants Y##Nb  de journ�es Z
Formation de base BDP               H65
Formation ABF                       H66
Formation continue                  H67
Voyage d'�tude                      H68 
TOTAL                               H69
"""
body, xyz_labels = f8.raw_text2lines(data=data)
f8.table(body, xyz_labels)
data = u"""
La BDP organise-t-telle des formations sur place dans les biblioth�ques du r�seau ?  H70
Si oui, combien de jours                                H71
La BDP organise-t-elle des r�unions de secteur avec les m�diath�ques du r�seau ?  H72
Si oui, combien                                         H73
"""
body, xyz_labels = f8.raw_text2lines(data=data)
f8.table(body, xyz_labels)

# f8 is no more genarated
f8.main_footer()

######################################################################## 
# Form BDP 9
########################################################################

f9 = GenForms(encoding='latin1', filename='FormBDP_report9_autogen.xml', no_generation=True)
f9.main_header()
f9.add_h1(title=(u"I - ACTIONS CULTURELLES(cf. notice explicative)."),
          help_file='help9')

f9.add_h2(title=u"I.1 ANIMATIONS")
data = u"""
La BDP a-t-elle (co-) organis� des manifestations culturelles dans l'ann�e?:    I11
"""
body, xyz_labels = f9.raw_text2lines(data=data)
f9.table(body, xyz_labels)
f9.add_th_comment(title=u"Si oui combien :")
data = u"""
F�te/salon du livre           I12
Exposition                    I13
Conf�rences                   I14
Rencontres d'auteurs/lectures I15
Ateliers d'�criture           I16
Festival                      I17
Conteurs                      I18
Concerts                      I19
Autres                        I20
"""
body, xyz_labels = f9.raw_text2lines(data=data)
f9.table(body, xyz_labels)

f9.add_h2(title=u"I.2 PUBLICATIONS")
data = u"""
La BDP a-t-elle publi� des documents dans l'ann�e ?  I21
"""
body, xyz_labels = f9.raw_text2lines(data=data)
f9.table(body, xyz_labels)
f9.add_th_comment(title=u"si oui, pr�ciser combien de titres ou de fascicules :")
data = u"""
Bulletin d'information                             I22
Guide du d�positaire                               I23
Annuaire des biblioth�ques                         I24
Catalogue des formations                           I25
Catalogue des expositions et valises th�matiques   I26
Bibliographies s�lectives                          I27
Autres                                             I28
"""
body, xyz_labels = f9.raw_text2lines(data=data)
f9.table(body, xyz_labels)

f9.add_h2(title=u"I.3 FORMATIONS HORS R�SEAU")
data = u"""
Nombre d'heures de cours assur�es par le personnel  (ENSSIB, CRFCB, ABF, CNFPT, BDP, ?) I31
"""
body, xyz_labels = f9.raw_text2lines(data=data)
f9.table(body, xyz_labels)


data = u"""##Z##Nb de stagiaires  Z
Professionnels                I32
Hors professionnels           I33
TOTAL                         I34
"""
body, xyz_labels = f9.raw_text2lines(data=data)
f9.table(body, xyz_labels)

f9.main_footer()
print ''
