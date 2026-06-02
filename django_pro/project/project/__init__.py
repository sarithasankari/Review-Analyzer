import pymysql
pymysql.install_as_MySQLdb()
import MySQLdb

# Patch version to satisfy Django checks if it's too old
if MySQLdb.version_info < (2, 2, 0):
    MySQLdb.version_info = (2, 2, 6, "final", 0)
    MySQLdb.__version__ = "2.2.6"