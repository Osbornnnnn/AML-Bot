from __future__ import annotations
import datetime
from ..db import db_session
from .base import BaseModel
from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, BigInteger, String, DATETIME, JSON, TEXT, Boolean, and_, func


class CheckReports(BaseModel):
    __tablename__ = "check_reports"

    report_id = Column(String(length=36), primary_key=True)
    aml_id = Column(String(length=36))
    user_id = Column(BigInteger())
    is_check = Column(Boolean(), default=False)
    check_date = Column(DATETIME())
    is_paid = Column(Boolean(), default=False)
    paid_date = Column(DATETIME())
    create_date = Column(DATETIME(), default=datetime.utcnow() + timedelta(hours=3))

    @staticmethod
    def get_by_id(report_id: str) -> CheckReports:
        with db_session() as session:
            return session.query(CheckReports).filter(CheckReports.report_id == report_id).first()

    @staticmethod
    def get_by_aml(aml_id: str) -> CheckReports:
        with db_session() as session:
            return session.query(CheckReports).filter(CheckReports.aml_id == aml_id).first()

    @staticmethod
    def get_by_user(user_id: int) -> list[CheckReports]:
        with db_session() as session:
            return session.query(CheckReports).filter(CheckReports.user_id == user_id).all()

#     @staticmethod
#     def update(report_data: dict) -> Reports:
#         with db_session() as session:
#             report = Reports(**report_data)
#             session.add(report)
#             session.commit()
#             return report
#
# CheckReports.__table__.create(checkfirst=True)
