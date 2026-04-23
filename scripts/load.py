import os
import sqlite3
import requests

def download_new_episodes(db_path, download_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, link FROM episodes WHERE downloaded = 0
    """)

    rows = cursor.fetchall()

    os.makedirs(download_path, exist_ok=True)

    for ep_id, link in rows:
        file_name = ep_id.split("/")[-1].split("?")[0] + ".mp3"
        file_path = os.path.join(download_path, file_name)

        try:
            print(f"Downloading {file_name}")

            response = requests.get(link, timeout=15)

            with open(file_path, "wb") as f:
                f.write(response.content)

            cursor.execute("""
                UPDATE episodes SET downloaded = 1 WHERE id = ?
            """, (ep_id,))

        except Exception as e:
            print(f"Failed: {file_name} -> {e}")

    conn.commit()
    conn.close()