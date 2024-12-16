from datetime import date
from flask import flash, redirect, request, session, url_for
from connect import create_connection


class RatingModel:

    @staticmethod
    def get_all_ratings(product_id):
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM ratings WHERE product_id = %s", (product_id,))
        ratings = cursor.fetchall()
        cursor.close()
        conn.close()
        return ratings

    @staticmethod
    def remove_rating(user_id, product_id):
        user_id = session.get('id')
        try:
            conn = create_connection()
            cursor = conn.cursor(dictionary=True)
            query = '''DELETE FROM ratings WHERE user_id = %s AND product_id= %s'''
            cursor.execute(query, ( user_id, product_id,))
            conn.commit()  # Commit the deletion
        
            flash('Rating has been deleted successfully!', 'success')
            return redirect(url_for('product_details', product_id=product_id))
            # Return the redirect to the favorite list
        except Exception as e:
            print(e)
            flash('An error occurred while trying to delete the Rating.', 'danger')  # Error feedback to the user
            return redirect(url_for('product_details', product_id=product_id))
        # Redirect back even if there's an error
        finally:
            cursor.close()
            conn.close()
    

    def add_new_rating(product_id):
        if request.method == 'POST':
            user_id = session.get('id')
            conn = create_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users_table WHERE id = %s", (user_id,))
            user = cursor.fetchone()

            # Check if user is logged in
            if not user_id:
                flash("You must be logged in to add a rating!", "error")
                return redirect(url_for('product_details', product_id=product_id))

            rating_value = request.form['rating_value']
            comment_text = request.form['comment_text']

            # Basic server-side validation
            if not rating_value or not comment_text:
                flash("All fields are required!", "danger")
                return redirect(url_for('product_details', product_id=product_id))

            try:
                conn = create_connection()
                cursor = conn.cursor(dictionary=True)

                # Check if the user has already rated this product
                check_query = '''SELECT * FROM ratings WHERE user_id = %s AND product_id = %s'''
                cursor.execute(check_query, (user_id, product_id))
                existing_rating = cursor.fetchone()

                if existing_rating:
                    # User has already rated this product
                    flash("You have already submitted a rating for this product!", "danger")
                    return redirect(url_for('product_details', product_id=product_id))

                # Insert the new rating into the database
                insert_query = '''INSERT INTO ratings (user_id, user_name, product_id, rating_value, comment, created_at) 
                                  VALUES (%s, %s, %s, %s, %s, %s)'''
                cursor.execute(insert_query, (user_id, user['name'], product_id, rating_value, comment_text, date.today()))

                # Commit the transaction
                conn.commit()

                # Success message
                flash("Rating added successfully!", "success")

            except Exception as e:
                # Rollback if there's an error
                conn.rollback()
                flash(f"An error occurred: {e}", "error")
                return redirect(url_for('product_details', product_id=product_id))

            finally:
                cursor.close()
                conn.close()

            # Redirect back to the product details page after successful insertion
            return redirect(url_for('product_details', product_id=product_id))
    