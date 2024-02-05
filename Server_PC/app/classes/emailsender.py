#Credit: Based on https://www.tutorialspoint.com/flask/flask_mail.htm

from flask_mail import Mail, Message
from .functions import *
import threading

class EmailSender:
    def __init__(self, app):

        # Lee la configuración de correo electrónico desde la base de datos
        self.email_conf = read_email_config()[0]
        self.mail = Mail()
        self.app = app
        self.init_app()


    def init_app(self):

        self.email_conf = read_email_config()[0] # Actualiza la configuración de correo electrónico desde la base de datos

        self.app.config['MAIL_SERVER'] = self.email_conf['MAIL_SERVER']
        self.app.config['MAIL_PORT'] = self.email_conf['MAIL_PORT']
        self.app.config['MAIL_USERNAME'] = self.email_conf['MAIL_USERNAME']
        self.app.config['MAIL_PASSWORD'] = self.email_conf['MAIL_PASSWORD']
        self.app.config['MAIL_USE_TLS'] = self.email_conf['MAIL_USE_TLS']
        self.app.config['MAIL_USE_SSL'] = self.email_conf['MAIL_USE_SSL']
        self.app.config['MAIL_DEFAULT_SENDER'] = self.email_conf['MAIL_DEFAULT_SENDER']
        self.mail.init_app(self.app)

    def _send(self, recipient, subject, body):
        '''Envía un correo electrónico al destinatario con el asunto y el cuerpo especificados. No utilices este método directamente, utiliza send() en su lugar.
        Args:
            recipient (str): La dirección de correo electrónico del destinatario.
            subject (str): El asunto del correo electrónico.
            body (str): El cuerpo del correo electrónico.'''
        


        with self.app.app_context():
            message = Message(subject=subject,
                              sender=f"Gotcha Security System <{self.email_conf['MAIL_DEFAULT_SENDER']}>",
                              recipients=[recipient],
                              body=body)
            print("Sending email...")
            self.mail.send(message)

    def send(self, recipient, subject, body):
        '''Envía un correo electrónico al destinatario con el asunto y el cuerpo especificados en un hilo separado (ÚSALO)
        Args:
            recipient (str): La dirección de correo electrónico del destinatario.
            subject (str): El asunto del correo electrónico.
            body (str): El cuerpo del correo electrónico.'''
        thread = threading.Thread(target=self._send, args=(recipient, subject, body))
        thread.start()
