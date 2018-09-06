I have made the application using Python3 in Anaconda environment. I have chosen to use anaconda because it provides a very easy hassle-free way to make packages. 

Install Anaconda from https://www.anaconda.com/download/ .

The default paths are C:\Users\<account-name>\Anaconda3\Scripts and C:\Users\<account-name>\Anaconda3\  . Add these paths to the environment variables in Windows.

I’ve had to use MySQL connector to bridge the application between python and MySQL Db. Execute the following command in command-prompt after installing python and adding conda to environment variables in windows.

conda install -c anaconda mysql-connector-python 

For UI, I’ve had to use the python package tkinter. This package provides UI elements to create interfaces within python. Execute the following command in command-prompt to install the tkinter package for python.

conda install -c anaconda tk

Insertion of the data from the csv files into the database has been done using the python files ‘Inserting from borrowers.py’ and ‘Inserting from book.py’. 

The data is stored on the database in the tables created by the queries in the file “queries”.





