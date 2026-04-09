import feedparser
import sqlite3

def fetch_and_store_episodes(rss_url, db_path):
    feed = feedparser.parse(rss_url)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    count = 0
    for entry in feed.entries:
        # Some feeds use different structures for audio links; links[1] is common for enclosures
        try:
            audio_link = entry.links[1].href
            cursor.execute('''
                INSERT OR IGNORE INTO episodes (id, title, pub_date, link)
                VALUES (?, ?, ?, ?)
            ''', (entry.id, entry.title, entry.published, audio_link))
            count += 1
        except (IndexError, AttributeError):
            continue
    
    conn.commit()
    conn.close()
    print(f"Extracted {count} episodes.")
podcast_pipeline_project/scripts/extract.py
Displaying podcast_pipeline_project/scripts/extract.py.