import logging
import prettytable as pt
import telegram.constants
import DB_CONN
import ENV_VARs as TOKEN
from telegram import __version__ as TG_VER, ReplyKeyboardRemove, ForceReply, ReplyKeyboardMarkup, KeyboardButton, \
    WebAppInfo, LabeledPrice
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

STORE_START, UPDATE_PRODUCTS, PAYMENTS_START = range(4)

COMPRA, BUTTON_HANDLER, END_ROUTES, SIGNUP, SHIPPING_LESS, FOUR, \
TEMP_USER, TEMP_MAIL, TEMP_PASS, EMAIL_CONFIRM, LOGIN, \
LOGIN_PASS, LOGIN_CONFIRM, SIGNUP_ROUT, PRODUCT, PRICE_PRODUCT, \
STOCK_PRODUCT, U_NAME, U_STOCK, U_CATEGORY, U_DESCRIPTION,\
U_PRICE, U_IMG, DETALLE, TEMP_COMPRA, THREE, TEMP_PAGO, I_PRICE,\
I_DESCRIPTION,I_CATEGORY, I_IMG, I_STOCK = range(32)

# --------------------------------------------------#
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
product_name="product"
product_price="0.00"
product_img="https//:image.com"
product_desc="description"
product_category="category"
product_stock="0.00"
var_up="attribute_to_update"


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
                    InlineKeyboardButton("Comprar", callback_data=str(PAYMENTS_START)),
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
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Dime perdón si quieres avanzar 🤣🤣🤣")
        return TEMP_COMPRA


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
                InlineKeyboardButton("Ver Detalles", callback_data=str(SHIPPING_LESS))
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
                                            'y TENER ALMENOS UNA LETRA MAYUSCULA,UN NUMERO Y UN SIMBOLO ESPECIAL\n ')
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

#----------INSERT DE NOMBRE------------#
async def InsertProductName(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,text="Introduce el nombre del producto, miamor")
    return PRODUCT


async def SaveProductN(update: Update, context: ContextTypes.DEFAULT_TYPE):
    DATA = await FUNCTIONS_LIB.return_msg(update)
    # print("El producto elegido es ",DATA)
    context.user_data[product_name] = DATA
    exists = DB_CONN.execute_select(f'SELECT nameproducts FROM products WHERE nameproducts="{DATA}"')
    if exists:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="El producto que introdujo ya existe, Que desea Actualizar?")
        keyboard = [
            [
                InlineKeyboardButton("NOMBRE", callback_data=str(U_NAME)),
            ], [
                InlineKeyboardButton("DESCRIPCION", callback_data=str(U_DESCRIPTION)),

            ],
            [
                InlineKeyboardButton("PRECIO", callback_data=str(U_PRICE)),

            ],
            [
                InlineKeyboardButton("IMAGEN", callback_data=str(U_IMG)),

            ],
            [
                InlineKeyboardButton("CATEGORIA", callback_data=str(U_CATEGORY)),

            ],
            [InlineKeyboardButton("NADA, GRACIAS.", callback_data=str(END_ROUTES)),
             ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text='ELIGE UNA OPCION!\n',
                                       reply_markup=reply_markup)
        return UPDATE_PRODUCTS
    else:
        # Pedimos descripcion, precio, imagen etc.
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Crearemos un producto nuevo...preparate")

    return SHIPPING_LESS



async def InsertDescription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    DATA=await FUNCTIONS_LIB.return_msg(update)
    context.user_data[product_desc]=DATA
    await context.bot.send_message(chat_id=update.effective_chat.id,text="Introduce su categoria.")
    return I_CATEGORY

async def InsertCategory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    DATA=await FUNCTIONS_LIB.return_msg(update)
    context.user_data[product_category]=DATA
    await context.bot.send_message(chat_id=update.effective_chat.id,text="Cual es el precio?")
    return I_PRICE
async def InsertPrice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    DATA=await FUNCTIONS_LIB.return_msg(update)

    try:
        price = float(DATA)
        msg = await FUNCTIONS_LIB.num_valid(price)
    except:
        msg = "Estas bien?? Te pedi un dato numerico. Escribelo denuevo."
    if msg == "TRUE":
        context.user_data[product_price] = DATA
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Necesito una imagen. Introduce el link de la imagen que quieras ponerle."
                                            "\nSi no tienes una imagen escribe (NO)")
        return I_IMG
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=msg)
        return I_PRICE
async def InsertIMG(update: Update, context: ContextTypes.DEFAULT_TYPE):
    DATA=await FUNCTIONS_LIB.return_msg(update)


    if DATA.lower()!="no":

        resp= await FUNCTIONS_LIB.ValidateUrl(DATA)
        if resp:
            context.user_data[product_img]=DATA
            await context.bot.send_message(chat_id=update.effective_chat.id,text="Ahora dime la cantidad o stock que quieres ingresar.")
            return I_STOCK
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text="Ese link que ingresaste no es valido, prueba con otro")
            return I_IMG
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Oskers.\nPor ultimo necesito que me digas que cantidad deseas ingresar de este producto bro.")
        context.user_data[product_img]="https://filestore.community.support.microsoft.com/api/images/ext?url=https%3A%2F%2Fanswersstaticfilecdnv2.azureedge.net%2Fstatic%2Fimages%2Fimage-not-found.jpg"
        return I_STOCK

async def InsertStock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    DATA=await FUNCTIONS_LIB.return_msg(update)

    try:
        stock= float(DATA)
        msg = await FUNCTIONS_LIB.num_valid(stock)
    except:
        msg = "Te crees gracioso? introduce un dato NUMERICO."
    if msg == "TRUE":
        context.user_data[product_stock] = DATA
        DB_CONN.execute_sql(f'INSERT INTO products(nameproducts,price,imgurl,descproducts,stock,category) '
                            f'VALUES("{context.user_data[product_name]}","{context.user_data[product_price]}",'
                            f'"{context.user_data[product_img]}","{context.user_data[product_desc]}","{context.user_data[product_stock]}"'
                            f',"{context.user_data[product_category]}")')
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Excelente, Te amo.\n\nEL PRODUCTO FUE AGREGADO EXITOSAMENTE...WAOS!!")
        return await Menu(context, update)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=msg)
        return I_STOCK

#---------------------------FIN DE LOS INSERT----------------------------------#


#-------------------------------INICIO DE UPDATES-----------------------------#

#----------------------UPDATE DE NOMBRE-------------------#
async def AskForName(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Introduce el nuevo nombre del producto.")
    context.user_data[var_up] = context.user_data[product_name]
    return U_NAME


async def UpdateNConfirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    DATA = await FUNCTIONS_LIB.return_msg(update)

    if DATA:
        DB_CONN.execute_sql(
            f'UPDATE products SET nameproducts="{DATA}" WHERE nameproducts="{context.user_data[var_up]}"')
        context.user_data[var_up] = ""
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text='EL PRODUCTO SE HA ACTUALIZADO EXITOSAMENTE')


    else:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text='ERROR AL INGRESAR NUEVO NOMBRE')
    return await Menu(context, update)


# ----------------------UPDATE DE DESCRIPCION-------------------#
async def AskForDescription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="INGRESA LA NUEVA DESCRIPCION.")
    return U_DESCRIPTION


async def DescriptionUpdate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    DATA = await FUNCTIONS_LIB.return_msg(update)
    DB_CONN.execute_sql(
        f'UPDATE products SET descproducts="{DATA}" WHERE nameproducts="{context.user_data[product_name]}"')
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text='LA DESCRIPCION HA SIDO ACTUALIZADA!!')
    return await Menu(context, update)


# ----------------------UPDATE DE PRECIOS-------------------#
async def AskForPrice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="$ INGRESA EL NUEVO PRECIO $.")
    return U_PRICE

async def PriceUpdate(update: Update,context: ContextTypes.DEFAULT_TYPE):
    DATA=await FUNCTIONS_LIB.return_msg(update)
    try:
        new_price = float(DATA)
        msg=await FUNCTIONS_LIB.num_valid(new_price)
    except:
        msg="ERROR: EL DATO DEBE SER DE TIPO NUMERICO"
    if msg=="TRUE":
        DB_CONN.execute_sql(f'UPDATE products SET price="{new_price}" WHERE nameproducts="{context.user_data[product_name]}"')
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text='WAOS...PRECIO ACTUALIZADO!!')
        return await Menu(context, update)
    else:
        print("Estoy en el else de precios")
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=msg)
        return U_PRICE


# ---------------------UPDATE DE IMAGENES-------------------#
async def AskForImg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="INGRESE EL LINK DE LA IMAGEN (png o jpg).")
    return U_IMG

async def ImgUpdate(update: Update,context: ContextTypes.DEFAULT_TYPE):
    DATA=await FUNCTIONS_LIB.return_msg(update)
    resp=await FUNCTIONS_LIB.ValidateUrl(DATA)
    if resp:
        DB_CONN.execute_sql(f'UPDATE products SET imgurl="{DATA}" WHERE nameproducts="{context.user_data[product_name]}"')
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text='IMAGEN ACTUALIZADA!, no burtos')
        return await Menu(context, update)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="ERROR: El formato del link es incorrecto")
        return U_IMG
#---------------------UPDATE DE CATEGORIAS----------------#
async def AskForCategory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="INGRESA LA NUEVA CATEGORIA.")
    return U_CATEGORY

async def CategoryUpdate(update: Update,context: ContextTypes.DEFAULT_TYPE):
    DATA=await FUNCTIONS_LIB.return_msg(update)
    DB_CONN.execute_sql(f'UPDATE products SET category="{DATA}" WHERE nameproducts="{context.user_data[product_name]}"')
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text='SE HA ACTUALIZADO LA CATEGORIA!!')
    return await Menu(context, update)

#---------------------UPDATE DE STOCK-------------------#
async def AskForStock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="INGRESA EL NUEVO STOCK.")
    return U_STOCK

async def StockUpdate(update: Update,context: ContextTypes.DEFAULT_TYPE):
    DATA=await FUNCTIONS_LIB.return_msg(update)
    try:
        new_stock = float(DATA)
        msg=await FUNCTIONS_LIB.num_valid(new_stock)
    except:
        msg="ERROR: EL DATO DEBE SER DE TIPO NUMERICO"
    if msg=="TRUE":

        DB_CONN.execute_sql(f'UPDATE products SET stock="{new_stock}" WHERE nameproducts="{context.user_data[product_name]}"')
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text='Manito EL Stock ha sido actualizado!!.')
        return await Menu(context, update)
    else:

        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=msg)
        return U_STOCK

#-----------------------------------FIN DE UPDATE------------------------------#
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
            # print("mamaguevo") profe no vea eso :(

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
                    InlineKeyboardButton("Historico de Pedidos", callback_data=str(SHIPPING_LESS)),

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
            return await Menu(context, update)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text='🤖 |LOGIN|\nY ESA BASURA? XDDDD\n')

    return LOGIN


async def Menu(context, update):
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
            InlineKeyboardButton("AGREGAR PRODUCTOS", callback_data=str(SHIPPING_LESS)),

        ],
        [
            InlineKeyboardButton("VER SEGMENTACION DE USUARIOS", callback_data=str(SHIPPING_LESS)),

        ], [
            InlineKeyboardButton("VER ESTADISTICA DE VENTAS", callback_data=str(SHIPPING_LESS)),

        ],
        [InlineKeyboardButton("Salir", callback_data=str(END_ROUTES)),
         ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text='🤖 ENTRE!\n',
                                   reply_markup=reply_markup)
    return STORE_START


async def storeStart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    DATA = await FUNCTIONS_LIB.return_msg(update)
    context.user_data[username_pass] = DATA


async def compra_sin_envio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Sends an invoice without shipping-payment."""
    IDCompra = context.user_data["TEMP_PRODid"]
    select = DB_CONN.execute_select(f"SELECT * FROM products where idproducts ={IDCompra}")
    for prods in select:
        print(prods)
        chat_id = context.user_data["ChatID"]
        title = prods[1]
        description = prods[4]
        payload = "Custom-Payload"
        currency = "USD"
        # price in dollars
        price = int(prods[2])
        # price * 100 to include 2 decimal points
        prices = [LabeledPrice("PRODUCTO", price * 100)]
        prices = [LabeledPrice("PRODUCTO", price * 100)]

        # optionally pass need_name=True, need_phone_number=True,
        # need_email=True, need_shipping_address=True, is_flexible=True
        await context.bot.send_invoice(chat_id, title, description, payload, ENV_VARs.PAYMENT_PROVIDER_TOKEN, currency,
                                       prices)
        return TEMP_PAGO


async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Answers the PreQecheckoutQuery"""
    query = update.pre_checkout_query
    # check the payload, is this from your bot?
    if query.invoice_payload != "Custom-Payload":
        # answer False pre_checkout_query
        await query.answer(ok=False, error_message="Something went wrong...")
    else:
        await query.answer(ok=True)


async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Returns `ConversationHandler.END`, which tells the
    ConversationHandler that the conversation is over.
    """
    query = update.callback_query
    await query.answer()
    print(query.data)
    if query.data == COMPRA:
        pass
    await query.edit_message_text(text="Lo suponia...🤨 🏳️‍🌈🏳️‍🌈")
    return ConversationHandler.END


async def Ready(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Confirms the successful payment."""
    # do something after successfully receiving payment?
    await update.message.reply_text("GRACIAS POR COMPRAR, NO VUELVAS!!")


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
                CallbackQueryHandler(storeStart, pattern="^" + str(PAYMENTS_START) + "$"),
                CallbackQueryHandler(descripcion, pattern="^" + str(DETALLE) + "$"),
                CallbackQueryHandler(button_click_handler, pattern="^" + str(BUTTON_HANDLER) + "$"),


            ],
            PAYMENTS_START: [
                CallbackQueryHandler(compra_sin_envio, pattern="^" + str(TEMP_PAGO) + "$"),
                CallbackQueryHandler(descripcion, pattern="^" + str(DETALLE) + "$"),
                CallbackQueryHandler(compra_sin_envio, pattern="^" + str(SHIPPING_LESS) + "$"),
            ],
            UPDATE_PRODUCTS: [
                CallbackQueryHandler(AskForName, pattern="^" + str(U_NAME) + "$"),
                CallbackQueryHandler(AskForDescription, pattern="^" + str(U_DESCRIPTION) + "$"),
                CallbackQueryHandler(AskForStock, pattern="^" + str(U_STOCK) + "$"),
                CallbackQueryHandler(AskForCategory, pattern="^" + str(U_CATEGORY) + "$"),
                CallbackQueryHandler(AskForPrice, pattern="^" + str(U_PRICE) + "$"),
                CallbackQueryHandler(AskForImg, pattern="^" + str(U_IMG) + "$"),
                CallbackQueryHandler(LoginConfirm, pattern="^" + str(END_ROUTES) + "$"),
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
            TEMP_COMPRA: [
                MessageHandler(filters.TEXT & (~filters.COMMAND), storeStart),
            ],
            PRODUCT: [
                MessageHandler(filters.TEXT & (~filters.COMMAND), SaveProductN),
            ],
            STOCK_PRODUCT: [
                # MessageHandler(filters.TEXT & (~filters.COMMAND), SaveStock),
            ],
            U_NAME: [
                MessageHandler(filters.TEXT & (~filters.COMMAND), UpdateNConfirm),
            ],
            U_DESCRIPTION: [
                MessageHandler(filters.TEXT & (~filters.COMMAND), DescriptionUpdate),
            ],
            U_STOCK: [
                MessageHandler(filters.TEXT & (~filters.COMMAND), StockUpdate),
            ],
            U_PRICE: [
                MessageHandler(filters.TEXT & (~filters.COMMAND), PriceUpdate),
            ],
            U_CATEGORY:[
                MessageHandler(filters.TEXT & (~filters.COMMAND), CategoryUpdate),
            ],
            U_IMG:[
                MessageHandler(filters.TEXT & (~filters.COMMAND), ImgUpdate),
            ],
            I_DESCRIPTION: [
                MessageHandler(filters.TEXT & (~filters.COMMAND), InsertDescription),
            ],
            I_PRICE: [
                MessageHandler(filters.TEXT & (~filters.COMMAND), InsertPrice),
            ],
            I_CATEGORY: [
                MessageHandler(filters.TEXT & (~filters.COMMAND), InsertCategory),
            ],
            I_IMG: [
                MessageHandler(filters.TEXT & (~filters.COMMAND), InsertIMG),
            ],
            I_STOCK: [
                MessageHandler(filters.TEXT & (~filters.COMMAND), InsertStock),
            ],
            TEMP_PAGO: [
                MessageHandler(filters.SUCCESSFUL_PAYMENT, Ready)
            ],

        },

        fallbacks=[CommandHandler("start", start)],
    )
    # Optional handler if your product requires shipping
    # application.add_handler(ShippingQueryHandler())

    application.add_handler(PreCheckoutQueryHandler(precheckout_callback))

    application.add_handler(
        MessageHandler(filters.SUCCESSFUL_PAYMENT, Ready)
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    # lista=DB_CONN.execute_select('SELECT * FROM products')
    #
    #
    # a =   FUNCTIONS_LIB.ProductsListProcessor(lista)

    main()
