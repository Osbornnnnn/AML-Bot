from __future__ import annotations
from ..db import db_session
from .base import BaseModel
from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, BigInteger, String, Boolean, Float, DATETIME


# Это класс, который представляет таблицу в базе данных.
class Users(BaseModel):
    __tablename__ = "users"

    user_id = Column(BigInteger(), primary_key=True)
    username = Column(String(length=32), unique=True, nullable=False)
    wallet = Column(String(length=128))                                 # КОШЕЛЕК ДЛЯ ВЫПЛАТЫ
    pending_balance = Column(Float(), default=0.0)                      # НА ВЫПЛАТУ
    total_balance = Column(Float(), default=0.0)                        # ВСЕГО ВЫПЛАЧЕНО
    pending_reports = Column(Integer(), default=0)                      # ОЖИДАЮТ ПРОВЕРКИ
    approved_reports = Column(Integer(), default=0)                     # УЖЕ ПРОВЕРЕНЫ
    paid_reports = Column(Integer(), default=0)                         # ВСЕГО ВЫПЛАЧЕНО
    decline_reports = Column(Integer(), default=0)                      # ВСЕГО ОТКЛОНЕНО
    is_blocked = Column(Boolean(), default=False)
    is_admin = Column(Boolean(), default=False)
    create_date = Column(DATETIME(), default=datetime.utcnow() + timedelta(hours=3))

    @staticmethod
    def get(user_id: int) -> Users:
        """
        Возвращает пользователя, с заданным `user_id`

        :param user_id: Telegram API
        :return: Пользовательский объект
        """

        with db_session() as session:
            return session.query(Users).filter(Users.user_id == user_id).first()

    @staticmethod
    def get_by_username(username: str) -> Users:
        """
        Возвращает пользователя, с заданным `username`

        :param username: Telegram API
        :return: Пользовательский объект
        """

        with db_session() as session:
            return session.query(Users).filter(Users.username == username).first()

    @staticmethod
    def get_admins() -> list[Users]:
        """
        Возвращает список всех пользователей, которые являются администраторами.

        :return: Список пользовательских объектов
        """

        with db_session() as session:
            return session.query(Users).filter(Users.is_admin).all()

    @staticmethod
    def get_all() -> list[Users]:
        """
        Эта функция возвращает список всех пользователей в базе данных

        :return: Список пользовательских объектов
        """

        with db_session() as session:
            return session.query(Users).select_from(Users).all()

    @staticmethod
    def update(user_id: int, username: str) -> Users:
        """
        Обновляет имя пользователя с заданным user_id, если пользователь не существует, то создается новый пользователь с заданными user_id и username

        :param user_id: int - идентификатор пользователя
        :param username: str - имя пользователя
        :return: Пользовательский объект
        """

        with db_session() as session:
            user = Users.get(user_id)
            if not user:
                user = Users(user_id=user_id, username=username)
                session.add(user)
            elif user.username != username:
                user.username = username
            else:
                return user
            session.commit()
            return user

    @staticmethod
    def update_permission(user_id: int, is_admin: bool = False, is_blocked: bool = False) -> Users:
        """
        Функция обновляет разрешения пользователя

        :param user_id: Идентификатор пользователя, которого вы хотите обновить
        :param is_admin: Если True, пользователь будет администратором. Если False, пользователь будет обычным пользователем, defaults to False
        :param is_blocked: Если True, пользователь будет заблокирован. Если False, пользователь будет разблокирован, defaults to False
        :return: Пользовательский объект
        """

        with db_session() as session:
            user = session.query(Users).get(user_id)
            user.is_admin = is_admin
            user.is_blocked = is_blocked
            session.commit()
            return user

    @staticmethod
    def update_wallet(user_id: int, wallet: str) -> str:
        """
        Функция обновляет кошелек пользователя с заданным `user_id`

        :param user_id: int
        :param wallet: str - Адрес кошелька пользователя

        :return: Кошелек пользователя.
        """
        with db_session() as session:
            user = session.query(Users).get(user_id)
            user.wallet = wallet
            session.commit()
            return user.wallet

    @staticmethod
    def update_statistics(user_id: int, pending_reports: int = 0, approved_reports: int = 0, decline_reports: int = 0,
                          pending_balance: float = 0.0, is_paid: bool = False, after_checked: bool = False) -> Users:
        """
        Обновляет статистику пользователя

        :param user_id: int - идентификатор пользователя
        :param pending_reports: int - количество отчетов, которые находятся в процессе проверки, defaults to 0
        :param approved_reports: int - количество утвержденных отчетов, defaults to 0
        :param decline_reports: int - количество отчетов, которые были отклонены, defaults to 0
        :param pending_balance: float - сумма денег, которую получит пользователь после проверки
        :param is_paid: bool - когда пользователю платят, общий баланс увеличивается на сумму ожидающего баланса,, defaults to False
        :param after_checked: bool - этот параметр используется, когда пользователь добавляет файл, а файл проверяется администратором, defaults to False
        :return: Пользовательский объект
        """

        with db_session() as session:
            user: Users = session.query(Users).get(user_id)
            if is_paid:                                     # КОГДА ВЫПЛАЧЕНО
                user.total_balance += user.pending_balance
                user.pending_balance = 0.0
                user.paid_reports += user.approved_reports
                user.approved_reports = 0
            if after_checked:                               # КОГДА ПРОВЕРЕНО
                if user.pending_reports <= 0:
                    return user
                user.pending_reports -= pending_reports
                user.pending_balance += pending_balance
                user.approved_reports += approved_reports
                user.decline_reports += decline_reports
            if not after_checked:
                user.pending_reports += pending_reports     # КОГДА ДОБАВЛЯЮТ ФАЙЛ
            session.commit()
            return user


# Он создает таблицу в базе данных, если она не существует.
Users.__table__.create(checkfirst=True)
