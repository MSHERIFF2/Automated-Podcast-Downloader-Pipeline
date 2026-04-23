from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import sys
import os

# add scripts folder
sys.path.append('/home/your-user/Automated-Podcast-Downloader-Pipeline/scripts')

from extract import fetch_and_store_episodes
from transform import clean_metadata
from load import download_new_episodes

DB_PATH = '/home/your-user/Automated-Podcast-Downloader-Pipeline/data/audio/podcast.db'
DOWNLOAD_PATH = '/home/your-user/Automated-Podcast-Downloader-Pipeline/data/audio'
RSS_URL = 'https://podcasts.files.bbci.co.uk/p02nq0gn.rss'

default_args = {
    "owner": "airflow",
    "start_date": datetime(2024, 1, 1),
    "retries": 1
}

def init_db():
    import sqlite3
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS episodes (
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
    dag_id="podcast_etl_pipeline",
    default_args=default_args,
    schedule="@daily",
    catchup=False
) as dag:

    setup = PythonOperator(
        task_id="init_db",
        python_callable=init_db
    )

    extract_task = PythonOperator(
        task_id="extract_episodes",
        python_callable=fetch_and_store_episodes,
        op_kwargs={"rss_url": RSS_URL, "db_path": DB_PATH}
    )

    transform_task = PythonOperator(
        task_id="transform_metadata",
        python_callable=clean_metadata,
        op_kwargs={"db_path": DB_PATH}
    )

    load_task = PythonOperator(
        task_id="download_audio",
        python_callable=download_new_episodes,
        op_kwargs={"db_path": DB_PATH, "download_path": DOWNLOAD_PATH}
    )

    setup >> extract_task >> transform_task >> load_task