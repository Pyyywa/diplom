import logging
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, Float, DateTime, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Определение модели данных
Base = declarative_base()


class Price(Base):
    __tablename__ = "prices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String, index=True)
    price = Column(Float)
    timestamp = Column(DateTime, index=True)


class AdjustedPrice(Base):
    __tablename__ = 'adjusted_prices'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    symbol = Column(String)
    adjusted_price = Column(Float)


class DatabaseManager:
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def get_session(self):
        """Возвращает новую сессию базы данных."""
        return self.Session()

    def save_price(self, symbol: str, price: float) -> None:
        """Сохранение цены в базе данных с текущей временной меткой."""
        session = self.get_session()
        try:
            new_price = Price(symbol=symbol, price=price, timestamp=datetime.now())
            session.add(new_price)
            session.commit()
            logging.info(f"Цена {price} для {symbol} успешно сохранена.")
        except Exception as e:
            logging.error(f"Ошибка при сохранении цены: {e}")
            session.rollback()
        finally:
            self.clear_old_prices()
            session.close()

    def clear_old_prices(self) -> None:
        """Очистка таблицы цен, если данные старше одного часа."""
        session = self.get_session()
        try:
            threshold_time = datetime.now() - timedelta(hours=1)
            deleted_count = session.query(Price).filter(Price.timestamp < threshold_time).delete(
                synchronize_session=False)
            session.commit()
            logging.info(f"Удалено {deleted_count} старых цен из базы данных.")
        except Exception as e:
            logging.error(f"Ошибка при удалении старых цен: {e}")
            session.rollback()
        finally:
            session.close()

    def check_price_changes(self) -> None:
        """Проверяет, изменилась ли цена на 1% и более."""
        session = self.get_session()
        try:
            prices = session.query(Price).filter(Price.symbol == "ETHUSDT").all()
            if not prices:
                logging.info("Нет данных за последний час.")
                return
            max_price = max(price.price for price in prices)
            min_price = min(price.price for price in prices)
            if min_price > 0:
                price_change_percentage = ((max_price - min_price) / min_price) * 100
                if price_change_percentage > 1:
                    print(
                        f"Изменение в течение часа более 1%: цена изменилась на {price_change_percentage:.2f}%")
        except Exception as e:
            logging.error(f"Ошибка при проверке изменений цен: {e}")
        finally:
            session.close()
