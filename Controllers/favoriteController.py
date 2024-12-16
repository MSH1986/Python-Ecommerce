from flask import flash, request, jsonify, redirect, session, url_for, render_template
from Models.favoriteModel import FavoriteModel

class FavoriteController:

    @staticmethod
    def show_favorites():
        favorites = FavoriteModel.get_all_favorite_products()
        email = session.get('email')
        return render_template('products/favorites.html', favorites=favorites, email=email)

    @staticmethod
    def delete_favorite(favorite_id):
        result = FavoriteModel.delete_favorite_By_Id(favorite_id)  # Return the result of the delete operation
        return result
    
    @staticmethod
    def add_to_favorite_controller(product_id):
        product = FavoriteModel.add_to_favorites(product_id)
        if product:
            return product 
        return redirect(url_for('product_details', product_id=product_id))
    