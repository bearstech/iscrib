# Copyright (C) 2006 Luis Belmar Letelier <luis@itaapy.com>
# Copyright (C) 2008 Hervé Cauwelier <herve@itaapy.com>
from sys import argv, exit

def no_args():
    msg = ("Usage : gen_all gen_all \n"
           "     or gen_all create_database \n"
           "     or gen_all find_python \n"
           "     or gen_all fill_tables")
    print msg

def gen_all():
    from gen import gen_sql
    from gen import gen_BDPreports
    from gen import gen_BMreports

def create_database():
    from gen.FillSql import Create_scrib
    # ask for SQL
    anwser = raw_input('Do you want to re/create SQL scrib database ? : (y/N) ')
    anwser = anwser.strip() or 'non'
    if anwser.lower().startswith('y'):
        cs = Create_scrib()
        cs.create()

def fill_tables():
    from gen.FillSql import Fill_tables
    anwser = raw_input('Do you want fill SQL tables ? : (y/N) ')
    anwser = anwser.strip() or 'non'
    if anwser.lower().startswith('y'):
        ft = Fill_tables()
        ft.fill()

def find_python():
    # when Zope start he write in input_data the python path used
    python = open('input_data/where_is_python.txt').read()
    try:
        python = python.strip()
        open(python)
    except IOError:
        # at least try the default python hopping he know about itools
        print "Start the zope instance first so we know where is you python !"
        python = 'python'
    return python

if __name__ == '__main__':
    #print find_python();  exit()
    try:
        arg = argv[1]
    except:
        arg = None
        no_args()
        exit()
    if arg == 'gen_all':
        gen_all()
    elif arg == 'create_database':
        create_database()
    elif arg == 'fill_tables':
        fill_tables()
    elif arg == 'find_python':
        print find_python()
    else:
        print ('command must be one of : gen_all, create_database, '
               ' find_python or fill_tables')
