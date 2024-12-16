import base64
from datetime import date
from email.message import EmailMessage
from email.mime.base import MIMEBase
from email import encoders
from email.header import Header
from email.mime.image import MIMEImage
from email.utils import formataddr, make_msgid
import mimetypes
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_email_register(user_name, user_email, confirmationCode):
    #email server settings
    sender_email ="mahershalash86@gmail.com"
    sender_password="zljj zrru wngk fxgm" # from gmail
    smtp_server="smtp.gmail.com"
    smtp_port= 587

    # Create the email content
    subject= "Registration Confirmation"
    body=f"Hallo {user_name},\nThank You for registring with us.\n\nThe Confirmation code is : {confirmationCode}\n\n Best regards\nBitLC\n\nThis Code is written with Python\nMaher Shalash :)"

    # Create email message
    msg = MIMEMultipart()
    # msg['From']= sender_email
    msg['From'] = formataddr((str(Header('Bitlc_Maher', 'utf-8')), sender_email))
    msg['To']= user_email
    msg['Subject']= subject
    msg.attach(MIMEText(body,'plain'))

    try:
        # Connect to the SMTP Server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls() #start TLS encryption

        # Login to the Email
        server.login(sender_email, sender_password)

        # send email to the user
        server.sendmail(sender_email, user_email, msg.as_string())

        print("Email has been sent successfully")

    except Exception as e:
        print(f"An Error accured: {e}")

    finally:
        server.quit()



def send_email_orders(user_name, user_email, carts):
    # Email server settings
    sender_email = "mahershalash86@gmail.com"
    sender_password = "zljj zrru wngk fxgm"  # App password for Gmail
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    # Create the email message
    msg = EmailMessage()

    # Set generic email headers
    msg['Subject'] = 'Order Confirmation'
    msg['From'] = formataddr((str(Header('Bitlc_Maher', 'utf-8')), sender_email))
    msg['To'] = user_email

    # Set the plain text body (fallback for email clients that don't support HTML)
    msg.set_content('Thank you for your order!')

    # Start building the HTML body
    html_body = f"""
    <html>
    <head>
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css" crossorigin="anonymous">
        <style>
            body {{
                font-size: 14px;  /* Set a smaller default font size */
                color: #333;  /* Slightly lighter text color for readability */
                }}
           
            table {{
                width: 100%;
                border-collapse: collapse;
                table-layout: fixed;  /* Set table layout to fixed */
            }}

            th, td {{
                padding: 8px;
                text-align: center;
                vertical-align: middle;
                word-wrap: break-word;  /* Break long words */
                font-size: 14px;  /* Smaller font size for table content */
            }}
            th {{
                background-color: #f2f2f2;  /* Add a background color for the header */
                font-size: 13px;  /* Slightly smaller font size for table headers */
            }}
            img {{
                display: block;
                margin: 0 auto;
                max-width: 100px;  /* Set a reasonable max-width for the image */
                height: auto;
            }}
            h2 {{
                font-size: 20px;  /* Smaller font size for the heading */
            }}
            p {{
                font-size: 14px;  /* Smaller font size for paragraphs */
            }}
        </style>
    </head>
    <body>
        <h2>Hello {user_name},</h2>
        <p>Thank you for buying from our shop! Below are the details of your order:</p>
        <table class="table table-bordered">
            <thead class="thead-light">
                <tr>
                    <th>Product Image</th>
                    <th>Product Name</th>
                    <th>Quantity</th>
                    <th>Price per Item</th>
                    <th>Total Price</th>
                </tr>
            </thead>
            <tbody>
    """

    # Loop through the cart items and add them to the email body
    for cart in carts:
        image_cid = make_msgid()[1:-1]  # Remove < and >

        # Get the absolute image path (fixing the extra 'crud' folder)
        image_path = os.path.abspath(os.path.join('static', 'images', cart['photo']))
        print(f"Image Path: {image_path}")

        if os.path.exists(image_path):
            with open(image_path, 'rb') as img:
                maintype, subtype = mimetypes.guess_type(img.name)[0].split('/')
                print(f"MIME Type: {maintype}/{subtype}")
                
                # Attach the image to the email with the correct MIME type
                msg.add_related(img.read(), maintype=maintype, subtype=subtype, cid=image_cid)
                print(f"Attached image with CID: {image_cid}")

            # Add the image tag to the HTML body
            image_tag = f'<img src="cid:{image_cid}" alt="{cart["name"]}">'
        else:
            print(f"Image not found: {image_path}")
            image_tag = '<img src="https://via.placeholder.com/100" alt="Image not available">'

        # Add the row for the current cart item
        html_body += f"""
        <tr>
            <td>{image_tag}</td>
            <td>{cart['name']}</td>
            <td>{cart['quantity']}</td>
            <td>${float(cart['price']):.2f}</td>
            <td>${float(cart['quantity']) * float(cart['price']):.2f}</td>
        </tr>
        """

    # Close the table and HTML tags
    html_body += """
            </tbody>
        </table>
        <br>
        <br>
        <p>We appreciate your business and hope to see you again!</p>
        <p>Best Regards,<br>Bitlc Shop</p>
    </body>
    </html>
    """

    # Add the HTML body as an alternative (to the plain text)
    msg.add_alternative(html_body, subtype='html')

    try:
        # Connect to the SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.ehlo()
        server.starttls()  # Start TLS encryption
        server.ehlo()

        # Log in to the email server
        server.login(sender_email, sender_password)

        # Send the email
        server.send_message(msg)

        print("Email has been sent successfully")

    except Exception as e:
        print(f"An Error occurred: {e}")

    finally:
        # Close the server connection
        server.quit()
