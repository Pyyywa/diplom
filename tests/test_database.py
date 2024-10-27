import unittest
from unittest.mock import MagicMock
from app.database import save_price_to_db


class TestDatabaseFunctions(unittest.TestCase):
    def setUp(self):
        self.session = MagicMock()  # Создаем мок для сессии

    def test_save_price_to_db_success(self):
        save_price_to_db(self.session, 2000)
        self.session.add.assert_called_once()  # Проверяем, что add был вызван
        self.session.commit.assert_called_once()  # Проверяем, что commit был вызван

    def test_save_price_to_db_failure(self):
        self.session.add.side_effect = Exception("Database error")
        save_price_to_db(self.session, 2000)
        self.session.rollback.assert_called_once()  # Проверяем, что rollback был вызван


if __name__ == "__main__":
    unittest.main()
