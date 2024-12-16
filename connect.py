import mysql.connector
from mysql.connector import Error


#Connection to DB 
def create_connection():
    connection = None
    try:
      connection = mysql.connector.connect(
         host = 'localhost',
         user = 'root',
         password = '',
         database = 'python_ECW'
      )
      if connection.is_connected():
         print("Connnected")
    except Error as e:
       print(f"error : {e}")
    
    return connection