# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 13:49:44 2018

@author: rohit

Thanks to EugeneBakin at https://gist.github.com/EugeneBakin/76c8f9bcec5b390e45df   
for VerticalScrollFrame class for tkinter. He really saved me from massive head scratching.

"""

from tkinter import *
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox

import mysql.connector as sqlcon

from datetime import datetime
from datetime import timedelta

from scrolltest import VerticalScrolledFrame
import re

LARGE_FONT = ("Verdana", 12)


class LibraryApplication(tk.Tk):
    
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        
        tk.Tk.wm_title(self, "Library Application")
        
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        w = 1200
        h = 700
        x = 80
        y = 100
        
        self.geometry("%dx%d+%d+%d" % (w, h, x, y))
        
        self.frames={}
        
        self.frame1 = VerticalScrolledFrame(container)
        self.frame1.pack(side="top",fill=BOTH, expand=True)
        
        self.connection = sqlcon.connect(host = 'localhost', user ='root',passwd='toor', database= 'library')
        self.cursor = self.connection.cursor(buffered = True)    
               
        for F in (StartPage, Book_search_page, Borrower_page, Fines_page):
            frame = F(self.frame1.interior, self, self.connection, self.cursor)
            
            self.frames[F] = frame
            
            frame.grid(column=0, row=0,  sticky=(N, S, E, W))
        
        self.show_frame(StartPage)
              
        
        
    def show_frame(self, cont, connection=None):
        
        frame = self.frames[cont]
        frame.update() 
        frame.tkraise()
        
        
class StartPage(tk.Frame):
    
    def __init__(self, parent, controller,connection, cursor, **kwargs):
        root = tk.Frame.__init__(self, parent,**kwargs)
        label = tk.Label(self, text="StartPage", font=LARGE_FONT)
        label.pack()
        
        button1 = tk.Button(self, text="Book Search", 
                            command=lambda: controller.show_frame(Book_search_page))
        button1.pack()
        
        
        
        button3 = tk.Button(self, text="Borrower Management", 
                            command=lambda: controller.show_frame(Borrower_page))
        button3.pack()
        
        button4 = tk.Button(self, text="Fines", 
                            command=lambda: controller.show_frame(Fines_page))
        button4.pack()
        
        
        
        
class Book_search_page(tk.Frame):
    def __init__(self, parent, controller, connection, cursor):
        
        
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.connection = connection
        self.cursor = cursor
        self.populate()
        
    def populate(self):   
            
        
        self.search_frame = tk.Frame(self)
        self.search_frame.pack(side='top')
        
        self.data_frame=None
        
        
        label = tk.Label(self.search_frame, text="Search :", font=LARGE_FONT)
        label.grid(row=0, column = 1, sticky='nw')
        
        
        inputEntry = tk.Entry(self.search_frame, width = 25)
        inputEntry.grid(row = 0, column=2, columnspan = 6)
        
        button1 = tk.Button(self.search_frame, text="Back to home", 
                            command=lambda: self.controller.show_frame(StartPage,self.connection))
        button1.grid(row=2, column = 2)      
        
        self.selection = tk.IntVar()
        self.selection.set(1)

        #tk.Label(self, text="Search by one of the following options").pack()

        tk.Radiobutton(self.search_frame, text='Title', value=1, variable=self.selection, command=self.print_selection).grid(row=1, column=1)
        
        tk.Radiobutton(self.search_frame, text='Author', value=2, variable=self.selection, command=self.print_selection).grid(row=1, column=2)

        tk.Radiobutton(self.search_frame, text='Publisher', value=3, variable=self.selection, command=self.print_selection).grid(row=1, column=3)

        tk.Radiobutton(self.search_frame, text='ISBN', value=4, variable=self.selection, command=self.print_selection).grid(row=1, column=4)

        button2 = tk.Button(self.search_frame, text = "GO!", command= lambda : self.selection_query(inputEntry.get()))
        button2.grid(row = 2, column = 4)
        
             
    def print_selection(self):
        pass
        
    def selection_query(self, inputEntry_val):
        # query value based on selection and input_value
       
        if self.data_frame!=None:
            self.data_frame.destroy()
            
        if inputEntry_val =="" or inputEntry_val == " " or len(inputEntry_val) < 2:
            ttk.Label(self.search_frame, text="Please re-enter your phrase").grid(row=0, column=4)
            self.selection.set(0)
        elif self.selection.get() == 1:
            select_stmt = ('select distinct(b.ISBN), Title, Cover, Publisher, availability from book as b join book_avail as ab where b.isbn=ab.isbn and b.title like \'%' + str(inputEntry_val) + '%\' order by b.title desc')
        elif self.selection.get() == 2:
            select_stmt = ('select distinct(b.ISBN), Title, Cover, Publisher, availability, a.author_name from book as b join book_author as ba join authors as a join book_avail as ab where b.isbn=ab.isbn and b.isbn=ba.isbn and ba.author_id = a.author_id and a.author_name like \'%' + str(inputEntry_val) + '%\' order by a.author_name desc')
        elif self.selection.get() == 3:
            select_stmt = ('select distinct(b.ISBN), Title, Cover, Publisher, availability from book as b join book_avail as ab where b.isbn=ab.isbn and b.publisher like \'%' + str(inputEntry_val) + '%\' order by b.publisher desc')
        elif self.selection.get() == 4:
            select_stmt = ('select distinct(b.ISBN), Title, Cover, Publisher, availability from book as b join book_avail as ab where b.isbn=ab.isbn and b.isbn like \'%' + str(inputEntry_val) + '%\'')
           
        self.data_frame = tk.Frame(self)
        self.data_frame.pack(side='top')
        
        if self.selection.get()!=0:
            
            self.cursor.execute(select_stmt,{'condition' : inputEntry_val})
            data = self.cursor.fetchall()
            for index, dat in enumerate(data):
                ttk.Label(self.data_frame, text="ISBN", width=10).grid(row=index*5+4, column=0, sticky='w')
                ttk.Label(self.data_frame, text="Title", width=10).grid(row=index*5+5, column=0, sticky='w')
                ttk.Label(self.data_frame, text="Authors", width=10).grid(row=index*5+6, column=0, sticky='w')
                ttk.Label(self.data_frame, text="Publisher", width=10).grid(row=index*5+7, column=0, sticky='w')             
                ttk.Label(self.data_frame, text="-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------").grid(row=index*5+8, column=0,columnspan=6, sticky='w')
                ttk.Label(self.data_frame, text=dat[0]).grid(row=index*5+4, column=1, sticky='w')
                select_stmt2 = ('select a.author_name from  book_author as ba join authors as a where ba.author_id = a.author_id and ba.isbn like \'%' + str(dat[0])+'%\'')
                author_list = ""
                self.cursor.execute(select_stmt2)
                authlist = self.cursor.fetchall()
                for index1, dat1 in enumerate(authlist):
                    author_list = author_list + ", " + dat1[0]
                ttk.Label(self.data_frame, text=dat[1].replace("\'","'").replace("\\'","'").replace("&amp;","&")).grid(row=index*5+5, column=1, sticky='w')
                ttk.Label(self.data_frame, text=author_list[2:len(author_list)].replace("\'","'").replace("\\'","'").replace("&amp;","&")).grid(row=index*5+6, column=1, sticky='w')
                ttk.Label(self.data_frame, text="cover: "+ dat[2].replace("\'","'").replace("\\'","'").replace("&amp;","&")).grid(row=index*5+4, column=3, sticky='w')
                ttk.Label(self.data_frame, text=dat[3].replace("\'","'").replace("\\'","'").replace("&amp;","&")).grid(row=index*5+7, column=1, sticky='w')
                ttk.Label(self.data_frame, text="Available copies: "+ str(dat[4])).grid(row=index*5+6, column=3, sticky='w')
                ttk.Button(self.data_frame, text = "Loan this Book", command= lambda x=dat[0], y=dat[4]: self.callLoaningWindow(x, y)).grid(row= index*5+7, column = 3, sticky='w')
                
                
        else:
            pass
            self.selection.set(1)
        
    def callLoaningWindow(self, isbn, avail):
        
        if avail == 0:
            tkinter.messagebox.showinfo('OOPS!!!', 'No copies of this book are available, please try again later')
        else:
            self.window = tk.Toplevel(self)
            ttk.Label(self.window, text = "Enter Card_ID ").grid(row=1, column =1 )
            cardidentry = ttk.Entry(self.window, width=30)
            cardidentry.grid(row =1 ,column =2, columnspan=2)
            ttk.Button(self.window, text ="Loan!!", command = lambda : self.database_access(isbn, avail, cardidentry.get())).grid(row=1, column=4)
            ttk.Button(self.window, text ="Done?", command = self.window.destroy).grid(row=1, column=5)
    
 
    def database_access(self, isbn, avail, card_id):
        if card_id == 0:
            tkinter.messagebox.showinfo('OOPS!!!', 'Invalid card id')
        else:
            stmt = ('select card_id from borrower where card_id  = %(card_id)s');
            self.cursor.execute(stmt, {'card_id': str(card_id)})
            value = self.cursor.fetchone()
            stmt = ('select count(card_id) from book_loans where card_id  = %(card_id)s and date_in is null');
            self.cursor.execute(stmt, {'card_id': str(card_id)});
            count_card_id = self.cursor.fetchone()
            if value == None:
                tkinter.messagebox.showinfo('OOPS!!!', 'Card ID not in record!')
            elif count_card_id[0] == 3 :
                tkinter.messagebox.showinfo('OOPS!!!', 'Already loaned 3 books!!')
            else:
                stmt = ('insert into book_loans (isbn, card_id, date_out, due_date) values (%s, %s, %s, %s)')
                data = (isbn, card_id, str(datetime.now()), str(datetime.now() + timedelta(days=14)))
                self.cursor.execute(stmt, data )
                stmt = ('update book_avail set availability = availability - 1 where isbn = %(isbn)s')
                self.cursor.execute(stmt, {'isbn' : isbn })   
                tkinter.messagebox.showinfo('YEAY!', 'loaning successful!')
                self.connection.commit()
                self.window.destroy()
               
                
         
      
          
        
class Borrower_page(tk.Frame):

    def __init__(self, parent, controller, connection, cursor):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.connection = connection
        self.cursor = cursor
        self.populate()
        
    def populate(self):   
        
        
        self.search_frame = tk.Frame(self)
        self.search_frame.pack(side='top')
        
        self.data_frame=None
        
        
        label = tk.Label(self.search_frame, text="Search for a borrower:", font=LARGE_FONT)
        label.grid(row=0, column = 1, sticky='nw')
        
        
        inputEntry = tk.Entry(self.search_frame, width = 25)
        inputEntry.grid(row = 0, column=2, columnspan = 6)
        
        button1 = tk.Button(self.search_frame, text="Back to home", 
                            command=lambda: self.controller.show_frame(StartPage, self.connection))
        button1.grid(row=2, column = 2)   
        
        button2 = tk.Button(self.search_frame, text="Create new user", 
                            command=self.create_new_user)
        button2.grid(row=2, column = 3)
        
        self.selection = tk.IntVar()
        self.selection.set(1)

        tk.Radiobutton(self.search_frame, text='By Card-ID', value=1, variable=self.selection, command=self.print_selection).grid(row=1, column=1)
        
        tk.Radiobutton(self.search_frame, text='By SSN [ 333-33-3333 ]', value=2, variable=self.selection, command=self.print_selection).grid(row=1, column=3)

        tk.Radiobutton(self.search_frame, text='By Name', value=3, variable=self.selection, command=self.print_selection).grid(row=1, column=5)

        tk.Radiobutton(self.search_frame, text='By Phone [ (333) 333-3333 ]', value=4, variable=self.selection, command=self.print_selection).grid(row=1, column=7)

        tk.Radiobutton(self.search_frame, text='By Email', value=5, variable=self.selection, command=self.print_selection).grid(row=1, column=9)
        
        button2 = tk.Button(self.search_frame, text = "Go!", command= lambda : self.selection_query(inputEntry.get()))
        button2.grid(row = 2, column = 4)
        
    def print_selection(self):
        pass
        
    def selection_query(self, inputEntry_val):
        # query value based on selection and input_value
        
        if self.data_frame!=None:
            self.data_frame.destroy()
        
        if inputEntry_val =="" or inputEntry_val == " ":
            ttk.Label(self.search_frame, text="Please re-enter your phrase").grid(row=0, column=4)
            
            self.selection.set(0)
        elif self.selection.get() == 1:
            select_stmt = ('select Card_id, ssn, B_first_name, B_last_name, email, address, City, State, Phone from borrower where card_id like \'%' + str(inputEntry_val) + '%\' order by card_id asc')
        elif self.selection.get() == 2:
            select_stmt = ('select Card_id, ssn, B_first_name, B_last_name, email, address, City, State, Phone from borrower where ssn like \'%' + str(inputEntry_val) + '%\' order by card_id asc')
        elif self.selection.get() == 3:
            select_stmt = ('select Card_id, ssn, B_first_name, B_last_name, email, address, City, State, Phone from borrower where B_first_name like \'%' + str(inputEntry_val) + '%\' or b_last_name like \'%' + str(inputEntry_val) + '%\'order by b_first_name asc, b_last_name asc')
        elif self.selection.get() == 4:
            select_stmt = ('select Card_id, ssn, B_first_name, B_last_name, email, address, City, State, Phone from borrower where phone like \'%' + str(inputEntry_val) + '%\' order by phone asc')
        elif self.selection.get() == 5:
            select_stmt = ('select Card_id, ssn, B_first_name, B_last_name, email, address, City, State, Phone from borrower where email like \'%' + str(inputEntry_val) + '%\' order by email asc')
                
        
        self.data_frame = tk.Frame(self)
        self.data_frame.pack(side='top')
        
        
        if self.selection.get()!=0:
            
            self.cursor.execute(select_stmt)
            data = self.cursor.fetchall()
            if data == None:
                ttk.Label(self.date_frame, text="No user with that info").grid(row=0, column=4)
                
            else:                
                for index, dat in enumerate(data):
                    ttk.Label(self.data_frame, text="Card ID", width=10).grid(row=index*7+4, column=0, sticky='w')
                    ttk.Label(self.data_frame, text="First Name, Last Name", width=25).grid(row=index*7+5, column=0, sticky='w')
                    ttk.Label(self.data_frame, text="SSN", width=10).grid(row=index*7+6, column=0, sticky='w')
                    ttk.Label(self.data_frame, text="Email", width=10).grid(row=index*7+7, column=0, sticky='w')       
                    ttk.Label(self.data_frame, text="Address", width=10).grid(row=index*7+8, column=0, sticky='w') 
                    ttk.Label(self.data_frame, text="Phone", width=10).grid(row=index*7+9, column=0, sticky='w') 
                    ttk.Label(self.data_frame, text="-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------").grid(row=index*7+10, column=0,columnspan=6, sticky='w')
                    ttk.Label(self.data_frame, text=dat[0] ).grid(row=index*7+4, column=1, sticky='w')
                    ttk.Label(self.data_frame, text=dat[2]+" " +dat[3] ).grid(row=index*7+5, column=1, sticky='w')
                    ttk.Label(self.data_frame, text=dat[1] ).grid(row=index*7+6, column=1, sticky='w')
                    ttk.Label(self.data_frame, text=dat[4] ).grid(row=index*7+7, column=1, sticky='w')
                    ttk.Label(self.data_frame, text=dat[5]+" "+dat[6]+" "+dat[7] ).grid(row=index*7+8, column=1, sticky='w')
                    ttk.Label(self.data_frame, text=dat[8] ).grid(row=index*7+9, column=1, sticky='w')
                    ttk.Button(self.data_frame, text="Check-in books of this user", command= lambda x=dat[0]: self.checkin_book(x)).grid(row=index*7+8, column=5, sticky='w')
                    ttk.Button(self.data_frame, text = "Delete this record", command= lambda x=dat[0]: self.delete_borrower(x)).grid(row= index*7+9, column = 5, sticky='w')
                             
        else:
            
            self.selection.set(1)
            
    def delete_borrower(self, card_id):
        
        select_stmt = ('select count(isbn) from book_loans where card_id like \'%' + str(card_id) +'%\' and date_in is null' )
        self.cursor.execute(select_stmt)
        value = self.cursor.fetchone()
        
        if value[0] > 0 :
            tkinter.messagebox.showinfo('OOPS!!!', 'This user has loaned books. Cannot delete ')
        else:
            self.cursor.execute('delete from borrower where card_id like \'%' + str(card_id) +'%\'')
            tkinter.messagebox.showinfo('Bye Bye!!', 'User deleted successfully!')
        self.connection.commit()    
            
    def create_new_user(self):
        
        self.window = tk.Toplevel(self)
        
        ttk.Label(self.window, text="Enter user details").grid(row=0, column=0)
        
        ttk.Label(self.window, text = "First Name ").grid(row=1, column=0)
        first_name = tk.Entry(self.window, width=10)
        first_name.grid(row=1,column=1)
                
        ttk.Label(self.window, text = "Last Name ").grid(row=2, column=0)
        last_name = tk.Entry(self.window, width=10)
        last_name.grid(row=2, column=1)
        
        ttk.Label(self.window, text = "SSN").grid(row=3, column=0)
        ssn1 = tk.Entry(self.window, width=3)
        ssn1.grid(row=3, column=1)
        ttk.Label(self.window, text = "-").grid(row=3, column=2)
        ssn2 = tk.Entry(self.window, width=2)
        ssn2.grid(row=3, column=3)
        ttk.Label(self.window, text = "-").grid(row=3, column=4)
        ssn3 = tk.Entry(self.window, width=4)
        ssn3.grid(row=3, column=5)
        
        ttk.Label(self.window, text = "E-mail ").grid(row=4, column=0)
        email = tk.Entry(self.window, width=10)
        email.grid(row=4, column=1)
        
        ttk.Label(self.window, text = "Address ").grid(row=5, column=0)
        address = tk.Entry(self.window, width=10)
        address.grid(row=5, column=1)
        
        ttk.Label(self.window, text = "City ").grid(row=6, column=0)
        city = tk.Entry(self.window, width=10)
        city.grid(row=6, column=1)
        
        ttk.Label(self.window, text = "State ").grid(row=7, column=0)
        state = tk.Entry(self.window, width=10)
        state.grid(row=7, column=1)
        
        ttk.Label(self.window, text = "Phone        (").grid(row=8, column=0, sticky = 'e')
        phone1 = tk.Entry(self.window, width=10)
        phone1.grid(row=8, column=1)
        ttk.Label(self.window, text = ") ").grid(row=8, column=2)
        phone2 = tk.Entry(self.window, width=10)
        phone2.grid(row=8, column=3)
        ttk.Label(self.window, text = "-").grid(row=8, column=4)
        phone3 = tk.Entry(self.window, width=10)
        phone3.grid(row=8, column=5)
        
        
        gobtn = ttk.Button(self.window, text = "Done", command = lambda: self.adduser(first_name.get(),last_name.get(), ssn1.get(), ssn2.get(), ssn3.get(), email.get(), address.get(), city.get(), state.get(), phone1.get(),phone2.get(), phone3.get()))
        gobtn.grid(row=9, column=0)
        ttk.Button(self.window, text = "Cancel", command = self.window.destroy).grid(row=9, column=1)
        
        
    def adduser(self, first_name, last_name, ssn1, ssn2, ssn3, email, address, city, state, phone1, phone2, phone3):
        
        try :
            print(int(phone1))
            print(int(phone2))
            print(int(phone3))
            print(int(ssn1))
            print(int(ssn2))
            print(int(ssn3))
            if len(first_name)==0 or len(last_name)==0 or len(email)==0 or len(address)==0 or len(city)==0 or len(state)==0 or len(phone1)!=3 or len(phone2)!=3 or len(phone3)!=4 or  len(ssn1)!=3 or len(ssn2)!=2 or len(ssn3)!=4 or not re.match(r"[^@\s?/\\!]+@[^@\s\.]+\.[^@\s\.]+$",email):
                tkinter.messagebox.showinfo('OOPS!!', 'Please check details.')
                
            else:    
                ssn = str(ssn1)+"-"+str(ssn2)+"-"+str(ssn3)
                phone = "("+str(phone1)+") "+str(phone2)+"-"+str(phone3)
                select_stmt = ('select ssn from borrower where ssn like \'%' + str(ssn) + '%\'')
                self.cursor.execute(select_stmt)
                dupssn = self.cursor.fetchone()
                
                select_stmt = ('select email from borrower where email like \'%' + str(email) + '%\'')
                self.cursor.execute(select_stmt)
                dupemail=self.cursor.fetchone()
                
                if dupssn != None or dupemail != None:
                    tkinter.messagebox.showinfo('OOPS!!', 'Please check details. A user with that ssn or email exists')
                else:
                    d = datetime.now().strftime("%Y%m%d%H%M%S")
                    select_stmt = ('insert into borrower values( %s, %s, %s, %s, %s, %s, %s, %s, %s)')
                    data = (d,  ssn, first_name, last_name, email, address, city, state, phone)
                    self.cursor.execute(select_stmt, data)
                    tkinter.messagebox.showinfo("Yeah!", "Users successfully inserted into database")
                    self.connection.commit()
        
        except  ValueError as valerror:
            print(valerror)
            tkinter.messagebox.showinfo('OOPS!!', 'Please check details.')
                        
        self.window.destroy();
                
    def checkin_book(self, card_id):
        
        select_stmt = ('select isbn from book_loans where card_id like \'%' + str(card_id) + '%\' and date_in is null')
        self.cursor.execute(select_stmt)
        books = self.cursor.fetchall()
        
        if books==[]:
            tkinter.messagebox.showinfo("OH","This user has no books loaned")
        else:
            window = tk.Toplevel(self)            
            ttk.Label(window, text= "Books borrowed by "+str(card_id)).grid(row=1, column=1)
            
            for index, dat in enumerate(books):
                select_stmt = ('select Title from book where isbn like \'%' + str(dat[0]) + '%\' ')
                self.cursor.execute(select_stmt)
                book = self.cursor.fetchall()
                
                
                ttk.Label(window, text= "ISBN").grid(row=index*3+2 , column=0, sticky='w')
                ttk.Label(window, text= "Title").grid(row=index*3+3 , column=0, sticky='w')
                ttk.Label(window, text= dat[0]).grid(row=index*3+2, column=1, sticky='w')
                ttk.Label(window, text= book[0][0]).grid(row=index*3+3, column=1, sticky='w')
                ttk.Label(window, text="----------------------------------------------------------------------------------------------------------------").grid(row=index*3+4, column=0,columnspan=4, sticky='w')
                ttk.Button(window, text = "Check-in this book", command=lambda x=dat[0]: self.check_in_one(x, card_id, window)).grid(row=index*3+3, column=3 ,sticky='w')
                
                
    def check_in_one(self, isbn, card_id, window):
        
        select_stmt = ('Update book_loans set Date_in = %(date)s where isbn like  \'%' + str(isbn) + '%\' and card_id like \'%' + str(card_id) + '%\'')
        self.cursor.execute(select_stmt,{'date': datetime.now()})
        
        select_stmt = ('Update book_avail set availability = availability + 1 where isbn like \'%' + str(isbn) + '%\'')
        self.cursor.execute(select_stmt)
        
        select_stmt = ('select due_date, date_in, loan_id from book_loans where isbn like  \'%' + str(isbn) + '%\' and card_id like \'%' + str(card_id) + '%\'')
        self.cursor.execute(select_stmt)
        
        value = self.cursor.fetchone()
        diff = value[1] - value[0]
        if diff.days > 0 :
            fine = diff.days * 0.25;
            decision = tkinter.messagebox.askyesno("Fine!", "This book is being returned late by " + str(diff.days)+ ".\nPlease incur a fine of $" +str(fine))
            if decision ==True:
                insert_stmt = ('insert into fines values('+str(value[2])+', '+str(fine)+',True)')
                self.cursor.execute(insert_stmt)
            else:
                insert_stmt = ('insert into fines values('+str(value[2])+', '+str(fine)+',False)')
                self.cursor.execute(insert_stmt)
                
        else:
            tkinter.messagebox.showinfo("yeah!", "Book is returned")
        
        window.destroy()
        self.connection.commit()
        
       
        
class Fines_page(tk.Frame):

    def __init__(self, parent, controller, connection, cursor):
        tk.Frame.__init__(self, parent)
        
        self.connection = connection
        self.cursor = cursor
        
        
        self.search_frame = tk.Frame(self)
        self.search_frame.pack(side="top")
        self.data_frame=None
        
        label = tk.Label(self.search_frame, text="Search for a borrower:", font=LARGE_FONT)
        label.grid(row=0, column = 1, sticky='nw')
        
        inputEntry = tk.Entry(self.search_frame, width = 25)
        inputEntry.grid(row = 0, column=2, columnspan = 6)
        
        self.selection = tk.IntVar()
        self.selection.set(1)
        
        button1 = tk.Button(self.search_frame, text="Back to home", 
                            command=lambda: controller.show_frame(StartPage, self.connection))
        button1.grid(row = 2, column = 3)

        tk.Radiobutton(self.search_frame, text='By Card-ID', value=1, variable=self.selection, command=self.print_selection).grid(row=1, column=1)
        tk.Radiobutton(self.search_frame, text='By SSN', value=2, variable=self.selection, command=self.print_selection).grid(row=1, column=2)
        tk.Radiobutton(self.search_frame, text='By Name', value=3, variable=self.selection, command=self.print_selection).grid(row=1, column=3)
        tk.Radiobutton(self.search_frame, text='By Phone', value=4, variable=self.selection, command=self.print_selection).grid(row=1, column=4)
        tk.Radiobutton(self.search_frame, text='By Email', value=5, variable=self.selection, command=self.print_selection).grid(row=1, column=5)
        
        button2 = tk.Button(self.search_frame, text = "Go!", command= lambda : self.selection_query(inputEntry.get()))
        button2.grid(row=2, column=4)
        
        button3 = tk.Button(self.search_frame, text="Show all fines",
                            command=self.show_fines)
        button3.grid(row=2, column = 5)
        
        
    def print_selection(self):
        pass
        
    def selection_query(self, inputEntry_val):
        # query value based on selection and input_value
        
        if self.data_frame!=None:
            self.data_frame.destroy()
        
        if inputEntry_val =="" or inputEntry_val == " ":
            ttk.Label(self.search_frame, text="Please re-enter your phrase").grid(row=0, column=4)
            
            self.selection.set(0)
        elif self.selection.get() == 1:
            select_stmt = ('select Card_id, ssn, B_first_name, B_last_name, email, address, City, State, Phone from borrower where card_id = \'%' + str(inputEntry_val) + '%\' order by card_id asc')
        elif self.selection.get() == 2:
            select_stmt = ('select Card_id, ssn, B_first_name, B_last_name, email, address, City, State, Phone from borrower where ssn like \'%' + str(inputEntry_val) + '%\' order by card_id asc')
        elif self.selection.get() == 3:
            select_stmt = ('select Card_id, ssn, B_first_name, B_last_name, email, address, City, State, Phone from borrower where B_first_name like \'%' + str(inputEntry_val) + '%\' or b_last_name like \'%' + str(inputEntry_val) + '%\'order by b_first_name asc, b_last_name asc')
        elif self.selection.get() == 4:
            select_stmt = ('select Card_id, ssn, B_first_name, B_last_name, email, address, City, State, Phone from borrower where phone like \'%' + str(inputEntry_val) + '%\' order by phone asc')
        elif self.selection.get() == 5:
            select_stmt = ('select Card_id, ssn, B_first_name, B_last_name, email, address, City, State, Phone from borrower where email like \'%' + str(inputEntry_val) + '%\' order by email asc')
                
        
        self.data_frame = tk.Frame(self)
        self.data_frame.pack(side='top')
        
        
        if self.selection.get()!=0:
            
            self.cursor.execute(select_stmt,{'condition' : inputEntry_val})
            data = self.cursor.fetchall()
            if data == None:
                ttk.Label(self.date_frame, text="No user with that info").grid(row=0, column=4)
                
            else:                
                for index, dat in enumerate(data):
                    
                    select_stmt = ('select sum(fine_amt) from fines where loan_id in (select loan_id from book_loans where card_id like \'%' + str(dat[0])+'%\') and paid=0' )
                    self.cursor.execute(select_stmt)                    
                    self.fine_amt = self.cursor.fetchone()
                    
                    ttk.Label(self.data_frame, text="Card ID", width=10).grid(row=index*7+4, column=0, sticky='w')
                    ttk.Label(self.data_frame, text="Last Name, First Name", width=10).grid(row=index*7+5, column=0, sticky='w')
                    ttk.Label(self.data_frame, text="SSN", width=10).grid(row=index*7+6, column=0, sticky='w')
                    ttk.Label(self.data_frame, text="Email", width=10).grid(row=index*7+7, column=0, sticky='w')       
                    ttk.Label(self.data_frame, text="Address", width=10).grid(row=index*7+8, column=0, sticky='w') 
                    ttk.Label(self.data_frame, text="Phone", width=10).grid(row=index*7+9, column=0, sticky='w') 
                    ttk.Label(self.data_frame, text="-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------").grid(row=index*7+10, column=0,columnspan=6, sticky='w')
                    ttk.Label(self.data_frame, text=dat[0] ).grid(row=index*7+4, column=1, sticky='w')
                    ttk.Label(self.data_frame, text=dat[2]+" " +dat[3] ).grid(row=index*7+5, column=1, sticky='w')
                    ttk.Label(self.data_frame, text=dat[1] ).grid(row=index*7+6, column=1, sticky='w')
                    ttk.Label(self.data_frame, text=dat[4] ).grid(row=index*7+7, column=1, sticky='w')
                    ttk.Label(self.data_frame, text=dat[5]+" "+dat[6]+" "+dat[7] ).grid(row=index*7+8, column=1, sticky='w')
                    ttk.Label(self.data_frame, text=dat[8] ).grid(row=index*7+9, column=1, sticky='w')
                    ttk.Label(self.data_frame, text="Fines: $"+ str(self.fine_amt[0])).grid(row=index*7+7, column=5, sticky='w')
                    ttk.Button(self.data_frame, text="Settle Due", command= lambda x=dat[0], y= self.fine_amt[0]: self.due_settlement(x,y)).grid(row=index*7+8, column=5, sticky='w')
                    
                             
        else:
            
            self.selection.set(1)
   
    def due_settlement(self, card_id, fine_amt ):
        
        if fine_amt != None: 
        
            decision = tk.messagebox.askyesno("Sure?", "Are you sure you want to settle the due of user " + str(card_id))
            
            if decision ==True:
                        
                update_stmt = ('update fines set paid = 1 where loan_id in (select loan_id from book_loans where card_id like \'%' + str(card_id)+'%\') and paid = 0')
                self.cursor.execute(update_stmt)
                self.connection.commit()
            
        else :
            tk.messagebox.showinfo("Oops!", "This user doesn't have any fine due")
            
    
    def show_fines(self):
        select_stmt = ('select Card_id, ssn, B_first_name, B_last_name, email, address, City, State, Phone, sum(fine_amt) from (borrower natural join book_loans) natural join fines where paid = 0 group by card_id')
        self.cursor.execute(select_stmt)
        data = self.cursor.fetchall()
        
        if self.data_frame!=None:
            self.data_frame.destroy()
            
        self.data_frame = tk.Frame(self)
        self.data_frame.pack(side='top')    
        
        for index, dat in enumerate(data):
            ttk.Label(self.data_frame, text="Card ID", width=10).grid(row=index*7+4, column=0, sticky='w')
            ttk.Label(self.data_frame, text="Last Name, First Name", width=10).grid(row=index*7+5, column=0, sticky='w')
            ttk.Label(self.data_frame, text="SSN", width=10).grid(row=index*7+6, column=0, sticky='w')
            ttk.Label(self.data_frame, text="Email", width=10).grid(row=index*7+7, column=0, sticky='w')       
            ttk.Label(self.data_frame, text="Address", width=10).grid(row=index*7+8, column=0, sticky='w') 
            ttk.Label(self.data_frame, text="Phone", width=10).grid(row=index*7+9, column=0, sticky='w') 
            ttk.Label(self.data_frame, text="-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------").grid(row=index*7+10, column=0,columnspan=6, sticky='w')
            ttk.Label(self.data_frame, text=dat[0] ).grid(row=index*7+4, column=1, sticky='w')
            ttk.Label(self.data_frame, text=dat[2]+" " +dat[3] ).grid(row=index*7+5, column=1, sticky='w')
            ttk.Label(self.data_frame, text=dat[1] ).grid(row=index*7+6, column=1, sticky='w')
            ttk.Label(self.data_frame, text=dat[4] ).grid(row=index*7+7, column=1, sticky='w')
            ttk.Label(self.data_frame, text=dat[5]+" "+dat[6]+" "+dat[7] ).grid(row=index*7+8, column=1, sticky='w')
            ttk.Label(self.data_frame, text=dat[8] ).grid(row=index*7+9, column=1, sticky='w')
            ttk.Label(self.data_frame, text="Fines: $"+ str(dat[9])).grid(row=index*7+7, column=5, sticky='w')
            ttk.Button(self.data_frame, text="Settle Due", command= lambda x=dat[0], y=dat[9]: self.due_settlement(x, y)).grid(row=index*7+8, column=5, sticky='w')
            
    
app = LibraryApplication()

def on_closing():
    if tk.messagebox.askokcancel("Quit", "Do you want to quit?"):
        app.connection.close()
        app.destroy()

app.protocol("WM_DELETE_WINDOW", on_closing)
app.mainloop()        
        
        