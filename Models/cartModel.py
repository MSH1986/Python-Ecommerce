from flask import session
from connect import create_connection

class CartModel:
    
    @staticmethod
    def get_all_cart_products():
        user_id = session.get('id')  # Retrieve the user ID from the session / abrufen
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        # Use a tuple to pass the parameters correctly
        cursor.execute("SELECT * FROM cart WHERE user_id=%s", (user_id,))  
        carts = cursor.fetchall()
        cursor.close()
        conn.close()
        return carts
