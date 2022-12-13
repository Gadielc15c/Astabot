import logging

import DB_CONN
import ENV_VARs as TOKEN
from telegram import __version__ as TG_VER, ReplyKeyboardRemove, ForceReply

import funct

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler, MessageHandler, filters, CallbackContext,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)
START_ROUTES, END_ROUTES, SIGNUP_ROUT = range(3)
COMPRA, BUTTON_HANDLER, SIGNUP, THREE, FOUR, TEMP_USER, TEMP_MAIL, TEMP_PASS, EMAIL_CONFIRM = range(9)

username_var = "user_data1"
email_var = "user_mail"
pass_var = "user_pass"
ver_code="Vercode"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send message on `/start`."""
    user = update.message.from_user
    saludo = "Hola " + user.first_name + " Bienvenido"
    logger.info("User %s started the conversation.", user.first_name)

    keyboard = [
        [
            InlineKeyboardButton("Comprar", callback_data=str(COMPRA)),
            InlineKeyboardButton("SALIR", callback_data=str(THREE)),
        ],

        [InlineKeyboardButton("Crear Cuenta", callback_data=str(BUTTON_HANDLER)),
         ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(saludo, reply_markup=reply_markup)

    return START_ROUTES


async def start_over(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Prompt same text & keyboard as `start` does but not as new message"""
    # Get CallbackQuery from Update
    query = update.callback_query
    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton("1", callback_data=str(COMPRA)),
            InlineKeyboardButton("2", callback_data=str(BUTTON_HANDLER)),

        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Instead of sending a new message, edit the message that
    # originated the CallbackQuery. This gives the feeling of an
    # interactive menu.

    await query.edit_message_text(text="Start handler, Choose a route", reply_markup=reply_markup)
    return START_ROUTES


async def Compra(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    keyboard = [
        [
            InlineKeyboardButton("Iniciar Sesion", callback_data=str(FOUR)),
        ],
        [
            InlineKeyboardButton("Crear Cuenta", callback_data=str(BUTTON_HANDLER)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text="Primero Inicia Sesion o Crea una Cuenta!", reply_markup=reply_markup
    )

    return START_ROUTES


async def button_click_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await  query.answer(f'Entendido {query.data} Crearemos tu cuenta')
    if query.data == str(BUTTON_HANDLER):
        await query.edit_message_text(f'BIEN CREEEMOS SU CUENTA')
        await context.bot.send_message(chat_id=update.effective_chat.id, text='PORFA INGRESE UN NOMBRE DE USUARIO\n ')
        # await singUp(update, context)
    return TEMP_USER


async def singUp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    DATA = await funct.return_msg(update)
    username = funct.userNameProcesor(DATA)  # RECIBO EL USER NAME Y LO LIMPIO
    if username:
        context.user_data[username_var] = username
        await context.bot.send_message(chat_id=update.effective_chat.id, text='PORFA INGRESE UN CORREOA\n')
        return TEMP_MAIL

    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='⚠️ NOMBRE DE USUARIO INCORECTO ⚠️\n '
                                                                              'Verifique que Su Nombre tenga dentro de'
                                                                              ' 3 y 10 Caracteres')
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=' PORFA INGRESE UN NOMBRE DE USUARIO VALIDO   \n ')
        return TEMP_USER


async def emailread(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    DATA = await funct.return_msg(update)
    emailVer = funct.emailValid(DATA)
    if emailVer:
        context.user_data[email_var] = DATA
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Porfavor Inserte una Contraseña\n')
        return TEMP_PASS
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='⚠️CORREO INVALIDO⚠️\n ')

        await context.bot.send_message(chat_id=update.effective_chat.id, text='PORFA INGRESE UN CORREO VÁLIDO\n ')
        return TEMP_MAIL


async def passreadl(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    DATA = await funct.return_msg(update)
    PassValidate = funct.passValidation(DATA)
    if PassValidate:
        username = context.user_data[username_var]
        email = context.user_data[email_var]
        context.user_data[pass_var] = DATA
        VerCode=funct.randomVercode()
        context.user_data[ver_code]=VerCode
        msg=funct.CrearCuadro(VerCode)
        DB_CONN.execute_sql(f'INSERT INTO user (username,email,pass) VALUES ("{username}","{email}","{DATA}")')
        await funct.sendHtmlMail(email,"asunto",msg)
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text='😍👁️ GENIAL SU CUENTA SE HA CREADO CON EXITO! \n'
                                            ' ENVIAMOS UN CORREO A TU EMAIL PARA QUE VERIFIQUES TU CUENTA 👍🏿')
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text='DIGITE SU NUMERO DE CONFIRM \n')
        return EMAIL_CONFIRM

    else:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text='⚠️ PORFA INGRESE UNA CONTRASEÑA VÁLIDA ⚠️ \n ')
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text='POR FAVOR INGRESE UNA CONTRASEÑA VÁLIDA ESTA DEBE SER MAYOR A 6 DIGITOS '
                                            'y TENER ALMENOS UNA LETRA MAYUSCULA Y UN SIMBOLO ESPECIAL\n ')
        return TEMP_PASS


async def emailConfirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    DATA = await funct.return_msg(update)


    #if True:
   #     return "Otra ruta"
    #else:
     #  await context.bot.send_message(chat_id=update.effective_chat.id,
       #                                text='EL CODIGO NO HA SIDO VERIFICADO CORRECTAMENTE, PORFAVOR VUELVA A INTENTARLO MMG\n')
      #  return EMAIL_CONFIRM

async def three(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show new choice of buttons. This is the end point of the conversation."""
    query = update.callback_query
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton("No, Reanudemos", callback_data=str(COMPRA)),
            InlineKeyboardButton("SI XD que cansando es.", callback_data=str(BUTTON_HANDLER)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="SEGURO QUE QUIERES CERRAR LA SESION?", reply_markup=reply_markup
    )
    # Transfer to conversation state `SECOND`
    return END_ROUTES


async def four(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    await query.answer()

    keyboard = [
        [
            InlineKeyboardButton("2", callback_data=str(BUTTON_HANDLER)),
            InlineKeyboardButton("3", callback_data=str(THREE)),
            InlineKeyboardButton("SEXO", callback_data=str(BUTTON_HANDLER)),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="Fourth CallbackQueryHandler, Choose a route", reply_markup=reply_markup
    )
    return START_ROUTES


async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Returns `ConversationHandler.END`, which tells the
    ConversationHandler that the conversation is over.
    """
    query = update.callback_query
    await query.answer()
    print(query.data)
    if query.data == COMPRA:
        pass
    await query.edit_message_text(text="Sa mmg")
    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN.CONN_TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            START_ROUTES: [
                CallbackQueryHandler(Compra, pattern="^" + str(COMPRA) + "$"),
                CallbackQueryHandler(button_click_handler, pattern="^" + str(BUTTON_HANDLER) + "$"),
                CallbackQueryHandler(three, pattern="^" + str(THREE) + "$"),
                CallbackQueryHandler(four, pattern="^" + str(FOUR) + "$"),
            ],

            SIGNUP_ROUT: [
                CallbackQueryHandler(emailread, pattern="^" + str(SIGNUP) + "$"),
            ],
            TEMP_USER: [
                MessageHandler(filters.TEXT & (~filters.COMMAND), singUp),
            ],
            TEMP_MAIL: [
                MessageHandler(filters.TEXT & (~filters.COMMAND), emailread),
            ],
            TEMP_PASS: [
                MessageHandler(filters.TEXT & (~filters.COMMAND), passreadl),
            ],
            EMAIL_CONFIRM: [
                MessageHandler(filters.TEXT & (~filters.COMMAND), emailConfirm),
            ],
            END_ROUTES: [
                CallbackQueryHandler(start_over, pattern="^" + str(COMPRA) + "$"),
                CallbackQueryHandler(end, pattern="^" + str(BUTTON_HANDLER) + "$"),
            ],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    # Add ConversationHandler to application that will be used for handling updates
    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
