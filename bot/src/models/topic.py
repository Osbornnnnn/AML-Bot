from __future__ import annotations
from ..db import db_session
from .base import BaseModel
from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DATETIME


class Topic(BaseModel):
    __tablename__ = "topics"

    id = Column(Integer(), primary_key=True, autoincrement=True)
    topic_link = Column(String(length=2048), unique=True, nullable=False)
    category = Column(Integer(), nullable=False)
    create_date = Column(DATETIME(), default=datetime.utcnow() + timedelta(hours=3))

    @staticmethod
    def update(topic_link: str, category: int) -> Topic | None:
        with db_session() as session:
            topic = Topic(topic_link=topic_link, category=category)
            try:
                session.add(topic)
                session.commit()
                return topic
            except:
                return None
