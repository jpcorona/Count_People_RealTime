import smtplib
import json

# Inicializar la configuración de características.
with open("utils/config.json", "r") as archivo:
    config = json.load(archivo)

class EnviadorCorreo:
    """ Clase para iniciar la función de alerta por correo electrónico. """

    def __init__(self):
        self.correo_envio = config["Email_Send"]
        self.contraseña = config["Email_Password"]
        self.puerto = 465
        self.servidor = smtplib.SMTP_SSL('smtp.gmail.com', self.puerto)

    def enviar(self, correo_destino):
        self.servidor = smtplib.SMTP_SSL('smtp.gmail.com', self.puerto)
        self.servidor.login(self.correo_envio, self.contraseña)
        # mensaje a enviar
        ASUNTO = '¡ALERTA!'
        TEXTO = f'¡Se ha excedido el límite de personas en su edificio!'
        mensaje = 'Subject: {}\n\n{}'.format(ASUNTO, TEXTO)
        # enviar el correo
        self.servidor.sendmail(self.correo_envio, correo_destino, mensaje)
        self.servidor.quit()
