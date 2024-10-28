import os
from dotenv import load_dotenv
from app.database import setup_database, get_session, clear_old_prices, save_price_to_db
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
    """Обработка входящего сообщения из веб-сокета."""
    try:
        if "s" in data:
            symbol = data["s"].lower()
            price = float(data["p"])
            if symbol == "ethusdt":
                # Получаем текущую цену ETHUSDT
                current_btc_price = price_analyzer.btc_prices[-1] if price_analyzer.btc_prices else None
                if price_analyzer.should_record_eth_price(price, current_btc_price):

                    save_price_to_db(session, price)  # Запись цены в БД
            elif symbol == "btcusdt":
                # Обновляем цену BTCUSDT
                print(f"цена BTC {price}")
                price_analyzer.btc_prices.append(price)

    except Exception:
        pass  # Игнорируем ошибки


def main():
    """Основная функция."""
    load_dotenv()
    database_url = os.getenv("DATABASE_URL")
    if database_url is None:
        raise ValueError("DATABASE_URL is not set in the environment variables.")

    session = check_database_connection(database_url)
    if session is None:
        return  # Если не удалось подключиться, завершаем выполнение

    # Очистка старых данных перед началом работы
    clear_old_prices(session)
    price_analyzer = PriceAnalyzer()  # Инициализация анализатора цен

    # Запуск веб-сокета
    websocket_client = BinanceWebSocket(lambda data: handle_message(data, price_analyzer, session))

    # Получение цены ETH после начала работы веб-сокета
    try:
        websocket_client.run()
    except Exception:
        pass  # Игнорируем ошибки
    finally:
        # Вывод текущей цены ETH на момент завершения программы
        final_price = price_analyzer.get_current_price()
        # min_price = price_analyzer.check_price_change()
        # max_price =

        print(f"Цена ETH на момент завершения программы: {final_price}")
        # print(f"Минимальная цена ETH за последний час: {min_price}")
        # print(f"Максимальная цена ETH за последний час: {max_price}")

        session.close()  # Закрытие сессии базы данных


if __name__ == "__main__":
    print("Запуск программы...")
    main()  # Запуск основной функции

