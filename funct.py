import logging
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

logger = logging.getLogger(__name__)

def delimiter(String):
    USERNAME,EMAIL,PASS=String.split(',')

    DATA=[USERNAME,EMAIL,PASS]

    return DATA