from __future__ import annotations
from ..db import db_session
from .base import BaseModel
from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DATETIME


class Forum(BaseModel):
    __tablename__ = "forums"

    id = Column(Integer(), primary_key=True, autoincrement=True)
    forum_link = Column(String(length=2048), unique=True, nullable=False),
    language = Column(String(length=2048), unique=True, nullable=False),
    create_date = Column(DATETIME(), default=datetime.utcnow() + timedelta(hours=3))

    @staticmethod
    def update(forum_link, language: str) -> Forum | None:
        with db_session() as session:
            forum = Forum(forum_link=forum_link, language=language)
            try:
                session.add(forum)
                session.commit()
                return forum
            except:
                return None

Forum.__table__.create(checkfirst=True)
