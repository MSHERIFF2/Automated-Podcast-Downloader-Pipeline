import os
import requests
import sqlite3

def download_new_episodes(db_path, download_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, link FROM episodes WHERE downloaded = 0 LIMIT 2')
    rows = cursor.fetchall()
    
    if not os.path.exists(download_path):
        os.makedirs(download_path)
        
    for row in rows:
        ep_id, link = row
        # Create a safe filename
        file_name = f"{ep_id.split('/')[-1].split('?')[0]}.mp3"
        if not file_name.endswith('.mp3'):
            file_name += '.mp3'
            
        print(f"Downloading: {file_name}")
        try:
            r = requests.get(link, timeout=10)
            with open(os.path.join(download_path, file_name), 'wb') as f:
                f.write(r.content)
            
            cursor.execute('UPDATE episodes SET downloaded = 1 WHERE id = ?', (ep_id,))
        except Exception as e:
            print(f"Failed to download {file_name}: {e}")
        
    conn.commit()
    conn.close()