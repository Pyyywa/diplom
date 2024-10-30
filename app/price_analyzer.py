import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta


class PriceProcessor:
    def __init__(self):
        self.eth_prices = []
        self.btc_prices = []
        self.timestamp = []

    def add_eth_price(self, price: float, timestamp: datetime = None) -> None:
        """Добавление цены ETH в список."""
        if timestamp is None:
            timestamp = datetime.now()
        self.eth_prices.append((timestamp, price))
        self.remove_old_data(timestamp)

    def add_btc_price(self, price: float, timestamp: datetime = None) -> None:
        """Добавление цены BTC в список."""
        if timestamp is None:
            timestamp = datetime.now()
        self.btc_prices.append((timestamp, price))
        self.remove_old_data(timestamp)

    def remove_old_data(self, current_time: datetime) -> None:
        """Удаление старых данных (старше 60 минут)."""
        one_hour_ago = current_time - timedelta(hours=1)
        self.eth_prices = [p for p in self.eth_prices if p[0] >= one_hour_ago]
        self.btc_prices = [p for p in self.btc_prices if p[0] >= one_hour_ago]

    def process_prices(self) -> None:
        """Исключение влияния цены BTC на цену ETH."""
        if len(self.eth_prices) < 2 or len(self.btc_prices) < 2:
            return  # Недостаточно данных для анализа

        # Удаление цен с одинаковыми временными метками
        unique_eth_prices = []
        unique_btc_prices = []
        eth_dict = {p[0]: p[1] for p in self.eth_prices}
        btc_dict = {p[0]: p[1] for p in self.btc_prices}

        # Подготовка данных для линейной регрессии
        eth_prices_array = np.array([price[1] for price in self.eth_prices]).reshape(-1, 1)
        btc_prices_array = np.array([price[1] for price in self.btc_prices]).reshape(-1, 1)

        # Создание модели линейной регрессии
        model = LinearRegression()
        model.fit(btc_prices_array, eth_prices_array)

        # Предсказание цен ETH на основе цен BTC
        predicted_eth_prices = model.predict(btc_prices_array)

        # Удаление влияния BTC
        self.eth_prices = [(timestamp, eth_price - predicted[0]) for (timestamp, eth_price), predicted in
                           zip(self.eth_prices, predicted_eth_prices)]

    def get_processed_prices(self):
        """Получение обработанных цен ETH без влияния BTC."""
        return [price for _, price in self.eth_prices]  # Возвращаем только цены
