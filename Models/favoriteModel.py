from flask import flash, jsonify, redirect, session, url_for
from connect import create_connection

class FavoriteModel:
    
    @staticmethod
    def get_all_favorite_products():
        user_id = session.get('id')  # Retrieve the user ID from the session / abrufen
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        # Use a tuple to pass the parameters correctly
        cursor.execute("SELECT * FROM favorites WHERE user_id=%s", (user_id,))  
        favorites = cursor.fetchall()
        cursor.close()
        conn.close()
        return favorites


    @staticmethod
    def delete_favorite_By_Id(favorite_id):
        try:
            conn = create_connection()
            cursor = conn.cursor(dictionary=True)
            query = '''DELETE FROM favorites WHERE id = %s'''
            cursor.execute(query, (favorite_id,))
            conn.commit()  # Commit the deletion
            
            flash('Favorite has been deleted successfully!', 'success')
            return redirect(url_for('display_favorites'))  # Return the redirect to the favorite list
        except Exception as e:
            print(e)
            flash('An error occurred while trying to delete the favorite.', 'error')  # Error feedback to the user
            return redirect(url_for('display_favorites'))  # Redirect back even if there's an error
        finally:
            cursor.close()
            conn.close()
  

    @staticmethod
    def add_to_favorites(product_id):
        user_id = session.get('id')  # Retrieve the email from the session
        try:
            conn = create_connection()
            cursor = conn.cursor(dictionary=True)

            # Corrected SQL query to fetch the product by ID
            queryGet = '''SELECT * FROM products_table WHERE id=%s'''
            cursor.execute(queryGet, (product_id,))
            datas = cursor.fetchone()

            # Check if the product was found
            if not datas:
                print("Product not found.")
                return redirect(url_for('display_products'))  # Redirect if the product does not exist
            
            # Insert into cart table using the fetched product details
            queryAdd = '''INSERT INTO favorites (user_id, name, category, price, photo) VALUES (%s, %s, %s, %s, %s)'''
            cursor.execute(queryAdd, (user_id, datas['name'], datas['category'], datas['price'], datas['photo']))
            conn.commit()

            # Success message
            flash("It has been added successfully!", "success")

        except Exception as e:
                conn.rollback()
                print(f"An error occurred: {e}")  # Log the error
        finally:
                # Ensure the cursor is closed properly
                cursor.close()
        
        #     # Redirect to the display_products page after adding to favorites
        # return redirect(url_for('display_products'))

    # def get_favorite_count():
    #     if 'id' in session:
    #         user_id = session['id']
    #         conn = create_connection()
    #         cursor = conn.cursor(dictionary=True)
    #         query = "SELECT COUNT(*) as count FROM favorites WHERE user_id = %s"
    #         cursor.execute(query, (user_id,))
    #         result = cursor.fetchone()
    #         favorite_count = result['count']
    #     else:
    #         favorite_count = 0
    #     return jsonify({'favorite_count': favorite_count})