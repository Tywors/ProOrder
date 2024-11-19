# copy_images.py

import os
import shutil
import sqlite3
from datetime import datetime

def get_month_name(month):
    months = {
        1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
        5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
        9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
    }
    return months.get(month, str(month))

def get_extension_type(ext):
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm', '.mpeg', '.mpg', '.3gp', '.ogg']
    document_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', 
                         '.odt', '.ods', '.odp', '.rtf', '.epub']
    
    ext = ext.lower()
    if ext in image_extensions:
        return "images"
    elif ext in video_extensions:
        return "videos"
    elif ext in document_extensions:
        return "documents"
    return "unknown"

def get_earliest_date(dates):
    valid_dates = [date for date in dates if date]
    if not valid_dates:
        return None
    return min(datetime.fromisoformat(date) for date in valid_dates).date()

def get_date_path(config, date):
    if not date:
        return "No_dates"
    
    year = str(date.year)
    month = get_month_name(date.month) if config["string_date"] == "Nombre" else f"{date.month:02d}"
    
    if config["order_date"] == "Año - Mes - Dia":
        return os.path.join(year, month, f"{date.day:02d}")
    else:  # "Año - Mes"
        return os.path.join(year, month)

def start_organizing(dest_folder, order_date, string_date, format_at_root, agrupar_formatos):
    # Crear el diccionario de configuración
    config = {
        "order_date": order_date,
        "string_date": string_date,
        "format_at_root": format_at_root,
        "extra_nsfw": False,  # Por ahora lo dejamos fijo
        "agrupar_formatos": agrupar_formatos
    }
    
    conn = sqlite3.connect('file_organizer.db')
    cursor = conn.cursor()
    cursor.execute('SELECT file_path, file_name, ext, mod_time, creation_time, name_date FROM files')
    rows = cursor.fetchall()

    for row in rows:
        file_path, file_name, ext, mod_time, creation_time, name_date = row
        earliest_date = get_earliest_date([name_date, mod_time, creation_time])
        
        # Determinar el tipo de archivo
        file_type = get_extension_type(ext)
        
        if config["format_at_root"] == "Cada fecha":
            # Primero la estructura de fechas, luego los formatos
            base_path = get_date_path(config, earliest_date)
            if config["agrupar_formatos"]:
                final_path = os.path.join(dest_folder, base_path)
            else:
                final_path = os.path.join(dest_folder, base_path, file_type)
        else:
            # Primero los formatos, luego la estructura de fechas
            if config["agrupar_formatos"]:
                base_path = ""
            else:
                base_path = file_type
            date_path = get_date_path(config, earliest_date)
            final_path = os.path.join(dest_folder, base_path, date_path)

        # Crear directorios y copiar archivo
        os.makedirs(final_path, exist_ok=True)
        dest_file_path = os.path.join(final_path, os.path.basename(file_path))
        shutil.copy2(file_path, dest_file_path)
        print(f"Copied {file_path} to {dest_file_path}")

    conn.close()
