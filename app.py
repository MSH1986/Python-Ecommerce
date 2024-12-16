from asyncio import Queue
from functools import wraps
import random
import time
import eventlet
import flask
from flask_socketio import SocketIO
import redis
import stripe
from flask import Flask, flash, jsonify, redirect, render_template, request, url_for,session
from Controllers.authController import AuthController
from Controllers.cartController import CartController
from Controllers.favoriteController import FavoriteController
from Controllers.hashController import HassController
from Controllers.productController import ProductController
from Controllers.ratingController import RatingController
from Controllers.registerController import RegisterController
from connect import create_connection
from send_email import send_email_orders, send_email_register
from datetime import date
from socketio_instance import socketio

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flashing messages / Benötigt für die Anzeige von Nachrichten


socketio = SocketIO(
    app, 
    async_mode= "eventlet",
    cors_allowed_origins="*",
    )

# Pass socket instance to ProductController
ProductController.socketio = socketio

# Use async mode (eventlet or gevent)
# socketio = SocketIO(app)  # or 'gevent'

stripe.api_key= "sk_test_51PvLzPCjORtALYJ4Bhy6BYJpHEhvtwIo4cXPHUCRUVo4RePOXHjUlA1eRxdcQD1wV0ZYohnM3M7YkOOacFW29NCt00faIKkUSq"


YOUR_DOMAIN= "http://127.0.0.1:5000"

# connection to the Database, Verbindung mit dem Datenbank
connection = create_connection()

# function to hash the password
# def hash_password(password_user):
#     # convert the string to bytes
#     password_bytes = password_user.encode()      
#     # generate a salt
#     salt = bcrypt.gensalt(14)               
#     # calculate a hash as bytes
#     password_hash_bytes = bcrypt.hashpw(password_bytes, salt)   
#     # decode bytes to a string
#     password_hash_str = password_hash_bytes.decode()   
#     return password_hash_str

# # Function to verify the password
# def verify_password(provided_password, stored_hash):
#     # Convert the provided password to bytes
#     provided_password_bytes = provided_password.encode()
#     # Convert the stored hash to bytes
#     stored_hash_bytes = stored_hash.encode()
#     # Verify the provided password against the stored hash
#     return bcrypt.checkpw(provided_password_bytes, stored_hash_bytes)



# A decorator to protect routes from logged-in users
# def login_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if 'logged_in' not in session:
#             return redirect(url_for('log_in'))
#         return f(*args, **kwargs)
#     return decorated_function

# ------------------------------
# @app.context_processor
# def inject_favorite_count():
#     # Check if the user is logged in
#      if 'id' in session:
#         user_id = session['id']
#         role = session.get('role')  # Retrieve the Role from the session
#         # Query to get the count of favorites for the logged-in user
#         cursor = connection.cursor(dictionary=True)
#         query = "SELECT * FROM favorites WHERE user_id = %s"
#         cursor.execute(query, (user_id,))
#         favorite_count = len(cursor.fetchall())
        
#         cursor2 = connection.cursor(dictionary=True)
#         query2 = "SELECT * FROM cart WHERE user_id = %s"
#         cursor2.execute(query2, (user_id,))
#         cart_count = len(cursor2.fetchall())    
      
#      else:
#             # User not logged in, so favorite count is 0
#             favorite_count = 0
#             cart_count = 0
#             role = session.get('role')
        
#         # Return the count to be available in all templates
#      return dict(favorite_count=favorite_count, cart_count=cart_count, role=role, confirm= session.get('confirm'))

# -----------------------------------------
@app.context_processor
def inject_favorite_count():
    if 'id' in session:
        user_id = session['id']
        role = session.get('role')
        conn = create_connection()
        
        # Get the favorite count
        cursor = conn.cursor(dictionary=True)
        query = "SELECT COUNT(*) as count FROM favorites WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        favorite_count = result['count']
        
        # Get the cart count
        cursor2 = conn.cursor(dictionary=True)
        query2 = "SELECT COUNT(*) as count FROM cart WHERE user_id = %s"
        cursor2.execute(query2, (user_id,))
        result2 = cursor2.fetchone()
        cart_count = result2['count']
        
         # Fetch unread notifications
        cursor.execute("SELECT COUNT(*) as unread_count FROM notifications WHERE user_id = %s AND is_read = FALSE", (user_id,))
        unread_count = cursor.fetchone()['unread_count']


        cursor.close()
        cursor2.close()
        conn.close()
    else:
        favorite_count = 0
        cart_count = 0
        unread_count =0
        role = None
    
    return dict(favorite_count=favorite_count, cart_count=cart_count, unread_count=unread_count, role=role, confirm=session.get('confirm'))


#-------------------Sign in/ Sign up Section----------------------

# Route to display log in page
@app.route('/', methods=['GET', 'POST'])
def log_in():
 return RegisterController.login_controller()


# Route to display sign up page
@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():   
 return RegisterController.sign_up_controller()

#-------------------Sign in/ Sign up Section----------------------


# Route to display loading page
@app.route('/loading', methods=['GET'])
def show_loading():
    # Load the loading.html template
    return render_template('loading.html')  


#-------------------Products Section----------------------
# Route to display Products page
@app.route('/products', methods=['GET'])
# @login_required
@AuthController.login_required
def display_products():
    return ProductController.show_products()

@app.route('/get_notifications', methods=['GET'])
def get_notifications():
    user_id = session.get('id')  # Assuming the user's ID is stored in the session
    
    if not user_id:
        return jsonify({'error': 'User not logged in'}), 401  # Handle the case where no user is logged in

    conn = create_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch unread notifications for the user
    cursor.execute("SELECT id, product_id, message, photo, created_at FROM notifications WHERE user_id = %s", (user_id,))
    notifications = cursor.fetchall()

    # Format the 'created_at' field to a string in each notification
    for notification in notifications:
        if notification['created_at']:
            notification['created_at'] = notification['created_at'].strftime('%Y-%m-%d')  # Convert to string in 'YYYY-MM-DD' format
            
    # Mark the notifications as read
    cursor.execute("UPDATE notifications SET is_read = TRUE WHERE user_id = %s", (user_id,))
    conn.commit()

    cursor.close()
    conn.close()
    return jsonify({'notifications': notifications})


# Route to add Product
@app.route('/Addproduct', methods=['GET','POST'])
def add_product():
    return ProductController.add_one_product()
    

# Route to details Product
@app.route('/detailsProduct/<int:product_id>', methods=['GET'])
def product_details(product_id):
    # Get ratings using the RatingController
    ratings = RatingController.show_rating(product_id)
    product = ProductController.show_one_product(product_id)
    return render_template('products/product-detials.html', product=product, ratings=ratings)

# Route to add Rating
@app.route('/Addrating/<int:product_id>', methods=['POST'])
def add_rating(product_id):
    # Call the method in the RatingController to add a rating
    return RatingController.add_one_rating(product_id)

@app.route('/deleteRating/<int:user_id>/<int:product_id>', methods=['GET'])
def delete_comment(user_id, product_id):
    return RatingController.delete_rating(user_id, product_id)
#-------------------Products Section----------------------



#-------------------Favorites Section----------------------

# Route to display favorites page
@app.route('/favorites', methods=['GET'])
@AuthController.login_required
def display_favorites():
    return FavoriteController.show_favorites()


# Route to add add_to_favorites
@app.route('/addtofavorites/<int:product_id>', methods=['GET', 'POST'])
def add_to_favorites(product_id):
   return FavoriteController.add_to_favorite_controller(product_id)


#add an item from the favorites table to the cart table and then remove it from the favorites table
@app.route('/addfavoritestocart/<int:favorite_id>', methods=['GET', 'POST'])
def add_from_favorites_to_cart(favorite_id):
    user_id = session.get('id')
    if not user_id:
        return redirect(url_for('log_in'))  # Redirect to login if user is not logged in

    try:
        cursor = connection.cursor(dictionary=True)
        
        # Corrected SQL query to fetch the product by ID
        queryGet = '''SELECT * FROM favorites WHERE id=%s'''
        cursor.execute(queryGet, (favorite_id,))
        datas = cursor.fetchone()

        # Check if the product was found
        if not datas:
            print("Product not found.")
            return redirect(url_for('display_products'))  # Redirect if the product does not exist
        
        # Insert into cart table using the fetched product details
        queryAdd = '''INSERT INTO cart (user_id, name, category, quantity, price, photo) VALUES (%s, %s, %s, %s, %s, %s)'''
        cursor.execute(queryAdd, (user_id, datas['name'], datas['category'], 1, datas['price'], datas['photo']))
        connection.commit()

        # Create a new cursor for the delete operation
        cursor = connection.cursor(dictionary=True)
        queryDelete = '''DELETE FROM favorites WHERE id = %s'''  # SQL query to delete the favorite item
        cursor.execute(queryDelete, (favorite_id,))
        connection.commit()  # Commit the deletion

    except Exception as e:
        connection.rollback()
        print(f"An error occurred: {e}")  # Log the error
    finally:
        # Ensure the cursor is closed properly
        cursor.close()
        
    # Redirect to the display_cart page after adding to cart
    return redirect(url_for('display_cart'))

  
@app.route('/deleteFavorite/<int:favorite_id>', methods=['GET'])
def delete_favorite(favorite_id):
    return FavoriteController.delete_favorite(favorite_id)
  
#-------------------Favorites Section----------------------



#-------------------Cart Section----------------------

@app.route('/cart', methods=['GET'])
@AuthController.login_required
def display_cart():
    return CartController.show_cart() 


# Route to add add_to_cart
@app.route('/addtocart/<int:product_id>', methods=['GET', 'POST'])
def add_to_cart(product_id):
    user_id = session.get('id')  # Retrieve the email from the session
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Corrected SQL query to fetch the product by ID
        queryGet = '''SELECT * FROM products_table WHERE id=%s'''
        cursor.execute(queryGet, (product_id,))
        datas = cursor.fetchone()

        # Check if the product was found
        if not datas:
            print("Product not found.")
            return redirect(url_for('display_products'))  # Redirect if the product does not exist
        
        # Insert into cart table using the fetched product details
        queryAdd = '''INSERT INTO cart (user_id, product_id, name, category, quantity, price, photo) VALUES (%s, %s, %s,%s, %s, %s, %s)'''
        cursor.execute(queryAdd, (user_id, datas['id'], datas['name'], datas['category'], 1, datas['price'], datas['photo']))
        connection.commit()

    except Exception as e:
        connection.rollback()
        print(f"An error occurred: {e}")  # Log the error
    finally:
        # Ensure the cursor is closed properly
        cursor.close()
        
    # Redirect to the display_products page after adding to favorites
    return redirect(url_for('display_products'))

  
@app.route('/deleteProduct/<int:cart_id>', methods=['GET'])
def delete_cart(cart_id):
    try:
        cursor = connection.cursor(dictionary=True)
        query = '''DELETE FROM cart WHERE id = %s'''  # SQL query to delete the user / SQL-Abfrage, um den Benutzer zu löschen
        cursor.execute(query, (cart_id,))
        connection.commit()  # Commit the deletion / Löschung abschließen
        
        # Flash a success message / Erfolgsnachricht anzeigen
        flash('Product has been deleted successfully!', 'success')
        
        return redirect(url_for('display_cart'))  # Redirect to the users list / Zur Benutzerliste weiterleiten
    except Exception as e:
        print(e)  
    finally:
        cursor.close()  
  

@app.route('/payment', methods=['GET'])
def payment():
    user_id = session.get('id')
    if not user_id:
        return redirect(url_for('login'))

    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM cart WHERE user_id = %s"
    cursor.execute(query, (user_id,))
    carts = cursor.fetchall()
    total_price = sum(float(cart['price']) for cart in carts)
    session['total_price'] = total_price
    
    return render_template('cart/payment.html', carts=carts, total_price=total_price)


@app.route('/create-checkout-session', methods=['GET','POST'])
def create_checkout_session():
    user_id = session.get('id')
    if not user_id:
        return redirect(url_for('login'))

    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM cart WHERE user_id = %s"
    cursor.execute(query, (user_id,))
    carts = cursor.fetchall()
    line_items = [{
        'price_data': {
            'currency': 'usd',
            'product_data': {
                'name': cart['name'],
            },
            'unit_amount': int(float(cart['price']) * 100),  # Ensure price is converted to float
        },
        'quantity': 1,
    } for cart in carts]

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url=url_for('payment_success', _external=True),
        cancel_url=url_for('payment_cancel', _external=True),
    )

    return redirect(checkout_session.url, code=303)


@app.route('/payment-success')
def payment_success():
    user_id = session.get('id')
    email = session.get('email')
    total_price = session.get('total_price')

    # Validate user and payment details
    if not user_id or not total_price:
        flash('Error: Missing user or payment information', 'error')
        return redirect(url_for('cart'))

    cursor = connection.cursor(dictionary=True)

    # Fetch the cart items from the database
    query = "SELECT * FROM cart WHERE user_id = %s"
    cursor.execute(query, (user_id,))
    carts = cursor.fetchall()

    if not carts:
        flash('Error: No items in cart to process', 'error')
        return redirect(url_for('cart'))

    # Fetch the user information from users_table
    query = "SELECT * FROM users_table WHERE id = %s"
    cursor.execute(query, (user_id,))
    user = cursor.fetchone()

    if not user:
        flash('Error: User not found', 'error')
        return redirect(url_for('cart'))
    
    # Insert each cart item into order_items table
    for item in carts:
        item_name = item['name']
        product_id = item['product_id']  # Assuming product_id is already in the cart table
        item_category = item['category']
        item_quantity = item['quantity']
        item_price = item['price']
        item_photo = item['photo']
    # Insert the order into the orders table
    query = """
        INSERT INTO orders (user_id, product_id, user_name, total_price, order_date)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (user_id, item['product_id'], user['name'], total_price, date.today()))
    order_id = cursor.lastrowid  # Get the ID of the newly created order

    

    query = """
        INSERT INTO order_items (order_id, product_id, item_name, item_category, item_quantity, item_price, item_photo)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (order_id, product_id, item_name, item_category, item_quantity, item_price, item_photo))

    # Commit the transaction for the order
    connection.commit()


    # send_email_orders(user['name'], email, carts)


    # Clear the cart items for this user from the database
    query = "DELETE FROM cart WHERE user_id = %s"
    cursor.execute(query, (user_id,))
    connection.commit()

    # Clear the cart-related session data
    session.pop('cart', None)
    session.pop('total_items', None)
    session.pop('total_price', None)

    # Redirect to the success page
    return render_template('cart/success.html')

@app.route('/payment-cancel')
def payment_cancel():
    return "Payment canceled!"


@app.route('/update-quantity', methods=['POST'])
def update_quantity():
    data = request.json  # Use request.json to get the JSON body
    cart_id = data.get('cart_id')
    new_quantity = data.get('quantity')
    
    cursor = connection.cursor()
    query = "UPDATE cart SET quantity = %s WHERE id = %s"
    cursor.execute(query, (new_quantity, cart_id))
    connection.commit()
    
    return jsonify({'success': True})

#-------------------Cart Section----------------------


#-------------------Orders Section----------------------


@app.route('/orders', methods=['GET'])
@AuthController.login_required
def view_orders():
    user_id = session.get('id')
    
    cursor = connection.cursor(dictionary=True)
    
    # Fetch orders for the user
    query = "SELECT * FROM orders WHERE user_id=%s"
    cursor.execute(query, (user_id,))
    orders = cursor.fetchall()


    if not orders:
        flash('You have no orders yet.', 'info')
        return render_template('orders/order.html', orders=[])

    order_items = {}


    # Fetch order items for each order
    for order in orders:
        order_id = order['id']
        query = "SELECT * FROM order_items WHERE order_id = %s"
        cursor.execute(query, (order_id,))
        order_items[order_id] = cursor.fetchall()

    return render_template('orders/order.html', orders=orders, order_items=order_items)


#-------------------Orders Section----------------------



#-------------------Send Email Section----------------------

@app.route('/confirmCode/<int:user_Id>', methods=['GET', 'POST'])
def send_email(user_Id):
    # Check if confirmation code is already in the session
    if 'confirmation_code' not in session:
        # Generate and store confirmation code in session
        confirmation_code = random.randint(111111, 999999)
        session['confirmation_code'] = confirmation_code

    if request.method == 'POST':
        # Get the confirmation code from the form input
        confirm = request.form['confirm']
        try:
            confirmCode = int(confirm)
        except ValueError:
            flash("Invalid confirmation code", "danger")
            return redirect(url_for('send_email', user_Id=user_Id))

        # Compare the input confirmation code with the session value
        if confirmCode == session['confirmation_code']:
            cursor = connection.cursor(dictionary=True)
            query = '''UPDATE users_table SET confirm = %s WHERE id = %s'''
            cursor.execute(query, (1, user_Id))
            connection.commit()
            cursor.close()

            # Clear confirmation code from session
            session.pop('confirmation_code', None)

            # Redirect to the user list page
            flash("User confirmed successfully!", "success")
            return redirect(url_for('read_users'))
        else:
            flash("Incorrect confirmation code", "danger")
            return redirect(url_for('send_email', user_Id=user_Id))

    # Fetch user details by ID
    cursor = connection.cursor(dictionary=True)
    query = '''SELECT * FROM users_table WHERE id=%s'''
    cursor.execute(query, (user_Id,))
    user = cursor.fetchone()
    cursor.close()

    # Send confirmation email (ensure this is a separate process or thread if possible)
    send_email_register(user['name'], user['email'], session['confirmation_code'])
    
    return render_template('confirmation.html', user=user)

#-------------------Send Email Section----------------------



#-------------------Account Section----------------------

@app.route('/show_profile', methods=['GET'])
def show_profile():
    email = session.get('email')
    return render_template('account/profile.html', email=email, name=session.get('name'))

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    email = session.get('email')
    if not email:  # Ensure the user is logged in
        return redirect('/login')  # Redirect to login if no email in session

    if request.method == 'POST':
        current_password = request.form['currentPassword']
        new_password = request.form['newPassword']

        if not current_password or not new_password:
            return render_template('account/change-password.html', email=email, error="All fields are required.")
        
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        
       # Validate current password
        cursor.execute('SELECT password FROM users_table WHERE email=%s', (email,))
        stored_password = cursor.fetchone()
        if not stored_password or not HassController.verify_password(current_password, stored_password['password']):
            return render_template('account/change-password.html', email=email, error="Current password is incorrect.")

        # Hash and update the new password
        password_hashed = HassController.hash_password(new_password)
        cursor.execute('UPDATE users_table SET password=%s WHERE email=%s', (password_hashed, email))
        conn.commit()
        
        # Close the connection
        cursor.close()
        conn.close()
        
        # Pass a success message to the template
        return render_template('account/change-password.html', email=email, success=True)

    return render_template('account/change-password.html', email=email)




@app.route('/confirmAccount', methods=['GET', 'POST'])
def show_confirm_account():
    email = session.get('email')
    if request.method == 'POST':  # If request is POST, handle form submission / Wenn die Anfrage POST ist, das Formular verarbeiten
          print("POST request received")
     
         # Generate and store confirmation code in session
          confirmation_code = random.randint(111111, 999999)
          session['confirmation_code'] = confirmation_code
    
          cursor = connection.cursor(dictionary = True)
          query = '''SELECT * FROM users_table WHERE email=%s'''
          cursor.execute(query, (email,))
          user = cursor.fetchone()  # Get the user details / Benutzerdetails abrufen
    
          # Send confirmation 
          # send_email_register(user['name'], email, confirmation_code)

          time.sleep(2)
          return redirect(url_for('confirmation_code_verify'))
      
    return render_template('account/account.html', email=email)


@app.route('/confirmAccountCode', methods=['GET', 'POST'])
def confirmation_code_verify():
    email = session.get('email')
    print(session.get('confirmation_code'))

    if request.method == 'POST':
        # Get the user-entered confirmation code
        code_user = request.form['confirm-code']
        
        # Get the correct confirmation code from the session
        confirmation_code = session.get('confirmation_code')
        
        # Validate user input and compare it with the stored confirmation code
        if str(code_user) == str(confirmation_code):
            try:
                # Update user confirmation status in the database
                cursor = connection.cursor(dictionary=True)
                query = '''UPDATE users_table SET confirm = %s WHERE email = %s'''
                cursor.execute(query, (1, email))
                connection.commit()
                
                # # Update session after successful confirmation
                session['confirm'] = 1  # Set 'confirm' in session to 1 (confirmed)
             
                # Redirect the user to the products page after successful confirmation
                return redirect(url_for('display_products'))
                
            except Exception as e:
                connection.rollback()
                print(f"An error occurred: {e}")
            finally:
                cursor.close()
        else:
            # Add error message if the confirmation code doesn't match
            flash("Invalid confirmation code. Please try again", "danger")
            
            return redirect(url_for('confirmation_code_verify', email=email))
    
    return render_template('account/confrmation-account.html', email=email)


#-------------------Account Section----------------------



#-------------------Users Section----------------------

@app.route('/users', methods = ['GET'])
# Call all Users / Alle Benutzer abrufen
@AuthController.login_required
def read_users():
    cursor = connection.cursor(dictionary=True)
    query = '''SELECT * FROM users_table'''  # SQL query to select all users / SQL-Abfrage, um alle Benutzer auszuwählen
    cursor.execute(query)
    datas = cursor.fetchall()  # Fetch all users / Alle Benutzer abrufen
    email = session.get('email')  # Retrieve the email from the session
    return render_template('users.html', datas=datas, email=email) 


# Add User / Benutzer hinzufügen
@app.route('/addUser', methods=['GET', 'POST'])
@AuthController.login_required
def add_user():
    if request.method == 'POST':  # If request is POST, handle form submission / Wenn die Anfrage POST ist, das Formular verarbeiten
        name = request.form['name']
        email = request.form['email']
        try:
            cursor = connection.cursor(dictionary=True)
            query = '''INSERT INTO users_table (name, email, confirm, registration) VALUES (%s, %s, %s, %s)'''  # SQL query to insert a new user / SQL-Abfrage, um einen neuen Benutzer hinzuzufügen
            cursor.execute(query, (name, email, 0, date.today()))  # Insert data into the table / Daten in die Tabelle einfügen
            connection.commit()  # Commit the transaction / Transaktion abschließen
            
            # send email to the user after registration
            # send_email_register(name, email)

        except Exception as e:
            connection.rollback()  # Rollback the transaction in case of error / Transaktion im Fehlerfall zurücksetzen
            print(f"An error occurred: {e}")  # Print error message / Fehlermeldung ausdrucken
        finally:
            cursor.close()  # Close the cursor / Cursor schließen
        return redirect(url_for('show_loading'))  # Redirect to users list after adding / Nach dem Hinzufügen zur Benutzerliste weiterleiten
    
    return render_template('add-user.html')  # Render form to add a new user / Formular zum Hinzufügen eines neuen Benutzers rendern


# Update User / Benutzer aktualisieren
@app.route('/updateUser/<int:user_Id>', methods = ['GET', 'POST'])
@AuthController.login_required
def update_user(user_Id):
    if request.method == 'POST':  # If request is POST, handle the update / Wenn die Anfrage POST ist, die Aktualisierung verarbeiten
        name = request.form['name']
        email = request.form['email']
        try:
            cursor = connection.cursor(dictionary=True)
            query = '''UPDATE users_table SET name= %s,  email= %s, registration= %s where id = %s'''  # SQL query to update the user / SQL-Abfrage, um den Benutzer zu aktualisieren
            cursor.execute(query, (name, email, date.today(), user_Id))  # Execute the update / Aktualisierung ausführen
            connection.commit()  # Commit the transaction / Transaktion abschließen
        except Exception as e:
            connection.rollback()  # Rollback in case of error / Im Fehlerfall zurücksetzen
            print(f"An error occurred: {e}")  # Print error message / Fehlermeldung ausdrucken
        finally:
            cursor.close()  # Close the cursor / Cursor schließen
        return redirect(url_for('read_users'))  # Redirect to the users list after update / Nach der Aktualisierung zur Benutzerliste weiterleiten

    # Fetch the user to prefill the form / Den Benutzer abrufen, um das Formular vorzufüllen
    cursor = connection.cursor(dictionary = True)
    query = '''SELECT * FROM users_table WHERE id=%s'''  # SQL query to get user by ID / SQL-Abfrage, um den Benutzer nach ID abzurufen
    cursor.execute(query, (user_Id,))
    user = cursor.fetchone()  # Get the user details / Benutzerdetails abrufen
    return render_template('update-user.html', user=user)  # Render the update form / Formular zum Aktualisieren rendern


# Delete User / Benutzer löschen
@app.route('/deleteUser/<int:user_Id>', methods=['GET'])
@AuthController.login_required
def delete_user(user_Id):
    try:
        cursor = connection.cursor(dictionary=True)
        query = '''DELETE FROM users_table WHERE id = %s'''  # SQL query to delete the user / SQL-Abfrage, um den Benutzer zu löschen
        cursor.execute(query, (user_Id,))
        connection.commit()  # Commit the deletion / Löschung abschließen
        # Flash a success message / Erfolgsnachricht anzeigen
        flash('User deleted successfully!', 'success')
        return redirect(url_for('read_users'))  # Redirect to the users list / Zur Benutzerliste weiterleiten
    except Exception as e:
        print(e)  # Print error message / Fehlermeldung ausdrucken
    finally:
        cursor.close()  # Close the cursor / Cursor schließen


# Mark notifications as read when user clicks the bell icon
@app.route('/mark_notifications_read', methods=['POST'])
def mark_notifications_read():
    user_id = session.get('id')
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE notifications SET is_read = TRUE WHERE user_id = %s", (user_id,))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"status": "success"})

#-------------------Users Section----------------------


# Logout route
@app.route('/logout',methods=['GET'])
def logout():
    return RegisterController.logout_controller()

# Disable caching
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response


# Run the application in debug mode / Anwendung im Debug-Modus ausführen
if __name__ == '__main__':
    socketio.run(app, debug=True)