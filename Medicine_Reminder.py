import logging
import pandas as pd
import sqlalchemy
import re
from sqlalchemy import create_engine, Table, MetaData, select, update
from sqlalchemy.orm import sessionmaker
import pytest
import subprocess

# Set up logging
logging.basicConfig(filename='Med_Reminder.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info("Script has started running.")

# Connect to SQL database
server = 'localhost'
database = 'Time_for_medicine'
driver = 'ODBC Driver 17 for SQL Server'
connection_string = f"mssql+pyodbc://@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server"
engine = create_engine(connection_string)
Session = sessionmaker(bind = engine)
session = Session()

# Run pytest to check if connection is established
result = subprocess.run(['pytest', 'test_sql_connection.py'], capture_output=True, text=True)

# Kontrollera om testet har passerat
if 'passed' in result.stdout:
    # Skriv ut loggmeddelandet
    logger.info("Connected to the database successfully!")
else:
    # Skriv ut ett felmeddelande
    logger.error("Failed to connect to the database")

# Load table metadata
metadata = MetaData(schema='dbo')
patients = Table('Patient_info', metadata, autoload_with=engine)

try:
    # Check if the table's columns have been loaded
    if patients.columns:
        logger.info("Table columns have been loaded successfully!")
        logger.info("Columns: %s", [column.name for column in patients.columns])
    else:
        logger.error("Failed to load table columns!")
except Exception as e:
    logger.error("Failed to load table metadata: %s", e)
    
# Execute medication distribution and update the total amount in stock

query = select(patients)
result = session.execute(query)
rows = result.fetchall()

for row in rows:
    medicine_name = row[2]    # column with ordinal position 3 ('medicine')
    dosage_required = row[3]  # column with ordinal position 4 ('dosage')
    patient_name = row[1]     # column with ordinal position 2 ('name')
    total_amount = row[4]     # column with ordinal position 5 ('total')

    try:
        if total_amount < dosage_required:
            logger.warning(f"Not enough {medicine_name} in stock. Current stock: {total_amount}")
        else:
            logger.info(f"Enough {medicine_name} in stock. Current stock: {total_amount}")
            total_amount = total_amount - dosage_required
            logger.info(f"Medicine {medicine_name} has been dispensed to patient {patient_name}")
            logger.info(f"Total amount of {medicine_name} in stock is: {total_amount}")

            # Uppdatera total_amount i tabellen
            update_query = update(patients).where(patients.c.name == patient_name).values(total = total_amount)
            session.execute(update_query)
            session.commit()
            
    except Exception as e:
        logger.error(f"Error processing patient {patient_name}: {e}")

session.close()
logger.info(f"Execution completed!")