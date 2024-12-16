import bcrypt

class HassController:

      # function to hash the password
    def hash_password(password_user):
        # convert the string to bytes
        password_bytes = password_user.encode()      
        # generate a salt
        salt = bcrypt.gensalt(14)               
        # calculate a hash as bytes
        password_hash_bytes = bcrypt.hashpw(password_bytes, salt)   
        # decode bytes to a string
        password_hash_str = password_hash_bytes.decode()   
        return password_hash_str
    
    # Function to verify the password
    def verify_password(provided_password, stored_hash):
        # Convert the provided password to bytes
        provided_password_bytes = provided_password.encode()
        # Convert the stored hash to bytes
        stored_hash_bytes = stored_hash.encode()
        # Verify the provided password against the stored hash
        return bcrypt.checkpw(provided_password_bytes, stored_hash_bytes)
    