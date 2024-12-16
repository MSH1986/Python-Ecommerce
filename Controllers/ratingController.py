from flask import flash, request, jsonify, redirect, url_for, render_template
from Models.productModel import ProductModel
from Models.ratingModel import RatingModel

class RatingController:

    @staticmethod
    def show_rating(product_id):
        ratings = RatingModel.get_all_ratings(product_id)
        return ratings

    # @staticmethod
    # def add_one_rating(product_id):
    #     rating = RatingModel.add_new_rating(product_id)
    #     if rating:  # if login_user returns a valid response (not None)
    #         return rating
    #     return render_template('products/product-details.html') 
    
    @staticmethod
    def add_one_rating(product_id):
        # Call the method that adds a new rating
        return RatingModel.add_new_rating(product_id)
    
    @staticmethod
    def delete_rating(user_id, product_id):
        result = RatingModel.remove_rating(user_id, product_id)  # Return the result of the delete operation
        return result