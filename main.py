import logging
import ENV_VARs as TOKEN
from telegram import __version__ as TG_VER, ReplyKeyboardRemove, ForceReply
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
#-----------------------------------------------------------------------------------------------------------------------

# Stages
START_ROUTES, END_ROUTES, SINGUP_ROUT = range(3)
# Callback data
COMPRA, BUTTON_HANDLER, SINGUP, THREE, FOUR, TEMP_TEXTO = range(6)
#0          1              2       3       4        5
#-----------------------------------------------------------------------------------------------------------------------

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

        [InlineKeyboardButton("SIN PROGRAMAR", callback_data=str(BUTTON_HANDLER)),
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
    # shows a small notification inside chat
    await  query.answer(f'Entendido {query.data} Crearemos tu cuenta')

    if query.data == str(BUTTON_HANDLER):
        await query.edit_message_text(f'BIEN CREEEMOS SU CUENTA')
        await context.bot.send_message(chat_id=update.effective_chat.id,text='PORFA INGRESE UN NOMBRE DE USUARIO\n ')
        # await singUp(update, context)
    return TEMP_TEXTO


async def singUp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    ''' The user's reply to the name prompt comes here  '''
    query = update.callback_query
    # querydata = query.data
    # context.user_data["key"] = querydata
    # logger.info(querydata)
    print(query)

    # if query.data == str(BUTTON_HANDLER):
    await update.callback_query.message.edit_text(f'BIEN CREEEMOS SU CUENTA')
    # await query.edit_message_text
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text='PORFA INGRESE UN CORREOA\n', reply_markup=ForceReply())
    # DATA = update.message.text
    # saves the name
    # context.user_data[str(BUTTON_HANDLER)] = DATA
    # await context.message.reply_text(f'Your name is saved as ')
    # await update.message.reply_text(f'Your name is saved as {DATA[:100]}')

    # ends this particular conversation flow
    return TEMP_TEXTO


async def passread(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    ''' The user's reply to the name prompt comes here  '''
    print("tototico")
    query = update.callback_query
    print(query)
    if query.data == str(BUTTON_HANDLER):
        await query.edit_message_text(f'BIEN CREEEMOS SU CUENTA')
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text='PORFA INGRESE  UNA CONTRASEÑA\n', reply_markup=ForceReply())
    # DATA = update.message.text
    # saves the name
    # context.user_data[str(BUTTON_HANDLER)] = DATA
    # await context.message.reply_text(f'Your name is saved as ')
    # await update.message.reply_text(f'Your name is saved as {DATA[:100]}')

    # ends this particular conversation flow
    return TEMP_TEXTO


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
#--------------------------------------------------------------------------------------------------------------

        entry_points=[CommandHandler("start", start)],
        states={
            START_ROUTES: [
                CallbackQueryHandler(Compra, pattern="^" + str(COMPRA) + "$"),
                CallbackQueryHandler(button_click_handler, pattern="^" + str(BUTTON_HANDLER) + "$"),
                CallbackQueryHandler(three, pattern="^" + str(THREE) + "$"),
                CallbackQueryHandler(four, pattern="^" + str(FOUR) + "$"),
            ],

            SINGUP_ROUT: [
                CallbackQueryHandler(passread, pattern="^" + str(SINGUP) + "$"),
            ],

            TEMP_TEXTO: [
                MessageHandler(filters.TEXT & (~filters.COMMAND), singUp),
                MessageHandler(filters.TEXT & (~filters.COMMAND), passread),
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
