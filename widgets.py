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

# Import from ikaaro
from ikaaro.access import is_admin
from ikaaro.skins import UIFile

# Import from scrib
from datatypes import Numeric, NumTime, Text, EnumBoolean
from form import SENT, EXPORTED


FIELD_PREFIX = u"#"


def is_mandatory_filled(datatype, value, context):
    if context.request.method != 'POST':
        return True
    if datatype.is_mandatory:
        return bool(value)
    return True



def make_element(tagname, attributes={}, content=u""):
    element = [u"<", tagname]
    for key, value in attributes.iteritems():
        if isinstance(value, list):
            value = u" ".join(value)
        element.extend((u" ", key, u'="', value, u'"'))
    if tagname == 'input':
        element.extend((u"/>", content))
    else:
        element.extend((u">", content, u"</", tagname, u">"))
    return u"".join(element)



def radio_widget(context, form, datatype, name, value, readonly):
    html = []

    # True -> '1' ; False -> '2'
    value = datatype.encode(value)
    if readonly:
        input = datatype.get_value(value, value)
        if input is None:
            input = u""
        else:
            input = XMLContent.encode(input)
        html.append(make_element(u"div", content=input))
    else:
        handler = form.handler
        for option in datatype.get_namespace(value):
            attributes = {u"type": u"radio", u"id": u"field_%s" % name,
                    u"name": name, u"value": option['name']}
            if option['selected']:
                attributes[u"checked"] = u"checked"
            if handler.is_disabled_by_dependency(name):
                attributes[u"disabled"] = u"disabled"
                attributes.setdefault(u"class", []).append(u"disabled")
            # 0005970: Le Javascript pour (dés)activer les autres champs
            if option['name'] == '1':
                disabled = u"false"
                toggle_class = u"removeClass"
            else:
                disabled = u"true"
                toggle_class = u"addClass"
            dep_names = []
            for dep_name in handler.get_reverse_dependencies(name):
                dep_names.append(dep_name)
                # Second level
                for dep_name in handler.get_reverse_dependencies(dep_name):
                    dep_names.append(dep_name)
                    # Third level
                    for dep_name in handler.get_reverse_dependencies(dep_name):
                        dep_names.append(dep_name)
            for dep_name in dep_names:
                attributes.setdefault(u"onchange", []).append(
                    u"$('[name=%s]').attr('disabled', %s).%s('disabled');" % (
                        dep_name, disabled, toggle_class))
            # 0005970 fin
            input = make_element(u"input", attributes, option['value'])
            if issubclass(datatype, EnumBoolean):
                # Oui/Non sur une seule ligne
                html.append(input)
            else:
                # Une option par ligne
                html.append(make_element(u"div", content=input))

    attributes = {}
    if name in context.bad_types:
        attributes[u"class"] = u"badtype"
    elif not is_mandatory_filled(datatype, value, context):
        attributes[u"class"] = u"mandatory"
    return make_element(u"div", attributes, u"".join(html))



def checkbox_widget(context, form, datatype, name, value, readonly):
    if readonly:
        return make_element(u"div", content=datatype.get_value(value, value))

    html = []
    handler = form.handler
    for option in datatype.get_namespace(value):
        attributes = {u"type": u"checkbox",  u"id": u"field_%s" % name,
                u"name": name, u"value": option['name']}
        if option['selected']:
            attributes[u"checked"] = u"checked"
        if handler.is_disabled_by_dependency(name):
            attributes[u"disabled"] = u"disabled"
            attributes.setdefault(u"class", []).append(u"disabled")
        input = make_element(u"input", attributes, option['value'])
        if name in context.bad_types:
            input = (u'<span class="badtype" title="Mauvaise valeur">'
                    + input + u"</span>")
        elif not is_mandatory_filled(datatype, value, context):
            input = (u'<span class="mandatory" title="Champ obligatoire">'
                    + input + u"</span>")
        html.append(input)
    return u"".join(html)



def select_widget(context, form, datatype, name, value, readonly):
    if readonly:
        return make_element(u"div", content=datatype.get_value(value, value))

    options = []
    for option in datatype.get_namespace(value):
        attributes = {u"value": option['name']}
        if option['selected']:
            attributes[u"selected"] = u"selected"
        options.append(make_element(u"option", attributes, option['value']))
    options = u"\n".join(options)
    attributes = {u"name": name}
    # Check for "errors"
    if name in context.bad_types:
        attributes[u"title"] = u"Mauvaise valeur"
        attributes[u"class"] = [u"badtype"]
    elif not is_mandatory_filled(datatype, value, context):
        attributes[u"title"] = u"Champ obligatoire"
        attributes[u"class"] = [u"mandatory"]
    if form.handler.is_disabled_by_dependency(name):
        attributes[u"disabled"] = u"disabled"
        attributes.setdefault(u"class", []).append(u"disabled")
    return make_element(u"select", attributes, options)



def textarea_widget(context, form, datatype, name, value, readonly):
    if readonly:
        attributes = {u"style": u"white-space: pre", u"class": u"readonly"}
        content = XMLContent.encode(value)
        return make_element(u"div", attributes, content)

    attributes = {u"name": name, u"rows": datatype.format, u"cols": 100}
    # special case for 'value'
    content = XMLContent.encode(value).replace(u"\\r\\n", u"\r\n")
    return make_element(u"textarea", attributes, content)



def text_widget(context, form, datatype, name, value, readonly, tabindex=None):
    value = unicode(datatype.encode(value), 'utf8')
    if readonly:
        tagname = u"div"
        attributes = {u"class": u"readonly"}
        content = XMLContent.encode(value)
    else:
        tagname = u"input"
        attributes = {u"type": u"text", u"id": u"field_%s" % name,
                u"name": name, u"value": XMLAttribute.encode(value),
                u"size": datatype.length, u"maxlength": datatype.format}
        if tabindex:
            attributes[u"tabindex"] = tabindex
        content = u""
    # Right-align numeric fields
    if isinstance(datatype, Numeric):
        attributes[u"class"] = [u"num"]
    # Check for errors
    if name in context.bad_types:
        attributes.setdefault(u"class", []).append(u"badtype")
        attributes[u"title"] = u"Mauvaise valeur"
    elif not is_mandatory_filled(datatype, value, context):
        attributes.setdefault(u"class", []).append(u"mandatory")
        attributes[u"title"] = u"Champ obligatoire"
    if form.handler.is_disabled_by_dependency(name):
        attributes[u"disabled"] = u"disabled"
        attributes.setdefault(u"class", []).append(u"disabled")
    return make_element(tagname, attributes, content)



def get_input_widget(name, form, context, tabindex=None, readonly=False):
    handler = form.handler
    datatype = handler.schema[name]
    readonly =  readonly or datatype.readonly
    # Take data from the request or from the form
    if context.has_form_value(name):
        value = context.get_form_value(name)
    else:
        value = handler.get_value(name)
    format = datatype.format.upper()
    if format == 'SELECT':
        return select_widget(context, form, datatype, name, value, readonly)
    elif format == 'RADIO':
        return radio_widget(context, form, datatype, name, value, readonly)
    elif format == 'CHECKBOX':
        return checkbox_widget(context, form, datatype, name, value, readonly)
    # Textarea
    elif isinstance(datatype, Text):
        return textarea_widget(context, form, datatype, name, value, readonly)
    # Basic text input
    return text_widget(context, form, datatype, name, value, readonly,
            tabindex)



class UITable(UIFile, CSVFile):

    def get_namespace(self, form, view, context, skip_print=False,
            readonly=False):
        # Force l'ordre de tabulation entre les champs
        tabindex = None
        page = view.n
        if page in [2, 3, 4]:
            tabindex = True

        # Lecture seule ?
        if not skip_print and not is_admin(context.user, form):
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

        # Calcul du (des) tableau(x)
        schema = form.handler.schema
        vars = form.get_vars()
        floating_vars = form.get_floating_vars()
        tables = []
        tables.append([])
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
                if column == u"-":
                    # Espace blanc insécable
                    try:
                        css_class = columns[-1]['class']
                    except IndexError:
                        css_class = u"field-label"
                    columns.append({'rowspan': None, 'colspan': None,
                                    'body': HTMLParser("&nbsp;"),
                                    'class': css_class})
                elif column == u"%break%":
                    # Saut de page
                    columns.append({'rowspan': None, 'colspan': None,
                                    'body': HTMLParser("&nbsp;"),
                                    'class': None})
                    # Commence un nouveau tableau
                    tables.append([])
                elif column.startswith(FIELD_PREFIX):
                    # Champ à remplacer par un widget
                    css_class = u"field-label"
                    if j > 0:
                        css_class += u" centered"
                    column = column[1:]
                    if not column:
                        # Un « # » seul pour préfixer les champs
                        # Fusionne avec la cellule précédente (svt un titre)
                        colspan = (columns[-1]['colspan'] or 1) + 1
                        columns[-1]['colspan'] = colspan
                        continue
                    elif str(column) in schema:
                        column = get_input_widget(column, form, context,
                                tabindex=tabindex, readonly=readonly)
                    else:
                        # 0004922 Fiche école ne fonctionne plus
                        column = column.replace('\n', '')
                        try:
                            if u"/" in column:
                                column = eval(column, floating_vars)
                            else:
                                column = eval(column, vars)
                        except ZeroDivisionError:
                            column = u"(division par 0)"
                        except SyntaxError:
                            raise SyntaxError, repr(column)
                    if not isinstance(column, basestring):
                        css_class += u" num"
                        if isinstance(column, NumTime):
                            # 0006611 numérique mais représentation textuelle
                            column = unicode(column)
                        elif isinstance(column, int):
                            # l'opération était préfixée par int
                            column = u"%d" % column
                        elif str(column) != 'NC':
                            column = u"%.1f" % column
                        else:
                            column = unicode(column)
                    body = HTMLParser(column.encode('utf8'))
                    columns.append({'rowspan': None, 'colspan': None,
                                    'body': body, 'class': css_class})
                elif column:
                    # Texte simple (ou pas)
                    # 0007975: Gestion des titres
                    if column[0] == u"*":
                        new_column = column.lstrip(u"*")
                        level = len(column) - len(new_column)
                        column = new_column.strip()
                        column = u"<h{level}>{column}</h{level}>".format(
                                # <h1> est déjà pris
                                level=int(level)+1,
                                column=column.strip())
                        css_class = u"section-header"
                    # 0007970: CSS spécifique pour numéros de rubriques
                    elif column in schema:
                        css_class = u"rubrique-label"
                    else:
                        css_class = u"field-label"
                    if j > 0:
                        css_class += u" centered"
                    if column == u"100%":
                        css_class += u" num"
                    # 0004946: les balises < et > ne sont pas interprétées
                    # -> ne pas utiliser XML.encode
                    column = column.replace('&', '&amp;')
                    body = HTMLParser(column.encode('utf8'))
                    columns.append({'rowspan': None, 'colspan': None,
                                    'body': body, 'class': css_class})
                elif columns:
                    # Vide : fusionne avec la précédente
                    colspan = (columns[-1]['colspan'] or 1) + 1
                    columns[-1]['colspan'] = colspan
                    continue
                else:
                    # Ligne vraiment vide
                    columns.append({'rowspan': None, 'colspan': None,
                                    'body': '', 'class': None})
            # La ligne calculée
            tables[-1].append(columns)

        namespace = {}
        namespace['form_title'] = form.get_title()
        namespace['page_title'] = view.get_title(context)
        namespace['page_number'] = page
        namespace['tables'] = tables
        namespace['readonly'] = skip_print or readonly
        namespace['first_time'] = form.is_first_time()
        namespace['skip_print'] = skip_print
        # Aide spécifique
        if not skip_print:
            if page == 11:
                namespace['help_onclick'] = ''
            else:
                namespace['help_onclick'] = ";aide?page=%s" % page

        return namespace
