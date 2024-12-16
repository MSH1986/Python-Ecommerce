from flask import flash, request, jsonify, redirect, url_for, render_template
from Models.productModel import ProductModel
from socketio_instance import socketio

class ProductController:
    socketio = None  # Initialized when app is created

    @staticmethod
    def show_products():
        products = ProductModel.get_all_products()
        return render_template('products/products.html', products=products)

    @staticmethod
    def show_one_product(product_id):
        product = ProductModel.get_one_product(product_id)
        return product  
    
    @staticmethod
    def add_one_product():
        product = ProductModel.add_new_product()
        
        if product:  # if login_user returns a valid response (not None)
          # Emit socket event for new product
            ProductController.socketio.emit('new_product', {
                'data': f"{product} has been added"
            })
            return product
        return render_template('products/add-product.html') 