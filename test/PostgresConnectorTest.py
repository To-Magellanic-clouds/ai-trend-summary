import unittest
from unittest.mock import patch, MagicMock
import os
from src.infrastructure.utils.db.PostgresConnector import PostgresConnector

class TestPostgresConnector(unittest.TestCase):

    @patch.dict(os.environ, {
        "POSTGRES_HOST": "localhost",
        "POSTGRES_PORT": "5432",
        "POSTGRES_USER": "testuser",
        "POSTGRES_PASSWORD": "testpassword",
        "POSTGRES_DB": "testdb"
    })
    @patch("psycopg2.connect")
    def test_connect(self, mock_connect):
        connector = PostgresConnector()
        connector.connect()
        mock_connect.assert_called_once_with(
            host="localhost",
            port="5432",
            user="testuser",
            password="testpassword",
            dbname="testdb"
        )

    @patch.dict(os.environ, {
        "POSTGRES_HOST": "localhost",
        "POSTGRES_PORT": "5432",
        "POSTGRES_USER": "testuser",
        "POSTGRES_PASSWORD": "testpassword",
        "POSTGRES_DB": "testdb"
    })
    @patch("psycopg2.connect")
    def test_execute_query(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        connector = PostgresConnector()
        query = "SELECT * FROM test_table"
        connector.execute_query(query)

        mock_cursor.execute.assert_called_once_with(query, None)
        mock_conn.commit.assert_called_once()
        mock_cursor.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()