from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from . import config
from .utils.logger import logger

# Cоздание механизма, который хранит данные в локальном каталоге sqlalchemy_example.db
engine = create_engine(config.DATABASE_URI)

# Создание базового класса для моделей.
base = declarative_base()

# Связывает метаданные с движком.
base.metadata.bind = engine

# Он создает все таблицы в базе данных.
base.metadata.create_all(engine)

logger.info("Database setup")

@contextmanager
def db_session():
    """
    Он создает объект сеанса, область действия которого ограничена текущим потоком, а затем передает этот сеанс вызывающей стороне.
    """

    session = scoped_session(sessionmaker(bind=engine, expire_on_commit=False))
    try:
        yield session
    except:
        session.rollback()
        logger.error("Session rollback")
        raise
    finally:
        session.close()
