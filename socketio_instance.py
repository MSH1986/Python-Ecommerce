from flask_socketio import SocketIO, emit

socketio = SocketIO()  # Initialize socketio here




# def send_notification_to_users(message):
#     conn = create_connection()
#     cursor = conn.cursor(dictionary=True)

#     # Insert notification into database for all users
#     cursor.execute("SELECT id FROM users_table")  # Assuming you have a users table
#     users = cursor.fetchall()
#     for user in users:
#         cursor.execute("INSERT INTO notifications (user_id, message, is_read) VALUES (%s, %s, %s)", (user['id'], message, False))

#     conn.commit()
#     cursor.close()
#     conn.close()

#     # Emit real-time notification to all connected clients
#     socketio.emit('new_notification', {'message': message}, broadcast=True)