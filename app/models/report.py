from __future__ import annotations
import datetime
from app.db import db_session
from app.models.base import BaseModel
from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, BigInteger, String, DATETIME, JSON, TEXT, Boolean, and_, func


class Report(BaseModel):
    __tablename__ = "reports"

    report_id = Column(String(length=36), primary_key=True)
    user_id = Column(BigInteger())
    btc_address = Column(String(length=62))
    eth_address = Column(String(length=42))
    trx_address = Column(String(length=34))
    topic_link = Column(String(length=2048))
    website_link = Column(String(length=2048))
    contact = Column(String(length=512))
    category = Column(Integer())
    description = Column(String(length=128))
    seller_lang = Column(String(length=128))
    website_lang = Column(String(length=128))
    welcome_screen = Column(String(length=512))
    contact_screen = Column(String(length=512))
    chat_screen = Column(JSON())
    chat_text = Column(TEXT())
    is_checked = Column(Boolean(), default=False)
    checked_date = Column(DATETIME())
    create_date = Column(DATETIME(), default=datetime.utcnow() + timedelta(hours=3))

    @staticmethod
    def get_by_address(addresses: list) -> list[Report]:
        with db_session() as session:
            return session.query(Report).filter(Report.btc_address.in_(addresses) | Report.eth_address.in_(addresses) | Report.trx_address.in_(addresses)).all()

    @staticmethod
    def get_by_date(date_start: datetime.date, date_end: datetime.date = None) -> list[Report]:
        with db_session() as session:
            if date_start and date_end:
                return session.query(Report).filter(and_(func.date(Report.create_date) >= date_start,
                                                         func.date(Report.create_date) <= date_end)).all()
            return session.query(Report).filter(func.date(Report.create_date) == date_start).all()

    @staticmethod
    def update(report_data: dict) -> Report:
        with db_session() as session:
            report = Report(**report_data)
            session.add(report)
            session.commit()
            return report

Report.__table__.create(checkfirst=True)
