#Credit: Based on https://www.tutorialspoint.com/flask/flask_mail.htm

from flask_mail import Mail, Message
from .functions import *
import threading

class EmailSender:
    '''Class to send emails using the Flask-Mail extension. It is designed to be used in a separate thread to avoid blocking the main thread.
    Args:
        app (Flask): The Flask application object (which contains the alerting object and context).
    '''


    def __init__(self, app):

        #Read email configuration from the database
        self.email_conf = read_email_config()[0]
        self.mail = Mail()
        self.app = app
        self.init_app()


    def init_app(self):
        '''Initializes the Flask-Mail extension with the email configuration from the database.'''

        self.email_conf = read_email_config()[0] #Read email configuration from the database

        self.app.config['MAIL_SERVER'] = self.email_conf['MAIL_SERVER']
        self.app.config['MAIL_PORT'] = self.email_conf['MAIL_PORT']
        self.app.config['MAIL_USERNAME'] = self.email_conf['MAIL_USERNAME']
        self.app.config['MAIL_PASSWORD'] = self.email_conf['MAIL_PASSWORD']
        self.app.config['MAIL_USE_TLS'] = self.email_conf['MAIL_USE_TLS']
        self.app.config['MAIL_USE_SSL'] = self.email_conf['MAIL_USE_SSL']
        self.app.config['MAIL_DEFAULT_SENDER'] = self.email_conf['MAIL_DEFAULT_SENDER']
        self.mail.init_app(self.app)

    #Private method to send the email
    def _send(self, recipient, subject, body, attachment=None):
        '''Sends an email to the recipient with the specified subject and body. 
        Do not use this method directly, use send() instead.
        Args:
            recipient (str): The email address of the recipient.
            subject (str): The subject of the email.
            body (str): The body of the email.'''
        
        #Context is needed to send the email
        with self.app.app_context():
            message = Message(subject=subject,
                              sender=f"Gotcha Security System <{self.email_conf['MAIL_DEFAULT_SENDER']}>",
                              recipients=[recipient],
                              html=body) #Sends as html
            
            if attachment: #Attach image if available (for alerts)
                try:
                    with self.app.open_resource(attachment) as fp:
                        message.attach(attachment, "image/jpeg", fp.read())
                except Exception as e:
                    print(f"Error attaching file: {e} video still recording?")
            
            print(f"Sending email...")
            self.mail.send(message)
            print(f"Email sent to {recipient}")

    #Public method to send the email
    def send(self, recipient, subject, body, attachment=None):
        '''Sends an email to the recipient with the specified subject and body in a separate thread (USE THIS)
        Args:
            recipient (str): The email address of the recipient.
            subject (str): The subject of the email.
            body (str): The body of the email.'''
        thread = threading.Thread(target=self._send, args=(recipient, subject, body, attachment))
        thread.start()
