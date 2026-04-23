from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import sys
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
sys.path.append(SCRIPTS_DIR)

from extract import fetch_and_store_episodes
from transform import clean_metadata
from load import download_new_episodes

DB_PATH = os.path.join(BASE_DIR, "data/audio/podcast_metadata.db")
DOWNLOAD_PATH = os.path.join(BASE_DIR, "data/audio")

RSS_URL = "https://podcasts.files.bbci.co.uk/p02nq0gn.rss"

default_args = {
    "owner": "airflow",
    "start_date": datetime(2024,1,1),
    "retries": 1
}

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS episodes(
        id TEXT PRIMARY KEY,
        title TEXT,
        pub_date TEXT,
        link TEXT,
        downloaded INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()

with DAG(
    dag_id="podcast_etl_modular",
    default_args=default_args,
    schedule="@daily",
    catchup=False
) as dag:

    setup = PythonOperator(
        task_id="setup_db",
        python_callable=init_db
    )

    extract_task = PythonOperator(
        task_id="extract",
        python_callable=fetch_and_store_episodes,
        op_kwargs={"rss_url": RSS_URL, "db_path": DB_PATH}
    )

    transform_task = PythonOperator(
        task_id="transform",
        python_callable=clean_metadata,
        op_kwargs={"db_path": DB_PATH}
    )

    load_task = PythonOperator(
        task_id="load",
        python_callable=download_new_episodes,
        op_kwargs={"db_path": DB_PATH, "download_path": DOWNLOAD_PATH}
    )

    setup >> extract_task >> transform_task >> load_task