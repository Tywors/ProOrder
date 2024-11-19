# duplicate_finder.py

import sqlite3

def find_duplicates():
    conn = sqlite3.connect('image_organizer.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT hash, COUNT(*)
    FROM images
    GROUP BY hash
    HAVING COUNT(*) > 1
    ''')

    duplicates = cursor.fetchall()

    duplicate_paths = []
    for hash_value, count in duplicates:
        cursor.execute('SELECT file_path FROM images WHERE hash = ?', (hash_value,))
        paths = cursor.fetchall()
        duplicate_paths.append((hash_value, [path[0] for path in paths]))

    conn.close()
    return duplicate_paths

def display_duplicates():
    duplicates = find_duplicates()
    for hash_value, paths in duplicates:
        print(f"Hash: {hash_value}")
        for path in paths:
            print(f"  {path}")
        print("\n")

# Ejemplo de uso
if __name__ == "__main__":
    display_duplicates()
