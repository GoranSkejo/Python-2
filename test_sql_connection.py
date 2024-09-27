import pytest
from sqlalchemy import create_engine
import logging

logging.basicConfig(filename='Med_Reminder.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

server = 'localhost'
database = 'Time_for_medicine'
driver = 'ODBC Driver 17 for SQL Server'
connection_string = f"mssql+pyodbc://@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server"
engine = create_engine(connection_string)

def test_database_connection():
    try:
        # Try to connect to the database
        conn = engine.connect()
        logger.debug("Connected to the database successfully!")
        assert conn is not None
    except Exception as e:
        logger.error("Failed to connect to the database: %s", e)
        assert False