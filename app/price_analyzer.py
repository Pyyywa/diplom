import logging
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from sqlalchemy import func
from app.models import Price, AdjustedPrice


class EthPriceAnalyzer:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def analyze_price_influence(self, eth_symbol='ETHUSDT', btc_symbol='BTCUSDT', lookback_period=10):
        """Анализирует влияние цены BTCUSDT на цену ETHUSDT за указанный период (в минутах)."""
        session = self.db_manager.get_session()
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(minutes=lookback_period)

            # Получаем данные цен ETH и BTC за указанный период
            eth_prices = session.query(Price).filter(
                Price.symbol == eth_symbol,
                Price.timestamp >= start_time,
                Price.timestamp <= end_time
            ).all()

            btc_prices = session.query(Price).filter(
                Price.symbol == btc_symbol,
                Price.timestamp >= start_time,
                Price.timestamp <= end_time
            ).all()

            if not eth_prices or not btc_prices:
                logging.info("Недостаточно данных для анализа.")
                return None

            # Извлекаем цены и временные метки
            eth_data = [(price.timestamp, price.price) for price in eth_prices]
            btc_data = [(price.timestamp, price.price) for price in btc_prices]

            # Объединяем данные по времени
            combined_data = {}
            for timestamp, price in eth_data:
                combined_data[timestamp] = {'eth_price': price, 'btc_price': None}
            for timestamp, price in btc_data:
                if timestamp in combined_data:
                    combined_data[timestamp]['btc_price'] = price

            # Убираем записи, где отсутствует цена BTC
            filtered_data = [(data['eth_price'], data['btc_price']) for data in combined_data.values() if
                             data['btc_price'] is not None]
            if not filtered_data:
                logging.info("Нет совпадающих данных для анализа.")
                return None

            eth_prices, btc_prices = zip(*filtered_data)

            # Вычисляем корреляцию
            correlation = self.calculate_correlation(eth_prices, btc_prices)
            logging.info(f"Корреляция между ценами {eth_symbol} и {btc_symbol}: {correlation:.2f}")
            return correlation

        except Exception as e:
            logging.error(f"Ошибка при анализе влияния цен: {e}")
            return None
        finally:
            session.close()

    @staticmethod
    def calculate_correlation(x, y):
        """Вычисляет корреляцию между двумя списками."""
        if len(x) != len(y):
            raise ValueError("Длины списков должны совпадать.")
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        sum_x_squared = sum(xi ** 2 for xi in x)
        sum_y_squared = sum(yi ** 2 for yi in y)

        # Формула для вычисления корреляции
        numerator = n * sum_xy - sum_x * sum_y
        denominator = ((n * sum_x_squared - sum_x ** 2) * (n * sum_y_squared - sum_y ** 2)) ** 0.5
        return numerator / denominator if denominator != 0 else 0  # Избегаем деления на ноль

    def calculate_adjusted_eth_prices(self, eth_symbol='ETHUSDT', btc_symbol='BTCUSDT', lookback_period=10):
        """Корректирует цены ETH на основе влияния цен BTC и сохраняет их в отдельной таблице."""
        correlation = self.analyze_price_influence(eth_symbol, btc_symbol, lookback_period)
        session = self.db_manager.get_session()

        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(minutes=lookback_period)

            # Получаем данные цен ETH за указанный период
            eth_prices = session.query(Price).filter(
                Price.symbol == eth_symbol,
                Price.timestamp >= start_time,
                Price.timestamp <= end_time
            ).all()

            if not eth_prices:
                logging.info("Недостаточно данных для анализа.")
                return []

            # Извлекаем цены ETH и их временные метки
            adjusted_prices = []
            for price in eth_prices:
                if correlation is not None and abs(correlation) > 0.5:  # Условие для высокой корреляции
                    adjusted_price = price.price * (1 - abs(correlation))  # Корректируем цену
                else:
                    adjusted_price = price.price  # Оставляем цену без изменений

                # Добавляем скорректированную цену в список
                adjusted_prices.append((price.timestamp, eth_symbol, adjusted_price))

            # Записываем скорректированные цены в таблицу adjusted_prices
            for timestamp, symbol, adjusted_price in adjusted_prices:
                new_adjusted_price = AdjustedPrice(timestamp=timestamp, symbol=symbol, adjusted_price=adjusted_price)
                session.add(new_adjusted_price)

            session.commit()  # Сохраняем изменения
            logging.info(f"Скорректированные цены ETH записаны в таблицу: {adjusted_prices}")
            return adjusted_prices

        except Exception as e:
            logging.error(f"Ошибка при вычислении скорректированных цен ETH: {e}")
            return []

        finally:
            session.close()
