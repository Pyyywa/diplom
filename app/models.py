from sqlalchemy import create_engine, Column, Integer, Float, DateTime, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Price(Base):
    __tablename__ = "prices"
    id = Column(Integer, primary_key=True, autoincrement=True)  # Изменено на Integer с автоинкрементом
    symbol = Column(String, index=True)  # Добавлен индекс для symbol
    price = Column(Float)
    timestamp = Column(DateTime, index=True)  # Добавлен индекс для timestamp

def get_engine(database_url):
    return create_engine(database_url)
