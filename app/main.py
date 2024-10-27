import os
from dotenv import load_dotenv
from app.database import setup_database, get_session, save_price_to_db
from app.websocket_client import BinanceWebSocket
from app.price_analyzer import PriceAnalyzer


def check_database_connection(database_url):
    """Проверка подключения к базе данных."""
    try:
        engine = setup_database(database_url)
        session = get_session(engine)
        print("Подключение к базе данных успешно.")
        return session
    except Exception as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return None


def handle_message(data, price_analyzer, session):
    """Обработка сообщений из веб-сокета."""
    if "s" in data:
        symbol = data["s"].lower()
        price = float(data["p"])
        if symbol == "ethusdt":
            price_analyzer.add_price(price)
            save_price_to_db(session, price)  # Запись цены в БД

            # Вывод текущей цены при первом получении
            if len(price_analyzer.eth_prices) == 1:
                print(f"Текущая цена ETH: {price}")

            # Проверка изменения цены
            if price_analyzer.check_price_change():
                print(f"Цена ETH изменилась на 1% или более: {price}")


def main():
    load_dotenv()
    database_url = os.getenv("DATABASE_URL")
    if database_url is None:
        raise ValueError("DATABASE_URL is not set in the environment variables.")

    session = check_database_connection(database_url)
    if session is None:
        return

    price_analyzer = PriceAnalyzer()  # Инициализация анализатора цен

    # Запуск веб-сокета
    websocket_client = BinanceWebSocket(lambda data: handle_message(data, price_analyzer, session))
    try:
        websocket_client.run()
    except Exception as e:
        print(f"Ошибка подключения к веб-сокету: {e}")


if __name__ == "__main__":
    main()