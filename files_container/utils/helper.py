import time
from datetime import datetime

import bcrypt

import smtplib
from email.message import EmailMessage
from .emails_format import verification_email_html, restoration_email_html



def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)


def check_password(hashed_password, password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)




def is_valid_date(date_str):
    try:
        # Check if the date is in the correct format YYYYMMDD
        date = datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except:
        # If the date is not in the correct format or is invalid
        return 'Incorrect date format'


def send_email_verification_code(receiver_email, code, link, type_of_email=0):
    # Data for sending email
    sender_email = 'elias.croatia@gmail.com'
    email = f'{receiver_email}'
    msg = EmailMessage()
    msg['From'] = sender_email
    msg['To'] = email
    if type_of_email == 0:
        subject = 'Verify your Presgram'
        msg.set_content(verification_email_html(link, code), subtype='html')
    elif type_of_email == 1:
        subject = 'Reset Your Password'
        msg.set_content(restoration_email_html(link, code), subtype='html')

    msg['Subject'] = subject
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login('elias.croatia@gmail.com', 'jnqjvholnjtmqifq')
        server.send_message(msg)
        server.quit()
    except smtplib.SMTPAuthenticationError as e:
        return False
    return True


def time_difference(time_stamp):
    return time.time() - float(time_stamp)

