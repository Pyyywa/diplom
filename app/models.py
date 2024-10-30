from sqlalchemy import create_engine, Column, Integer, Float, DateTime, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Price(Base):
    __tablename__ = "prices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String, index=True)
    price = Column(Float)
    timestamp = Column(DateTime, index=True)


def get_engine(database_url: str) -> create_engine:
    """Создает и возвращает движок базы данных."""
    return create_engine(database_url)

