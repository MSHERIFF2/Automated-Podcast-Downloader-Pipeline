import sqlite3
import logging

logger = logging.getLogger(__name__)

def clean_metadata(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE episodes
        SET title = TRIM(title)
    """)

    conn.commit()
    conn.close()

    logger.info("Metadata cleaned successfully")