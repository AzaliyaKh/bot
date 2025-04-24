from sqlalchemy import BigInteger, Integer, Text, ForeignKey, String, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .init_db import Base


# Модель для таблицы пользователей
class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str] = mapped_column(String, nullable=True)
    full_name: Mapped[str] = mapped_column(String, nullable=True)
    role: Mapped[str] = mapped_column(String, nullable=True)
    switching: Mapped[int] = mapped_column(Integer, nullable=True)


# Модель для таблицы заметок
class Reminder(Base):
    __tablename__ = 'reminder'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    time: Mapped[str] = mapped_column(String, nullable=False)
    scene_name: Mapped[str] = mapped_column(String, nullable=True)
    characters: Mapped[str] = mapped_column(String, nullable=True)

