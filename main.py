# Бот все еще кривой и инвалид, чтобы не задерживать работу остальных выложу пока таким,
# какой он есть, впоследствии буду дорабатывать

import asyncio
from aiogram import Bot, Dispatcher
from app.handlers import router


async def main():
    bot = Bot(token='7860908085:AAH29QpmtHU4_VOPQN2zZMgf3Bre6LLqPBU')
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен')