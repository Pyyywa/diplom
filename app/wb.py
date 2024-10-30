import asyncio
import websockets
import websocket
import json


async def listenBinanceStreams():
    async with websockets.connect("wss://fstream.binance.com/stream?streams=ethusdt@aggTrade/btcusdt@aggTrade") as wb:
        while True:
            message = await wb.recv()  # Получаем сообщение от WebSocket
            data = json.loads(message)  # Парсим JSON-строку в словарь Python
            if 'data' in data:
                yield data['data']  # Возвращаем только нужные данные

            await asyncio.sleep(10)  # Задержка на 60 секунд
