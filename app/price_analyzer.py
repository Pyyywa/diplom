from datetime import datetime, timedelta

class PriceAnalyzer:
    def __init__(self):
        self.eth_prices = []  # Список для хранения цен ETH
        self.timestamps = []  # Список для хранения временных меток

    def add_price(self, eth_price):
        """Добавление цены ETH в список с текущей временной меткой."""
        self.eth_prices.append(eth_price)
        self.timestamps.append(datetime.now())
        self.clean_old_prices()

    def clean_old_prices(self):
        """Удаление цен и временных меток старше 60 минут."""
        current_time = datetime.now()
        while self.timestamps and self.timestamps[0] < current_time - timedelta(minutes=60):
            self.timestamps.pop(0)
            self.eth_prices.pop(0)

    def check_price_change(self):
        """Проверка изменения цены на 1% за последние 60 минут относительно всех значений."""
        if len(self.eth_prices) < 2:
            return False  # Не хватает данных для проверки
        current_price = self.eth_prices[-1]
        min_price = min(self.eth_prices)  # Минимальная цена за последний час
        max_price = max(self.eth_prices)  # Максимальная цена за последний час

        # Проверка изменения относительно минимальной и максимальной цены
        min_change_percentage = ((current_price - min_price) / min_price) * 100
        max_change_percentage = ((current_price - max_price) / max_price) * 100
        return abs(min_change_percentage) >= 1 or abs(max_change_percentage) >= 1

    def get_current_price(self):
        """Получение текущей цены ETH."""
        return self.eth_prices[-1] if self.eth_prices else None
