# -*- coding: utf-8 -*-
"""
Created on Mon Feb 26 21:02:48 2018

@author: rohit
"""

import mysql.connector as sqlcon
import csv
from datetime import datetime
from datetime import timedelta
connection = sqlcon.connect(host = 'localhost', user ='root',passwd='toor', database= 'library')


cursor = connection.cursor()

with open('Test files\\borrowers.csv', 'r', encoding = "utf8") as f:
    reader = csv.reader(f, delimiter=',')
    d=datetime.now() - timedelta(days=5*365)
    for index, row in enumerate(reader):
        d = d + timedelta(days=1)
        insert_stmt = ('insert into borrower values ( %s,%s,%s,%s,%s,%s,%s,%s,%s)')
        data = (d.strftime("%Y%m%d%H%M%S"), row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8])
        cursor.execute(insert_stmt, data)
connection.commit()



# Code for removing data 


#cursor.execute("set foreign_key_checks = 0")
#cursor.execute("truncate book")
#cursor.execute("truncate authors")
#cursor.execute("truncate book_author")
#cursor.execute("set foreign_key_checks = 1")

#connection.commit()