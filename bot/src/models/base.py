from .. import db


class BaseModel(db.base):
    __abstract__ = True
