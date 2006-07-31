# -*- coding: ISO-8859-1 -*-

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

