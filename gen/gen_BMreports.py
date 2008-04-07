# -*- coding: ISO-8859-1 -*-
#### to check if the autogen and the original one are different
## for i in `ls FormBM_report*autogen.xml` ;
## do  diff $i `basename $i _autogen.xml`.xml ;done

# Import from python
from pprint import pprint

# Import from scrib
from GenFormsTemplates import GenForms


########################################################################
# Form BM 1 A
########################################################################

f1 = GenForms(bibType='BM', encoding='latin1',
              filename='FormBM_report1_autogen.xml', no_generation=True)
f1.main_header()
f1.add_h1(title=u'A- ÉLÉMENTS FINANCIERS ( en euros, sans décimales)',
          help_file='help1')
# A1
f1.add_h2(title=u'A.1 DEPENSES DE FONCTIONNEMENT PROPRES A LA BIBLIOTHÈQUE')
data = u"""
Pour le personnel : salaires et charges,  A11
Pour les acquisitions de tous documents et abonnements A12
Pour la reliure et l'équipement des documents A13
Pour la maintenance informatique A14
Pour l'animation (communication, impression, défraiement) A15
TOTAL (A11à A15) A16"""
body, trach = f1.raw_text2lines(data=data)
f1.table(body)

# A2
f1.add_h2(title=u"A.2 DEPENSES D'INVESTISSEMENT PROPRES A LA BIBLIOTHÈQUE")
data = u"""
Pour le bâtiment (construction, agrandissement, rénovation)     A21
Pour le mobilier et le matériel (y compris achat de véhicules)  A22
Pour l'informatique (logiciel et matériel)                      A23
Pour les acquisitions de tous documents et abonnements          A24
TOTAL (A21à A24)                                                A25
"""
body, trach = f1.raw_text2lines(data=data)
f1.table(body)

# A3
f1.add_h2(title=u"A.3 RECETTES PROPRES A LA BIBLIOTHÈQUE")
data = u"""
Montant total des droits d'inscription perçus dans l'année   A31
Montant des subventions de fonctionnement                    A32
Montant des subventions d'investissement                     A33
Autres                                                       A34
"""
body, trach = f1.raw_text2lines(data=data)
f1.table(body)
f1.main_footer()

########################################################################
# Form BM 2 B
########################################################################

f2 = GenForms(bibType='BM', encoding='latin1',
              filename='FormBM_report2_autogen.xml', no_generation=True)
f2.main_header()
f2.add_h1(title=(u"B- LOCAUX - VÉHICULES - ÉQUIPEMENT INFORMATIQUE"
                 u" ET INFORMATISATION "),
          help_file='help2')
# B1
f2.add_h2(title=u'B.1 LOCAUX')
data = u"""
##XYZ## Centrale  X ##  Annexes Y ##  Total Z
Surface en m² horsoeuvre nette SHON (services publics et intérieurs confondus)   B11
Nombre de bâtiments                                                              B12
Nombre de places assises (hors auditorium et cafétéria)                          B13
"""
body, xyz_labels = f2.raw_text2lines(data=data)
f2.table(body, xyz_labels)
data = u"""
La bibliothèque possède-t-elle un espace spécifique pour l'accueil des personnes handicapées ?   B14
Nombre de places assises dans cet espace spécifique                                              B15
"""
body, xyz_labels = f2.raw_text2lines(data=data)
f2.table(body, xyz_labels)

# B2
f2.add_h2(title=u'B. 2 VÉHICULES')
data = u"""
Nombre total de bus : bibliobus ou médiabus (musibus, artobus, etc.) B21
Dont nombre de bus faisant du prêt direct                            B22
Autres véhicules (fourgonnettes, voitures légères)                   B23
"""
body, xyz_labels = f2.raw_text2lines(data=data)
f2.table(body, xyz_labels)
# B3
f2.add_h2(title=u'B.3/4 ÉQUIPEMENT INFORMATIQUE ET INFORMATISATION')
data = u"""
La bibliothèque est-t-elle équipée d'un logiciel de gestion de  catalogue ?  B31
Si oui, préciser lequel :                B32
Dans l'année, la bibliothèque a-t-elle importé des notices pour alimenter  catalogue ?  B33
Si oui, dans quelle proportion ? %    B34
Si la bibliothèque possède des documents patrimoniaux, leur catalogue est- au moins en partie informatisé ? B35
Si oui : nombre de notices   B36
"""
body, xyz_labels = f2.raw_text2lines(data=data)
f2.table(body, xyz_labels)
# B4

data = u"""
##XY##  Professionnels  X ##  Publics   Y
Nombre de postes informatiques sans accès internet                      B37
Nombre de postes informatique avec accès internet                       B38
TOTAL                                                                   B39
"""
body, xyz_labels = f2.raw_text2lines(data=data)
f2.table(body, xyz_labels)
data = u"""
Possédez-vous un accès public à internet ?      B40
"""
body, xyz_labels = f2.raw_text2lines(data=data)
f2.table(body, xyz_labels)

f2.add_th_comment(u"Si oui, l'accès public à internet est-il :")
data = u"""
Entièrement gratuit ?          B41
Payant, même partiellement ?   B42
"""
body, xyz_labels = f2.raw_text2lines(data=data)
f2.table(body, xyz_labels)

data = u"""
La bibliothèque a-t-elle des équipements informatiques spécifiques pour les personnes handicapées ? B43
"""
body, xyz_labels = f2.raw_text2lines(data=data)
f2.table(body, xyz_labels)

f2.add_th_comment(u"Si oui, lesquels ?")
data = u"""
Appareils de grossissement          B44
Règles tactiles                     B45
Logiciels adaptés                   B46
Autres, préciser :                  B47
"""
body, xyz_labels = f2.raw_text2lines(data=data)
f2.table(body, xyz_labels)

f2.main_footer()
########################################################################
# Form BM 3 C
########################################################################

f3 = GenForms(bibType='BM', encoding='latin1',
              filename='FormBM_report3_autogen.xml', no_generation=True )
f3.main_header()
f3.add_h1(title='C-  PERSONNEL EN POSTE AU 31 DECEMBRE 2005', help_file='help3')
# C10
f3.add_h2(title=u"CADRES D' EMPLOIS")
f3.add_h2(title=u"C.1 FONCTION PUBLIQUE : FILIÈRE CULTURELLE")

data = u"""
##WXYZ##  NB DE PERSONNES ##  NB  D'EMPLOIS Equivalent Temps Plein (ETP)## NB DE PERSONNES AYANT SUIVI UNE FORMATION DANS L'ANNEE##Responsable de la bibliothèque ?
Conservateurs d'Etat                    C11
Conservateurs territoriaux              C12
Bibliothécaires                         C13
Assistants qualifiés de conservation    C14
Assistants de conservation              C15
Agents qualifiés du patrimoine          C16
Agents du patrimoine                    C17
"""
body, xyz_labels = f3.raw_text2lines(data=data)
f3.table(body, xyz_labels)
# C20
f3.add_h2(title=(u"C.2 FONCTION PUBLIQUE : AUTRES FILIÈRES  (administrative, "
                  "technique, sociale...)"))
data = u"""
##WXYZ##  NB DE PERSONNES ##  NB  D'EMPLOIS D'ETP  ## NB DE PERSONNES AYANT SUIVI UNE FORMATION DANS L'ANNEE ##Responsable de la bibliothèque ?
Personnels d'autres filières  Cat. A C21
Personnels d'autres filières  Cat. B C22
Personnels d'autres filières  Cat. C C23
"""
body, xyz_labels = f3.raw_text2lines(data=data)
f3.table(body, xyz_labels)
# C30
f3.add_h2(title=(u"C.3 AUTRES PERSONNELS REMUNÉRÉS"))
data = u"""
##WXYZ##  NB DE PERSONNES##  NB  D'EMPLOIS D'ETP  ## NB DE PERSONNES AYANT SUIVI UNE FORMATION DANS L'ANNEE##Responsable de la bibliothèque ?
Agents non titulaires/emplois non aidés par l'Etat (contractuels, vacataires...) qualifiés C31
Agents non titulaires/emplois non aidés par l'Etat (contractuels, vacataires...) non qualifiés C32
Agents non titulaires/ emplois aidés par l'Etat ( C.E.S., C.E.C., C.E.J,...) qualifiés  C33
Agents non titulaires/ emplois aidés par l'Etat ( C.E.S., C.E.C., C.E.J,...) non qualifiés   C34
"""
body, xyz_labels = f3.raw_text2lines(data=data)
f3.table(body, xyz_labels)
# C40
f3.add_h2(title=u"C.4 BÉNÉVOLES")
data = u"""
##WXYZ##  NB DE PERSONNES ##  NB  D'EMPLOIS D'ETP  ## NB DE PERSONNES AYANT SUIVI UNE FORMATION DANS L'ANNEE ##Responsable de la bibliothèque ?
Bénévoles qualifiés (exemple : ABF, BDP, etc)        C41
Bénévoles non formés           C42
TOTAL (C11 à C42)              C43
"""
body, xyz_labels = f3.raw_text2lines(data=data)
f3.table(body, xyz_labels)
# C50
f3.add_h2(title=(u"C.5 NOMBRE TOTAL DE PERSONNES AYANT SUIVI UNE FIA"
                  " (formation initiale d'application)"))
data = u"""
DANS L'ANNÉE :                           C51
"""
body, xyz_labels = f3.raw_text2lines(data=data)
f3.table(body, xyz_labels)

f3.main_footer()
########################################################################
# Form BM 4 D- COLLECTIONS
########################################################################
f4 = GenForms(bibType='BM', encoding='latin1',
              filename='FormBM_report4_autogen.xml', no_generation=True)
f4.main_header()
f4.add_h1(title=(u"D- COLLECTIONS au 31 DECEMBRE 2005"),
          help_file='help4')

f4.add_th_comment(u"COLLECTIONS : nombre de documents (en nombre d'unités)"
                  u" appartenant à la bibliothèque")
# D10 et D20
f4.add_h2(title=u"D. 1/ 2  LIVRES ET AUTRES DOCUMENTS (hors patrimoine et "
                u"périodiques)")
data = u"""
##XYZ##    ADULTES X ##  ENFANTS Y ##  TOTAL   Z
Nombre de livres en libre accès pour le prêt                            D11
Nombre de livres en libre accès réservés a la consultation sur place    D12
Nombre total de livres en libre accès  (D11+D12)                        D13
Livres non patrimoniaux en magasin                                      D14
TOTAL  (D13 + D14)                                                      D15
Vidéogrammes                                                            D16
Phonogrammes                                                            D17
Cédéroms sauf périodiques                                               D18
"""
body, xyz_labels = f4.raw_text2lines(data=data)
f4.table(body, xyz_labels)

data = u"""
Cartes et plans                            D19
Partitions                                 D20
Documents graphiques                       D21
Autres                                     D22
Documents numériques                       D23
Bases de données                           D24
"""
body, xyz_labels = f4.raw_text2lines(data=data)
f4.table(body, xyz_labels)

data = u"""
##XYZ##    ADULTES X ##  ENFANTS Y ##  TOTAL   Z
Dont documents adaptés aux personnes handicapées (braille, livres en gros caractères, livres parlés,...) D25
"""
body, xyz_labels = f4.raw_text2lines(data=data)
f4.table(body, xyz_labels)

# D30
f4.add_h2(title=u"D.3 DOCUMENTS PATRIMONIAUX (hors périodiques)")
data = u"""
Livres imprimés                            D31
Manuscrits                                 D32
Documents graphiques, cartes et plans      D33
Documents numériques                       D34
Bases de données                           D35
Autres : monnaies, etc.                    D36
TOTAL (D31 à D36)                          D37
"""
body, xyz_labels = f4.raw_text2lines(data=data)
f4.table(body, xyz_labels)

# D40
f4.add_h2(title=u"D.4 PÉRIODIQUES")
data = u"""
Nombre de titres de périodiques conservés (titres morts ou courants) imprimés                  D41
Dont nombre de périodiques patrimoniaux                                                        D42
Nombre de titres de périodiques conservés (titres morts ou courants) sur Cédéroms ou en ligne  D43
Nombre total de titres de périodiques conservés ou non conservés                               D44
"""
body, xyz_labels = f4.raw_text2lines(data=data)
f4.table(body, xyz_labels)
                            

f4.main_footer()
########################################################################
# Form BM 5 E- ACQUISITIONS ET ÉLIMINATIONS DE L'ANNÉE
########################################################################
f5 = GenForms(bibType='BM', encoding='latin1',
              filename='FormBM_report5_autogen.xml', no_generation=True)
f5.main_header()
f5.add_h1(title=(u"E- ACQUISITIONS ET ÉLIMINATIONS DE L'ANNÉE"),
          help_file='help5')
# E10
f5.add_h2(title=u"E. 1 NOMBRE DE DOCUMENTS ACHETÉS  (hors périodiques "
                u"et documents patrimoniaux)")
data = u"""
##XYZ##   ADULTES X ##  ENFANTS Y ##  TOTAL Z
Livres                            E11
Phonogrammes                      E12
Vidéogrammes                      E13
Cédéroms                          E14
Autres documents                  E15
Documents numériques  			  E16
Dont documents adaptés aux personnes handicapées (braille, livres en gros caractères, livres parlés...)  E17
"""
body, xyz_labels = f5.raw_text2lines(data=data)
f5.table(body, xyz_labels)
# E20
f5.add_h2(title=u"E. 2 NOMBRE DE DOCUMENTS ENTRÉS PAR DONS, LEGS OU DÉPÔT LEGAL "
                u"(hors périodiques et documents patrimoniaux )")
data = u"""
##XYZ##   ADULTES X ##  ENFANTS Y ##  TOTAL Z
Livres                                E21
Phonogrammes                          E22
Vidéogrammes                          E23
Cédéroms                              E24
Autres documents                      E25
Documents numériques                  E26
dont documents adaptés aux personnes handicapées (braille, livres en gros caractères, livres parlés...) E27
"""
body, xyz_labels = f5.raw_text2lines(data=data)
f5.table(body, xyz_labels)
# E30
f5.add_h2(title=u"E. 3 NOMBRE DE DOCUMENTS RETIRÉS DE L'INVENTAIRE"
                u" (hors documents patrimoniaux)")
data = u"""
##XYZ##   ADULTES X ##  ENFANTS Y ##  TOTAL Z
Livres                                E31
Périodiques (unités matérielles)      E32
Phonogrammes                          E33
Vidéogrammes                          E34
Cédéroms                              E35
Autres documents                      E36
Documents numériques                  E37
Dont documents adaptés aux personnes handicapées (braille, livres en gros caractères, livres parlés...) E38
"""
body, xyz_labels = f5.raw_text2lines(data=data)
f5.table(body, xyz_labels)
# E40
f5.add_h2(title=u"E.4 NOMBRE DE DOCUMENTS PATRIMONIAUX ACQUIS "
                u"(achats, dons, legs)")
data = u"""
##XYZ## ACHATS  X ##  DONS, LEGS  Y ##  TOTAL Z
Livres imprimés                          E41
Périodiques                              E42
Manuscrits : nombre de cotes             E43
Documents graphiques, cartes et plans    E44
Autres (monnaies, ...)                   E45
TOTAL (E41 à  E45)                       E46
"""
body, xyz_labels = f5.raw_text2lines(data=data)
f5.table(body, xyz_labels)
# E50
f5.add_h2(title=u"E. 5  NOMBRE DE PÉRIODIQUES ACQUIS"
                u"(ACHÂTS, DONS, LEGS)")
data = u"""
##XYZ##   ADULTES X ##  ENFANTS Y ##  TOTAL Z
Nombre d'abonnements en cours (payants et gratuits, support imprimé ou microforme)   E51
Nombre d'abonnements en cours sur cédéroms                                           E52
Nombre d'abonnements en cours en ligne                                               E53
"""
body, xyz_labels = f5.raw_text2lines(data=data)
f5.table(body, xyz_labels)
# E60
f5.add_h2(title=u" E. 6/7 DÉPENSES D'ACQUISITION"
                u" (en euros, sans  décimale)")
data = u"""
##XYZ##   ADULTES X ##  ENFANTS Y ##  TOTAL Z
Livres                              E61
Phonogrammes                        E62
Vidéogrammes                        E63
Cédéroms                            E64
Autres documents                    E65
dont documents adaptés aux personnes handicapées (braille, livres en gros caractères, livres parlés...) E66
SOUS-TOTAL (E61 à E65)                         E67
Périodiques imprimés                           E68
Périodiques sur cédéroms                       E69
Périodiques en ligne                           E70
SOUS-TOTAL (E68 à E70)                         E71
Documents numériques                           E72
Documents patrimoniaux                         E73
TOTAL (E67 + E71 + E72 + E73)                  E74
"""
body, xyz_labels = f5.raw_text2lines(data=data)
f5.table(body, xyz_labels)

f5.main_footer()
########################################################################
# Form BM 6 F- COOPÉRATION ET RÉSEAU
########################################################################
f6 = GenForms(bibType='BM', encoding='latin1',
              filename='FormBM_report6_autogen.xml', no_generation=True)
f6.main_header()
f6.add_h1(title=(u"COOPÉRATION ET RÉSEAU (F17-F20)"),
          help_file='help6')
# F10
data = u"""
La bibliothèque appartient-elle au réseau de la BDP ?                  F11
La bibliothèque appartient-elle à un autre réseau documentaire ?       F12
si oui, lequel :                                                       F13
La bibliothèque participe-t-elle à des actions de coopération ?        F14
si oui, préciser lesquelles :                                          F15
"""
body, xyz_labels = f6.raw_text2lines(data=data)
f6.table(body, xyz_labels)

data = u"""
La bibliothèque a-t-elle mené en 2005 des actions internationales ?    F16
"""
body, xyz_labels = f6.raw_text2lines(data=data)
f6.table(body, xyz_labels)

f6.add_th_comment(u"Si oui préciser :")
data= u"""
Accueils / échanges de professionnels, écrivains                       F17
Voyages d'étude, expertises à l'étranger                               F18
Dons de livres                                                         F19
Autres actions de coopération                                          F20
"""
body, xyz_labels = f6.raw_text2lines(data=data)
f6.table(body, xyz_labels)

f6.add_th_comment(u"Si la bibliothèque entretient des partenariats avec des structures publiques ou privées (associations...) oeuvrant dans le domaine du handicap, préciser les domaines d'intervention :")

data = u"""
Accueil de bénévoles dans la bibliothèque                              F21
Dépôt de livres dans les locaux du partenaire                          F22
Autres                                                                 F23
"""
body, xyz_labels = f6.raw_text2lines(data=data)
f6.table(body, xyz_labels)

f6.main_footer()


########################################################################
# Form BM 7 G- ACTIVITÉS DE LA BIBLIOTHÈQUE
########################################################################

# FormBM_report7.xml n'est plus autogénére
f7 = GenForms(bibType='BM', encoding='latin1',
              filename='FormBM_report7_autogen.xml', no_generation=True)
f7.main_header()
f7.add_h1(title=(u"G-  ACTIVITÉS DE LA BIBLIOTHÈQUE"),
          help_file='help7')
# G10
f7.add_h2(title=u"G.1 OUVERTURE À TOUS LES PUBLICS"
                u"(hors accueils de publics spécifiques et de classes)")
data = u"""
##HM## Heures H## Minutes M
Nombre d'heures d'ouverture par semaine    G12
Nombre d'heures d'ouverture dans l'année   G13
"""

body, xyz_labels = f7.raw_text2lines(data=data)
f7.table(body, xyz_labels)

# G20 et G30
f7.add_h2(title=u"G.2/3 INSCRITS ET EMPRUNTEURS")
data = u"""
##WXYZ## HOMMES  W## FEMMES  X ## TOTAL Y## TOTAL EMPRUNTEURS ACTIFS  Z
Age non déclaré           G20
ENFANTS 0-14 ans          G21
ADULTES 15-24 ans         G22
ADULTES 25-59 ans         G23
ADULTES 60 ans et +       G24
TOTAL ADULTES             G25
"""
body, xyz_labels = f7.raw_text2lines(data=data)
f7.table(body, xyz_labels)

data = u"""
##YZ##TOTAL INSCRITS (G21Y+G25Y)##TOTAL EMPRUNTEURS ACTIFS(G21Z+G25Z)
TOTAL (G21+G25)  G26
Préciser combien d'entre eux résident dans la commune (ou dans les communes du groupement si la bibliothèque est intercommunale) G27
"""
body, xyz_labels = f7.raw_text2lines(data=data)
f7.table(body, xyz_labels)

data = u"""
Nombre d'entrées dans la bibliothèque centrale                                    G28
Nombre d'entrées dans les bibliothèques annexes ou autres bibliothèques du réseau G29
Nombre total  d'entrées dans l'année (bibliothèque centrale et annexes)           G30
Nombre de collectivités utilisatrices                                             G31
dont nombre de classes                                                            G32
Préciser combien d'entre elles sont situées dans la commune (ou le groupement de communes si la bibliothèque est intercommunale) G33
"""
body, xyz_labels = f7.raw_text2lines(data=data)
f7.table(body, xyz_labels)

# G40
f7.add_h2(title=u"G. 4/5 NOMBRE DE PRÊTS ET COMMUNICATIONS EFFECTUÉS DANS L'ANNÉE")
data = u"""
##XYZ## ADULTES X ##  ENFANTS Y ##   TOTAL Z
Prêts de livres             G41
Prêts de périodiques        G42
Prêts de phonogrammes       G43
Prêts de vidéogrammes       G44
Prêts de cédéroms           G45
Prêts d'autres documents    G47
TOTAL DES PRÊTS (G41 à G47) G48
"""
body, xyz_labels = f7.raw_text2lines(data=data)
f7.table(body, xyz_labels)

f7.add_h2(title=u"Nombre de communications sur place (documents en magasin)")
data = u"""
Documents hors patrimoine   G49
Documents patrimoniaux      G50
TOTAL (G49 à G50)           G51
"""
body, xyz_labels = f7.raw_text2lines(data=data)
f7.table(body, xyz_labels)
              
f7.main_footer()

########################################################################
# Form BM 8 H-   SERVICES OFFERTS PAR LA BIBLIOTHÈQUE
########################################################################
f8 = GenForms(bibType='BM', encoding='latin1',
              filename='FormBM_report8_autogen.xml',
              no_generation=True)

f8.main_header()
f8.add_h1(title=(u" SERVICES OFFERTS PAR LA BIBLIOTHÈQUE"),
          help_file='help8')
# H10
f8.add_h2(title=u"H. 1/2 SERVICES AUX USAGERS")
data = u"""
La bibliothèque organise-t-elle des actions de formation pour les usagers ?  H11
"""
body, xyz_labels = f8.raw_text2lines(data=data)
f8.table(body, xyz_labels)

f8.add_th_comment(u"La bibliothèque offre-t-elle ces services ?")
data = u"""
Guide du lecteur              H12
Réservation                   H13
Portage à domicile            H14
Services pour les personnes handicapées           H15
Prêt inter-bibliothèques                          H16
"""
body, xyz_labels = f8.raw_text2lines(data=data)
f8.table(body, xyz_labels)
f8.add_th_comment(u"  Si oui")
data = u"""
Nombre de demandes reçues                         H17
Nombre de demandes reçues satisfaites             H18
Nombre de demandes émises                         H19
Nombres de demandes émises satisfaites            H20
"""
body, xyz_labels = f8.raw_text2lines(data=data)
f8.table(body, xyz_labels)
data = u"""
Autres                                            H21
"""
body, xyz_labels = f8.raw_text2lines(data=data)
f8.table(body, xyz_labels)
# H30
f8.add_h2(title=u"H. 3 SERVICES À DISTANCE")
data = u"""
La bibliothèque a-t-elle un site web ?                           H31
Ce site donne-t-il accès au catalogue de la bibliothèque ?       H32
"""
body, xyz_labels = f8.raw_text2lines(data=data)
f8.table(body, xyz_labels)
f8.add_th_comment(u"Quels services sont offerts sur le site web ?")
data = u"""
Consultation du catalogue                H33
Réservation en ligne                     H34
Consultation du compte lecteur           H35
Consultation des fonds numérisés         H36
Autres (préciser)                        H37
"""
body, xyz_labels = f8.raw_text2lines(data=data)
f8.table(body, xyz_labels)
data = u"""
##XYZ## SUR PLACE X ##  A DISTANCE  Y ##  TOTAL Z
Nombre de sessions / an                             H38
"""
body, xyz_labels = f8.raw_text2lines(data=data)
f8.table(body, xyz_labels)
data = u"""
Le site de la bibliothèque est-il accessible aux déficients visuels par des procédés techniques adaptés ?  H39
"""
body, xyz_labels = f8.raw_text2lines(data=data)
f8.table(body, xyz_labels)

#H30 H40
f8.add_h2(title=u"H. 4/5 SERVICES AUX COLLECTIVITÉS")
data = u"""
La bibliothèque organise-t-elle des actions de formation pour les collectivités ?  H41
Si oui, préciser : ( multimédia, formation des enseignants)  H42
"""
body, xyz_labels = f8.raw_text2lines(data=data)
f8.table(body, xyz_labels)
f8.add_th_comment(u"DÉPÔT DANS LES COLLECTIVITÉS DESSERVIES")
data = u"""
##YZ##NB DE COLLECTIVITÉS Y ##  NB DOC DÉPOSÉS  Z
Ecoles                         H52
Collèges                       H53
Lycées                         H54
Prisons                        H55
Hôpitaux                       H56
Maisons de retraite            H57
Comité d'entreprise            H58
Petite enfance (crèche, PMI)   H59
Centres sociaux                H60
Centres de loisirs et de vacances  H61
Autres                         H62
TOTAL (H52 à H62)              H63
"""
body, xyz_labels = f8.raw_text2lines(data=data)
f8.table(body, xyz_labels)
f8.main_footer()
########################################################################
# Form BM 9 I- ANIMATIONS, PUBLICATIONS ET FORMATION
########################################################################
f9 = GenForms(bibType='BM', encoding='latin1',
              filename='FormBM_report9_autogen.xml', no_generation=True )
f9.main_header()
f9.add_h1(title=(u"I- ANIMATIONS, PUBLICATIONS ET FORMATION"),
          help_file='help9')
# I10  I20
f9.add_h2(title=u" I.1/2 ANIMATIONS")
f9.add_th_comment(u"La bibliothèque organise-t-elle  régulièrement des"
                  u" animations dans l'année (heures du conte, club de "
                  u"lecteurs) ?")
data = u"""
à destination des enfants      I11
à destination des adultes      I12
"""
body, xyz_labels = f9.raw_text2lines(data=data)
f9.table(body, xyz_labels)
data = u"""
La bibliothèque a-t-elle organisé ou co-organisé dans l'année des manifestations culturelles ?        I13
"""
body, xyz_labels = f9.raw_text2lines(data=data)
f9.table(body, xyz_labels)
f9.add_th_comment(u"si oui, combien ?")
data = u"""
Fête/salon du livre             I14
Expositions                     I15
Conférences                     I16
Rencontres d'auteurs/lectures   I17
Ateliers d'écriture             I18
Spectacles                      I19
Concerts                        I20
Autres                          I21
"""
body, xyz_labels = f9.raw_text2lines(data=data)
f9.table(body, xyz_labels)

# I30
f9.add_h2(title=u"I.3 PUBLICATIONS")

data = u"""
La bibliothèque édite-t-elle des : Bulletin d'information I31
La bibliothèque édite-t-elle des : Bibliographies sélectives I32
La bibliothèque édite-t-elle des : Catalogue d'exposition I33
La bibliothèque édite-t-elle des : Autres I34
"""
body, xyz_labels = f9.raw_text2lines(data=data)
f9.table(body, xyz_labels)

data = u"""
La bibliothèque a-t-elle édité des documents dans l'année ? oui non I35
"""
body, xyz_labels = f9.raw_text2lines(data=data)
f9.table(body, xyz_labels)

f9.add_th_comment(u"si oui, préciser combien de titres ou de fascicules ")

data = u"""
Bulletin d'information I36
Bibliographies sélectives I37
Catalogue d'exposition I38
Autres I39
"""
body, xyz_labels = f9.raw_text2lines(data=data)
f9.table(body, xyz_labels)


# I40
f9.add_h2(title=u"I.4 FORMATIONS DISPENSÉES PAR LA BIBLIOTHÈQUE")
data = u"""
Nombre d'heures de cours assurées par le personnel (ENSSIB, CRFCB, ABF, CNFPT, BDP, )  I41
"""
body, xyz_labels = f9.raw_text2lines(data=data)
f9.table(body, xyz_labels)
f9.add_th_comment(u"ACCUEIL DE STAGIAIRES")
data = u"""
##YZ## NB DE STAGIAIRES  Y ##  NB DE JOURNÉES CONSACRÉES  À L'ACCUEIL  Z
Corps et cadres d'emploi des métiers des bibliothèques, de la documentation ou des archives        I42
Autres   I43
TOTAL                 I44
"""
body, xyz_labels = f9.raw_text2lines(data=data)
f9.table(body, xyz_labels)

f9.add_th_comment(u"FORMATIONS ORGANISÉES PAR LA BIBLIOTHÈQUE")
data = u"""
##YZ##NB DE PARTICIPANTS  Y ##  NB DE JOURNÉES DE FORMATION Z
Professionnels I45
Autres                I46
TOTAL                 I47
"""
body, xyz_labels = f9.raw_text2lines(data=data)
f9.table(body, xyz_labels)

data =u"""
##YZ## NB DE JOURNEES D'ETUDE  Y  ## NB DE PARTICIPANTS  Z
JOURNEES D'ETUDE, RENCONTRES PROFESSIONNELLES I48
"""
body, xyz_labels = f9.raw_text2lines(data=data)
f9.table(body, xyz_labels)


f9.main_footer()


########################################################################
# Form BM 10 J- Annexes
# Form BM 11 K- EPCI
########################################################################
f10 = GenForms(bibType='BM', encoding='latin1',
               filename='FormBM_report10_autogen.xml',
               no_generation=True )
f10.main_header()
f10.add_h1(title=(u"Annexes"),
          help_file='help2')
# F10
data = u"""
##TUVWXYZ##NOM ##ADRESSE ##CP##  VILLE ##TÉLÉPHONE## TÉLÉCOPIE ##COURRIEL
1  J1
2  J2
3  J3
4  J4
5  J5
6  J6
7  J7
8  J8
9  J9
10 J10
11 J11
12 J12
13 J13
14 J14
15 J15
"""
body, xyz_labels = f10.raw_text2lines(data=data)
f10.table(body, xyz_labels)

# Manual changes were made so now 'FormBM_report11.xml' is the one
# So we comment  f10.main_footer()
f10.main_footer()

########################################################################
# Form BM 11 K- EPCI
########################################################################
f11 = GenForms(bibType='BM', encoding='latin1',
              filename='FormBM_report11_autogen.xml', no_generation=True)
f11.main_header()
f11.add_h1(title=(u"FICHE DE RENSEIGNEMENTS concernant les Etablissements"
                  u" publics de coopération intercommunale (EPCI) <br/> ayant "
                  u"compétence culturelle"),
          help_file='help2')
# f11
data = u"""
Intitulé de l'EPCI :         K1
Population totale :          K2
"""
body, xyz_labels = f11.raw_text2lines(data=data)
f11.table(body, xyz_labels)
#
body, xyz_labels = f11.raw_text2lines(data=data)
f11.table(body, xyz_labels)
#
data = u"""
Date de création de l'EPCI :   K7
Date du tansfert de la compétence culturelle :   K8
"""
body, xyz_labels = f11.raw_text2lines(data=data)
f11.table(body, xyz_labels)


f11.add_th_comment(u"Liste des communes adhérentes :")
data = u"""
commune 1 :     K9
commune 2 :     K10
commune 3 :     K11
commune 4 :     K12
commune 5 :     K13
commune 6 :     K14
commune 7 :     K15
"""
body, xyz_labels = f11.raw_text2lines(data=data)
f11.table(body, xyz_labels)

data = u"""
Intitulé et adresse de la bibliothèque de la ville-centre :     K16
"""
body, xyz_labels = f11.raw_text2lines(data=data)
f11.table(body, xyz_labels)

data = u"""
##VWXYZ##Communes ayant une bibliothèque (1)## Population  ## Gestion de la bibliothèque Communale## Gestion de la bibliothèque Intercom-munale   ## Cas particulier(2)
Commune1     K17
Commune2     K18
Commune3     K19
Commune4     K20
Commune5     K21
Commune6     K22
Commune7     K23
Commune8     K24
Commune9     K25
Commune10    K26
Commune11    K27
Commune12    K28
Commune13    K29
Commune14    K30
Commune15    K31
"""
body, xyz_labels = f11.raw_text2lines(data=data)
f11.table(body, xyz_labels)
f11.add_th_comment(u"(1) y compris la ville-centre)")
f11.add_th_comment(u"(2) par exemple : gestion différente pour la centrale " \
                  u" et les annexes ou gestion déléguée à une association")

f11.main_footer()
print ''
