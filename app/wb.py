import asyncio
import websockets
import json
import logging
from collections import deque

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


async def listenBinanceStreams():
    async with websockets.connect(
            "wss://fstream.binance.com/stream?streams=ethusdt@aggTrade/btcusdt@aggTrade") as wb:
        while True:
            message = await wb.recv()  # Получаем сообщение от WebSocket
            data = json.loads(message)  # Парсим JSON-строку в словарь Python
            if 'data' in data:
                yield data['data']  # Возвращаем только нужные данные


class CryptoFetcher:
    def __init__(self, symbol: str, interval: str = "1m", max_candles: int = 10):
        self.symbol = symbol
        self.interval = interval
        self.max_candles = max_candles
        self.candles = deque(maxlen=max_candles)  # Хранение последних N свечей
        self.current_price = float  # Для хранения текущей цены

    async def fetch_candlesticks(self):
        url = f"wss://fstream.binance.com/ws/{self.symbol.lower()}@kline_{self.interval}"
        async with websockets.connect(url) as websocket:
            logging.info(f"Подключение к WebSocket для {self.symbol} с интервалом {self.interval}...")
            while True:
                try:
                    message = await websocket.recv()
                    data = json.loads(message)
                    kline = data['k']  # Получаем данные о свече

                    # Проверяем, что кline закрылся
                    if kline['x']:  # x = True, если кline завершен
                        candle = {
                            'open_time': kline['t'],
                            'open_price': kline['o'],
                            'high_price': kline['h'],
                            'low_price': kline['l'],
                            'close_price': kline['c'],
                            'close_time': kline['T'],
                        }
                        self.candles.append(candle)
                        logging.info(f"Получена свеча: {candle}")
                        if len(self.candles) >= self.max_candles:
                            logging.info(f"Получено {self.max_candles} свечей. Завершение работы.")
                            break  # Завершение цикла после получения
                except Exception as e:
                    logging.error(f"Ошибка при получении данных: {e}")
                    break

    def get_last_candlesticks(self):
        return list(self.candles)

    def get_price(self):
        """Будем анализировать по цене закрытия"""
        return [float(candle['high_price']) for candle in self.candles]

    async def fetch_price(self):
        url = f"wss://stream.binance.com:9443/ws/{self.symbol.lower()}@ticker"
        async with websockets.connect(url) as websocket:
            logging.info(f"Подключение к WebSocket для получения цены {self.symbol}...")
            while True:
                try:
                    message = await websocket.recv()
                    data = json.loads(message)
                    self.current_price = float(data['c'])  # 'c' - это текущая цена
                    logging.info(f"Текущая цена {self.symbol}: {self.current_price}")
                except Exception as e:
                    logging.error(f"Ошибка при получении цены {self.symbol}: {e}")
