import sqlite3

def clean_metadata(db_path):
    # Example transform: ensure titles are stripped of excess whitespace
    # or filter out episodes without valid mp3 links
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("UPDATE episodes SET title = TRIM(title)")
    conn.commit()
    conn.close()
    print("Metadata transformed/cleaned.")
podcast_pipeline_project/scripts/transform.py
Displaying podcast_pipeline_project/scripts/transform.py.