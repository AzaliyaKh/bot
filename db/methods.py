import asyncio

from aiogram.utils.chat_member import ADMINS
import datetime
import threading
from sqlalchemy import select
from typing import List, Dict, Any, Optional
from sqlalchemy.exc import SQLAlchemyError

from bot_init import logger, dp, bot
from .models import User, Reminder
from .base import connection


@connection
async def set_user(session, user_id: int, username: str, full_name: str, role=None, switching=0) -> Optional[User]:
    try:
        user = await session.scalar(select(User).filter_by(id=user_id))

        if not user:
            new_user = User(id=user_id, username=username, full_name=full_name, role=role, switching=switching)
            session.add(new_user)
            await session.commit()
            logger.info(f"Зарегистрировал пользователя с ID {user_id}!")
            return None
        else:
            logger.info(f"Пользователь с ID {user_id} найден!")
            return user
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при добавлении пользователя: {e}")
        await session.rollback()


@connection
async def set_role(session, user_id: int, username: str, full_name: str, role: str) -> Optional[User]:
    try:
        user = await session.scalar(select(User).filter_by(id=user_id))

        if not user:
            await set_user(id=user_id, username=username, full_name=full_name, role=role)
        else:
            user.role = role
            await session.commit()
            logger.info(f"Пользователь с ID {user_id} найден!")
            return user
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при добавлении роли: {e}")
        await session.rollback()

@connection
async def switch(session, user_id: int, username: str, full_name: str, switching=0) -> Optional[User]:
    try:
        user = await session.scalar(select(User).filter_by(id=user_id))

        if not user:
            await set_user(id=user_id, username=username, full_name=full_name, switching=switching)
        else:
            user.switching = switching
            await session.commit()
            logger.info(f"Пользователь с ID {user_id} найден!")
            return user
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при добавлении роли: {e}")
        await session.rollback()

@connection
async def set_reminder(session, user_id: int, text: str) -> Optional[Reminder]:
    try:
        repetition_info = text.split(";")
        reminder_time = datetime.datetime.strptime(repetition_info[0], '%Y-%m-%d %H:%M:%S')
        print(type(reminder_time))
        print(type(repetition_info[0]))
        scene_name = repetition_info[1]
        characters = repetition_info[2]
        # print(reminder_time, scene_name, characters)

        reminder = await session.scalar(select(Reminder).filter_by(time=reminder_time))

        if not reminder:
            new_Reminder = Reminder(
                user_id=user_id,
                time=repetition_info[0],
                scene_name=scene_name,
                characters=characters
            )

            session.add(new_Reminder)
            await session.commit()
            logger.info(f"Заметка для пользователя с ID {user_id} успешно добавлена!")
            print("set_reminder -- ok")

            await activate_reminder(reminder_time, characters)
        else:
            logger.info(f"В это время уже есть репетиция(")
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при добавлении заметки: {e}")
        await session.rollback()


@connection
async def activate_reminder(session, reminder_time, reminder_characters):
    try:
        # Преобразуем введенную пользователем дату и время в формат datetime
        now = datetime.datetime.now()
        print(now)
        delta = (reminder_time - now).total_seconds()

        if delta > 0:
            await asyncio.sleep(delta)  # Ожидаем до времени напоминания
            await send_reminder(characters=reminder_characters)  # Вызываем send_reminder
        print("activate_reminder -- ok")

    except ValueError:
        pass


# Функция, которая отправляет напоминание пользователю
@connection
async def send_reminder(session, characters):
    print("дошел")
    characters = list(s.strip() for s in characters.split(","))
    for character in characters:
        result = await session.execute(select(User).filter_by(role=character, switching=1))

        users = result.scalars().all()  # Получаем список пользователей по роли

        print(character)
        for user in users:
            print(user.id, user.username)
            await bot.send_message(user.id, 'Тебе сегодня на репетицию!')
    print("send_reminder -- ok")





    # user: Mapped["User"] = relationship("User", back_populates="notes")
# @connection
# async def update_text_Reminder(session, Reminder_id: int, content_text: str) -> Optional[Reminder]:
#     try:
#         Reminder = await session.scalar(select(Reminder).filter_by(id=Reminder_id))
#         if not Reminder:
#             logger.error(f"Заметка с ID {Reminder_id} не найдена.")
#             return None
#
#         Reminder.content_text = content_text
#         await session.commit()
#         logger.info(f"Заметка с ID {Reminder_id} успешно обновлена!")
#         return Reminder
#     except SQLAlchemyError as e:
#         logger.error(f"Ошибка при обновлении заметки: {e}")
#         await session.rollback()
#
#
# @connection
# async def get_Reminder_by_id(session, Reminder_id: int) -> Optional[Dict[str, Any]]:
#     try:
#         Reminder = await session.get(Reminder, Reminder_id)
#         if not Reminder:
#             logger.info(f"Заметка с ID {Reminder_id} не найдена.")
#             return None
#
#         return {
#             'id': Reminder.id,
#             'content_type': Reminder.content_type,
#             'content_text': Reminder.content_text,
#             'file_id': Reminder.file_id
#         }
#     except SQLAlchemyError as e:
#         logger.error(f"Ошибка при получении заметки: {e}")
#         return None
#
# @connection
# async def delete_Reminder_by_id(session, Reminder_id: int) -> Optional[Reminder]:
#     try:
#         Reminder = await session.get(Reminder, Reminder_id)
#         if not Reminder:
#             logger.error(f"Заметка с ID {Reminder_id} не найдена.")
#             return None
#
#         await session.delete(Reminder)
#         await session.commit()
#         logger.info(f"Заметка с ID {Reminder_id} успешно удалена.")
#         return Reminder
#     except SQLAlchemyError as e:
#         logger.error(f"Ошибка при удалении заметки: {e}")
#         await session.rollback()
#         return None
#
# @connection
# async def get_Reminders_by_user(session, user_id: int, date_add: str = None, text_search: str = None,
#                             content_type: str = None) -> List[Dict[str, Any]]:
#     try:
#         result = await session.execute(select(Reminder).filter_by(user_id=user_id))
#         Reminders = result.scalars().all()
#
#         if not Reminders:
#             logger.info(f"Заметки для пользователя с ID {user_id} не найдены.")
#             return []
#
#         Reminder_list = [
#             {
#                 'id': Reminder.id,
#                 'content_type': Reminder.content_type,
#                 'content_text': Reminder.content_text,
#                 'file_id': Reminder.file_id,
#                 'date_created': Reminder.created_at
#             } for Reminder in Reminders
#         ]
#
#         if date_add:
#             Reminder_list = [Reminder for Reminder in Reminder_list if Reminder['date_created'].strftime('%Y-%m-%d') == date_add]
#
#         if text_search:
#             Reminder_list = [Reminder for Reminder in Reminder_list if text_search.lower() in (Reminder['content_text'] or '').lower()]
#
#         if content_type:
#             Reminder_list = [Reminder for Reminder in Reminder_list if Reminder['content_type'] == content_type]
#
#         return Reminder_list
#     except SQLAlchemyError as e:
#         logger.error(f"Ошибка при получении заметок: {e}")
#         return []