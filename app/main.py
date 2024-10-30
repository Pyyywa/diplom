import os
import logging
import asyncio
from dotenv import load_dotenv
from app.database import setup_database, get_session, save_price_to_db
from app.price_analyzer import PriceProcessor
from app.wb import listenBinanceStreams

# Настройка логирования
logging.basicConfig(level=logging.INFO)


def check_database_connection(database_url: str):
    """Проверка подключения к базе данных."""
    try:
        engine = setup_database(database_url)
        session = get_session(engine)
        logging.info("Подключение к базе данных успешно.")
        return session
    except Exception as e:
        logging.error(f"Ошибка подключения к базе данных: {e}")
        return None


async def main():
    """Основная функция."""
    load_dotenv()
    database_url = os.getenv("DATABASE_URL")
    if database_url is None:
        raise ValueError("DATABASE_URL is not set in the environment variables.")

    session = check_database_connection(database_url)
    if session is None:
        return  # Если не удалось подключиться, завершаем выполнение

    processor = PriceProcessor()  # Создаем экземпляр процессора цен

    # Запуск веб-сокета
    try:
        async for data in listenBinanceStreams():
            symbol = data['s']  # Получаем символ
            price = float(data['p'])  # Получаем цену и преобразуем в float
            logging.info(f"Symbol: {symbol}, Price: {price}")  # Выводим символ и цену

            # Добавляем цены в процессор
            if symbol == "ETHUSDT":
                processor.add_eth_price(price)
            elif symbol == "BTCUSDT":
                processor.add_btc_price(price)

            # Обработка цен для исключения влияния BTC на ETH
            processor.process_prices()
            new_ETH_prices = processor.get_processed_prices()
            logging.info(f"Новая цена ETH: {new_ETH_prices}")

            # Сохраняем цену в БД
            save_price_to_db(session, new_ETH_prices, symbol)

    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        session.close()  # Закрываем сессию базы данных


if __name__ == "__main__":
    logging.info("Запуск программы...")
    asyncio.run(main())  # Запуск основной функции
