# -*- coding: ISO-8859-1 -*-
# Import from python
from pprint import pprint
import os

# Import from itools
from itools import get_abspath
from itools.handlers import get_handler
from itools.handlers import IO

# Import from scrib

print_save = """
   <div align="right">
    <input stl:if="not printable" type="button" 
           onclick="window.open('?view=printable', 'xxx', 'toolbar=yes, location=no, status=no, menubar=yes, scrollbars=yes, width=800, height=600') ;return 0;"           value="Imprimer"></input>
    <input stl:if="not printable" type="submit" value="Enregistrer"
           stl:if="is_allowed_to_edit"></input>
  </div>
"""



class GenForms:
    """
    In **GenFormsTemplates.py** we have now an API for genrating complex forms

    This API is called in : **gen_BDPreports.py** and **gen_BMreports.py**
    Schema information is provide by **schemaBDP.py** and **schemaBM.py**

    by executing::

    $ python gen_BMreports.py
    $ python gen_BDPreports.py

    this STL files are created::

    ui/FormBDP_report1_autogen.xml
    ui/FormBDP_report2_autogen.xml
    ui/FormBM_report1_autogen.xml
    ui/FormBM_report2_autogen.xml
    ui/FormBM_report3_autogen.xml

    ####################
    # Exemple 
    f2 = GenForms(encoding='latin1', filename='FormBDP_report2_autogen.xml')
    f2.main_header()
    f2.add_h1(title=(u'B  LOCAUX - VÉHICULES - ÉQUIPEMENT INFORMATIQUE'),
              help_file='help2')
    # B1
    f2.add_h2(title=(u'B.1 LOCAUX : BDP et réseau (surface en m² SHON- '
                     u'hors oeuvre nette)'))

    data = (u' ##XYZ##Centrale X##Annexes Y##Total Z \n'
            u'Surface de la BDP  B11 \n'
            u'Nombre de bâtiments de la BDP ouverts à tous publics    B12 \n'
            u'Nombre de m² ouverts à tous publics                     B13 ')
    body, xyz_labels = f2.raw_text2lines(data=data)
    f2.table(body, xyz_labels)
    f2.main_footer()
    """

    def __init__(self, filename='Form_report2_autogen.xml', encoding='utf8', 
                 bibType='BDP', no_generation=False):
        self.no_generation = no_generation
        self.filename = filename 
        self.encoding = encoding 
        self.data = ''
        if bibType is 'BM':
            from schemaBM import schema 
            self.schema = schema
        if bibType is 'BDP':
            from schemaBDP import schema 
            self.schema = schema


    def main_header(self):
        data = self.data
        out = ("""<?xml version="1.0" encoding="ISO-8859-1"?>\n"""
               """<div xmlns="http://www.w3.org/1999/xhtml" \n"""
               """     xmlns:stl="http://xml.itools.org/namespaces/stl"\n"""
               """     id="formBiblio">\n"""
               """<form action=";report" method="post" name="form">\n """) 
        out += print_save
        out = out % {'current_form' : self.filename.split('.')[0]}
        self.data += out

    def get_depends_fields(self):
        schema = self.schema
        dependencies = {}
        for field_id in schema.keys():
            field_def = schema[field_id]
            if len(field_def) == 3:
                dependencies[field_id] = field_def[2].get('depend_field')
                
        return dependencies

    def get_dependencies(self):
        schema = self.schema
        dependencies = {}
        for field_id in schema.keys():
            field_def = schema[field_id]
            if len(field_def) == 3:
                fields = field_def[2].get('depend_field')
                for field in fields:
                    dependencies[field] = field_id
                
        return dependencies

    def main_footer(self):
        if self.no_generation is True:
            print '  No autogen for STL template   ui/%s' %  self.filename
            return None
        self.data += """</form>\n <p style = "page-break-after:always "></p>\n</div>"""
        path = os.getcwd()
        open('%s/ui/%s' % (path, self.filename), 'w').write(self.data)
        print 'autogen STL template   ui/%s' %  self.filename

    def add_h1(self, title=u'A- ÉLÉMENTS FINANCIERS', help_file='help2'):
        title = title.encode(self.encoding)


        h1 = ('<h1>%(title)s\n' 
              '   <a stl:if="not printable" href="#" style="color:red; border: 1px solid red;"\n'
            """      onclick="window.open(';%(help_file)s', 'xxx', 
              '      toolbar=no,\n"""
              '      location=no, status=no, menubar=no, scrollbars=yes,\n'
            """      width=440, height=600');return 0;">Aide</a>\n"""
              '</h1>\n') % {'title': title, 'help_file': help_file}
        self.data += h1
         
    def add_th_comment(self, title=u'La bibliothèque offre-t-elle ces '
                                   u'services ?'):
        # I do a table here because I want to keep the same th
        title = title.encode(self.encoding)
        th = ("<table>\n" "  <tr>\n" "    <th>%(title)s</th>\n"
              "  </tr>\n" "</table>\n") % {'title': title}
        self.data += th

    def add_h2(self, title=u'A.1 DÉPENSES PROPRES A LA BDP'):
        title = title.encode(self.encoding)
        h1 = ('<h2>%(title)s</h2>\n') % {'title': title}
        self.data += h1


    def raw_text2lines(self, data=None):
        """
        from data make liste
        #####
        data = "
        Pour le personnel : salaires et charges,  A11
        Pour les acquisitions de tous documents et abonnements A12"

        liste = 
        [{'code': ' A11', 
          'code_label': 'Pour le personnel : salaires et charges, '},
         {'code': ' A12',
          'code_label': 'Pour les acquisitions de tous documents 
                         et abonnements'}]
        #####
        or from data2 make liste2

        data2 = "##XYZ##Centrale X##Annexes Y##Total Z
        Surface de laBDP (services publics et intérieurs confondus)   B11
        Nombre de bâtiments de la BDP ouverts à tous publics          B12"

        liste2 = 
        [{'code': 'B11', 'code_values':['fieldB11X','fieldB11Y','fieldB11Z'], 
          'code_label': 'Surface de laBDP (services publics et intérieurs 
                         confondus)'},
         {'code': 'B12', 'code_values':['fieldB12X','fieldB12Y','fieldB12Z'], 
          'code_label': 'Nombre de bâtiments de la BDP ouverts à tous publics'}]

        Les dépendances sont issues du schema
        """
        if self.no_generation is True:
            return None, None
        if data is None:
            data = u"""
        Pour le personnel : salaires et charges,  A11
        Pour les acquisitions de tous documents et abonnements A12
        Pour la reliure et l'équipement des documents A13
        Pour la maintenance informatique A14
        Pour l'animation (communication, impression, défraiement) A15
        Pour la formation A16
        TOTAL (A11à A16) A17"""

        new = []
        lines = [l.strip() for l in data.split('\n')]
        lines = [l for l in lines if l]
       
        firstline = lines[0]
        code_values, xyz_labels = None, None

        if firstline.startswith('##'):
            firstline_list = firstline.split('##')
            xyz_labels = [x.strip() for x in firstline_list[2:]]
            xyz = firstline_list[1].strip()
            xyz_list = [x.strip() for x in xyz]
            for line in lines[1:]:
                line = line.strip()
                if line:
                    dic = {}
                    code_label, code =  line[:-4].strip(), line[-4:].strip()
                    code_values = ['field%s%s' % (code, x)  for x in xyz_list] 
                    dic['code_label'] = code_label 
                    dic['code'] = code 
                    dic['code_values'] = code_values
                    new.append(dic)
        else:
            depends_fields = self.get_depends_fields()
            for line in lines:
                line = line.strip()
                if line:
                    dic = {}
                    code_label, code =  line[:-4], line[-4:]
                    code = code.strip()
                    field_id = 'field' + code
                    
                    if field_id in depends_fields.keys():
                        dic['control_dep'] = depends_fields[field_id]
                            
                    dic['code_label'] = code_label 
                    dic['code'] = code
                    new.append(dic)


        accu = [] 
        for dic in new: 
            accu.append(self.line(**dic))
        body = '\n'.join(accu)
        return body, xyz_labels 
  

    def line(self, code='A11', 
             code_label=u'Pour le personnel: salaires et charges',
             code_values=None, control_dep=None):
        """ 
        code_values is the list of fields ex : [fieldA11]
        the number of columns is len(code_values) + 2
        if code_values is None we assume that the only value is the fieldcode
        Can be called with a dictionary as argument : line(**dic) with
        dic = {'code_label': 'Pour le personnel : salaires et charges, ',
               'code': ' A11', 'code_values':[]}
        """

        temp_nodep = (
        '    <td>\n'
        '      <table><tr style="padding: 10px; text-align: left">'
        '<td>'
        '        <input %(control_dep_on)s type="radio" '
                    ' name="%(col_code)s" ' 
                    'value="1" style="font-size: 8pt;  border:0px"\n'             
        '               stl:attributes="checked %(col_code)s" />Oui'
        '      </td>\n'
        '      <td style="border-left: 1px solid black;text-align: right">'
        '        <input %(control_dep_off)s type="radio" name="%(col_code)s" '
        '               value="0"\n style="font-size: 8pt;  border:0px"\n'
        '               stl:attributes="checked %(col_code)s_not" />Non'
        '      </td>'
        '      </tr></table>'
        '    </td>\n') 


        temp_dep = (
        '    <td>\n'
        '      <table stl:if="%(dependance)s" id="display_%(col_code)s" >'
        '        <tr style="padding: 10px; text-align: left"><td>'
        '        <input %(control_dep_on)s type="radio" name="%(col_code)s" ' 
        '                     value="1" style="font-size: 8pt;  border:0px"\n'             
        '                     stl:attributes="checked %(col_code)s" />Oui'
        '      </td><td style="border-left: 1px solid black;text-align: right">'
        '        <input %(control_dep_off)s type="radio" name="%(col_code)s" '
        '               value="0"\n style="font-size: 8pt;  border:0px"\n'
        '               stl:attributes="checked %(col_code)s_not" />Non'
        '      </td>'
        '      </tr></table>'
        '      <table stl:if="not %(dependance)s" id="display_%(col_code)s" '
                     'style="visibility:hidden">'
        '        <tr style="padding: 10px; text-align: left"><td>'
        '        <input %(control_dep_on)s type="radio" name="%(col_code)s" ' 
        '                     value="1" style="font-size: 8pt;  border:0px"\n'             
        '                     stl:attributes="checked %(col_code)s" />Oui'
        '      </td><td style="border-left: 1px solid black;text-align: right">'
        '        <input %(control_dep_off)s type="radio" name="%(col_code)s" '
        '               value="0"\n style="font-size: 8pt;  border:0px"\n'
        '               stl:attributes="checked %(col_code)s_not" />Non'
        '      </td>'
        '      </tr></table>'
        '    </td>\n')

        string_dep = (
            '    <td>\n'
            '       <div stl:if="not %(dependance)s" id="display_%(col_code)s"'
            '           style="visibility:hidden">'
            '         <input stl:if="not %(dependance)s"\n'
            '             type="text" name="%(col_code)s"\n'
            '             value="" size="8"></input></div>\n'
            '       <div stl:if="%(dependance)s" id="display_%(col_code)s">'
            '         <input stl:if="%(dependance)s" '
                          'stl:attributes="value %(col_code)s"\n'
            '             type="text" name="%(col_code)s"\n'
            '             value="" size="8"></input>\n'
            '       </div>'
            '    </td>\n')

        string_nodep = (
            '    <td>\n'
            '       <input stl:attributes="value %(col_code)s"\n'
            '              type="text" name="%(col_code)s"\n'
            '              value="" size="8"></input>\n'
            '    </td>\n')
         
         
        # make _A11 from fieldA11
        code = code.strip()
        code_label = code_label.strip()


        class_code = '_' + code
        if code_values is None:
            code_values = ['field%s' % code]
        dic = {'code_label': code_label, 
               'code': code, 'class_code': class_code,
               'control_dep' : control_dep}

        start_line = ('  <tr>\n'
                      '    <th>%(code_label)s</th> \n')
        body_line = ''
                
        # print code_values
        dependencies = self.get_dependencies()
        
        for col_code in code_values:
            field_def = self.schema.get(col_code)
            if field_def is None:
                continue
            dependance = dependencies.get(col_code)
            type = field_def[0]
            default = field_def[1]
            params = None
            
            if len(field_def) == 3:
                params = field_def[2]
            
            if type is IO.Boolean:
                # Bool
                control_dep_on = ''
                control_dep_off = ''
        
                if control_dep is not None:
                    deps = "[%s]" % ','.join(["'%s'" % item for item 
                                             in control_dep])
                    control_dep_on = """onclick="switch_on(%s)" """ % deps
                    control_dep_off = """onclick="switch_off(%s)" """ % deps
                    
                if dependance is None:
                    temp = temp_nodep % { 'col_code' : col_code,
                                          'control_dep_on' : control_dep_on, 
                                          'control_dep_off' : control_dep_off}
                    
                else:
                    temp = temp_dep % { 'dependance' : dependance ,
                                        'col_code' : col_code,
                                        'control_dep_on' : control_dep_on, 
                                        'control_dep_off' : control_dep_off}
                
            else:
                # String and Interger
                if dependance is not None:
                    temp = string_dep % {'col_code': col_code,
                                         'dependance' : dependance}
                else:
                    temp = string_nodep  % {'col_code': col_code}
            body_line += temp

        end_line = ('    <td><b stl:attributes="class %(class_code)s">'
                    '%(code)s</b></td>\n'
                    '  </tr>\n')
        all_line = start_line + body_line + end_line 
        return all_line % dic


    def table(self, body='', xyz_labels=None, br_col=None):
        """
        data = (u' ##XYZ##Centrale X##Annexes Y##Total Z \n'
                u'Surface de la BDP  B11 \n'
                u'Nombre de bâtiments de la BDP ouverts à tous publics B12 \n'
                u'Nombre de m² ouverts à tous publics                  B13 ')

        body, xyz_labels = f2.raw_text2lines(data=data)
        f2.table(body, xyz_labels)
        # give :

        <table>
          <colgroup><col width="59%"/><col width="12%"/><col width="12%"/>
                    <col width="12%"/> <col width="5%"/> </colgroup> 
          <tr>
            <td></td>
              <th style="text-align: center">Centrale X</th>
              <th style="text-align: center">Annexes Y</th>
              <th style="text-align: center">Total Z</th>
            <td></td>
          </tr>
          <tr>
            <th>Surface de la BDP </th> 
            <td> <input stl:attributes="value fieldB11X" type="text" 
                        name="fieldB11X" value="" size="8"></input> </td>
            <td> <input stl:attributes="value fieldB11Y" type="text" 
                        name="fieldB11Y" value="" size="8"></input> </td>
            <td> <input stl:attributes="value fieldB11Z" type="text" 
                        name="fieldB11Z" value="" size="8"></input> </td>
            <td> <b stl:attributes="class _B11">B11</b></td>
          </tr>
          <tr> ... </tr>
          <tr> ... </tr>
        </table>

        """
        if self.no_generation is True:
            return None
        if xyz_labels is None:
            nbr_col = 3
        else:
            nbr_col = 2 + len(xyz_labels)

          
        #start = '<table width="100%">\n  <colgroup>\n'
        start = '<table>\n  <colgroup>\n'
        col = []
        first_col = 59
        if nbr_col == 3:
            first_col = 76
        last_col = 5
        rest = 100 - (first_col + last_col)
        width = xyz_labels and int(rest / len(xyz_labels)) or rest
        for i in range(nbr_col):
            if i == 0:
                col.append('    <col width="%s%%"/>\n' % first_col)
            if i == nbr_col - 1:
                col.append('    <col width="%s%%"/>\n' % last_col)
            if i not in [0, nbr_col - 1]:
                col.append('    <col width="%s%%"/>\n' % width)
        cols = ''.join(col)
        cols += '   </colgroup>\n'

        xyz_type_table = ''
        if xyz_labels:
            xyz_type_table += ('  <tr>\n' '  <td></td>\n')
            for x_label in xyz_labels:
                th_col = ('    <th style="text-align: center">' 
                          '%s</th>\n') % x_label
                xyz_type_table += th_col
            xyz_type_table += ('  <td></td>\n' '  </tr>\n')
                

        end = '</table>\n'
        #print start, cols , xyz_type_table , body , end
        all = start + cols + xyz_type_table + body + end
        all = all.encode(self.encoding)
        self.data += all
