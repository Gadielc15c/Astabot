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


def userNameProcesor(userN):
    sizeOfName = len(userN)
    # TODO: MAKE DB SELECT QUERY TO GET DATA IN ORDER TO KNOW IF ITS ALREADY THERE

    if 3 <= sizeOfName <= 10:
        UserName = SpaceRemover(userN)
        return UserName

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


def emailValid(mail):
    # TODO: MAKE DB SELECT QUERY TO GET DATA IN ORDER TO KNOW IF ITS ALREADY THERE

    # Function thtat recieves an email and sees if is valid or not
    # @PARAM
    # EMAIL REVIEVES EMAIL
    # @RETUNS
    # RETURNS EMAIL IF VALID OR BOOL FALSE IF NOT
    spacelessEmail = SpaceRemover(mail)
    regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')

    if re.fullmatch(regex, spacelessEmail):
        print('Correo Valido')
        return spacelessEmail
    return False


def passValidation(passW):
    regex = re.compile("^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$")
    if re.search(regex, passW):
        print('Clave Valida')
        return passW
    return False

def CrearCuadro(Vercode):
    msg="""\<div class="Container">
   <h2>"""+Vercode+"""</h2>
</div>

<style>
.Container {
    width: 30vh;
    height: 20vh;
  box-shadow: 0px 6px 13px 6px rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>"""
    return msg
async def sendmail(to: str, subject: str, msg,msg2):
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
def sendHtmlMail(to: str, subject: str,msg2):
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = ENV_VARs.email
    message["To"] = to

    text = """\
    Gracias por Suscribirte a Astabot,
    Este Correo no pretende ser respondido"""
    html = msg2
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    message.attach(part1)
    message.attach(part2)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 587, context=context) as server:
        server.login(ENV_VARs.email, ENV_VARs.passw)
        server.sendmail(
            ENV_VARs.email, subject, message.as_string()
        )
def randomVercode():
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
