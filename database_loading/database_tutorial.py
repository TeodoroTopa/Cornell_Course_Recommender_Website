
# https://towardsdatascience.com/python-and-postgresql-how-to-access-a-postgresql-database-like-a-data-scientist-b5a9c5a0ea43

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

''' NOTE: do not forget to [heroku login] before starting '''

''' creating a cursor object '''
cur = conn.cursor()

# https://www.tutorialspoint.com/python_data_access/python_postgresql_introduction.htm

''' create a new table '''
sql = '''CREATE TABLE EMPLOYEE(
   FIRST_NAME CHAR(20) NOT NULL,
   LAST_NAME CHAR(20),
   AGE INT,
   SEX CHAR(1),
   INCOME FLOAT
)'''
# cur.execute(sql)
print("Table created successfully........")

''' insert into database '''
insert_stmt = (
   "INSERT INTO EMPLOYEE(FIRST_NAME, LAST_NAME, AGE, SEX, INCOME)"
   "VALUES (%s, %s, %s, %s, %s)"
)
data = [('Ramya', 'Ramapriya', 25, 'F', 5000),
         ('John', 'Smith', 21, 'M', 10000), 
         ('Kurt', 'Lovejoy', 20, 'M', 15000)]

''' Executing the SQL command '''
for d in data:
   print (insert_stmt, d)
   # cur.execute(insert_stmt, d)

# ''' Commit your changes in the database '''
# conn.commit()

# ''' select '''
# cur.execute('''SELECT * FROM EMPLOYEE''')
# result = cur.fetchall()
# print(result)

# ''' Commit your changes in the database '''
# conn.commit()

cur.close()
conn.close()
