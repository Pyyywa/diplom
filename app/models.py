from sqlalchemy import create_engine, Column, Float, DateTime, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Price(Base):
    __tablename__ = "prices"
    id = Column(Float, primary_key=True)  # Измените на Integer, если id должен быть целым числом
    symbol = Column(String)  # Для хранения символа валюты
    price = Column(Float)
    timestamp = Column(DateTime)

def get_engine(database_url):
    return create_engine(database_url)

def get_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()
