from __future__ import annotations
from ..db import db_session
from .base import BaseModel
from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, BigInteger, String, Boolean, Float, DATETIME


class User(BaseModel):
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
    def get(user_id: int) -> User:
        with db_session() as session:
            return session.query(User).filter(User.user_id == user_id).first()

    @staticmethod
    def get_by_username(username: str) -> User:
        with db_session() as session:
            return session.query(User).filter(User.username == username).first()

    @staticmethod
    def get_admins() -> list[User]:
        with db_session() as session:
            return session.query(User).filter(User.is_admin).all()

    @staticmethod
    def get_all() -> list[User]:
        with db_session() as session:
            return session.query(User).select_from(User).all()

    @staticmethod
    def update(user_id: int, username: str) -> User:
        with db_session() as session:
            user = User.get(user_id)
            if not user:
                user = User(user_id=user_id, username=username)
                session.add(user)
            elif user.username != username:
                user.username = username
            else:
                return user
            session.commit()
            return user

    @staticmethod
    def update_permission(user_id: int, is_admin: bool = False, is_blocked: bool = False) -> User:
        with db_session() as session:
            user = session.query(User).get(user_id)
            user.is_admin = is_admin
            user.is_blocked = is_blocked
            session.commit()
            return user

    @staticmethod
    def update_wallet(user_id: int, wallet: str) -> str:
        with db_session() as session:
            user = session.query(User).get(user_id)
            user.wallet = wallet
            session.commit()
            return user.wallet

    @staticmethod
    def update_statistics(user_id: int, pending_reports: int = 0, approved_reports: int = 0, decline_reports: int = 0,
                          pending_balance: float = 0.0, is_paid: bool = False, after_checked: bool = False) -> User:
        with db_session() as session:
            user = session.query(User).get(user_id)
            if is_paid:                                     # КОГДА ВЫПЛАЧЕНО
                user.total_balance += user.pending_balance
                user.pending_balance = 0.0
                user.paid_reports += user.approved_reports
                user.approved_reports = 0
            if after_checked:                               # КОГДА ПРОВЕРЕНО
                user.pending_balance += pending_balance
                user.pending_reports -= pending_reports
                user.approved_reports += approved_reports
                user.decline_reports += decline_reports
            if not after_checked:
                user.pending_reports += pending_reports     # КОГДА ДОБАВЛЯЮТ ФАЙЛ
            session.commit()
            return user


User.__table__.create(checkfirst=True)
