from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os
import sqlite3

# Add scripts folder to path so Airflow can find our modules
sys.path.append('/workspaces/Automated-Podcast-Downloader-Pipeline/scripts')

from extract import fetch_and_store_episodes
from transform import clean_metadata
from load import download_new_episodes

DB_PATH = '/workspaces/Automated-Podcast-Downloader-Pipeline/data/audio/podcast_metadata.db'
DOWNLOAD_PATH = '/workspaces/Automated-Podcast-Downloader-Pipeline/data/audio/'
RSS_URL = 'https://podcasts.files.bbci.co.uk/p02nq0gn.rss'

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2026, 4, 1),
    'retries': 1,
}

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS episodes (
            id TEXT PRIMARY KEY,
            title TEXT,
            pub_date TEXT,
            link TEXT,
            downloaded INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

with DAG(
    'podcast_etl_modular',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False,
) as dag:

    setup = PythonOperator(
        task_id='setup_db',
        python_callable=init_db
    )

    extract = PythonOperator(
        task_id='extract_episodes',
        python_callable=fetch_and_store_episodes,
        op_kwargs={'rss_url': RSS_URL, 'db_path': DB_PATH}
    )

    transform = PythonOperator(
        task_id='transform_metadata',
        python_callable=clean_metadata,
        op_kwargs={'db_path': DB_PATH}
    )

    load = PythonOperator(
        task_id='load_audio_files',
        python_callable=download_new_episodes,
        op_kwargs={'db_path': DB_PATH, 'download_path': DOWNLOAD_PATH}
    )

    setup >> extract >> transform >> load