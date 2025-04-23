from aiogram import F, Router#, types
from aiogram.types import Message
from aiogram.filters import  CommandStart, Command
import app.keyboards as kb
#from app.keyboards import start_button

router = Router()

#@router.message(CommandStart())
#async def send_welcome(message: types.Message):
#    await message.answer("Добро пожаловать! Я ваш бот-помощник.", reply_markup=start_button.main)
@router.message(CommandStart())
async def cmd_start(message:Message):
    await message.answer ('Привет!', reply_markup=kb.main)
    await message.reply ('Как дела?')

@router.message(Command('help'))
async def cmd_help(message:Message):
    await message.answer ('Вы нажали на кнопку помощи')

@router.message(F.text == 'У меня все хорошо')
async def nice(message:Message):
    await message.answer('Я очень рад')