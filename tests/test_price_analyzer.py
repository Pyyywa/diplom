import unittest
from datetime import datetime, timedelta
from app.price_analyzer import PriceAnalyzer


class TestPriceAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = PriceAnalyzer()

    def test_add_price(self):
        self.analyzer.add_price(2000, 40000)
        self.assertEqual(len(self.analyzer.eth_prices), 1)
        self.assertEqual(len(self.analyzer.btc_prices), 1)
        self.assertEqual(self.analyzer.eth_prices[0], 2000)
        self.assertEqual(self.analyzer.btc_prices[0], 40000)

    def test_clean_old_prices(self):
        # Добавляем цены с временными метками, которые будут очищены
        self.analyzer.timestamps.append(datetime.now() - timedelta(minutes=61))
        self.analyzer.eth_prices.append(2000)
        self.analyzer.btc_prices.append(40000)
        self.analyzer.clean_old_prices()
        self.assertEqual(len(self.analyzer.eth_prices), 0)
        self.assertEqual(len(self.analyzer.btc_prices), 0)

    def test_check_price_change(self):
        # Добавляем цены для тестирования изменения
        self.analyzer.add_price(2000, 40000)
        self.analyzer.add_price(2020, 40500)
        self.assertTrue(self.analyzer.check_price_change())  # Изменение > 1%
        self.analyzer.add_price(2010, 40300)
        self.assertFalse(self.analyzer.check_price_change())  # Изменение < 1%

    def test_should_record_eth_price(self):
        self.analyzer.add_price(2000, 40000)
        self.analyzer.add_price(2020, 40500)
        self.analyzer.add_price(2010, 40300)
        # Проверяем, что запись происходит при низкой корреляции
        self.assertTrue(
            self.analyzer.should_record_eth_price(2015, 40200)
        )  # Низкая корреляция
        # Проверяем, что запись не происходит при высокой корреляции
        self.analyzer.add_price(2040, 41000)
        self.assertFalse(
            self.analyzer.should_record_eth_price(2030, 41050)
        )  # Высокая корреляция


if __name__ == "__main__":
    unittest.main()
