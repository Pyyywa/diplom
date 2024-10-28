from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Price
from datetime import datetime, timedelta


def setup_database(database_url):
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    return engine


def get_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()


def save_price_to_db(session, price):
    """Сохранение цены в базе данных с текущей временной меткой."""
    try:
        new_price = Price(symbol='ETHUSDT', price=price, timestamp=datetime.now())
        session.add(new_price)
        session.commit()
    except Exception:
        session.rollback()  # Откат транзакции в случае ошибки
    finally:
        clear_old_prices(session)


def clear_old_prices(session):
    """Очистка таблицы цен, если данные старше одного часа."""
    try:
        threshold_time = datetime.now() - timedelta(hours=1)
        deleted_count = session.query(Price).filter(Price.timestamp < threshold_time).delete(synchronize_session=False)
        session.commit()
    except Exception:
        print(f"Ошибка при удалении старых цен из базы данных: {e}")
        session.rollback()  # Откат транзакции в случае ошибки
