from aiogram import Bot, Dispatcher
import logging

from aiogram.fsm.state import StatesGroup, State
from decouple import config

bot = Bot(token=config("API_TOKEN"))
dp = Dispatcher()

logger = logging.getLogger(__name__)

class Form(StatesGroup):
    set_reminder = State()