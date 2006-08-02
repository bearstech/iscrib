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

# Import from python 
import os

# Import from itools
from itools import get_abspath


def get_setup_conf():
    # use in the Makefile call from the "culture" product directory
    if 'Setup.conf' in os.listdir('.'):
        path = 'Setup.conf'
    # use from zope 
    else:
        path = get_abspath(globals(), 'Setup.conf')
    _data = open(path, 'r').read()
    lines = [line for line in _data.split('\n') 
             if not line.startswith('#') and line.count('=')]
    dic = {}
    for line in lines:
        key, value = line.split('=')
        key = key.strip()
        value = value.strip()
        dic[key] = value
        if not key:
            raise 'One line has no left value' 
        if not value:
            raise 'No value for the %s in Setup.conf file' % key
    return dic


class Bunch:
    """
    With : 
    mail = Bunch(SMTPServer='localhost',
                 MailResponsableBDP='luis@itaapy.com',
                 MailResponsableBM='alex@itaapy.com')
    We can call : 
    mail.SMTPServer
    mail.MailResponsableBM
    """
    def __init__(self, **kw):
        self.__dict__ = kw


## read the file 
data = get_setup_conf()

## Mail configuration
sql_struct = Bunch( SqlHost=data.get('SqlHost'),
                    SqlDatabase=data.get('SqlDatabase'),
                    SqlUser=data.get('SqlUser'),
                    SqlPasswd=data.get('SqlPasswd'))
## SQL configuration
mail_struct = Bunch( SMTPServer=data.get('SMTPServer'), 
                     MailResponsableBDP=data.get('MailResponsableBDP'),
                     MailResponsableBM=data.get('MailResponsableBM'))
setup = Bunch(mail=mail_struct, sql=sql_struct)


#check
sql, mail = setup.sql, setup.mail

