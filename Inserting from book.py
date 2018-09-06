
import mysql.connector as sqlcon
import csv

connection = sqlcon.connect(host = 'localhost', user ='root',passwd='toor', database= 'library')


cursor = connection.cursor()

with open('book.csv', 'r', encoding = "utf8") as f:
    reader = csv.reader(f, dialect = 'excel-tab')
    for row in reader:
        authors_list = []
        authors_list = row[3].split(",")
        
        
        insert_stmt = ( 'Insert into BOOK values (%s, %s, %s, %s, %s);' )
        data = ( (row[1].replace("'", "\\"+"\'")).replace("\"","\\"+"\""), 
                 (row[2].replace("'", "\\"+"\'")).replace("\"","\\"+"\""),
                 (row[4].replace("'", "\\"+"\'")).replace("\"","\\"+"\""), 
                 (row[5].replace("'", "\\"+"\'")).replace("\"","\\"+"\""), 
                  row[6])
        cursor.execute(insert_stmt, data)
        
        print(authors_list)
        
        for i in range(0, len(authors_list)):
            select_stmt = ('select AUTHOR_ID from AUTHORS WHERE AUTHOR_NAME =  %(author_name)s  ')
            cursor.execute(select_stmt, { 'author_name' : authors_list[i]})
            iterator1 = cursor.fetchone()
            print(iterator1)
            if iterator1 == None:
                insert_stmt = ('insert into AUTHORS (AUTHOR_NAME) values (%(author_name)s)' )
                cursor.execute(insert_stmt, {'author_name' : authors_list[i]})
            
            cursor.execute(select_stmt, { 'author_name' : authors_list[i]})
            iterator2 = cursor.fetchone()
            print(iterator2)
            insert_stmt = ('insert into BOOK_AUTHOR values (%s, %s)')
            data = (iterator2[0], row[1])
            cursor.execute(insert_stmt, data)
            connection.commit()

connection.commit()            
            
            