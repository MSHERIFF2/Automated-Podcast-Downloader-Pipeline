import sqlite3

def clean_metadata(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE episodes
        SET title = TRIM(title)
    """)

    conn.commit()
    conn.close()

    print("Metadata cleaned")