
# https://towardsdatascience.com/python-and-postgresql-how-to-access-a-postgresql-database-like-a-data-scientist-b5a9c5a0ea43

import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy.engine.url import make_url
''' connect to database '''
''' note that these credentials may need to change '''
DATABASE_URL = os.environ['DATABASE_URL']
url = make_url(DATABASE_URL)
DB_NAME = url.database
DB_PORT = url.port
DB_USER = url.username
DB_PASS = url.password
DB_HOST = url.host

conn = psycopg2.connect(dbname=DB_NAME, port=DB_PORT, user=DB_USER, password=DB_PASS, host=DB_HOST)
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

''' creating a cursor object '''
cur = conn.cursor()
sql = 'DROP TABLE IF EXISTS users;'

cur.execute(sql)
conn.commit()

sql  = "CREATE TABLE users (fname TEXT NOT NULL, lname TEXT NOT NULL, email TEXT UNIQUE NOT NULL PRIMARY KEY);"

cur.execute(sql)
conn.commit()

cur.close()
conn.close()
