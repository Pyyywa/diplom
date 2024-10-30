import os
import logging
import asyncio
from dotenv import load_dotenv
from app.models import DatabaseManager, AdjustedPrice
from app.wb import listenBinanceStreams
from app.price_analyzer import EthPriceAnalyzer

# Настройка логирования
logging.basicConfig(level=logging.INFO)


async def main():
    """Основная функция."""
    load_dotenv()
    database_url = os.getenv("DATABASE_URL")
    if database_url is None:
        raise ValueError("DATABASE_URL is not set in the environment variables.")

    # Создаем экземпляр DatabaseManager
    db_manager = DatabaseManager(database_url)
    adjusted = AdjustedPrice()

    # Создаем экземпляр EthPriceAnalyzer
    eth_price_analyzer = EthPriceAnalyzer(db_manager)

    # Запуск веб-сокета
    try:
        logging.info("Запуск веб-сокета...")
        async for data in listenBinanceStreams():
            symbol = data['s']  # Получаем символ
            price = float(data['p'])  # Получаем цену и преобразуем в float
            logging.info(f"Symbol: {symbol}, Price: {price}")  # Выводим символ и цену

            # Сохраняем цену в базу данных
            db_manager.save_price(symbol, price)

            # Если символ ETHUSDT, анализируем влияние на цену ETH
            if symbol == 'ETHUSDT':
                correlation = eth_price_analyzer.analyze_price_influence()
                if correlation is not None:  # Проверяем, не является ли correlation None
                    logging.info(f"Корреляция между BTC и ETH: {correlation:.2f}")

                    # Вычисляем и сохраняем скорректированные цены ETH
                    adjusted_prices = eth_price_analyzer.calculate_adjusted_eth_prices()
                    if adjusted_prices:
                        logging.info(f"Скорректированные цены ETH записаны: {adjusted_prices}")
                    else:
                        logging.info("Нет скорректированных цен для записи.")
                else:
                    logging.info("Не удалось вычислить корреляцию.")



    except Exception as e:
        logging.error(f"An error occurred: {e}")


if __name__ == "__main__":
    logging.info("Запуск программы...")
    asyncio.run(main())  # Запуск основной функции
