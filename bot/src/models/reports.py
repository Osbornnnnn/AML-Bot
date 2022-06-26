from __future__ import annotations
import datetime
from ..db import db_session
from .base import BaseModel
from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, BigInteger, String, DATETIME, JSON, TEXT, Boolean, and_, func


class Reports(BaseModel):
    __tablename__ = "reports"

    report_id = Column(String(length=36), primary_key=True)
    aml_id = Column(String(length=36))
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
    is_check = Column(Boolean(), default=False)
    check_date = Column(DATETIME())
    is_paid = Column(Boolean(), default=False)
    paid_date = Column(DATETIME())
    create_date = Column(DATETIME(), default=datetime.utcnow() + timedelta(hours=3))

    @staticmethod
    def get_by_address(addresses: list) -> list[Reports]:
        with db_session() as session:
            return session.query(Reports).filter(Reports.btc_address.in_(addresses) | Reports.eth_address.in_(addresses) | Reports.trx_address.in_(addresses)).all()

    @staticmethod
    def get_by_date(date_start: datetime.date, date_end: datetime.date = None) -> list[Reports]:
        with db_session() as session:
            if date_start and date_end:
                return session.query(Reports).filter(and_(func.date(Reports.create_date) >= date_start,
                                                          func.date(Reports.create_date) <= date_end)).all()
            return session.query(Reports).filter(func.date(Reports.create_date) == date_start).all()

    @staticmethod
    def get_by_reports(report_ids: list) -> list[Reports]:
        with db_session() as session:
            return session.query(Reports).filter(Reports.report_id.in_(report_ids)).all()

    @staticmethod
    def update(report_data: dict) -> Reports:
        with db_session() as session:
            report = Reports(**report_data)
            session.add(report)
            session.commit()
            return report

    @staticmethod
    def update_aml_report(ids: dict) -> bool:
        with db_session() as session:
            reports = Reports.get_by_reports(list(ids.keys()))
            if reports:
                for report in reports:
                    report.aml_id = ids.get(report.report_id, None)
                    report.is_check = True
                    report.check_date = datetime.utcnow() + timedelta(hours=3)
                session.commit()
                return True
            return False

Reports.__table__.create(checkfirst=True)
