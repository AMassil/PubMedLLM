import unittest
from unittest.mock import patch

from pubmedllm.database import Database


class DatabaseTests(unittest.TestCase):
    def test_connection_urls_escape_credentials(self):
        with (
            patch("pubmedllm.database.Config.DB_USER", "test user"),
            patch("pubmedllm.database.Config.DB_PASSWORD", "p@ss/word"),
            patch("pubmedllm.database.Config.DB_HOST", "localhost"),
            patch("pubmedllm.database.Config.DB_PORT", "5432"),
            patch("pubmedllm.database.Config.DB_NAME", "pubmedllm"),
        ):
            sqlalchemy_url = Database.get_connection_string()
            psycopg_url = Database.get_psycopg_connection_string()

        self.assertEqual(
            sqlalchemy_url,
            "postgresql+psycopg://test%20user:p%40ss%2Fword@localhost:5432/pubmedllm",
        )
        self.assertEqual(
            psycopg_url,
            "postgresql://test%20user:p%40ss%2Fword@localhost:5432/pubmedllm",
        )


if __name__ == "__main__":
    unittest.main()