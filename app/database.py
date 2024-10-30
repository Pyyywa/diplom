import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Price
from datetime import datetime, timedelta

# Настройка логирования
logging.basicConfig(level=logging.INFO)


def setup_database(database_url: str) -> create_engine:
    """Настройка базы данных и создание таблиц."""
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    return engine


def get_session(engine) -> sessionmaker:
    """Возвращает новую сессию базы данных."""
    Session = sessionmaker(bind=engine)
    return Session()


def save_price_to_db(session, price: float, symbol: str) -> None:
    """Сохранение цены в базе данных с текущей временной меткой."""
    try:
        new_price = Price(symbol=symbol, price=price, timestamp=datetime.now())
        session.add(new_price)
        session.commit()
        logging.info(f"Цена {price} для {symbol} успешно сохранена.")
    except Exception as e:
        logging.error(f"Ошибка при сохранении цены: {e}")
        session.rollback()
    finally:
        check_price_changes(session)
        clear_old_prices(session)


def clear_old_prices(session) -> None:
    """Очистка таблицы цен, если данные старше одного часа."""
    try:
        threshold_time = datetime.now() - timedelta(hours=1)
        deleted_count = session.query(Price).filter(Price.timestamp < threshold_time).delete(synchronize_session=False)
        session.commit()
        logging.info(f"Удалено {deleted_count} старых цен из базы данных.")
    except Exception as e:
        logging.error(f"Ошибка при удалении старых цен: {e}")
        session.rollback()


def check_price_changes(session) -> None:
    """Проверяет, изменилась ли цена на 1% и более."""
    prices = session.query(Price).all()
    if not prices:
        logging.info("Нет данных за последний час.")
        return

    max_price = max(price.price for price in prices)
    min_price = min(price.price for price in prices)

    if min_price > 0:
        price_change_percentage = ((max_price - min_price) / min_price) * 100
        if price_change_percentage > 1:
            logging.info(f"Изменение за последний час превышает 1%: цена изменилась на {price_change_percentage:.2f}%")
