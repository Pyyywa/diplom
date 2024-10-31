import os
import logging
import asyncio
import time
from dotenv import load_dotenv
from app.models import DatabaseManager
from app.wb import CryptoFetcher, listenBinanceStreams
from app.price_analyzer import calculate_dependent_movement

# Настройка логирования
# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


async def main():
    """Основная функция."""
    load_dotenv()
    database_url = os.getenv("DATABASE_URL")
    if database_url is None:
        raise ValueError("DATABASE_URL не определена в виртуальном окружении.")

    # Создаем экземпляр DatabaseManager
    db_manager = DatabaseManager(database_url)

    # Получаем свечи для анализа
    btc_fetcher = CryptoFetcher("BTCUSDT", max_candles=2)
    eth_fetcher = CryptoFetcher("ETHUSDT", max_candles=2)

    await asyncio.gather(
        btc_fetcher.fetch_candlesticks(),
        eth_fetcher.fetch_candlesticks()
    )

    btc_prices = btc_fetcher.get_price()
    eth_prices = eth_fetcher.get_price()

    # Проверка типов данных
    logging.info(f"BTC Prices: {btc_prices}, Types: {[type(price) for price in btc_prices]}")
    logging.info(f"ETH Prices: {eth_prices}, Types: {[type(price) for price in eth_prices]}")

    # Находим коэф влияние цены BTC на ETH
    slope, intercept = calculate_dependent_movement(btc_prices, eth_prices)
    logging.info(f"Наклон: {slope}, Пересечение: {intercept}")

    while True:
        # Запускаем потоки получения цен BTC и ETH
        btc_price_task = asyncio.create_task(btc_fetcher.fetch_price())
        eth_price_task = asyncio.create_task(eth_fetcher.fetch_price())

        # Удаляем зависимость для каждого элемента (пример)
        await asyncio.sleep(1)  # Пауза для получения цен

        try:
            if btc_fetcher.current_price is None or eth_fetcher.current_price is None:
                logging.error("Не удалось получить текущие цены.")
                continue  # Пропустить итерацию, если цены не получены

            adjusted_price = float(eth_fetcher.current_price) - (slope * float(btc_fetcher.current_price) + intercept)
            logging.info(f"Скорректированная цена ETH: {adjusted_price}")
            db_manager.save_to_price_data("ETHUSDT", float(adjusted_price))
            db_manager.check_price_changes()
            db_manager.clear_old_prices(1)

        except Exception as e:
            logging.error(f"Ошибка при расчете скорректированной цены: {e}")

    # Завершите потоки получения цен BTC и ETH
    btc_price_task.cancel()
    eth_price_task.cancel()


if __name__ == "__main__":
    asyncio.run(main())
