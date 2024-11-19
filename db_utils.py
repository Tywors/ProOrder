
import sqlite3
import os

def create_database(force_new=True):
    db_path = 'file_organizer.db'
    
    # Si force_new es True y la base de datos existe, la eliminamos
    if force_new and os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY,
        file_path TEXT NOT NULL,
        file_name TEXT NOT NULL,
        ext TEXT NOT NULL,
        mod_time TEXT NOT NULL,
        creation_time TEXT NOT NULL,
        resolution TEXT NOT NULL,
        hash TEXT,
        name_date TEXT
    )
    ''')
    conn.commit()
    conn.close()

def store_file_info(file_info_batch):
    conn = sqlite3.connect('file_organizer.db')
    cursor = conn.cursor()
    cursor.executemany('INSERT INTO files (file_path, file_name, ext, mod_time, creation_time, resolution, hash, name_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', file_info_batch)
    conn.commit()
    conn.close()