from datetime import date
from multiprocessing import connection
import time
import bcrypt
from flask import flash, redirect, render_template, request, session, url_for
from Controllers.hashController import HassController
from connect import create_connection


class RegisterModel:
  
    @staticmethod
    def Register_user():   
        if request.method == 'POST':  # If request is POST, handle form submission / Wenn die Anfrage POST ist, das Formular verarbeiten
            name = request.form['name']
            email = request.form['email']
            password = request.form['password']
        
            if name != '' and email != '' and password != '':
                try:
                    conn = create_connection()
                    passwordHashed = HassController.hash_password(password)
                    cursor = conn.cursor(dictionary=True)
                    query = '''INSERT INTO users_table (name, email,password, confirm, registration, role) VALUES (%s, %s,%s, %s, %s, %s)'''  # SQL query to insert a new user / SQL-Abfrage, um einen neuen Benutzer hinzuzufügen
                    cursor.execute(query, (name, email, passwordHashed, 0, date.today(), 'user'))  # Insert data into the table / Daten in die Tabelle einfügen
                    conn.commit()  # Commit the transaction / Transaktion abschließen
                
                except Exception as e:
                    connection.rollback()  # Rollback the transaction in case of error / Transaktion im Fehlerfall zurücksetzen
                    print(f"An error occurred: {e}")  # Print error message / Fehlermeldung ausdrucken
                finally:
                    cursor.close()  # Close the cursor / Cursor schließen
                    time.sleep(3)
                return  redirect(url_for('log_in')) # Redirect to users list after adding / Nach dem Hinzufügen zur Benutzerliste weiterleiten
            else:
                flash('All fields are requierd!', 'error')
        # return render_template('signup.html') 

    @staticmethod
    def login_user():
        if request.method =='POST':
            email = request.form['email']
            password = request.form['password']
            
            conn = create_connection()
            cursor = conn.cursor(dictionary = True)
            query = '''SELECT * FROM users_table WHERE email=%s'''
            cursor.execute(query, (email,))
            user = cursor.fetchone()  # Get the user details / Benutzerdetails abrufen
            
            # if user was found / falls Der Benutzer gefunden wurde
        
            if user and HassController.verify_password(password, user['password']):
                session['logged_in'] = True
                session['role'] = user['role'] # Store the Role in the session
                session['email'] = email 
                session['name'] = user['name']
                session['confirm'] = user['confirm']
                session['id'] = user['id']  

                return render_template('loading.html') 
            
            else:
                return render_template('error.html')    
        
        if 'logged_in' in session:
            return redirect(url_for('display_products'))  # Prevent access to login page if logged in
            
    @staticmethod
    def logout_user():
        session.pop('logged_in', None)
           