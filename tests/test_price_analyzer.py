import unittest
from unittest.mock import MagicMock, patch
from app.models import DatabaseManager, Price  # Предполагаем, что эти классы уже существуют
from app.price_analyzer import EthPriceAnalyzer
from datetime import timedelta

class TestEthPriceAnalyzer(unittest.TestCase):
    def setUp(self):
        # Создаем поддельный экземпляр DatabaseManager
        self.db_manager = MagicMock(spec=DatabaseManager)
        self.eth_price_analyzer = EthPriceAnalyzer(self.db_manager)

    @patch('app.price_analyzer.datetime')
    def test_analyze_price_influence(self, mock_datetime):
        # Настраиваем mock для получения данных
        mock_datetime.now.return_value = mock_datetime(2023, 10, 1, 12, 0, 0)
        mock_datetime.timedelta = timedelta

        # Поддельные данные для ETH и BTC
        self.db_manager.get_session.return_value.query.return_value.filter.return_value.all.side_effect = [
            [Price(timestamp=mock_datetime(2023, 10, 1, 11, 59, 0), price=3000.0),
             Price(timestamp=mock_datetime(2023, 10, 1, 12, 0, 0), price=3050.0)],
            [Price(timestamp=mock_datetime(2023, 10, 1, 11, 59, 0), price=45000.0),
             Price(timestamp=mock_datetime(2023, 10, 1, 12, 0, 0), price=45500.0)]
        ]

        correlation = self.eth_price_analyzer.analyze_price_influence(eth_symbol='ETHUSDT', btc_symbol='BTCUSDT',
                                                                      lookback_period=60)

        # Проверяем, что корреляция возвращается и больше 0
        self.assertIsNotNone(correlation)
        self.assertGreater(correlation, 0)

    @patch('app.price_analyzer.datetime')
    def test_calculate_adjusted_eth_prices(self, mock_datetime):
        # Настраиваем mock для получения данных
        mock_datetime.now.return_value = mock_datetime(2023, 10, 1, 12, 0, 0)
        mock_datetime.timedelta = timedelta

        # Поддельные данные для ETH и BTC
        self.db_manager.get_session.return_value.query.return_value.filter.return_value.all.side_effect = [
            [Price(timestamp=mock_datetime(2023, 10, 1, 11, 59, 0), price=3000.0),
             Price(timestamp=mock_datetime(2023, 10, 1, 12, 0, 0), price=3050.0)],
            [Price(timestamp=mock_datetime(2023, 10, 1, 11, 59, 0), price=45000.0),
             Price(timestamp=mock_datetime(2023, 10, 1, 12, 0, 0), price=45500.0)]
        ]

        # Устанавливаем корреляцию для теста
        self.eth_price_analyzer.analyze_price_influence = MagicMock(return_value=0.8)

        adjusted_prices = self.eth_price_analyzer.calculate_adjusted_eth_prices(eth_symbol='ETHUSDT',
                                                                                btc_symbol='BTCUSDT',
                                                                                lookback_period=10)

        # Проверяем, что скорректированные цены возвращаются и не пустые
        self.assertTrue(len(adjusted_prices) > 0)

        # Проверяем, что обновление цен произошло
        self.db_manager.get_session.return_value.commit.assert_called_once()


if __name__ == '__main__':
    unittest.main()
