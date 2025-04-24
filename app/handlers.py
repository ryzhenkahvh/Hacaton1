from aiogram import F, Router, types
#from aiogram.types import Message
from aiogram.filters import  CommandStart
from app.keyboards import kb, kb2, kb_remove, start_kb

last_report = {}
router = Router()
#keyboard = main

#@router.message(CommandStart())
#async def start_command(message: types.Message):
#    await message.answer("Выберите опцию:", reply_markup=kb)

@router.message(CommandStart())
async def start_command(message: types.Message):
    await message.answer("Добро пожаловать! Нажмите «Запустить», чтобы начать.", reply_markup=start_kb)

@router.message(F.text == "🚀 Запустить")
async def launch_bot(message: types.Message):
    await message.reply("Выберите дальнейшие действия:", reply_markup=kb)

@router.message(F.text == "🚀 Запуск работы")
async def start_work(message: types.Message):
    last_report[message.from_user.id] = "Отчет1"
    await message.reply("Отчет1", reply_markup=kb2)

@router.message(F.text == "⏸️ Приостановка работы")
async def pause_work(message: types.Message):
    last_report[message.from_user.id] = "Отчет2"
    await message.reply("Отчет2", reply_markup=kb2)

@router.message(F.text == "🔄 Повторная отправка отчета")
async def resend_report(message: types.Message):
    report = last_report.get(message.from_user.id, "Нет доступного отчета для повторной отправки.")
    await message.reply(report, reply_markup=kb2)

@router.message(F.text == "🏠 Вернуться к списку доступных опций")
async def back_to_main_menu(message: types.Message):
    await message.reply("Вы вернулись в главное меню. Выберите опцию:", reply_markup=kb)

@router.message(F.text == "⚙️ Настройки")
async def settings(message: types.Message):
    await message.reply("Введите ключевые значения:", reply_markup=kb_remove)

#@router.message(CommandStart())
#async def send_welcome(message: types.Message):
#    await message.answer("Добро пожаловать! Я ваш бот-помощник.", reply_markup=start_button.main)
#@router.message(CommandStart())
#async def cmd_start(message:Message):
#    await message.answer ('Привет!', reply_markup=kb.main)
#    await message.reply ('Как дела?')

#@router.message(Command('help'))
#async def cmd_help(message:Message):
#    await message.answer ('Вы нажали на кнопку помощи')

#@router.message(F.text == 'У меня все хорошо')
#async def nice(message:Message):
#    await message.answer('Я очень рад')