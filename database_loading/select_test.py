import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

''' connect to database '''
''' note that these credentials may need to change '''
DATABASE_URL = os.environ['DATABASE_URL']
DB_NAME = "d79u63b2cbg9om"
DB_PORT = 5432
DB_USER = "kugnzgerojalup"
DB_PASS = "f4c347af5b4f5818e118cf656221324546d81dd0c539cd588f9f80e9bf7ecdc9"
DB_HOST = "ec2-54-211-176-156.compute-1.amazonaws.com"

conn = psycopg2.connect(dbname=DB_NAME, port=DB_PORT, user=DB_USER, password=DB_PASS, host=DB_HOST)
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

''' creating a cursor object '''
cur = conn.cursor()


''' select - to test '''
cur.execute('''SELECT classNbr, subject, catalogNbr, description FROM CLASS''')
result = cur.fetchall()
print(result)

''' Commit your changes in the database '''
conn.commit()

cur.close()
conn.close()