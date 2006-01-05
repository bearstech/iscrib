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
f1.add_h1(title=u'A- ÉLÉMENTS FINANCIERS ( en euros, sans décimales)', 
          help_file='help1')
# A1
f1.add_h2(title=u'A.1 DÉPENSES PROPRES A LA BDP')
data = u"""
Pour le personnel : salaires et charges,  A11
Pour les acquisitions de tous documents et abonnements A12
Pour la reliure et l'équipement des documents A13
Pour la maintenance informatique A14
Pour l'animation (communication, impression, défraiement) A15
Pour la formation A16
TOTAL (A11à A16) A17"""
body, trach = f1.raw_text2lines(data=data)
f1.table(body)

# A2
f1.add_h2(title=u"""A.2 DÉPENSES D'INVESTISSEMENT POUR LA BDP (hors documents)
                    : construction, équipement, informatisation""")
data = u"""
Pour les bâtiments de la BDP, centrale et annexes (construction, agrandissement, rénovation) A21
Pour le mobilier et le matériel (y compris achat de véhicules) A22
Pour l'informatique (logiciel et matériel) A23
TOTAL (A21à A23) A24 """
body, trach = f1.raw_text2lines(data=data)
f1.table(body)

# A3
f1.add_h2(title=u"A.3 RECETTES PROPRES A LA BIBLIOTHÈQUE")
data = u"""
Montant total des droits d'inscription (prêts directs, cotisations des communes) perçus dans l'année sur budget départemental (hors association) A31
Montant total des autres recettes (inscription aux formations, droits de location) A32"""
body, trach = f1.raw_text2lines(data=data)
f1.table(body)
f1.main_footer()

######################################################################## 
# Form BDP 2
######################################################################## 

f2 = GenForms(encoding='latin1', filename='FormBDP_report2_autogen.xml', no_generation=True)
f2.main_header()
f2.add_h1(title=(u'B  LOCAUX - VÉHICULES - ÉQUIPEMENT INFORMATIQUE'),
          help_file='help2')
# B1
f2.add_h2(title=(u'B.1 LOCAUX : BDP et réseau (surface en m² SHON- '
                 u'hors oeuvre nette)'))

data = u"""
##XYZ##Centrale X##Annexes Y##Total Z
Surface de la BDP (services publics et intérieurs confondus)   B11
Nombre de bâtiments de la BDP ouverts à tous publics          B12
Nombre de m² ouverts à tous publics                           B13
"""
body, xyz_labels = f2.raw_text2lines(data=data)
f2.table(body, xyz_labels)

data = u"""
##Z##Total Z
Surface totaledes bibliothèques du réseau tous publics        B14
"""
body, xyz_labels = f2.raw_text2lines(data=data)
f2.table(body, xyz_labels)

f2.add_h2(title=u"B. 2 VÉHICULES DE LA BDP")
data = u"""
Nombre total de bus : bibliobus ou médiabus (musibus, artobus, etc.) B21
Dont nombre de bus faisant du prêt direct                            B22 
Autres véhicules (fourgonnettes, voitures légères)                   B23
"""
body, xyz_labels = f2.raw_text2lines(data=data)
f2.table(body, xyz_labels)

f2.add_h2(title=u"B.3 ÉQUIPEMENT INFORMATIQUE (BDP et annexes)")
data = u"""
La BDP est-t-elle équipée d'un logiciel de gestion ?                       B31
Si oui, préciser lequel:                                                              B32 
La BDP constitue-t-elle son catalogue à partir de notices importée         B33
Si oui, quelle est la proportion des notices importées dans votre catalogue ? (en %)  B34
préciser les sources :                                                                B35
"""
body, xyz_labels = f2.raw_text2lines(data=data)
f2.table(body, xyz_labels)

f2.add_th_comment(title=u"Nombre de postes informatiques")
data = u"""##XY##Professionnels X##Publics Y
Sans accès internet           B36
Avec accès internet           B37
Total                         B38
"""
body, xyz_labels = f2.raw_text2lines(data=data)
f2.table(body, xyz_labels)

f2.add_th_comment(title=u"Dans les bâtiments ouverts tous publics, l'accès public à internet est-il ?")
data = u"""
Entièrement gratuit                            B39
Payant, même partiellement                     B40
"""
body, xyz_labels = f2.raw_text2lines(data=data)
f2.table(body, xyz_labels)

f2.main_footer()

######################################################################## 
# Form BDP 3
######################################################################## 

f3 = GenForms(encoding='latin1', filename='FormBDP_report3_autogen.xml', no_generation=True)
f3.main_header()
f3.add_h1(title=(u'C - PERSONNEL EN POSTE AU 31 DÉCEMBRE 2005'),
          help_file='help3')
# B1
f3.add_h2(title=u'C.1 FONCTION PUBLIQUE : FILIÈRE CULTURELLE')

data = u"""
##STUVWXYZ##Nb de personnes##Nb d'emplois d'ETP (1)##Nb de personnes ayant suivi une formation dans l'année##Responsable de la bibliothèque ?(2)##Nb de personnes##Nb d'emplois d'ETP (1)##Nb de personnes ayant suivi une formation dans l'année##Nb de responsables par statut
Conservateurs                         C11
Bibliothécaires                       C12
Assistants qualifiés de conservation  C13
Assistants de conservation            C14
Agents qualifiés du patrimoine        C15
Agents du patrimoine                  C16
"""
body, xyz_labels = f3.raw_text2lines(data=data)
f3.table(body, xyz_labels)
f3.add_th_comment(title=u"(1)ETP : Equivalent temps plein.")
f3.add_th_comment(title=u"(2) cocher la case correspondante")
f3.add_th_comment(title=u"(3) PERSONNELS OUBENEVOLES QUALIFIES : personnes ayant suivi des formations (exemple : ABF, BDP, etc)")

f3.add_h2(title=u'C.2 FONCTION PUBLIQUE : AUTRE FILIÈRE')
f3.add_th_comment(title=u"Personnels d'autres filières (administrative, technique, sociale...)")
data = u"""
##STUVWXYZ##Nb de personnes##Nb d'emplois d'ETP (1)##Nb de personnes ayant suivi une formation dans l'année##Responsable de la bibliothèque ?(2)##Nb de personnes##Nb d'emplois d'ETP (1)##Nb de personnes ayant suivi une formation dans l'année##Nb de responsables par statut
Cat. A    C21
Cat. B    C22
Cat. C    C23
"""
body, xyz_labels = f3.raw_text2lines(data=data)
f3.table(body, xyz_labels)
f3.add_th_comment(title=u"(1)ETP : Equivalent temps plein.")
f3.add_th_comment(title=u"(2) cocher la case correspondante")
f3.add_th_comment(title=u"(3) PERSONNELS OUBENEVOLES QUALIFIES : personnes ayant suivi des formations (exemple : ABF, BDP, etc)")

f3.add_h2(title=u'C.3 AUTRES PERSONNELS REMUNERÉS')
data = u"""
##STUVWXYZ##Nb de personnes##Nb d'emplois d'ETP (1)##Nb de personnes ayant suivi une formation dans l'année##Responsable de la bibliothèque ?(2)##Nb de personnes##Nb d'emplois d'ETP (1)##Nb de personnes ayant suivi une formation dans l'année##Nb de responsables par statut
Agents non titulaires/emplois non aidés par l'Etat (contractuels,vacataires...) C31
dont personnels qualifiés (3)                                                   C32
Agents non titulaires/ emplois aidés par l'Etat ( C.E.S., C.E.C., C.EJ...)      C33
dont personnels qualifiés                                                       C34
"""
body, xyz_labels = f3.raw_text2lines(data=data)
f3.table(body, xyz_labels)

f3.add_th_comment(title=u"(1)ETP : Equivalent temps plein.")
f3.add_th_comment(title=u"(2) cocher la case correspondante")
f3.add_th_comment(title=u"(3) PERSONNELS OUBENEVOLES QUALIFIES : personnes ayant suivi des formations (exemple : ABF, BDP, etc)")
f3.add_h2(title=u'C.4 BÉNÉVOLES')
data = u"""
##STUVWXYZ##Nb de personnes##Nb d'emplois d'ETP (1)##Nb de personnes ayant suivi une formation dans l'année##Responsable de la bibliothèque ?(2)##Nb de personnes##Nb d'emplois d'ETP (1)##Nb de personnes ayant suivi une formation dans l'année##Nb de responsables par statut
Bénévoles qualifiés (3)    C41
Bénévoles non formés       C42
TOTAL (C11 à C42)          C43
"""
body, xyz_labels = f3.raw_text2lines(data=data)
f3.table(body, xyz_labels)
f3.add_th_comment(title=u"(1)ETP : Equivalent temps plein.")
f3.add_th_comment(title=u"(2) cocher la case correspondante")
f3.add_th_comment(title=u"(3) PERSONNELS OUBENEVOLES QUALIFIES : personnes ayant suivi des formations (exemple : ABF, BDP, etc)")
f3.add_h2(title=u"C.5 NOMBRE TOTAL DE PERSONNES AYANT SUIVI UNE FIA (formation initiale d'application) ")

data = u"""
##Z##Nb de responsables par statut Z
DANS L'ANNÉE :          C51
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

f4.add_h2(title=u'D. 1/ D. 2  LIVRES ET AUTRES DOCUMENTS (hors périodiques)')

data = u"""
##XYZ##BDP X##Réseau public Y##Total Z
Livres adultes                            D11
Livres enfants                            D12
TOTAL des livres (D11+D12)                D13
Phonogrammes adultes (tous supports)      D14
Phonogrammes enfants (tous supports)      D15
TOTAL des phonogrammes (D14 + D15)        D16
Vidéogrammes adultes (tous supports)      D17
Vidéogrammes enfants (tous supports)      D18
TOTAL des vidéogrammes (D17 + D18)        D19
Cédéroms adultes                          D20
Cédéroms enfants                          D21
TOTAL des cédéroms (D20 = D21)            D22
Autres documents                          D23
Bases de données                          D24
"""
body, xyz_labels = f4.raw_text2lines(data=data)
f4.table(body, xyz_labels)

f4.add_h2(title=u'D.3 PÉRIODIQUES')
data = u"""
Nombre de titres de périodiques conservés (titres morts ou courants) D31
Nombre d'unités matérielles                                          D32
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
f5.add_h1(title=(u"E- ACQUISITIONS ET ÉLIMINATIONS DE L'ANNÉE(cf. notice explicative)"),
          help_file='help5')

f5.add_h2(title=u"E. 1 / 2 NOMBRE DE DOCUMENTS ACHETÉS  (hors périodiques)")
data = u"""
##XYZ##BDP X##Réseau public Y##Total Z
Livres adultes                         E11
Livres enfants                         E12
TOTAL des livres (E11+E12)             E13
Phonogrammes adultes (tous supports)   E14
Phonogrammes enfants (tous supports)   E15
TOTAL des phonogrammes (E14 + E15)     E16
Vidéogrammes adultes (tous supports)   E17
Vidéogrammes enfants (tous supports)   E18
TOTAL des vidéogrammes (E17 + E18)     E19
Cédéroms adultes                       E20
Cédéroms enfants                       E21
TOTAL des cédéroms (E20 + E21)         E22
Autres documents                       E23
"""
body, xyz_labels = f5.raw_text2lines(data=data)
f5.table(body, xyz_labels)

f5.add_h2(title=u"E. 3 / 4  NOMBRE DE DOCUMENTS ENTRÉS PAR DONS, LEGS   (hors périodiques )")
data = u"""
##XYZ##BDP X##Réseau public Y##Total Z
Livres adultes                         E31
Livres enfants                         E32
TOTAL des livres (E31+E32)             E33
Phonogrammes adultes (tous supports)   E34
Phonogrammes enfants (tous supports)   E35
TOTAL des phonogrammes                 E36
Vidéogrammes adultes (tous supports)   E37
Vidéogrammes enfants (tous supports)   E38
TOTAL des vidéogrammes                 E39
Cédéroms adultes                       E40
Cédéroms enfants                       E41
TOTAL des cédéroms                     E42
Autres documents                       E43
"""
body, xyz_labels = f5.raw_text2lines(data=data)
f5.table(body, xyz_labels)

f5.add_h2(title=u"E. 5 / 6  NOMBRE DE DOCUMENTS RETIRÉS DE L'INVENTAIRE (hors périodiques et documents patrimoniaux)")
data = u"""
##XYZ##BDP X##Réseau public Y##Total Z
Livres adultes                          E51
Livres enfants                          E52
TOTAL des livres (E31+E32)              E53
Phonogrammes adultes (tous supports)    E54
Phonogrammes enfants (tous supports)    E55
TOTAL des phonogrammes (E54 + E55)      E56
Vidéogrammes adultes (tous supports)    E57
Vidéogrammes enfants (tous supports)    E58
TOTAL des vidéogrammes (E57 + E58)      E59
Cédéroms adultes                        E60
Cédéroms enfants                        E61
TOTAL des cédéroms (E60 + E61)          E62
Autres documents                        E63
"""
body, xyz_labels = f5.raw_text2lines(data=data)
f5.table(body, xyz_labels)

f5.add_h2(title=u"E. 7  NOMBRE DE PÉRIODIQUES ACQUIS (ACHÂTS, DONS, LEGS?)")
data = u"""
##XYZ##BDP X##Réseau public Y##Total Z
Nombre d'abonnements en cours ( payants et gratuits, support imprimé ou microforme)  E71
Nombre de fascicules                                                                 E72
Nombre d'abonnements en cours sur cédéroms ou en ligne                               E73
"""
body, xyz_labels = f5.raw_text2lines(data=data)
f5.table(body, xyz_labels)


f5.add_h2(title=u"E. 8  NOMBRE DE PÉRIODIQUES RETIRÉS DE L'INVENTAIREE.")
data = u"""
##XYZ##BDP X##Réseau public Y##Total Z
Nombre d'abonnements supprimés                       E81
Nombre de fascicules retirés                         E82
"""
body, xyz_labels = f5.raw_text2lines(data=data)
f5.table(body, xyz_labels)


f5.add_h2(title=u"E. 8 / 9  DÉPENSES D'ACQUISITION(en euros, sans  décimale)")
data = u"""
##XYZ##BDP X##Réseau public Y##Total Z
Livres adultes                          E83
Livres enfants                          E84
TOTAL des livres (E83 + E84 )           E85
Phonogrammes adultes                    E86
Phonogrammes enfants                    E87
TOTAL des phonogrammes (E86 + E87)      E88
Vidéogrammes adultes                    E89
Vidéogrammes enfants                    E90
TOTAL des vidéogrammes (E89 + E90)      E91
Cédéroms adultes                        E92
Cédéroms enfants                        E93
TOTAL des cédéroms (E92 + E93)          E94
Autres documents                        E95
Périodiques imprimés                    E96
Périodiques sur cédéroms ou en ligne    E97
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
f6.add_h1(title=(u"F-  RÉSEAU TOUS PUBLICS"),
          help_file='help6')

f6.add_h2(title=u"F.1 / 2 DESSERTE DU RÉSEAU TOUS PUBLICS (cf. notice explicative)")
data = u"""
##WXY##Nombre de points W##Nombre de commune X##Population desservie Y
Bibliothèques municipales niveau 1            F11
Bibliothèques municipales niveau 2            F12
Bibliothèques relais niveau 3                 F13
Point-lecture                                 F14
Autres dépôts tous publics                    F15
TOTAL (F11 à F15)                             F16
Arrêts bibliobus-médiabus prêt direct         F17
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
communes desservies par plusieurs modes de desserte (ex BM + prêt direct)  F21
"""
body, xyz_labels = f6.raw_text2lines(data=data)
f6.table(body, xyz_labels)

f6.add_h2(title=u"F. 3 DÉPÔTS DE LA BDP")
data = u"""
##YZ##Nombre de documents déposés dans l'année Y##Nombre de documents en dépôt au 31.12. Z
Imprimés adultes                            F31
Imprimés enfants                            F32
TOTAL ( F31 + F32)                          F33
Phonogrammes                                F34
Vidéogrammes                                F35
Cédéroms                                    F36
Autres documents                            F37
TOTAL (F33 à F37 )                          F38
"""
body, xyz_labels = f6.raw_text2lines(data=data)
f6.table(body, xyz_labels)

f6.add_h2(title=u"F. 4 BIBLIOTHÈQUES AYANT FOURNI DES STATISTIQUES")
data = u"""
##WXY##Nombre de points W##Nombre de communes  X##Population desservie Y
Bibliothèques niveau 1                                 F41
Bibliothèques niveau 2                                 F42 
Bibliothèques-relais niveau 3                          F43 
Points-lecture                                         F44
Dépôts tous publics                                    F45  
TOTAL (F41 à F45  )                                    F46
"""
body, xyz_labels = f6.raw_text2lines(data=data)
f6.table(body, xyz_labels)

f6.add_h2(title=u"F. 5 ACTIVITÉS DU RÉSEAU TOUS PUBLICS : INSCRITS")
f6.add_th_comment(title=u"Nombre d'inscrits enfants")
data = u"""
##WXYZ##BDP/Annexes ouvertes à tous publics W##Bibliobus de prêts direct X##Réseau public Y##Total Z
0-14 ans                                F51
"""
body, xyz_labels = f6.raw_text2lines(data=data)
f6.table(body, xyz_labels)
f6.add_th_comment(title=u"Nombre d'inscrits adultes")
data = u"""
##WXYZ##BDP/Annexes ouvertes à tous publics W##Bibliobus de prêts direct X##Réseau public Y##Total Z
15-24 ans                             F52
25-59 ans                             F53
60 ans et +                           F54
TOTAL Adultes                         F55
TOTAL DES INSCRITS (F51 + F55)        F56
"""
body, xyz_labels = f6.raw_text2lines(data=data)
f6.table(body, xyz_labels)

f6.add_h2(title=u"F. 6 ACTIVITÉS DU RÉSEAU TOUS PUBLICS : NOMBRE DE PRÊTS (1)")
data = u"""
##WXYZ##BDP/Annexes ouvertes à tous publics W##Bibliobus de prêts direct X##Réseau public Y##Total Z
Prêts de livres adultes                       F61
Prêts de livres enfants                       F62
TOTAL (F61+F62)                               F63
Prêts de périodiques                          F64
Prêts de phonogrammes                         F65
Prêts de vidéogrammes                         F66
Prêts de disques optiques numériques          F67
Prêts d'autres documents                      F68
TOTAL DES PRÊTS (F63 à F68)                   F69
"""
body, xyz_labels = f6.raw_text2lines(data=data)
f6.table(body, xyz_labels)

f6.main_footer()


######################################################################## 
# Form BDP 7
########################################################################

f7 = GenForms(encoding='latin1', filename='FormBDP_report7_autogen.xml', no_generation=True)
f7.main_header()
f7.add_h1(title=(u"G-  RÉSEAU SPÉCIFIQUE (cf. notice explicative)"),
          help_file='help7')

f7.add_h2(title=u"G.1 / 2 DÉPÔTS DANS LES COLLECTIVITÉS (Public spécifique)")
data = u"""
##VWXYZ##Nb de collectivités V##Nb de documents déposés dans l'année W##Nb de documents X##Nb d'inscrits Y##Nb de prêts
Ecoles                                     G11
Collèges                                   G12
Lycées                                     G13
Prisons                                    G14
Hôpitaux                                   G15
Maisons de retraite                        G16
Comité d'entreprise                        G17
Petite enfance (crèche, PMI)               G18
Centres sociaux, foyers ruraux             G19
Centres de vacances et de loisirs          G20
Autres                                     G21
TOTAL (G11 à G21)                          G22
"""
body, xyz_labels = f7.raw_text2lines(data=data)
f7.table(body, xyz_labels)

f7.add_h2(title=u"G. 3 / 4 PRÊT DIRECT (Public spécifique)")
data = u"""
##XYZ##Nb de lieux de stationnement X##Nb d'inscrits Y##Nb de prêts Z
Ecoles                                     G31
Collèges                                   G32
Lycées                                     G33
Prisons                                    G34
Hôpitaux                                   G35
Maisons de retraite                        G36
Comité d'entreprise                        G37
Petite enfance (crèche, PMI)               G38
Centres sociaux, foyers ruraux             G39
Centres de vacances et de loisirs          G40
Autres                                     G41
TOTAL (G31 à G41)                          G42
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
f8.add_h2(title=u"H. 1 SERVICES À DISTANCE POUR LES BIBLIOTHÈQUES DU RÉSEAU")
data = u"""
La bibliothèque a-t-elle un site Web?:    H11
"""
body, xyz_labels = f8.raw_text2lines(data=data)
f8.table(body, xyz_labels)
f8.add_th_comment(title=u"Si oui : adresse URL à préciser en 1ère page")
data = u"""
Ce site donne-t-il accès au catalogue de la bibliothèque?   H12

"""
body, xyz_labels = f8.raw_text2lines(data=data)
f8.table(body, xyz_labels)
f8.add_th_comment(title=u"Quels services sont offerts aux bibliothèques du réseau sur le site web? (cocher les cases)")
data = u"""
consultation du catalogue                      H13
Réservation en ligne                           H14
Consultation du compte lecteur                 H15
Autres (préciser)                              H16
"""
body, xyz_labels = f8.raw_text2lines(data=data)
f8.table(body, xyz_labels)
data = u"""
Nb de sessions/an (à distance)        H17
Nb de pages vues/an (à distance)      H18
"""
body, xyz_labels = f8.raw_text2lines(data=data)
f8.table(body, xyz_labels)

f8.add_h2(title=u"H. 2 COOPÉRATION, RÉSEAU")
data = u"""
La BDP organise-t-elle un catalogue collectif départemental ?    H21
Si oui, préciser le nb de bibliothèques participantes                       H22
La BDP utilise-t-elle un logiciel pour l'évaluation de son réseau ?  H23
Si oui, préciser lequel                                                     H24 
La BDP appartient-elle à un réseau documentaire autre que le réseau qu'elle déssert ?  H25
Si oui, préciser lequel                                                     H26 
La BDP a-t-elle menée des actions internationales ?         H27

"""
body, xyz_labels = f8.raw_text2lines(data=data)
f8.table(body, xyz_labels)


f8.add_th_comment(title=u"Si oui, cocher les cases correspondantes")
data = u"""
Voyage d'étude, expertise à l'étranger   H28
Don de livres                            H29
"""
body, xyz_labels = f8.raw_text2lines(data=data)
f8.table(body, xyz_labels)

f8.add_h2(title=u"H. 3 SUBVENTIONS DÉPARTEMENTALES AUX COLLECTIVITÉS DANS L'ANNÉE")
data = u"""##VWXYZ##Subventions du conseil  général V##Nb de communes aidées inf. à 10000h W##Montant des aides versées X##Nombre de communes aidées sup. à 10000h Y##Montant des aides versées Z
Construction                                    H31
Aménagement                                     H32
Informatisation                                 H33
Equipement multimedia                           H34
"""
body, xyz_labels = f8.raw_text2lines(data=data)
f8.table(body, xyz_labels)

data = u"""##VWXYZ##Subventions du conseil  général V##Nb de communes aidées inf. à 10000h W##Montant des aides versées X##Nombre de communes aidées sup. à 10000h Y##Montant des aides versées Z
 Acquisition de documents : Imprimés          H35
 Acquisition de documents : Phonogrammes      H36
 Acquisition de documents : Multmedia         H37
Animation                                     H38
Emplois                                       H39
"""
body, xyz_labels = f8.raw_text2lines(data=data)
f8.table(body, xyz_labels)

f8.add_h2(title=u"H. 4 CONSEILS DE LA BDP AUX COLLECTIVITÉS DANS L'ANNÉE")
data = u"""##XYZ##Conseils, aides et assistance BDP X##Nombre de communes aidées inf. à 10000h Y##Nombre de communes aidées sup. à 10000h Z
Construction                                  H41
Aménagement                                   H42
Informatisation                               H43
Equipement multimedia                         H44
"""
body, xyz_labels = f8.raw_text2lines(data=data)
f8.table(body, xyz_labels)

data = u"""##XYZ##Conseils, aides et assistance BDP X##Nombre de communes aidées inf. à 10000h Y##Nombre de communes aidées sup. à 10000h Z 
 Acquisition de documents : Imprimés          H45
 Acquisition de documents : Phonogrammes      H46
 Acquisition de documents : Multmedia         H47
"""
body, xyz_labels = f8.raw_text2lines(data=data)
f8.table(body, xyz_labels)

data = u"""##XYZ##Conseils, aides et assistance BDP X##Nombre de communes aidées inf. à 10000h Y##Nombre de communes aidées sup. à 10000h Z 
Animation                      H48
Emplois                        H49
"""
body, xyz_labels = f8.raw_text2lines(data=data)
f8.table(body, xyz_labels)

f8.add_h2(title=u"H. 5 - SERVICES AU RÉSEAU (réseau public et spécifique)")
f8.add_h2(title=u"Services particuliers au réseau")
f8.add_th_comment(title=u"La BDP offre-t-elle ces services ?")

data = u"""
Réservation                      H51
"""
body, xyz_labels = f8.raw_text2lines(data=data)
f8.table(body, xyz_labels)
f8.add_th_comment(title=u"Si oui")
data = u"""
Nb de demandes reçues                   H52
Nb de demandes satisfaites              H53
"""
body, xyz_labels = f8.raw_text2lines(data=data)
f8.table(body, xyz_labels)

data = u"""
Portage de documents par navette          H54
Prêt Inter Bibliothèques                  H55
"""
body, xyz_labels = f8.raw_text2lines(data=data)
f8.table(body, xyz_labels)

f8.add_th_comment(title=u"Si oui")
data = u"""
Nb de demandes reçues                   H56
Nb de demandes satisfaites              H57
"""
body, xyz_labels = f8.raw_text2lines(data=data)
f8.table(body, xyz_labels)

data = u"""
Prêt d'expositions                                                    H58
Prêt de valises thématiques                                           H59
Prêt de matériel d'animation                                          H60  
Groupements d'achats (matériel, documents)                            H61
Comités de lecture, offices en consultation pour les bibliothèques du réseau   H62
Autre                                                      H63
Si oui, préciser                                           H74
"""
body, xyz_labels = f8.raw_text2lines(data=data)
f8.table(body, xyz_labels)

f8.add_h2(title=u"Formations pour les partenaires du réseau dans l'année")
data = u"""
Nombre de thèmes formations différents proposés            H64
"""
body, xyz_labels = f8.raw_text2lines(data=data)
f8.table(body, xyz_labels)

f8.add_th_comment(title=u"Formations organisées par la BDP")
data = u"""##YZ##Nombre de participants Y##Nb  de journées Z
Formation de base BDP               H65
Formation ABF                       H66
Formation continue                  H67
Voyage d'étude                      H68 
TOTAL                               H69
"""
body, xyz_labels = f8.raw_text2lines(data=data)
f8.table(body, xyz_labels)
data = u"""
La BDP organise-t-telle des formations sur place dans les bibliothèques du réseau ?  H70
Si oui, combien de jours                                H71
La BDP organise-t-elle des réunions de secteur avec les médiathèques du réseau ?  H72
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
La BDP a-t-elle (co-) organisé des manifestations culturelles dans l'année?:    I11
"""
body, xyz_labels = f9.raw_text2lines(data=data)
f9.table(body, xyz_labels)
f9.add_th_comment(title=u"Si oui combien :")
data = u"""
Fête/salon du livre           I12
Exposition                    I13
Conférences                   I14
Rencontres d'auteurs/lectures I15
Ateliers d'écriture           I16
Festival                      I17
Conteurs                      I18
Concerts                      I19
Autres                        I20
"""
body, xyz_labels = f9.raw_text2lines(data=data)
f9.table(body, xyz_labels)

f9.add_h2(title=u"I.2 PUBLICATIONS")
data = u"""
La BDP a-t-elle publié des documents dans l'année ?  I21
"""
body, xyz_labels = f9.raw_text2lines(data=data)
f9.table(body, xyz_labels)
f9.add_th_comment(title=u"si oui, préciser combien de titres ou de fascicules :")
data = u"""
Bulletin d'information                             I22
Guide du dépositaire                               I23
Annuaire des bibliothèques                         I24
Catalogue des formations                           I25
Catalogue des expositions et valises thématiques   I26
Bibliographies sélectives                          I27
Autres                                             I28
"""
body, xyz_labels = f9.raw_text2lines(data=data)
f9.table(body, xyz_labels)

f9.add_h2(title=u"I.3 FORMATIONS HORS RÉSEAU")
data = u"""
Nombre d'heures de cours assurées par le personnel  (ENSSIB, CRFCB, ABF, CNFPT, BDP, ?) I31
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
