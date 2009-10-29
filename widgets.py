# -*- coding: UTF-8 -*-
# Copyright (C) 2005  <jdavid@favela.(none)>
# Copyright (C) 2006 J. David Ibanez <jdavid@itaapy.com>
# Copyright (C) 2006 luis <luis@lucifer.localdomain>
# Copyright (C) 2006-2008 Hervé Cauwelier <herve@itaapy.com>
# Copyright (C) 2008 Henry Obein <henry@itaapy.com>
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

# Import from itools
from itools.csv import CSVFile
from itools.datatypes import XMLContent, XMLAttribute
from itools.html import HTMLParser
from itools.stl import stl

# Import from ikaaro
from ikaaro.skins import UIFile

# Import from scrib
from datatypes import Numeric, NumDecimal, NumTime, Text
from form import SENT, EXPORTED


FIELD_PREFIX = u"#"
WHITESPACE_DIV = u'<div>%s</div>'
BORDER_DIV = u'<div style="border: 1px solid #D7D3D7;">%s</div>'
ENABLE = (u'''onchange="this.form.%s.disabled=false;'''
          u'''this.form.%s.className=''"''')
DISABLE = (u'''onchange="this.form.%s.disabled=true;'''
          u'''this.form.%s.className='access_False'"''')


def radio_widget(context, form, datatype, name, value, readonly=False):
    html = []

    if readonly:
        span = datatype.get_value(value, value)
        if span is None:
            span = ''
        else:
            span = XMLContent.encode(span)
        html.append(WHITESPACE_DIV % span)
    else:
        for option in datatype.get_namespace(value):
            # 0005970: Rendre certains champs d'une fiche professeur
            # accessible suivant une condition oui/non (E5)
            onclick = u""
            for radio_name, select_name in [('TYPE_PED', u'TYPE2'),
                                            ('DIP2', u'DISCCA'),
                                            ('DIP3', u'DISCDE')]:
                if name == radio_name:
                    if option['name'] == '1':
                        onclick = ENABLE % (select_name, select_name)
                    else:
                        onclick = DISABLE % (select_name, select_name)
            checked = u'checked="checked" ' if option['selected'] else u''
            input = u'<input type="radio" name="%s" value="%s" %s %s /> %s' % (
                    name, option['name'], checked, onclick, option['value'])
            if name in context.bad_types:
                input = u'<span class="badtype" title="%s">%s</span>' %\
                        (u'Mauvaise valeur', input)
            elif datatype.is_mandatory and not value:
                input = u'<span class="mandatory" title="%s">%s</span>' %\
                        (u'Champ obligatoire', input)
            html.append(WHITESPACE_DIV % input)

    return BORDER_DIV % u''.join(html)



def checkbox_widget(context, form, datatype, name, value, readonly=False):
    html = []

    if readonly:
        span = datatype.get_value(value, value)
        html.append(WHITESPACE_DIV % span)
    else:
        for option in datatype.get_namespace(value):
            checked = u'checked="checked" ' if option['selected'] else u''
            input = u'<input type="checkbox" name="%s" value="%s" %s /> %s' % (
                    name, option['name'], checked, option['value'])
            if name in context.bad_types:
                input = u'<span class="badtype" title="%s">%s</span>' %\
                        (u'Mauvaise valeur', input)
            elif datatype.is_mandatory and not value:
                input = u'<span class="mandatory" title="%s">%s</span>' %\
                        (u'Champ obligatoire', input)
            html.append(WHITESPACE_DIV % input)

    return BORDER_DIV % u''.join(html)



def select_widget(context, form, datatype, name, value, readonly=False):
    html = []

    if readonly:
        span = datatype.get_value(value, value)
        html.append(WHITESPACE_DIV % span)
    else:
        select = [u'<select name="%s"' % name]
        css_class = []
        # 0005970: Rendre certains champs d'une fiche professeur
        # accessible suivant une condition oui/non (E5)
        for select_name, radio_name in [('TYPE2', 'TYPE_PED'),
                                        ('DISCCA', 'DIP2'),
                                        ('DISCDE', 'DIP3')]:
            if name == select_name:
                radio_value = form.handler.get_value(radio_name)
                if radio_value not in (True, '1'):
                    select.append(u' disabled="disabled"')
                    css_class.append(u"access_False")
                break
        # Check for "errors"
        if name in context.bad_types:
            select.append(u' title="Mauvaise valeur"')
            css_class.append(u"badtype")
        elif datatype.is_mandatory and not value:
            select.append(u' title="Champ obligatoire"')
            css_class.append(u"mandatory")
        if css_class:
            select.append(u' class="%s"' % u" ".join(css_class))
        select.append(u">")
        html.append(u"".join(select))
        for option in datatype.get_namespace(value):
            checked = u'selected="selected" ' if option['selected'] else u''
            input = u'<option value="%s" %s>%s</option>' % (
                    option['name'], checked, option['value'])
            html.append(input)
        html.append(u'</select>')

    return BORDER_DIV % (WHITESPACE_DIV % u''.join(html))



def get_input_widget(name, form, context, tabindex=None, readonly=False):
    datatype = form.handler.schema[name]
    # take data from the request or from the form
    if context.has_form_value(name):
        value = context.get_form_value(name)
    else:
        value = form.handler.get_value(name)

    format = datatype.format.upper()
    if format == 'SELECT':
        return select_widget(context, form, datatype, name, value, readonly)
    elif format == 'RADIO':
        return radio_widget(context, form, datatype, name,
                datatype.encode(value), readonly)
    elif format == 'CHECKBOX':
        return checkbox_widget(context, form, datatype, name, value,
                readonly)
    else:
        size = format
    # Complex representation
    if not isinstance(value, basestring):
        value = datatype.encode(value)
    if not isinstance(value, unicode):
        value = unicode(value, 'utf8')
    if isinstance(datatype, Text):
        if readonly:
            attrs = {'style': u'white-space: pre', 'class': 'readonly'}
            pattern = u'<div %s>'
        else:
            attrs = {'name': name, 'rows': datatype.format, 'cols': 100}
            pattern = u'<textarea %s>'
    else:
        if readonly:
            attrs = {'class': 'readonly'}
            pattern = u'<div %s>'
        else:
            attrs = {'type': u'text', 'name': name,
                     'value': XMLAttribute.encode(value),
                     'size': size, 'maxlength': size}
            if tabindex:
                attrs['tabindex'] = tabindex
            pattern = u'<input %s />\n'
    # Right-align numeric fields
    if isinstance(datatype, Numeric):
        attrs['class'] = u'num'
    # Check for "errors"
    if name in context.bad_types:
        attrs['class'] = u'badtype'
        attrs['title'] = u'Mauvaise valeur'
    elif datatype.is_mandatory and not value:
        attrs['class'] = u'mandatory'
        attrs['title'] = u'Champ obligatoire'
    get_value = form.handler.get_value
    # Disabled fields
    # TODO abrégé ou complet
    #if (datatype.mdt == 'M' and not get_value('MUSIQUE')
    #    or datatype.mdt == 'D' and not get_value('DANSE')
    #    or datatype.mdt == 'T' and not get_value('ARTDRAMA')):
    #    attrs['disabled'] = u'disabled'
    #    attrs['class'] = u'disabled'
    #    attrs['value'] = u''
    attrs = [ u'%s="%s"' % x for x in attrs.items()
              if x[1] is not None ]
    pattern = pattern % u' '.join(attrs)
    if isinstance(datatype, Text):
        if readonly:
            pattern =  pattern + XMLContent.encode(value) + u'</div>\n'
        else:
            # special case for 'value'
            pattern = (pattern + XMLContent.encode(value).replace(u'\\r\\n', u'\r\n')
                    + u'</textarea>\n')
    elif readonly:
        # close element
        pattern =  pattern + XMLContent.encode(value) + u'</div>\n'
    return pattern



class UITable(UIFile, CSVFile):

    ######################################################################
    # User Interface
    def to_html(self, context, form, view, skip_print=False, readonly=False):
        tabindex = None
        page = view.n
        if page in [2, 3, 4]:
            tabindex = True
        user = context.user
        ac = form.get_access_control()
        if not skip_print and not ac.is_admin(user, form):
            state = form.get_statename()
            if state == SENT:
                if page < 10 or page in (12, 14) or page > 50:
                    # Comments 11 and 13 remain available
                    readonly = True
            elif state == EXPORTED:
                readonly = True
        # 0005160: affiche les champs même en lecture seule
        elif skip_print:
            readonly = True
        vars = {}
        floating_vars = {}
        handler = form.handler
        schema = handler.schema
        for name in schema:
            value = handler.get_value(name)
            vars[name] = value
            if isinstance(value, Numeric):
                floating_vars[name] = NumDecimal(value.value)
            else:
                floating_vars[name] = value
        tables = []
        tables.append([])
        table_index = 0
        for i, row in enumerate(self.get_rows()):
            if tabindex:
                tabindex = i + 1
            columns = []
            for j, column in enumerate(row):
                if tabindex:
                    tabindex = j * 100 + tabindex
                if isinstance(column, str):
                    column = unicode(column, 'utf8')
                column = column.strip()
                if column == u'-':
                    try:
                        css_class = columns[-1]['class']
                    except IndexError:
                        css_class = None
                    columns.append({'rowspan': None, 'colspan': None,
                                    'body': HTMLParser("&nbsp;"),
                                    'class': css_class})
                elif column == u'%break%':
                    columns.append({'rowspan': None, 'colspan': None,
                                    'body': HTMLParser("&nbsp;"),
                                    'class': None})
                    # new table but leave the index
                    tables.append([])
                elif column.startswith(FIELD_PREFIX):
                    css_class = u'field-label'
                    if j > 0:
                        css_class += u' centered'
                    column = column[1:]
                    if not column:
                        # Just a single "#" for obscure reason
                        pass
                    elif str(column) in schema:
                        column = get_input_widget(column, form, context,
                                tabindex=tabindex, readonly=readonly)
                    else:
                        # 0004922 Fiche école ne fonctionne plus
                        column = column.replace('\n', '')
                        try:
                            if u'/' in column:
                                column = eval(column, floating_vars)
                            else:
                                column = eval(column, vars)
                        except ZeroDivisionError:
                            column = u'(division par 0)'
                        except SyntaxError:
                            raise SyntaxError, repr(column)
                    if not isinstance(column, basestring):
                        css_class += u' num'
                        if isinstance(column, NumTime):
                            # 0006611 numérique mais représentation textuelle
                            column = unicode(column)
                        elif isinstance(column, int):
                            # l'opération était préfixée par int
                            column = u'%d' % column
                        elif str(column) != 'NC':
                            column = u'%.1f' % column
                        else:
                            column = unicode(column)
                    body = HTMLParser(column.encode('utf8'))
                    columns.append({'rowspan': None, 'colspan': None,
                                    'body': body, 'class': css_class})
                elif column:
                    css_class = u'field-label'
                    if j > 0:
                        css_class += u' centered'
                    # 0004946: les balises < et > ne sont pas interprétées
                    # -> ne pas utiliser XML.encode
                    column = column.replace('&', '&amp;')
                    if column == u'100%':
                        css_class += u' num'
                    body = HTMLParser(column.encode('utf8'))
                    columns.append({'rowspan': None, 'colspan': None,
                                    'body': body, 'class': css_class})
                elif columns:
                    colspan = columns[-1]['colspan']
                    if colspan is None:
                        colspan = 2
                    else:
                        colspan += 1
                    columns[-1]['colspan'] = colspan
                else:
                    columns.append({'rowspan': None, 'colspan': None,
                                    'body': '', 'class': None})
            # Section headers
            if len(columns) == 1 and columns[0]['body']:
                columns[0]['class'] = u'section-header'

            tables[table_index].append(columns)
            # new table added?
            if table_index + 1 < len(tables):
                table_index = table_index + 1
        namespace = {}
        namespace['form_title'] = form.get_title()
        namespace['page_title'] = view.get_title(context)
        namespace['page_number'] = page
        namespace['tables'] = tables
        namespace['readonly'] = skip_print or readonly
        namespace['first_time'] = not form.handler.fields
        namespace['skip_print'] = skip_print
        if not skip_print:
            if page == 11:
                namespace['help_onclick'] = ''
            else:
                namespace['help_onclick'] = """window.open(';help_page?page=%s',\
                    'xxx', 'toolbar=no, location=no, status=no, menubar=no,\
                    scrollbars=yes, width=440, height=540');\
                    return false""" % page
        template = self.get_resource('/ui/scrib2009/Table_to_html.xml')
        return stl(template, namespace)
