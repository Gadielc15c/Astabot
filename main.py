import logging
import prettytable as pt
import telegram.constants
import DB_CONN
import ENV_VARs as TOKEN
from telegram import __version__ as TG_VER, ReplyKeyboardRemove, ForceReply, ReplyKeyboardMarkup, KeyboardButton, \
    WebAppInfo
import FUNCTIONS_LIB

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
START_ROUTES = range(1)

STORE_START = range(2)
COMPRA, BUTTON_HANDLER, END_ROUTES, SIGNUP, THREE, FOUR, \
    TEMP_USER, TEMP_MAIL, TEMP_PASS, EMAIL_CONFIRM, LOGIN, \
    LOGIN_PASS, LOGIN_CONFIRM, SIGNUP_ROUT, DETALLE = range(15)

# VARS FOR SIGN UP ROUTS
username_var = "user_data1"
email_var = "user_mail"
pass_var = "user_pass"
ver_code = "Vercode"

# VARS FOR LOGIN
username_login = "login_username"
username_pass = "login_pass"

# VARS FOR PRODUCT HANDLE
productud = "product_id"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send message on `/start`."""
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.first_name)

    keyboard = [
        [
            InlineKeyboardButton("INICIAR SESION 🔐", callback_data=str(LOGIN)),
            InlineKeyboardButton("SALIR 🏳️‍🌈", callback_data=str(END_ROUTES)),
        ],

        [InlineKeyboardButton("Crear Cuenta", callback_data=str(BUTTON_HANDLER)),
         ],

    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text='\n\t HOLAAAAA!!')

    await update.message.reply_text("\nSoy AstaBot 🤖\n¿En que Te Puedo Ayudar? 🤔",
                                    reply_markup=reply_markup)

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
    DATA = await FUNCTIONS_LIB.return_msg(update)

    a = DB_CONN.execute_select('SELECT * FROM products')
    # for productos in a:
    #     msg += f"{productos[1]} - <b>CODIGO: {productos[0]}</b>\n"
    #     msg2+= f"\n``` {productos[1]}     CODIGO: {productos[0]} ```\n"

    table = pt.PrettyTable(['PRODUCTOS', 'CODIGOS'])
    table.align['PRODUCTOS'] = 'l'
    table.align['CODIGOS'] = 'r'

    for productos in a:
        table.add_row([productos[1], f'{productos[0]}'])

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Nuestros Productos Actuales son: ")

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f'<pre>{table}</pre>',
        parse_mode=telegram.constants.ParseMode.HTML)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Ingrese el Codigo del Producto que desea Visualizar",
        parse_mode=telegram.constants.ParseMode.HTML)
    return DETALLE


async def detallador(update: Update, context: CallbackContext):
    DATA = await FUNCTIONS_LIB.return_msg(update)
    productud = DB_CONN.execute_select(f"SELECT * FROM products WHERE Idproducts ={DATA}")
    if productud:
        for detalle in productud:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f'ARTICULO: {detalle[1]}')
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=detalle[3])
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Precio: {detalle[2]}US$')
            keyboard = [
                [
                    InlineKeyboardButton("Comprar", callback_data=str(COMPRA)),
                    InlineKeyboardButton("Ver Detalles", callback_data=str(DETALLE))
                ],

            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text=f'🤖ID ARTICULO: {detalle[0]}\n',
                                           reply_markup=reply_markup)
            return STORE_START
    else:
        await context.bot.send_photo(chat_id=update.effective_chat.id,
                                     photo="https://i.postimg.cc/pXXcy9rS/5d055c32-1a19-452e-aaae-92276049e27e.jpg")
        return DETALLE


async def descripcion(update: Update, context: CallbackContext):
    id = context.user_data[productud]
    product = DB_CONN.execute_select(f"SELECT * FROM products where idproducts= '{id}'")
    for detalle in product:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f'ARTICULO: {detalle[1]}')
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=detalle[3])
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Precio: {detalle[2]}US$')
        keyboard = [
            [
                InlineKeyboardButton("Comprar", callback_data=str(COMPRA)),
                InlineKeyboardButton("Ver Detalles", callback_data=str(THREE))
            ],

        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=f'🤖ID ARTICULO: {detalle[0]}\n',
                                       reply_markup=reply_markup)
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
    DATA = await FUNCTIONS_LIB.return_msg(update)
    status, msg, Username = await FUNCTIONS_LIB.userNameProcesor(DATA)
    if status:
        context.user_data[username_var] = Username
        await context.bot.send_message(chat_id=update.effective_chat.id, text='PORFA INGRESE UN CORREO\n')
        return TEMP_MAIL

    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=msg)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Inserte El Nombre De Usuario")
        return TEMP_USER


async def emailread(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    DATA = await FUNCTIONS_LIB.return_msg(update)
    emailVer = await FUNCTIONS_LIB.emailValid(DATA)
    if emailVer:
        context.user_data[email_var] = DATA
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Porfavor Inserte una Contraseña\n')
        return TEMP_PASS
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='⚠️CORREO INVALIDO⚠️\n ')
        await context.bot.send_message(chat_id=update.effective_chat.id, text='PORFA INGRESE UN CORREO VÁLIDO\n ')
        return TEMP_MAIL


async def passreadl(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    DATA = await FUNCTIONS_LIB.return_msg(update)
    PassValidate = await FUNCTIONS_LIB.passValidation(DATA)
    if PassValidate:
        username = context.user_data[username_var]
        email = context.user_data[email_var]
        context.user_data[pass_var] = DATA
        VerCode = await FUNCTIONS_LIB.randomVercode()
        context.user_data[ver_code] = VerCode
        DB_CONN.execute_sql(f'INSERT INTO user (username,email,pass) VALUES ("{username}","{email}","{DATA}")')
        await FUNCTIONS_LIB.sendHtmlMail(email, VerCode)
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text='😍👁️ GENIAL SU CUENTA SE HA CREADO CON EXITO! \n'
                                            ' ENVIAMOS UN CORREO A TU EMAIL PARA QUE VERIFIQUES TU CUENTA \n AVECES EL CORREO PUEDE APARECER EN SPAM👍🏿')
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text='DIGITE SU NUMERO DE CONFIRM \n')
        return EMAIL_CONFIRM

    else:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text='⚠️ PORFA INGRESE UNA CONTRASEÑA VÁLIDA ⚠️ \n ')
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text='POR FAVOR INGRESE UNA CONTRASEÑA VÁLIDA ESTA DEBE SER MAYOR A 6 DIGITOS '
                                            'y TENER ALMENOS UNA LETRA MAYUSCULA, UN NUMERO Y UN SIMBOLO ESPECIAL\n ')
        return TEMP_PASS


async def emailConfirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    DATA = await FUNCTIONS_LIB.return_msg(update)
    verc = context.user_data[ver_code]
    if DATA == verc:
        username = context.user_data[username_var]
        DB_CONN.execute_sql(f'UPDATE user SET state=1 WHERE username="{username}"')
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text='🎉🍾🎊FELICIDADES!!🎉🍾🎊\n Su cuenta se ha verificado con Exito')
        return LOGIN
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text='EL CODIGO NO HA SIDO VERIFICADO CORRECTAMENTE, PORFAVOR VUELVA A '
                                            'INTENTARLO\n')
        return EMAIL_CONFIRM


async def Login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    DATA = await FUNCTIONS_LIB.return_msg(update)

    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text='🤖 |LOGIN| \n Porfavor Digite su Nombre de Usuario')

    return LOGIN_PASS


async def LoginPass(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    DATA = await FUNCTIONS_LIB.return_msg(update)
    context.user_data[username_login] = DATA

    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text='🤖 |LOGIN| \n Porfavor Digite su Contraseña')
    return LOGIN_CONFIRM


async def LoginConfirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global variable
    DATA = await FUNCTIONS_LIB.return_msg(update)
    context.user_data[username_pass] = DATA
    UserLogin = context.user_data[username_login]
    login = DB_CONN.execute_select(f'SELECT * FROM user WHERE username = "{UserLogin}" AND pass ="{DATA}"')
    if login:

        for estado in login:
            variable = estado[4]
        if variable == "1":
            print("mamaguevo")
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text='🤖 |TIENDA| \n')
            """Send message on `/start`."""
            user = update.message.from_user
            # saludo = "Hola " + user.first_name + " Bienvenido"
            logger.info("User %s Entró a la tienda", user.first_name)

            keyboard = [
                [
                    InlineKeyboardButton("Comprar", callback_data=str(COMPRA)),
                ], [
                    InlineKeyboardButton("Historico de Pedidos", callback_data=str(THREE)),

                ],

                [InlineKeyboardButton("Salir", callback_data=str(END_ROUTES)),
                 ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text='🤖 ENTRE!\n',
                                           reply_markup=reply_markup)

            return STORE_START
        elif variable == "4":
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text='🤖 |ADMIN| \n')
            """Send message on `/start`."""
            user = update.message.from_user
            # saludo = "Hola " + user.first_name + " Bienvenido"
            logger.info("User %s Entró a la tienda", user.first_name)

            keyboard = [
                [
                    InlineKeyboardButton("INVENTARIO", callback_data=str(STORE_START)),
                ], [
                    InlineKeyboardButton("AGREGAR PRODUCTOS", callback_data=str(THREE)),

                ],
                [
                    InlineKeyboardButton("VER SEGMENTACION DE USUARIOS", callback_data=str(THREE)),

                ], [
                    InlineKeyboardButton("VER ESTADISTICA DE VENTAS", callback_data=str(THREE)),

                ],
                [InlineKeyboardButton("Salir", callback_data=str(END_ROUTES)),
                 ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text='🤖 ENTRE!\n',
                                           reply_markup=reply_markup)

            return STORE_START
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text='🤖 |LOGIN| Y ESA BASURA XDDDD\n')

    return LOGIN


async def storeStart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    DATA = await FUNCTIONS_LIB.return_msg(update)
    context.user_data[username_pass] = DATA

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
    await query.edit_message_text(text="Lo suponia...🤨 🏳️‍🌈🏳️‍🌈👁")
    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    application = Application.builder().token(TOKEN.CONN_TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            START_ROUTES: [
                CallbackQueryHandler(Login, pattern="^" + str(LOGIN) + "$"),
                CallbackQueryHandler(button_click_handler, pattern="^" + str(BUTTON_HANDLER) + "$"),
                CallbackQueryHandler(end, pattern="^" + str(END_ROUTES) + "$"),

            ],
            STORE_START: [
                CallbackQueryHandler(Compra, pattern="^" + str(COMPRA) + "$"),
                CallbackQueryHandler(descripcion, pattern="^" + str(DETALLE) + "$"),
                CallbackQueryHandler(button_click_handler, pattern="^" + str(BUTTON_HANDLER) + "$"),

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
            LOGIN: [
                MessageHandler(filters.TEXT & (~filters.COMMAND), Login),
            ],
            LOGIN_PASS: [
                MessageHandler(filters.TEXT & (~filters.COMMAND), LoginPass),
            ],
            DETALLE: [
                MessageHandler(filters.TEXT & (~filters.COMMAND), detallador),
            ],
            LOGIN_CONFIRM: [
                MessageHandler(filters.TEXT & (~filters.COMMAND), LoginConfirm),
            ],

        },
        fallbacks=[CommandHandler("start", start)],
    )

    # Add ConversationHandler to application that will be used for handling updates
    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    # lista=DB_CONN.execute_select('SELECT * FROM products')
    #
    #
    # a =   FUNCTIONS_LIB.ProductsListProcessor(lista)

    main()
