"""
Use by the ./gen_all.py script to create DB and fill table with ./input_data/ 
SQL files
"""

import os 
class Fill_tables:
    def __init__(self):
        str = "mysql -u scrib -p'Scrib-2005*' scrib < ./input_data/%s "
        self.cmd_line = str

    def fill(self):
        for name in os.listdir('./input_data/'):
            if name.endswith('.sql'):
                res = os.system(self.cmd_line % name)
                print './input_data/%s' % name, not res and 'OK' or 'Echec'

class Create_scrib:
    def __init__(self):
        self.cmd_line = "mysql -u root -p < ./input_data/%s "

    def create(self):
        for name in os.listdir('./input_data/'):
            if name.endswith('.SQL'):
                res = os.system(self.cmd_line % name)
                print './input_data/%s' % name, not res and 'OK' or 'Echec'

