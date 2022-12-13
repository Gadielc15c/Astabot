import ENV_VARs as TOKEN
import logging
import funct
from telegram import __version__ as TG_VER, InlineKeyboardButton, InlineKeyboardMarkup

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 5):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters, CallbackQueryHandler,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

GENDER, PHOTO, LOCATION, BIO = range(4)
#0       1        2       3

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about their gender."""

    user = update.message.from_user
    "Hola "+user.first_name+"!!\n\n Bienvenido A IA STORE. \n\n"
    keyboard=[
        [
            InlineKeyboardButton("COMPRAR", callback_data=str(1)),
            InlineKeyboardButton("AGREGAR METODO DE PAGO", callback_data=str(2)),
            InlineKeyboardButton("VER HISTORIAL DE COMPRAS", callback_data=str(3)),
            InlineKeyboardButton("SALIR", callback_data=str(2)  ),

        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Send message with text and appended InlineKeyboard
    await update.message.reply_text("Comencemos "+user.first_name+" Que Deseas hacer?", reply_markup=reply_markup)
    return GENDER


async def gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    x=await funct.gender(update,context)
    return x


async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the photo and asks for a location."""
    user = update.message.from_user
    # photo_file = await update.message.photo[-1].get_file()
    # await photo_file.download_to_drive("user_photo.jpg")
    logger.info("Photo of %s: %s", user.first_name, "user_photo.jpg")
    await update.message.reply_text(
        "El diablaso!, Enviame tu location pa comerme eso xd /skip si no quieres ."
    )

    return LOCATION


async def skip_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Skips the photo and asks for a location."""
    user = update.message.from_user
    logger.info("User %s did not send a photo.", user.first_name)
    await update.message.reply_text(
        "Sa!!!, ni tan buena que estes rata! Almenos manda la ubicacion pa llegarte, o escribe para saltar /skip."
    )

    return LOCATION




async def skip_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Skips the location and asks for info about the user."""
    user = update.message.from_user
    logger.info("User %s did not send a location.", user.first_name)
    await update.message.reply_text(
        "Diablo pero e neegao xdddd, almenos dime algo de ti, Despues que escribas me voy a buguear porque el mmg de gadiel no programo mas nada"
    )

    return BIO


async def bio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the info about the user and ends the conversation."""
    user = update.message.from_user
    logger.info("Bio of %s: %s", user.first_name, update.message.text)
    await update.message.reply_text("Gracias mmg minimo tenias que decir algo xddd.")

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Ruede que usted no viaja", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN.CONN_TOKEN).build()

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={

            GENDER: [
                CallbackQueryHandler(funct.location, pattern="^" + str(0) + "$"),
                CallbackQueryHandler(skip_location, pattern="^" + str(1) + "$"),
                CallbackQueryHandler(bio, pattern="^" + str(2) + "$"),
                CallbackQueryHandler(cancel, pattern="^" + str(3) + "$"),
            ],
            PHOTO: [MessageHandler(filters.PHOTO, photo), CommandHandler("skip", skip_photo)],
            LOCATION: [
                MessageHandler(filters.LOCATION,  funct.location),CommandHandler("skip", skip_location),
            ],
            BIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, bio)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()