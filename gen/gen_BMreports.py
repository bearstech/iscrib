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
f1.add_h1(title=u'A- �L�MENTS FINANCIERS ( en euros, sans d�cimales)',
          help_file='help1')
# A1
f1.add_h2(title=u'A.1 DEPENSES DE FONCTIONNEMENT PROPRES A LA BIBLIOTH�QUE')
data = u"""
Pour le personnel : salaires et charges,  A11
Pour les acquisitions de tous documents et abonnements A12
Pour la reliure et l'�quipement des documents A13
Pour la maintenance informatique A14
Pour l'animation (communication, impression, d�fraiement) A15
TOTAL (A11� A15) A16"""
body, trach = f1.raw_text2lines(data=data)
f1.table(body)

# A2
f1.add_h2(title=u"A.2 DEPENSES D'INVESTISSEMENT PROPRES A LA BIBLIOTH�QUE")
data = u"""
Pour le b�timent (construction, agrandissement, r�novation)     A21
Pour le mobilier et le mat�riel (y compris achat de v�hicules)  A22
Pour l'informatique (logiciel et mat�riel)                      A23
Pour les acquisitions de tous documents et abonnements          A24
TOTAL (A21� A24)                                                A25
"""
body, trach = f1.raw_text2lines(data=data)
f1.table(body)

# A3
f1.add_h2(title=u"A.3 RECETTES PROPRES A LA BIBLIOTH�QUE")
data = u"""
Montant total des droits d'inscription per�us dans l'ann�e   A31
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
f2.add_h1(title=(u"B- LOCAUX - V�HICULES - �QUIPEMENT INFORMATIQUE"
                 u" ET INFORMATISATION "),
          help_file='help2')
# B1
f2.add_h2(title=u'B.1 LOCAUX')
data = u"""
##XYZ## Centrale  X ##  Annexes Y ##  Total Z
Surface en m� horsoeuvre nette SHON (services publics et int�rieurs confondus)   B11
Nombre de b�timents                                                              B12
Nombre de places assises (hors auditorium et caf�t�ria)                          B13
"""
body, xyz_labels = f2.raw_text2lines(data=data)
f2.table(body, xyz_labels)
data = u"""
La biblioth�que poss�de-t-elle un espace sp�cifique pour l'accueil des personnes handicap�es ?   B14
Nombre de places assises dans cet espace sp�cifique                                              B15
"""
body, xyz_labels = f2.raw_text2lines(data=data)
f2.table(body, xyz_labels)

# B2
f2.add_h2(title=u'B. 2 V�HICULES')
data = u"""
Nombre total de bus : bibliobus ou m�diabus (musibus, artobus, etc.) B21
Dont nombre de bus faisant du pr�t direct                            B22
Autres v�hicules (fourgonnettes, voitures l�g�res)                   B23
"""
body, xyz_labels = f2.raw_text2lines(data=data)
f2.table(body, xyz_labels)
# B3
f2.add_h2(title=u'B.3/4 �QUIPEMENT INFORMATIQUE ET INFORMATISATION')
data = u"""
La biblioth�que est-t-elle �quip�e d'un logiciel de gestion de  catalogue ?  B31
Si oui, pr�ciser lequel :                B32
Dans l'ann�e, la biblioth�que a-t-elle import� des notices pour alimenter  catalogue ?  B33
Si oui, dans quelle proportion ? %    B34
Si la biblioth�que poss�de des documents patrimoniaux, leur catalogue est- au moins en partie informatis� ? B35
Si oui : nombre de notices   B36
"""
body, xyz_labels = f2.raw_text2lines(data=data)
f2.table(body, xyz_labels)
# B4

data = u"""
##XY##  Professionnels  X ##  Publics   Y
Nombre de postes informatiques sans acc�s internet                      B37
Nombre de postes informatique avec acc�s internet                       B38
TOTAL                                                                   B39
"""
body, xyz_labels = f2.raw_text2lines(data=data)
f2.table(body, xyz_labels)
data = u"""
Poss�dez-vous un acc�s public � internet ?      B40
"""
body, xyz_labels = f2.raw_text2lines(data=data)
f2.table(body, xyz_labels)

f2.add_th_comment(u"Si oui, l'acc�s public � internet est-il :")
data = u"""
Enti�rement gratuit ?          B41
Payant, m�me partiellement ?   B42
"""
body, xyz_labels = f2.raw_text2lines(data=data)
f2.table(body, xyz_labels)

data = u"""
La biblioth�que a-t-elle des �quipements informatiques sp�cifiques pour les personnes handicap�es ? B43
"""
body, xyz_labels = f2.raw_text2lines(data=data)
f2.table(body, xyz_labels)

f2.add_th_comment(u"Si oui, lesquels ?")
data = u"""
Appareils de grossissement          B44
R�gles tactiles                     B45
Logiciels adapt�s                   B46
Autres, pr�ciser :                  B47
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
f3.add_h2(title=u"C.1 FONCTION PUBLIQUE : FILI�RE CULTURELLE")

data = u"""
##WXYZ##  NB DE PERSONNES ##  NB  D'EMPLOIS Equivalent Temps Plein (ETP)## NB DE PERSONNES AYANT SUIVI UNE FORMATION DANS L'ANNEE##Responsable de la biblioth�que ?
Conservateurs d'Etat                    C11
Conservateurs territoriaux              C12
Biblioth�caires                         C13
Assistants qualifi�s de conservation    C14
Assistants de conservation              C15
Agents qualifi�s du patrimoine          C16
Agents du patrimoine                    C17
"""
body, xyz_labels = f3.raw_text2lines(data=data)
f3.table(body, xyz_labels)
# C20
f3.add_h2(title=(u"C.2 FONCTION PUBLIQUE : AUTRES FILI�RES  (administrative, "
                  "technique, sociale...)"))
data = u"""
##WXYZ##  NB DE PERSONNES ##  NB  D'EMPLOIS D'ETP  ## NB DE PERSONNES AYANT SUIVI UNE FORMATION DANS L'ANNEE ##Responsable de la biblioth�que ?
Personnels d'autres fili�res  Cat. A C21
Personnels d'autres fili�res  Cat. B C22
Personnels d'autres fili�res  Cat. C C23
"""
body, xyz_labels = f3.raw_text2lines(data=data)
f3.table(body, xyz_labels)
# C30
f3.add_h2(title=(u"C.3 AUTRES PERSONNELS REMUN�R�S"))
data = u"""
##WXYZ##  NB DE PERSONNES##  NB  D'EMPLOIS D'ETP  ## NB DE PERSONNES AYANT SUIVI UNE FORMATION DANS L'ANNEE##Responsable de la biblioth�que ?
Agents non titulaires/emplois non aid�s par l'Etat (contractuels, vacataires...) qualifi�s C31
Agents non titulaires/emplois non aid�s par l'Etat (contractuels, vacataires...) non qualifi�s C32
Agents non titulaires/ emplois aid�s par l'Etat ( C.E.S., C.E.C., C.E.J,...) qualifi�s  C33
Agents non titulaires/ emplois aid�s par l'Etat ( C.E.S., C.E.C., C.E.J,...) non qualifi�s   C34
"""
body, xyz_labels = f3.raw_text2lines(data=data)
f3.table(body, xyz_labels)
# C40
f3.add_h2(title=u"C.4 B�N�VOLES")
data = u"""
##WXYZ##  NB DE PERSONNES ##  NB  D'EMPLOIS D'ETP  ## NB DE PERSONNES AYANT SUIVI UNE FORMATION DANS L'ANNEE ##Responsable de la biblioth�que ?
B�n�voles qualifi�s (exemple : ABF, BDP, etc)        C41
B�n�voles non form�s           C42
TOTAL (C11 � C42)              C43
"""
body, xyz_labels = f3.raw_text2lines(data=data)
f3.table(body, xyz_labels)
# C50
f3.add_h2(title=(u"C.5 NOMBRE TOTAL DE PERSONNES AYANT SUIVI UNE FIA"
                  " (formation initiale d'application)"))
data = u"""
DANS L'ANN�E :                           C51
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

f4.add_th_comment(u"COLLECTIONS : nombre de documents (en nombre d'unit�s)"
                  u" appartenant � la biblioth�que")
# D10 et D20
f4.add_h2(title=u"D. 1/ 2  LIVRES ET AUTRES DOCUMENTS (hors patrimoine et "
                u"p�riodiques)")
data = u"""
##XYZ##    ADULTES X ##  ENFANTS Y ##  TOTAL   Z
Nombre de livres en libre acc�s pour le pr�t                            D11
Nombre de livres en libre acc�s r�serv�s a la consultation sur place    D12
Nombre total de livres en libre acc�s  (D11+D12)                        D13
Livres non patrimoniaux en magasin                                      D14
TOTAL  (D13 + D14)                                                      D15
Vid�ogrammes                                                            D16
Phonogrammes                                                            D17
C�d�roms sauf p�riodiques                                               D18
"""
body, xyz_labels = f4.raw_text2lines(data=data)
f4.table(body, xyz_labels)

data = u"""
Cartes et plans                            D19
Partitions                                 D20
Documents graphiques                       D21
Autres                                     D22
Documents num�riques                       D23
Bases de donn�es                           D24
"""
body, xyz_labels = f4.raw_text2lines(data=data)
f4.table(body, xyz_labels)

data = u"""
##XYZ##    ADULTES X ##  ENFANTS Y ##  TOTAL   Z
Dont documents adapt�s aux personnes handicap�es (braille, livres en gros caract�res, livres parl�s,...) D25
"""
body, xyz_labels = f4.raw_text2lines(data=data)
f4.table(body, xyz_labels)

# D30
f4.add_h2(title=u"D.3 DOCUMENTS PATRIMONIAUX (hors p�riodiques)")
data = u"""
Livres imprim�s                            D31
Manuscrits                                 D32
Documents graphiques, cartes et plans      D33
Documents num�riques                       D34
Bases de donn�es                           D35
Autres : monnaies, etc.                    D36
TOTAL (D31 � D36)                          D37
"""
body, xyz_labels = f4.raw_text2lines(data=data)
f4.table(body, xyz_labels)

# D40
f4.add_h2(title=u"D.4 P�RIODIQUES")
data = u"""
Nombre de titres de p�riodiques conserv�s (titres morts ou courants) imprim�s                  D41
Dont nombre de p�riodiques patrimoniaux                                                        D42
Nombre de titres de p�riodiques conserv�s (titres morts ou courants) sur C�d�roms ou en ligne  D43
Nombre total de titres de p�riodiques conserv�s ou non conserv�s                               D44
"""
body, xyz_labels = f4.raw_text2lines(data=data)
f4.table(body, xyz_labels)
                            

f4.main_footer()
########################################################################
# Form BM 5 E- ACQUISITIONS ET �LIMINATIONS DE L'ANN�E
########################################################################
f5 = GenForms(bibType='BM', encoding='latin1',
              filename='FormBM_report5_autogen.xml', no_generation=True)
f5.main_header()
f5.add_h1(title=(u"E- ACQUISITIONS ET �LIMINATIONS DE L'ANN�E"),
          help_file='help5')
# E10
f5.add_h2(title=u"E. 1 NOMBRE DE DOCUMENTS ACHET�S  (hors p�riodiques "
                u"et documents patrimoniaux)")
data = u"""
##XYZ##   ADULTES X ##  ENFANTS Y ##  TOTAL Z
Livres                            E11
Phonogrammes                      E12
Vid�ogrammes                      E13
C�d�roms                          E14
Autres documents                  E15
Documents num�riques  			  E16
Dont documents adapt�s aux personnes handicap�es (braille, livres en gros caract�res, livres parl�s...)  E17
"""
body, xyz_labels = f5.raw_text2lines(data=data)
f5.table(body, xyz_labels)
# E20
f5.add_h2(title=u"E. 2 NOMBRE DE DOCUMENTS ENTR�S PAR DONS, LEGS OU D�P�T LEGAL "
                u"(hors p�riodiques et documents patrimoniaux )")
data = u"""
##XYZ##   ADULTES X ##  ENFANTS Y ##  TOTAL Z
Livres                                E21
Phonogrammes                          E22
Vid�ogrammes                          E23
C�d�roms                              E24
Autres documents                      E25
Documents num�riques                  E26
dont documents adapt�s aux personnes handicap�es (braille, livres en gros caract�res, livres parl�s...) E27
"""
body, xyz_labels = f5.raw_text2lines(data=data)
f5.table(body, xyz_labels)
# E30
f5.add_h2(title=u"E. 3 NOMBRE DE DOCUMENTS RETIR�S DE L'INVENTAIRE"
                u" (hors documents patrimoniaux)")
data = u"""
##XYZ##   ADULTES X ##  ENFANTS Y ##  TOTAL Z
Livres                                E31
P�riodiques (unit�s mat�rielles)      E32
Phonogrammes                          E33
Vid�ogrammes                          E34
C�d�roms                              E35
Autres documents                      E36
Documents num�riques                  E37
Dont documents adapt�s aux personnes handicap�es (braille, livres en gros caract�res, livres parl�s...) E38
"""
body, xyz_labels = f5.raw_text2lines(data=data)
f5.table(body, xyz_labels)
# E40
f5.add_h2(title=u"E.4 NOMBRE DE DOCUMENTS PATRIMONIAUX ACQUIS "
                u"(achats, dons, legs)")
data = u"""
##XYZ## ACHATS  X ##  DONS, LEGS  Y ##  TOTAL Z
Livres imprim�s                          E41
P�riodiques                              E42
Manuscrits : nombre de cotes             E43
Documents graphiques, cartes et plans    E44
Autres (monnaies, ...)                   E45
TOTAL (E41 �  E45)                       E46
"""
body, xyz_labels = f5.raw_text2lines(data=data)
f5.table(body, xyz_labels)
# E50
f5.add_h2(title=u"E. 5  NOMBRE DE P�RIODIQUES ACQUIS"
                u"(ACH�TS, DONS, LEGS)")
data = u"""
##XYZ##   ADULTES X ##  ENFANTS Y ##  TOTAL Z
Nombre d'abonnements en cours (payants et gratuits, support imprim� ou microforme)   E51
Nombre d'abonnements en cours sur c�d�roms                                           E52
Nombre d'abonnements en cours en ligne                                               E53
"""
body, xyz_labels = f5.raw_text2lines(data=data)
f5.table(body, xyz_labels)
# E60
f5.add_h2(title=u" E. 6/7 D�PENSES D'ACQUISITION"
                u" (en euros, sans  d�cimale)")
data = u"""
##XYZ##   ADULTES X ##  ENFANTS Y ##  TOTAL Z
Livres                              E61
Phonogrammes                        E62
Vid�ogrammes                        E63
C�d�roms                            E64
Autres documents                    E65
dont documents adapt�s aux personnes handicap�es (braille, livres en gros caract�res, livres parl�s...) E66
SOUS-TOTAL (E61 � E65)                         E67
P�riodiques imprim�s                           E68
P�riodiques sur c�d�roms                       E69
P�riodiques en ligne                           E70
SOUS-TOTAL (E68 � E70)                         E71
Documents num�riques                           E72
Documents patrimoniaux                         E73
TOTAL (E67 + E71 + E72 + E73)                  E74
"""
body, xyz_labels = f5.raw_text2lines(data=data)
f5.table(body, xyz_labels)

f5.main_footer()
########################################################################
# Form BM 6 F- COOP�RATION ET R�SEAU
########################################################################
f6 = GenForms(bibType='BM', encoding='latin1',
              filename='FormBM_report6_autogen.xml', no_generation=True)
f6.main_header()
f6.add_h1(title=(u"COOP�RATION ET R�SEAU (F17-F20)"),
          help_file='help6')
# F10
data = u"""
La biblioth�que appartient-elle au r�seau de la BDP ?                  F11
La biblioth�que appartient-elle � un autre r�seau documentaire ?       F12
si oui, lequel :                                                       F13
La biblioth�que participe-t-elle � des actions de coop�ration ?        F14
si oui, pr�ciser lesquelles :                                          F15
"""
body, xyz_labels = f6.raw_text2lines(data=data)
f6.table(body, xyz_labels)

data = u"""
La biblioth�que a-t-elle men� en 2005 des actions internationales ?    F16
"""
body, xyz_labels = f6.raw_text2lines(data=data)
f6.table(body, xyz_labels)

f6.add_th_comment(u"Si oui pr�ciser :")
data= u"""
Accueils / �changes de professionnels, �crivains                       F17
Voyages d'�tude, expertises � l'�tranger                               F18
Dons de livres                                                         F19
Autres actions de coop�ration                                          F20
"""
body, xyz_labels = f6.raw_text2lines(data=data)
f6.table(body, xyz_labels)

f6.add_th_comment(u"Si la biblioth�que entretient des partenariats avec des structures publiques ou priv�es (associations...) oeuvrant dans le domaine du handicap, pr�ciser les domaines d'intervention :")

data = u"""
Accueil de b�n�voles dans la biblioth�que                              F21
D�p�t de livres dans les locaux du partenaire                          F22
Autres                                                                 F23
"""
body, xyz_labels = f6.raw_text2lines(data=data)
f6.table(body, xyz_labels)

f6.main_footer()


########################################################################
# Form BM 7 G- ACTIVIT�S DE LA BIBLIOTH�QUE
########################################################################

# FormBM_report7.xml n'est plus autog�n�re
f7 = GenForms(bibType='BM', encoding='latin1',
              filename='FormBM_report7_autogen.xml', no_generation=True)
f7.main_header()
f7.add_h1(title=(u"G-  ACTIVIT�S DE LA BIBLIOTH�QUE"),
          help_file='help7')
# G10
f7.add_h2(title=u"G.1 OUVERTURE � TOUS LES PUBLICS"
                u"(hors accueils de publics sp�cifiques et de classes)")
data = u"""
##HM## Heures H## Minutes M
Nombre d'heures d'ouverture par semaine    G12
Nombre d'heures d'ouverture dans l'ann�e   G13
"""

body, xyz_labels = f7.raw_text2lines(data=data)
f7.table(body, xyz_labels)

# G20 et G30
f7.add_h2(title=u"G.2/3 INSCRITS ET EMPRUNTEURS")
data = u"""
##WXYZ## HOMMES  W## FEMMES  X ## TOTAL Y## TOTAL EMPRUNTEURS ACTIFS  Z
Age non d�clar�           G20
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
Pr�ciser combien d'entre eux r�sident dans la commune (ou dans les communes du groupement si la biblioth�que est intercommunale) G27
"""
body, xyz_labels = f7.raw_text2lines(data=data)
f7.table(body, xyz_labels)

data = u"""
Nombre d'entr�es dans la biblioth�que centrale                                    G28
Nombre d'entr�es dans les biblioth�ques annexes ou autres biblioth�ques du r�seau G29
Nombre total  d'entr�es dans l'ann�e (biblioth�que centrale et annexes)           G30
Nombre de collectivit�s utilisatrices                                             G31
dont nombre de classes                                                            G32
Pr�ciser combien d'entre elles sont situ�es dans la commune (ou le groupement de communes si la biblioth�que est intercommunale) G33
"""
body, xyz_labels = f7.raw_text2lines(data=data)
f7.table(body, xyz_labels)

# G40
f7.add_h2(title=u"G. 4/5 NOMBRE DE PR�TS ET COMMUNICATIONS EFFECTU�S DANS L'ANN�E")
data = u"""
##XYZ## ADULTES X ##  ENFANTS Y ##   TOTAL Z
Pr�ts de livres             G41
Pr�ts de p�riodiques        G42
Pr�ts de phonogrammes       G43
Pr�ts de vid�ogrammes       G44
Pr�ts de c�d�roms           G45
Pr�ts d'autres documents    G47
TOTAL DES PR�TS (G41 � G47) G48
"""
body, xyz_labels = f7.raw_text2lines(data=data)
f7.table(body, xyz_labels)

f7.add_h2(title=u"Nombre de communications sur place (documents en magasin)")
data = u"""
Documents hors patrimoine   G49
Documents patrimoniaux      G50
TOTAL (G49 � G50)           G51
"""
body, xyz_labels = f7.raw_text2lines(data=data)
f7.table(body, xyz_labels)
              
f7.main_footer()

########################################################################
# Form BM 8 H-   SERVICES OFFERTS PAR LA BIBLIOTH�QUE
########################################################################
f8 = GenForms(bibType='BM', encoding='latin1',
              filename='FormBM_report8_autogen.xml',
              no_generation=True)

f8.main_header()
f8.add_h1(title=(u" SERVICES OFFERTS PAR LA BIBLIOTH�QUE"),
          help_file='help8')
# H10
f8.add_h2(title=u"H. 1/2 SERVICES AUX USAGERS")
data = u"""
La biblioth�que organise-t-elle des actions de formation pour les usagers ?  H11
"""
body, xyz_labels = f8.raw_text2lines(data=data)
f8.table(body, xyz_labels)

f8.add_th_comment(u"La biblioth�que offre-t-elle ces services ?")
data = u"""
Guide du lecteur              H12
R�servation                   H13
Portage � domicile            H14
Services pour les personnes handicap�es           H15
Pr�t inter-biblioth�ques                          H16
"""
body, xyz_labels = f8.raw_text2lines(data=data)
f8.table(body, xyz_labels)
f8.add_th_comment(u"  Si oui")
data = u"""
Nombre de demandes re�ues                         H17
Nombre de demandes re�ues satisfaites             H18
Nombre de demandes �mises                         H19
Nombres de demandes �mises satisfaites            H20
"""
body, xyz_labels = f8.raw_text2lines(data=data)
f8.table(body, xyz_labels)
data = u"""
Autres                                            H21
"""
body, xyz_labels = f8.raw_text2lines(data=data)
f8.table(body, xyz_labels)
# H30
f8.add_h2(title=u"H. 3 SERVICES � DISTANCE")
data = u"""
La biblioth�que a-t-elle un site web ?                           H31
Ce site donne-t-il acc�s au catalogue de la biblioth�que ?       H32
"""
body, xyz_labels = f8.raw_text2lines(data=data)
f8.table(body, xyz_labels)
f8.add_th_comment(u"Quels services sont offerts sur le site web ?")
data = u"""
Consultation du catalogue                H33
R�servation en ligne                     H34
Consultation du compte lecteur           H35
Consultation des fonds num�ris�s         H36
Autres (pr�ciser)                        H37
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
Le site de la biblioth�que est-il accessible aux d�ficients visuels par des proc�d�s techniques adapt�s ?  H39
"""
body, xyz_labels = f8.raw_text2lines(data=data)
f8.table(body, xyz_labels)

#H30 H40
f8.add_h2(title=u"H. 4/5 SERVICES AUX COLLECTIVIT�S")
data = u"""
La biblioth�que organise-t-elle des actions de formation pour les collectivit�s ?  H41
Si oui, pr�ciser : ( multim�dia, formation des enseignants)  H42
"""
body, xyz_labels = f8.raw_text2lines(data=data)
f8.table(body, xyz_labels)
f8.add_th_comment(u"D�P�T DANS LES COLLECTIVIT�S DESSERVIES")
data = u"""
##YZ##NB DE COLLECTIVIT�S Y ##  NB DOC D�POS�S  Z
Ecoles                         H52
Coll�ges                       H53
Lyc�es                         H54
Prisons                        H55
H�pitaux                       H56
Maisons de retraite            H57
Comit� d'entreprise            H58
Petite enfance (cr�che, PMI)   H59
Centres sociaux                H60
Centres de loisirs et de vacances  H61
Autres                         H62
TOTAL (H52 � H62)              H63
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
f9.add_th_comment(u"La biblioth�que organise-t-elle  r�guli�rement des"
                  u" animations dans l'ann�e (heures du conte, club de "
                  u"lecteurs) ?")
data = u"""
� destination des enfants      I11
� destination des adultes      I12
"""
body, xyz_labels = f9.raw_text2lines(data=data)
f9.table(body, xyz_labels)
data = u"""
La biblioth�que a-t-elle organis� ou co-organis� dans l'ann�e des manifestations culturelles ?        I13
"""
body, xyz_labels = f9.raw_text2lines(data=data)
f9.table(body, xyz_labels)
f9.add_th_comment(u"si oui, combien ?")
data = u"""
F�te/salon du livre             I14
Expositions                     I15
Conf�rences                     I16
Rencontres d'auteurs/lectures   I17
Ateliers d'�criture             I18
Spectacles                      I19
Concerts                        I20
Autres                          I21
"""
body, xyz_labels = f9.raw_text2lines(data=data)
f9.table(body, xyz_labels)

# I30
f9.add_h2(title=u"I.3 PUBLICATIONS")

data = u"""
La biblioth�que �dite-t-elle des : Bulletin d'information I31
La biblioth�que �dite-t-elle des : Bibliographies s�lectives I32
La biblioth�que �dite-t-elle des : Catalogue d'exposition I33
La biblioth�que �dite-t-elle des : Autres I34
"""
body, xyz_labels = f9.raw_text2lines(data=data)
f9.table(body, xyz_labels)

data = u"""
La biblioth�que a-t-elle �dit� des documents dans l'ann�e ? oui non I35
"""
body, xyz_labels = f9.raw_text2lines(data=data)
f9.table(body, xyz_labels)

f9.add_th_comment(u"si oui, pr�ciser combien de titres ou de fascicules ")

data = u"""
Bulletin d'information I36
Bibliographies s�lectives I37
Catalogue d'exposition I38
Autres I39
"""
body, xyz_labels = f9.raw_text2lines(data=data)
f9.table(body, xyz_labels)


# I40
f9.add_h2(title=u"I.4 FORMATIONS DISPENS�ES PAR LA BIBLIOTH�QUE")
data = u"""
Nombre d'heures de cours assur�es par le personnel (ENSSIB, CRFCB, ABF, CNFPT, BDP, )  I41
"""
body, xyz_labels = f9.raw_text2lines(data=data)
f9.table(body, xyz_labels)
f9.add_th_comment(u"ACCUEIL DE STAGIAIRES")
data = u"""
##YZ## NB DE STAGIAIRES  Y ##  NB DE JOURN�ES CONSACR�ES  � L'ACCUEIL  Z
Corps et cadres d'emploi des m�tiers des biblioth�ques, de la documentation ou des archives        I42
Autres   I43
TOTAL                 I44
"""
body, xyz_labels = f9.raw_text2lines(data=data)
f9.table(body, xyz_labels)

f9.add_th_comment(u"FORMATIONS ORGANIS�ES PAR LA BIBLIOTH�QUE")
data = u"""
##YZ##NB DE PARTICIPANTS  Y ##  NB DE JOURN�ES DE FORMATION Z
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
##TUVWXYZ##NOM ##ADRESSE ##CP##  VILLE ##T�L�PHONE## T�L�COPIE ##COURRIEL
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
                  u" publics de coop�ration intercommunale (EPCI) <br/> ayant "
                  u"comp�tence culturelle"),
          help_file='help2')
# f11
data = u"""
Intitul� de l'EPCI :         K1
Population totale :          K2
"""
body, xyz_labels = f11.raw_text2lines(data=data)
f11.table(body, xyz_labels)
#
body, xyz_labels = f11.raw_text2lines(data=data)
f11.table(body, xyz_labels)
#
data = u"""
Date de cr�ation de l'EPCI :   K7
Date du tansfert de la comp�tence culturelle :   K8
"""
body, xyz_labels = f11.raw_text2lines(data=data)
f11.table(body, xyz_labels)


f11.add_th_comment(u"Liste des communes adh�rentes :")
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
Intitul� et adresse de la biblioth�que de la ville-centre :     K16
"""
body, xyz_labels = f11.raw_text2lines(data=data)
f11.table(body, xyz_labels)

data = u"""
##VWXYZ##Communes ayant une biblioth�que (1)## Population  ## Gestion de la biblioth�que Communale## Gestion de la biblioth�que Intercom-munale   ## Cas particulier(2)
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
f11.add_th_comment(u"(2) par exemple : gestion diff�rente pour la centrale " \
                  u" et les annexes ou gestion d�l�gu�e � une association")

f11.main_footer()
print ''
