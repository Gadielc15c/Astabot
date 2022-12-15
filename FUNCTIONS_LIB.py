import logging
import re
import smtplib
import random
import ssl
import string
import telegram
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

logger = logging.getLogger(__name__)


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

    return False

def SpaceRemover(DATA):
    return "".join([i for i in DATA.split(" ") if i])


async def return_msg(update: Update):
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
    return c * r


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


async def sendmail(to: str, subject: str, msg, msg2):
    user = ENV_VARs.email
    passW = ENV_VARs.passw

    msg = "\r\n".join([
                          f"From: {user}",
                          f"To: {to}",
                          f"Subject: {subject}",
                          ""
                      ] + msg).encode('utf-8')

    with smtplib.SMTP('smtp.gmail.com:587') as server:
        msg
        server.ehlo()
        server.starttls()
        server.login(user, passW)
        server.sendmail(user, to, msg)

    return


async def sendHtmlMail(to: str, msg2: str):
    """

    :param to:
    :param msg2:
    :return:
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
    # With combination of lower and upper case
    result_str = ''.join(random.choice(string.ascii_letters) for i in range(5))
    # print random string
    print(result_str)
    return result_str


async def edit_message(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str,
                       reply_markup: InlineKeyboardMarkup = None, msg_content: telegram.Message = None):
    query = update.callback_query
    parse = 'markdown'

    if query:
        await query.answer()
        if reply_markup:
            msg = await query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=parse)
        else:
            msg = await query.edit_message_text(text=text, parse_mode=parse)
    elif msg_content:
        if reply_markup:
            msg = await context.bot.edit_message_text(chat_id=msg_content.chat_id,
                                                      message_id=msg_content.message_id,
                                                      text=text,
                                                      reply_markup=reply_markup,
                                                      parse_mode=parse)
        else:
            msg = await context.bot.edit_message_text(chat_id=msg_content.chat_id,
                                                      message_id=msg_content.message_id,
                                                      text=text,
                                                      parse_mode=parse)
    else:
        if reply_markup:
            msg = await update.message.reply_text(text=text, reply_markup=reply_markup,
                                                  parse_mode=parse)
        else:
            msg = await update.message.reply_text(text=text,
                                                  parse_mode=parse)

    return msg
