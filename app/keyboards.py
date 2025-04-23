from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

#start_button = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Запустить')]],
#                                   resize_keyboard=True)

main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Запустить')],
                                     [KeyboardButton(text='Запустить'),
                                      KeyboardButton(text='Запустить'),
                                      KeyboardButton(text='Запустить')]],
                           resize_keyboard=True,
                           input_field_placeholder='Выберите пункт меню...')