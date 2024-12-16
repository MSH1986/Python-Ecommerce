from datetime import date, datetime
from flask import flash, redirect, render_template, request, url_for
from connect import create_connection
from socketio_instance import socketio
import threading

class ProductModel:
    
    @staticmethod
    def get_all_products():
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM products_table")  
        products = cursor.fetchall()
        cursor.close()
        conn.close()
        return products
    
    @staticmethod
    def get_one_product(product_id):
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        query = '''SELECT * FROM products_table WHERE id=%s'''
        cursor.execute(query, (product_id,))
        product = cursor.fetchone()
        return product
    
    @staticmethod
    def add_new_product():
        if request.method == 'POST':
            name = request.form['name']
            category = request.form['category']
            description = request.form['description']
            price = request.form['price']
            photo = request.form['photo']
            
            # Basic server-side validation
            if not name or not category or not description or not price or not photo:
                flash("All fields are required!", "error")
                return redirect(url_for('add_product'))

            try:
                conn = create_connection()
                cursor = conn.cursor(dictionary=True)
            
                # Insert the new product into the database
                query = '''INSERT INTO products_table (name, category, description, price, photo) 
                           VALUES (%s, %s, %s, %s, %s)'''
                cursor.execute(query, (name, category, description, price, photo))
                
                # Commit the new product insertion
                conn.commit()

                 # Get the inserted product ID
                product_id = cursor.lastrowid
                
                # Create notification message
                message = f"A new product '{name}' from Category: {category} has been added!"
                created_at = datetime.now().date()

                # Fetch all user IDs
                cursor.execute("SELECT id FROM users_table")
                users = cursor.fetchall()
            
                # Insert notifications for each user
                for user in users:
                    cursor.execute(
                        "INSERT INTO notifications (user_id, product_id , message, photo, is_read, created_at) VALUES (%s, %s, %s, %s, %s, %s)", 
                        (user['id'], product_id, message, photo, False, created_at)
                        # "INSERT INTO notifications (user_id, message, photo, is_read) VALUES (%s, %s, %s, %s)", 
                        # (user['id'], message, photo, False)
                    )

                conn.commit()

                
                 # Emit notification and unread count for all users
                # def emit_notification():
                #     cursor.execute("SELECT COUNT(*) as unread_count FROM notifications WHERE is_read = FALSE")
                #     unread_count = cursor.fetchone()['unread_count']
                    
                #     # Emit real-time notification with updated unread count using SocketIO
                #     socketio.emit('add_new', {'message': message, 'photo': photo, 'unread_count': unread_count, 'created_at': created_at.strftime('%Y-%m-%d')})

                # # Start a new thread to handle the SocketIO emission
                # thread = threading.Thread(target=emit_notification)
                # thread.start()
                
                flash("Product added successfully!", "success")
                return redirect(url_for('display_products'))
        
            except Exception as e:
                # Rollback if there's an error
                conn.rollback()
                flash(f"An error occurred: {e}", "error")
                return redirect(url_for('add_product'))
        
            finally:
                cursor.close()
                conn.close()
