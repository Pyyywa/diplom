import logging
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, Float, DateTime, String, func, and_
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import numpy as np

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Определение модели данных
Base = declarative_base()


class ETHPriceData(Base):
    __tablename__ = 'price'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    symbol = Column(String)  # 'BTCUSDT' или 'ETHUSDT'
    price = Column(Float)


class DatabaseManager:
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def get_session(self):
        """Возвращает новую сессию базы данных."""
        return self.Session()

    def save_to_price_data(self, symbol: str, price: float) -> None:
        """Сохранение цены в базе данных с текущей временной меткой."""
        session = self.get_session()
        try:
            new_price = ETHPriceData(symbol=symbol, price=price)
            session.add(new_price)
            session.commit()
            logging.info(f"Цена {price} для {symbol} успешно сохранена.")
        except Exception as e:
            logging.error(f"Ошибка при сохранении цены: {e}")
            session.rollback()
        finally:
            session.close()

    def clear_old_prices(self, hours: int) -> None:
        """Очистка таблицы цен, если данные старше указанного количества часов."""
        session = self.get_session()
        try:
            threshold_time = datetime.utcnow() - timedelta(hours=hours)
            deleted_count = session.query(ETHPriceData).filter(ETHPriceData.timestamp < threshold_time).delete(
                synchronize_session=False)
            session.commit()
            logging.info(f"Удалено {deleted_count} старых цен из таблицы {ETHPriceData.__tablename__}.")
        except Exception as e:
            logging.error(f"Ошибка при удалении старых цен: {e}")
            session.rollback()
        finally:
            session.close()

    def check_price_changes(self) -> None:
        """Проверяет, изменилась ли цена на 1% и более."""
        session = self.get_session()
        try:
            prices = session.query(ETHPriceData).all()
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
