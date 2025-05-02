from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

#start_button = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Запустить')]],
#                                   resize_keyboard=True)

kb_remove = ReplyKeyboardRemove()

start_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='🚀 Запустить')]],
                               resize_keyboard=True,
                               input_field_placeholder='Нажмите "Запустить", чтобы начать...')


kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='🚀 Запуск работы')],
                                      [KeyboardButton(text='⏸️ Приостановка работы')],
                                      [KeyboardButton(text='⚙️ Настройки')],
                                      [KeyboardButton(text='💵Ввести сумму')]],
                           resize_keyboard=True,
                           input_field_placeholder='Выберите интересующую опцию...')

kb2 = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='🔄 Повторная отправка отчета')],
                                      [KeyboardButton(text='🏠 Вернуться к списку доступных опций')]],
                           resize_keyboard=True,
                           input_field_placeholder='Выберите интересующую опцию...')