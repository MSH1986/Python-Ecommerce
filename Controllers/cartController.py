from flask import flash, request, jsonify, redirect, session, url_for, render_template
from Models.cartModel import CartModel


class CartController:

    @staticmethod
    def show_cart():
        carts = CartModel.get_all_cart_products()
        email = session.get('email')
        # Calculate the total price of all items
        total_price = sum(float(cart['price']) * cart['quantity'] for cart in carts)
        return render_template('cart/cart.html', carts=carts, email=email, total_price= total_price)

