import json
import websocket


class BinanceWebSocket:
    def __init__(self, on_message_callback):
        self.on_message_callback = on_message_callback

    def on_message(self, ws, message):
        """Обработка входящего сообщения."""
        data = json.loads(message)
        self.on_message_callback(data)

    def run(self):
        """Запуск веб-сокета."""
        ws = websocket.WebSocketApp(
            "wss://fstream.binance.com/stream?streams=ethusdt@aggTrade/btcusdt@aggTrade",
            on_message=self.on_message,
        )
        ws.run_forever()


