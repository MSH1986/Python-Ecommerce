from flask import flash, request, jsonify, redirect, session, url_for, render_template
from Models.favoriteModel import FavoriteModel
from Models.registerModel import RegisterModel

class RegisterController:

    @staticmethod
    def sign_up_controller():
       RegisterModel.Register_user()
       return render_template('signup.html') 

    @staticmethod
    def login_controller():
        # Call the login_user method
        result = RegisterModel.login_user()
        if result:  # if login_user returns a valid response (not None)
            return result
        return render_template('login.html')

    @staticmethod
    def logout_controller():
        RegisterModel.logout_user()
        return redirect(url_for('log_in'))  