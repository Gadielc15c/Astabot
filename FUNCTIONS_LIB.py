import logging
import re
import smtplib
from geopy.geocoders import Nominatim
from rfc3986 import validators

import DB_CONN
import random
import ssl
import string
import telegram
import DB_CONN
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

import ENV_VARs

geolocator = Nominatim(user_agent="geoapiExercises")

logger = logging.getLogger(__name__)


def getAdress(lat, lon):
    """
    :param lat: recieves latitude
    :param lon: recieves longitud
    :return: returns message with client address
    """
    location = geolocator.reverse(str(lat) + "," + str(lon))
    address = location.raw['address']
    suburb = address.get('suburb', '')
    city = address.get('city', '')
    state = address.get('state', '')
    country = address.get('country', '')
    code = address.get('country_code')
    zipcode = address.get('postcode')
    msg = f"Enviar a:{suburb, state} en {city, country} {zipcode}"
    return msg


def ProductsListProcessor(pList):
    """
    :param pList: Recieves list of products
    :return: returns producto
    """
    for productos in pList:
        msg = f"TENEMOS LOS SIGUIENTES PRODUCTOS \n" \
              f"- {productos[1]}"
    return msg


async def userNameProcesor(userN):
    """
    :param userN: param that includes non formatted username
    :return - Username: Formated Username (String)
    :return - msg: Returns message With Warnings (String)
    :return - State: Returns State (String)

    """
    UserName = SpaceRemover(userN)
    msg = "⚠️ NOMBRE DE USUARIO INCORECTO ⚠️"

    if 3 <= len(UserName) <= 10:
        exists = DB_CONN.execute_select(f'SELECT username FROM user WHERE username = "{UserName}"')

        if not exists:
            return True, "", UserName

        msg = "El Usuario existe Y no puede ser creado"
    else:
        msg += '\n Verifique que Su Nombre tenga dentro de 3 y 10 Caracteres'

    return False, msg, UserName


def SpaceRemover(DATA):
    """
    :param DATA: REVIEVES DATA FOR SPACES TRIM
    :return: TRIMMED DATA
    """
    return "".join([i for i in DATA.split(" ") if i])


async def return_msg(update: Update):
    """
    :param update: gets update status
    :return: returns message
    """
    query = update.callback_query
    if query:
        await query.answer()
        return query.data
    else:
        return update.message.text


async def emailValid(mail):
    """
    :param mail: REVIEVES EMAIL
    :return: EMAIL IF VALID OR BOOL FALSE IF NOT
    """
    spacelessEmail = SpaceRemover(mail)
    regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
    if re.fullmatch(regex, spacelessEmail):
        exists = DB_CONN.execute_select(
            f'SELECT email FROM user WHERE email= "{spacelessEmail}"')
        if not exists:
            print('Correo Valido')
            return spacelessEmail

    return False


async def passValidation(passW):
    regex = re.compile("^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$")
    if re.search(regex, passW):
        print('Clave Valida')
        return passW
    return False


async def geo_distance(lon1, lat1, lon2, lat2):
    """
        Parametros: lon1: float con las coordenadas de longitud del local
                    lat1: float con las coordenadas de latitud del local
                    lon2: float con las coordenadas de longitud de la ubicacion introducida por el usuario
                    lat2: float con las coordenadas de latitud de la ubicacion introducida por el usuario

        Descripcion: calcula la distancia entre 2 puntos de la tierra por medio de la formula de haversine

        Return: la distancia en kilometros (float)
    """
    from math import radians, cos, sin, asin, sqrt
    # convertir decimales a radianes
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # formula de haversine
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radio de la tierra en kilometros
    km = c * r
    return round(km, 1)


def emailInvoice(NombreArt: str, Img: str, IDFac, Precio, Ship, Disc, Total, Name, Desc):
    html = F"""
<!DOCTYPE html>
<html>
<head>
<title></title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="X-UA-Compatible" content="IE=edge" />
<style type="text/css">

/* RESET STYLES */

/* iOS BLUE LINKS *

/* MEDIA QUERIES */

/* ANDROID CENTER FIX */

</style>
</head>
<body style="margin: 0 !important; padding: 0 !important; background-color: #eeeeee;" bgcolor="#eeeeee">

<!-- HIDDEN PREHEADER TEXT -->
<div style="display: none; font-size: 1px; color: #fefefe; line-height: 1px; font-family: Open Sans, Helvetica, Arial, sans-serif; max-height: 0px; max-width: 0px; opacity: 0; overflow: hidden;">
ASTABOT ES EL MEJOR BOT DEL MUNDO !
</div>

<table border="0" cellpadding="0" cellspacing="0" width="100%">
    <tr>
        <td align="center" style="background-color: #eeeeee;" bgcolor="#eeeeee">
        <!--[if (gte mso 9)|(IE)]>
        <table align="center" border="0" cellspacing="0" cellpadding="0" width="600">
        <tr>
        <td align="center" valign="top" width="600">
        <![endif]-->
        <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width:600px;">
            <tr>
                <td align="center" valign="top" style="font-size:0; padding: 35px;" bgcolor="#3bb7ff">        
                <div style="display:inline-block; max-width:50%; min-width:100px; vertical-align:top; width:100%;">
                    <table align="left" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width:300px;">
                        <tr>
                            <td align="left" valign="top" style="font-family: Open Sans, Helvetica, Arial, sans-serif; font-size: 36px; font-weight: 800; line-height: 48px;" class="mobile-center">
                                <h1 style="font-size: 36px; font-weight: 800; margin: 0; color: #ffffff;"></h1>
                            </td>
                        </tr>
                    </table>
                </div>
                
                <div style="display:inline-block; max-width:50%; min-width:100px; vertical-align:top; width:100%;" class="mobile-hide">
                    <table align="left" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width:300px;">
                        <tr>
                           
                        </tr>
                    </table>
                </div>
                <!--[if (gte mso 9)|(IE)]>
                </td>
                </tr>
                </table>
                <![endif]-->
                </td>
            </tr>
            <tr>
                <td align="center" style="padding: 35px 35px 20px 35px; background-color: #ffffff;" bgcolor="#ffffff">
                <!--[if (gte mso 9)|(IE)]>
                <table align="center" border="0" cellspacing="0" cellpadding="0" width="600">
                <tr>
                <td align="center" valign="top" width="600">
                <![endif]-->
                <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width:600px;">
                    <tr>
                        <td align="center" style="font-family: Open Sans, Helvetica, Arial, sans-serif; font-size: 16px; font-weight: 400; line-height: 24px; padding-top: 25px;">
                             <h3 style="font-size: 20px; font-weight: 800; line-height: 36px; color: #333333; margin: 0;">
                               Parece que Alguien Estará Muy Contento con su Nuevo: """ + NombreArt + """
                            </h3>
                            <img src="  """ + Img + """  "  style="display: block; border: 0px;" /><br><!-- insertar img-->
                            <h2 style="font-size: 30px; font-weight: 800; line-height: 36px; color: #333333; margin: 0;">
                               Gracias Por Su Compra """ + Name + """
                            </h2>
                        </td>
                    </tr>
                    <tr>
                        <td align="left" style="font-family: Open Sans, Helvetica, Arial, sans-serif; font-size: 16px; font-weight: 400; line-height: 24px; padding-top: 10px;">
                            <p style="font-size: 16px; font-weight: 400; line-height: 24px; color: #777777;">
                               Descripción del Articulo: """ + Desc + """
                            </p>
                        </td>
                    </tr>
                    <tr>
                        <td align="left" style="padding-top: 20px;">
                            <table cellspacing="0" cellpadding="0" border="0" width="100%">
                                <tr>
                                    <td width="75%" align="left" bgcolor="#eeeeee" style="font-family: Open Sans, Helvetica, Arial, sans-serif; font-size: 16px; font-weight: 800; line-height: 24px; padding: 10px;">
                                        FACTURA 
                                    </td>
                                    <td width="25%" align="left" bgcolor="#eeeeee" style="font-family: Open Sans, Helvetica, Arial, sans-serif; font-size: 16px; font-weight: 800; line-height: 24px; padding: 10px;">
                                       COD# """ + IDFac + """
                                    </td>
                                </tr>
                                <tr>
                                    <td width="75%" align="left" style="font-family: Open Sans, Helvetica, Arial, sans-serif; font-size: 16px; font-weight: 400; line-height: 24px; padding: 15px 10px 5px 10px;">
                                        Articulo
                                    </td>
                                    <td width="25%" align="left" style="font-family: Open Sans, Helvetica, Arial, sans-serif; font-size: 16px; font-weight: 400; line-height: 24px; padding: 15px 10px 5px 10px;">
                                       USD$ """ + Precio + """
                                    </td>
                                </tr>
                                <tr>
                                    <td width="75%" align="left" style="font-family: Open Sans, Helvetica, Arial, sans-serif; font-size: 16px; font-weight: 400; line-height: 24px; padding: 5px 10px;">
                                        Envío
                                    </td>
                                    <td width="25%" align="left" style="font-family: Open Sans, Helvetica, Arial, sans-serif; font-size: 16px; font-weight: 400; line-height: 24px; padding: 5px 10px;">
                                        USD$ """ + Ship + """
                                    </td>
                                </tr>
                                <tr>
                                    <td width="75%" align="left" style="font-family: Open Sans, Helvetica, Arial, sans-serif; font-size: 16px; font-weight: 400; line-height: 24px; padding: 5px 10px;">
                                       Descuento %10
                                    </td>
                                    <td width="25%" align="left" style="font-family: Open Sans, Helvetica, Arial, sans-serif; font-size: 16px; font-weight: 400; line-height: 24px; padding: 5px 10px;">
                                        USD$ """ + Disc + """
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <tr>
                        <td align="left" style="padding-top: 20px;">
                            <table cellspacing="0" cellpadding="0" border="0" width="100%">
                                <tr>
                                    <td width="75%" align="left" style="font-family: Open Sans, Helvetica, Arial, sans-serif; font-size: 16px; font-weight: 800; line-height: 24px; padding: 10px; border-top: 3px solid #217aad; border-bottom: 3px solid #217aad;">
                                        TOTAL
                                    </td>
                                    <td width="25%" align="left" style="font-family: Open Sans, Helvetica, Arial, sans-serif; font-size: 16px; font-weight: 800; line-height: 24px; padding: 10px; border-top: 3px solid #217aad; border-bottom: 3px solid #217aad;">
                                        USD$ """ + Total + """
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
                <!--[if (gte mso 9)|(IE)]>
                </td>
                </tr>
                </table>
                <![endif]-->
                </td>
            </tr>
             <tr>
                
            </tr>
            <tr>
                <td align="center" style=" padding: 35px; background-color: #3bb7ff;" bgcolor="#3bb7ff">
                <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width:600px;">
                    <tr>
                        <td align="center" style="font-family: Open Sans, Helvetica, Arial, sans-serif; font-size: 16px; font-weight: 400; line-height: 24px; padding-top: 25px;">
                            <h2 style="font-size: 24px; font-weight: 800; line-height: 30px; color: #ffffff; margin: 0;">
                                ¡Recuerda Compartirnos!
                            </h2>
                        </td>
                    </tr>
                    <tr>
                        <td align="center" style="padding: 25px 0 15px 0;">
                            <table border="0" cellspacing="0" cellpadding="0">
                                <tr>
                                    <td align="center" style="border-radius: 5px;" bgcolor="#3bb7ff">
                                      <a href="https://web.telegram.org/k/#@AstaC_bot" target="_blank" style="font-size: 18px; font-family: Open Sans, Helvetica, Arial, sans-serif; color: #ffffff; text-decoration: none; border-radius: 5px; background-color: #217aad; padding: 15px 30px; border: 1px solid #3bb7ff; display: block;">Mugiwara Bot</a>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
     
                </td>
            </tr>
            <tr>
                <td align="center" style="padding: 35px; background-color: #ffffff;" bgcolor="#ffffff">

                <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width:600px;">
                    <tr>
                        <td align="center">
                            <img src="https://www.nicepng.com/png/full/781-7818059_monkey-d-luffy-one-piece-luffy-logo.png" width="47" height="47" style="display: block; border: 0px;"/>
                        </td>
                    </tr>
                    <tr>
                        <td align="center" style="font-family: Open Sans, Helvetica, Arial, sans-serif; font-size: 14px; font-weight: 400; line-height: 24px; padding: 5px 0 10px 0;">
                            <p style="font-size: 14px; font-weight: 800; line-height: 18px; color: #333333;">
                              <br>
                               EL ONE PIECE ES REAL
                            </p>
                        </td>
                    </tr>
                    <tr>
                        <td align="left" style="font-family: Open Sans, Helvetica, Arial, sans-serif; font-size: 14px; font-weight: 400; line-height: 24px;">
                            <p style="font-size: 14px; font-weight: 400; line-height: 20px; color: #777777;">
                               Recomendamos encarecidamente que veas One Piece Para que le llegues al flow <a href="https://www3.animeflv.to/ver/one-piece-tv-1" target="_blank" style="color: #777777;">Ver One Piece </a>.
                            </p>
                        </td>
                    </tr>
                </table>
      
                </td>
            </tr>
        </table>
      
        </td>
    </tr>
</table>
    <table border="0" cellpadding="0" cellspacing="0" width="100%">
        <tr>
            <td bgcolor="#ffffff" align="center">
    
                <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px;" >
                    <tr>
                        <td bgcolor="#ffffff" align="center" style="padding: 30px 30px 30px 30px; color: #666666; font-family: Helvetica, Arial, sans-serif; font-size: 14px; font-weight: 400; line-height: 18px;" >
                            <p style="margin: 0;">Este disparate fue hecho por alguien con mucho café en la cabeza, leer con discreción <a href="https://medlineplus.gov/spanish/caffeine.html" style="color: #5db3ec;">Tomás porfa, dejenos dormir xd</a></p>
                        </td>
                    </tr>
                </table>

            </td>
        </tr>
    </table>
</body>
</html>
"""
    return html


def CrearCuadro(Vercode: str):
    msg = """<!DOCTYPE html>
<html>
<head>
<title></title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="X-UA-Compatible" content="IE=edge" />
<style type="text/css">
    /* FONTS */
    @media screen {
        @font-face {
          font-family: 'Lato';
          font-style: normal;
          font-weight: 400;
          src: local('Lato Regular'), local('Lato-Regular'), url(https://fonts.gstatic.com/s/lato/v11/qIIYRU-oROkIk8vfvxw6QvesZW2xOQ-xsNqO47m55DA.woff) format('woff');
        }
        
        @font-face {
          font-family: 'Lato';
          font-style: normal;
          font-weight: 700;
          src: local('Lato Bold'), local('Lato-Bold'), url(https://fonts.gstatic.com/s/lato/v11/qdgUG4U09HnJwhYI-uK18wLUuEpTyoUstqEm5AMlJo4.woff) format('woff');
        }
        
        @font-face {
          font-family: 'Lato';
          font-style: italic;
          font-weight: 400;
          src: local('Lato Italic'), local('Lato-Italic'), url(https://fonts.gstatic.com/s/lato/v11/RYyZNoeFgb0l7W3Vu1aSWOvvDin1pK8aKteLpeZ5c0A.woff) format('woff');
        }
        
        @font-face {
          font-family: 'Lato';
          font-style: italic;
          font-weight: 700;
          src: local('Lato Bold Italic'), local('Lato-BoldItalic'), url(https://fonts.gstatic.com/s/lato/v11/HkF_qI1x_noxlxhrhMQYELO3LdcAZYWl9Si6vvxL-qU.woff) format('woff');
        }
    }
    
    /* CLIENT-SPECIFIC STYLES */
    body, table, td, a { -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }
    table, td { mso-table-lspace: 0pt; mso-table-rspace: 0pt; }
    img { -ms-interpolation-mode: bicubic; }

    /* RESET STYLES */
    img { border: 0; height: auto; line-height: 100%; outline: none; text-decoration: none; }
    table { border-collapse: collapse !important; }
    body { height: 100% !important; margin: 0 !important; padding: 0 !important; width: 100% !important; }

    /* iOS BLUE LINKS */
    a[x-apple-data-detectors] {
        color: inherit !important;
        text-decoration: none !important;
        font-size: inherit !important;
        font-family: inherit !important;
        font-weight: inherit !important;
        line-height: inherit !important;
    }
    
    /* MOBILE STYLES */
    @media screen and (max-width:600px){
        h1 {
            font-size: 32px !important;
            line-height: 32px !important;
        }
    }

    /* ANDROID CENTER FIX */
    div[style*="margin: 16px 0;"] { margin: 0 !important; }
</style>
</head>
<body style="background-color: #f4f4f4; margin: 0 !important; padding: 0 !important;">

<!-- HIDDEN PREHEADER TEXT -->
<div style="display: none; font-size: 1px; color: #fefefe; line-height: 1px; font-family: 'Lato', Helvetica, Arial, sans-serif; max-height: 0px; max-width: 0px; opacity: 0; overflow: hidden;">
    We're thrilled to have you here! Get ready to dive into your new account.
</div>

<table border="0" cellpadding="0" cellspacing="0" width="100%">
    <!-- LOGO -->
    <tr>
        <td bgcolor="#3bb7ff" align="center">
           
            <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px;" >
                <tr>
                    <td align="center" valign="top" style="padding: 40px 10px 40px 10px;">
                        <a href=" " target="_blank">
                  
                        </a>
                    </td>
                </tr>
            </table>
            <!--[if (gte mso 9)|(IE)]>
            </td>
            </tr>
            </table>
            <![endif]-->
        </td>
    </tr>
    <!-- HERO -->
    <tr>
        <td bgcolor="#3bb7ff" align="center" style="padding: 0px 10px 0px 10px;">
            <!--[if (gte mso 9)|(IE)]>
            <table align="center" border="0" cellspacing="0" cellpadding="0" width="600">
            <tr>
            <td align="center" valign="top" width="600">
            <![endif]-->
            <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px;" >
                <tr>
                    <td bgcolor="#ffffff" align="center" valign="top" style="padding: 40px 20px 20px 20px; border-radius: 4px 4px 0px 0px; color: #111111; font-family: 'Lato', Helvetica, Arial, sans-serif; font-size: 48px; font-weight: 400; letter-spacing: 4px; line-height: 48px;">
                      <h1 style="font-size: 48px; font-weight: 400; margin: 0;">WAOS !!!!</h1>
                    </td>
                </tr>
            </table>
            <!--[if (gte mso 9)|(IE)]>
            </td>
            </tr>
            </table>
            <![endif]-->
        </td> 
    </tr>
    <!-- COPY BLOCK -->
    <tr>
        <td bgcolor="#f4f4f4" align="center" style="padding: 0px 10px 0px 10px;">
            
            <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px;" >
              <!-- COPY -->
              <tr>
                <td bgcolor="#ffffff" align="left" style="padding: 20px 30px 40px 30px; color: #666666; font-family: 'Lato', Helvetica, Arial, sans-serif; font-size: 18px; font-weight: 400; line-height: 25px;" >
                  <p style="margin: 0; "> GRACIAS POR USAR ASTABOT, ESTMOS AGRADECIDOS XD</p>
                  <p style="margin: 0; "> SU CODIGO DE VERIFICACION ES EL SIGUIENTE</p> 
                  
                </td>
              </tr>
  
              <tr>
                <td bgcolor="#ffffff" align="left">
                  <table width="100%" border="0" cellspacing="0" cellpadding="0">
                    <tr>
                      <td bgcolor="#ffffff" align="center" style="padding: 20px 30px 60px 30px;">
                        <table border="0" cellspacing="0" cellpadding="0">
                          <tr>
                              <td align="center" style="border-radius: 3px;" bgcolor="#000000"><a href="https://youtu.be/LysXEC5cWl0?t=28" target="_blank" style="font-size: 20px; font-family: Helvetica, Arial, sans-serif; color: #ffffff; text-decoration: none; color: #ffffff; text-decoration: none; padding: 15px 25px; border-radius: 2px; border: 1px solid #000000; display: inline-block;">""" + Vercode + """</a></td>
                          </tr>
                        </table>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
              <!-- COPY -->
              <tr>
                <td bgcolor="#ffffff" align="left" style="padding: 0px 30px 0px 30px; color: #666666; font-family: 'Lato', Helvetica, Arial, sans-serif; font-size: 18px; font-weight: 400; line-height: 25px;" >
                  <p style="margin: 0;">Esperemos que el código funcione, porque si no te jodiste xd</p>
                </td>
              </tr>
              <!-- COPY -->
                <tr>
         
                </tr>
              <!-- COPY -->

              <!-- COPY -->
              <tr>
                <td bgcolor="#ffffff" align="left" style="padding: 0px 30px 40px 30px; border-radius: 0px 0px 4px 4px; color: #666666; font-family: 'Lato', Helvetica, Arial, sans-serif; font-size: 18px; font-weight: 400; line-height: 25px;" >
               <br>   <p style="margin: 0;">Con Mucho amor<br>AstoBot</p>
                </td>
              </tr>
            </table>
            <!--[if (gte mso 9)|(IE)]>
            </td>
            </tr>
            </table>
            <![endif]-->
        </td>
    </tr>

</table>
    
</body>
</html>"""
    return msg


# async def sendmail(to: str, subject: str, msg, msg2):
#     user = ENV_VARs.email
#     passW = ENV_VARs.passw
#
#     msg = "\r\n".join([
#                           f"From: {user}",
#                           f"To: {to}",
#                           f"Subject: {subject}",
#                           ""
#                       ] + msg).encode('utf-8')
#
#     with smtplib.SMTP('smtp.gmail.com:587') as server:
#         msg
#         server.ehlo()
#         server.starttls()
#         server.login(user, passW)
#         server.sendmail(user, to, msg)
#
#     return


async def Createinvoice(to: str, Lista):
    """
    :param to: param to mail reciever
    :param msg2: message on html formalt
    :return: retuns email send
    """

    message = MIMEMultipart("alternative")
    user = ENV_VARs.email
    passW = ENV_VARs.passw

    message["Subject"] = "RECIBO DE COMPRA"
    message["From"] = user
    message["To"] = to

    text = """\
    Gracias por Suscribirte a Astabot,
    Este Correo no pretende ser respondido"""

    for elementos in Lista:
        html = emailInvoice(elementos[0], elementos[1], str(elementos[2]), str(elementos[3]), str(elementos[4]),
                            str(elementos[5]), str(elementos[6]), elementos[7], elementos[8])
        # NombreArt: , Img: ,          IDFac: ,  Precio: ,     Ship: ,     Disc: ,       Total:
    # html = msg2
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    message.attach(part1)
    message.attach(part2)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(user, passW)

        server.sendmail(
            user, to, message.as_string()
        )


async def sendHtmlMail(to: str, msg2: str):
    """
    :param to: param to mail reciever
    :param msg2: message on html formalt
    :return: retuns email send
    """

    message = MIMEMultipart("alternative")
    user = ENV_VARs.email
    passW = ENV_VARs.passw

    message["Subject"] = "CODIGO DE CONFIRMACION"
    message["From"] = user
    message["To"] = to

    text = """\
    Gracias por Suscribirte a Astabot,
    Este Correo no pretende ser respondido"""

    html = CrearCuadro(msg2)

    # html = msg2
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    message.attach(part1)
    message.attach(part2)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(user, passW)

        server.sendmail(
            user, to, message.as_string()
        )


async def randomVercode():
    """
    :return: creates random comfirmation code
    """
    result_str = ''.join(random.choice(string.ascii_letters) for i in range(5))
    print(result_str)
    return result_str


async def num_valid(num):
    """
    :param num: RECIEVES NUMBER TO SEE IF NUMBER
    :return:
    """
    if num <= 0:
        return "ERROR: EL NUMERO DEBE SER MAYOR A CERO"
    else:
        return "TRUE"


async def ValidateUrl(url):
    """
    This function is in charge of validating if a text string is a url and if it is an image.
    param: url: Link of image.
    return: resp (bool,string)
    """
    format = [".jpg", ".png", ".jpeg", ".jpge", ".tiff"]

    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    if any(x in url for x in format):
        resp = re.match(regex, url) is not None
    else:
        resp = "ERROR: El link que introduciste no esta dentro de los formatos aceptados, intentalo nuevamente."
    return resp
