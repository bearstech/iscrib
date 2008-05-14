
# installation  $ mysql -u root < create_scrib.SQL
# ou alors
#  $ mysql -u root
#  mysql> source create_scrib.SQL;

use mysql;
delete from mysql.user where user='scrib' and host='localhost';
delete from db where user='scrib' and host='localhost';

# Base de données: `scrib`
DROP DATABASE IF EXISTS scrib;
CREATE DATABASE  scrib;
USE  scrib;
GRANT ALL PRIVILEGES ON scrib.* to 'scrib'@'localhost' identified by 'chili';

FLUSH PRIVILEGES;
