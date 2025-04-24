import asyncio
import datetime

from aiogram import types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from decouple import config

import reminder_func
from bot_init import dp, bot, logger, Form
from db.base import create_tables
import db.methods
from db.methods import set_reminder

admins = config("ADMIN")

# Функция, которая выполнится когда бот запустится
# async def start_bot():
#     # await set_commands()
#     await create_tables()
#     for admin_id in admins:
#         try:
#             await dp.send_message(admin_id, f'Я запущен🥳.')
#         except:
#             pass
#
# # Функция, которая выполнится когда бот завершит свою работу
# async def stop_bot():
#     try:
#         for admin_id in admins:
#             await bot.send_message(admin_id, 'Бот остановлен. За что?😔')
#     except:
#         pass

@dp.message(CommandStart())
async def send_welcome(message: types.Message):
    await message.reply('Привет! Я бот-напоминалка студентческого театра Гротеск.'
                        '\n/add_reminder -- добавить напоминание'
                        '\n/turn_on_reminder -- включить напоминания'
                        '\n/turn_off_reminder -- выключить напоминания'
                        '\n/add_role -- добавить свою роль')
    # await db.methods.set_user(message)
    # await db.methods.set_user(message.from_user.id, message.from_user.username)
    print(message.from_user.id, message.from_user.username, message.from_user.full_name)
    await db.methods.set_user(user_id=message.from_user.id,
                              username=message.from_user.username,
                              full_name=message.from_user.full_name)

# Обработчик команды /add_role
@dp.message(F.text.contains("add_role"))
async def role_message(message, state: FSMContext):
# Запрашиваем у пользователя название напоминания и дату и время напоминания
    await message.reply('Какую роль вы исполняете?\n'
                        'Например, Леди Кэйрлесс')
    await state.set_state(Form.set_role)


# Обработчик команды /add_role
@dp.message(F.text, Form.set_role)
async def add_role(message, state: FSMContext):
    await db.methods.set_role(user_id=message.from_user.id,
                              username=message.from_user.username,
                              full_name=message.from_user.full_name,
                              role=message.text)
    await state.clear()
    await message.reply("Роль добавлена!")


# Обработчик команды /add_reminder
@dp.message(F.text.contains("add_reminder"))
async def reminder_message(message, state: FSMContext):
# Запрашиваем у пользователя название напоминания и дату и время напоминания
    await message.reply('Добавьте репетицию (дата, время, номер сцены и список действующих персонажей)\n'
                        'Например, 2025-05-05 18:30:00; 6; Леди Кэйрлесс, Джозеф, Сэр Питер')
    # await dp.register_next_step_handler(message, add_reminder)
    await state.set_state(Form.set_reminder)


# Обработчик команды /reminder
@dp.message(F.text, Form.set_reminder)
async def add_reminder(message, state: FSMContext):
    await db.methods.set_reminder(user_id=message.from_user.id, text=message.text)
    await state.clear()


@dp.message(F.text.contains("turn_on_reminder"))
async def switch_on_message(message):
    await db.methods.switch(user_id=message.from_user.id,
                            username=message.from_user.username,
                            full_name=message.from_user.full_name,
                            switching=1)
    await message.reply("Напоминания о репетициях включены!")


@dp.message(F.text.contains("turn_off_reminder"))
async def switch_off_message(message):
    await db.methods.switch(user_id=message.from_user.id,
                            username=message.from_user.username,
                            full_name=message.from_user.full_name,
                            switching=0)
    await message.reply("Напоминания о репетициях выключены(")

# if __name__ == '__main__':
#     asyncio.run(create_tables())
#     asyncio.run(dp.start_polling(bot))

async def main():
    await create_tables()
    print("db created")
    # запуск бота в режиме long polling при запуске бот очищает все обновления, которые были за его моменты бездействия
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())