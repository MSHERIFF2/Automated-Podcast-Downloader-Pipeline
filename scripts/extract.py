import feedparser
import sqlite3

def fetch_and_store_episodes(rss_url, db_path):
    feed = feedparser.parse(rss_url)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    count = 0

    for entry in feed.entries:
        try:
            audio_link = entry.links[1].href

            cursor.execute("""
                INSERT OR IGNORE INTO episodes (id, title, pub_date, link)
                VALUES (?, ?, ?, ?)
            """, (entry.id, entry.title, entry.published, audio_link))

            count += 1
        except Exception:
            continue

    conn.commit()
    conn.close()

    print(f"Extracted {count} episodes")