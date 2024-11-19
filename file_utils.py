# image_utils.py

import os
import hashlib
from datetime import datetime
from PIL import Image
import re

image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']
video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm', '.mpeg', '.mpg', '.3gp', '.ogg']
document_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.odt', '.ods', '.odp', '.rtf', '.epub']

def find_files(directory):
    # Expresiones regulares generales para buscar fechas en nombres de archivo
    date_patterns = [
        r'(\d{4})[-_]?(\d{2})[-_]?(\d{2})',  # AñoMesDía
        r'(\d{2})[-_]?(\d{2})[-_]?(\d{4})',  # DíaMesAño
        r'(\d{2})[-_]?(\d{2})[-_]?(\d{2})'   # AñoMesDía o DíaMesAño en formato corto
    ]

    def convert_short_year(year):
        year = int(year)
        if 0 <= year <= 69:
            return 2000 + year
        elif 70 <= year <= 99:
            return 1900 + year
        else:
            return year

    def extract_date_from_filename(filename):
        for pattern in date_patterns:
            match = re.search(pattern, filename)
            if match:
                groups = match.groups()
                if len(groups) == 3:
                    part1, part2, part3 = groups
                    # Determinar si el formato es AñoMesDía o DíaMesAño
                    if len(part3) == 4:  # DíaMesAño
                        day, month, year = part1, part2, part3
                    elif len(part1) == 4:  # AñoMesDía
                        year, month, day = part1, part2, part3
                    else:  # Formato corto
                        if int(part3) > 31:  # Asumimos AñoMesDía
                            year, month, day = part3, part2, part1
                        else:  # Asumimos DíaMesAño
                            day, month, year = part1, part2, part3
                            year = convert_short_year(year)
                    year = convert_short_year(year)
                    try:
                        date = datetime(year, int(month), int(day)).date()
                        if date.year >= 1970 and date.year <= 2030:
                            return date.isoformat()
                    except ValueError:
                        continue
        return None

    for root, _, files in os.walk(directory):
        for file in files:
            ext = os.path.splitext(file)[1].lower() or "unknown"
            if any(file.lower().endswith(ext) for ext in image_extensions):
                full_path = os.path.join(root, file)
                mod_time = datetime.fromtimestamp(os.path.getmtime(full_path)).date().isoformat()
                creation_time = datetime.fromtimestamp(os.path.getctime(full_path)).date().isoformat()
                name_date = extract_date_from_filename(file)
                try:
                    with Image.open(full_path) as img:
                        width, height = img.size
                        resolution = f"{width}x{height}"
                except Exception as e:
                    print(f"Error al obtener la resolución de la imagen {full_path}: {e}")
                    resolution = "unknown"
                yield (full_path, file, ext, mod_time, creation_time, resolution, name_date)

            else:
                full_path = os.path.join(root, file)
                mod_time = datetime.fromtimestamp(os.path.getmtime(full_path)).date().isoformat()
                creation_time = datetime.fromtimestamp(os.path.getctime(full_path)).date().isoformat()
                name_date = extract_date_from_filename(file)
                resolution = "unknown"
                yield (full_path, file, ext, mod_time, creation_time, resolution, name_date)

def calculate_hash(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
