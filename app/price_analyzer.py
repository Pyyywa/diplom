from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import statsmodels.api as sm


class PriceAnalyzer:
    def __init__(self):
        self.eth_prices = []  # Список для хранения цен ETH
        self.btc_prices = []  # Список для хранения цен BTC
        self.timestamps = []  # Список для хранения временных меток

    def clean_old_prices(self):
        """Удаление цен и временных меток старше 60 минут."""
        current_time = datetime.now()
        old_index = 0
        while old_index < len(self.timestamps) and self.timestamps[old_index] < current_time - timedelta(minutes=60):
            old_index += 1
        self.eth_prices = self.eth_prices[old_index:]
        self.btc_prices = self.btc_prices[old_index:]
        self.timestamps = self.timestamps[old_index:]

    def check_price_change(self):
        """Проверка изменения цены на 1% за последние 60 минут относительно всех значений."""
        if len(self.eth_prices) < 2:
            return False  # Не хватает данных для проверки

        current_price = self.eth_prices[-1]  # Текущая цена
        min_price = min(self.eth_prices)  # Минимальная цена за последний час
        max_price = max(self.eth_prices)  # Максимальная цена за последний час
        # Проверка изменения относительно минимальной и максимальной цены
        min_change_percentage = ((current_price - min_price) / min_price) * 100
        max_change_percentage = ((current_price - max_price) / max_price) * 100
        return abs(min_change_percentage) >= 1 or abs(max_change_percentage) >= 1


    def should_record_eth_price(self, current_eth_price, current_btc_price):
        """Проверка, следует ли записывать цену ETH в БД, исключая влияние BTC."""
        if len(self.eth_prices) < 2 or len(self.btc_prices) < 2:
            return True  # Если нет достаточных данных, записываем ETH

        # Исключение влияния BTC на ETH
        adjusted_eth_price = self.remove_btc_influence(self.eth_prices, self.btc_prices)
        self.eth_prices.append(adjusted_eth_price[-1])  # Записываем скорректированную цену ETH
        return True

    def remove_btc_influence(self, eth_prices, btc_prices):
        """Исключение влияния цены BTC на цену ETH с использованием линейной регрессии."""
        # Проверка, что длины списков совпадают
        if len(eth_prices) != len(btc_prices):
            raise ValueError("Длины списков eth_prices и btc_prices должны совпадать.")

        # Создание DataFrame для удобства работы
        data = pd.DataFrame({
            'ETH': eth_prices,
            'BTC': btc_prices
        })

        # Удаление строк с NaN значениями (если есть)
        data = data.dropna()

        # Определение зависимой переменной (ETH) и независимой (BTC)
        X = data['BTC']
        y = data['ETH']

        # Добавление константы для регрессионной модели
        X = sm.add_constant(X)

        # Построение модели линейной регрессии
        model = sm.OLS(y, X).fit()

        # Получение предсказанных значений ETH на основе модели
        predictions = model.predict(X)

        # Возвращаем скорректированные цены ETH, исключая влияние BTC
        adjusted_eth_prices = y - predictions + np.mean(predictions)  # Центрируем предсказания
        return adjusted_eth_prices.tolist()
