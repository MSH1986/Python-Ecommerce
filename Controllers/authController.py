
from functools import wraps
from multiprocessing import connection
from flask import app, flash, request, jsonify, redirect, session, url_for, render_template
from Models.cartModel import CartModel


class AuthController:


    def __init__(self):
        # You can add initialization code here if needed
        pass

    # A decorator to protect routes from logged-in users
    def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'logged_in' not in session:
                return redirect(url_for('log_in'))
            return f(*args, **kwargs)
        return decorated_function
    
   