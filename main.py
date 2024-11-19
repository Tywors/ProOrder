import gradio as gr
import os
import shutil
import sqlite3
from datetime import datetime
from file_utils import find_files, calculate_hash, image_extensions, document_extensions, video_extensions
from db_utils import create_database, store_file_info
from copy_images import start_organizing

batch_size = 10



def scan_images(src_directories):
    create_database()
    file_info_batch = []
    total_files_images = 0
    total_unique_images = 0
    total_files_doc = 0
    total_files_video = 0
    total_files = 0
    other_formats = 0
    duplicate_hashes = set()

    for i in range(len(src_directories)):
        for file in find_files(src_directories[i]):
            file_path, file_name, ext, mod_time, creation_time, resolution, name_date = file
            total_files += 1
            if ext.lower() in image_extensions:
                hash_value = calculate_hash(file_path)
                total_files_images += 1
            
                if hash_value in duplicate_hashes:
                    continue
                
                duplicate_hashes.add(hash_value)
                file_info_batch.append((file_path, file_name, ext, mod_time, creation_time, resolution, hash_value, name_date))
                total_unique_images += 1

            elif ext.lower() in video_extensions:
                file_info_batch.append((file_path, file_name, ext, mod_time, creation_time, resolution, None, name_date))
                total_files_video += 1

            elif ext.lower() in document_extensions:
                file_info_batch.append((file_path, file_name, ext, mod_time, creation_time, resolution, None, name_date))
                total_files_doc += 1

            else:
                file_info_batch.append((file_path, file_name, ext, mod_time, creation_time, resolution, None, name_date))
                other_formats += 1

            if (len(file_info_batch) >= batch_size):
                store_file_info(file_info_batch)
                file_info_batch = []
            
        if file_info_batch:
            store_file_info(file_info_batch)
        
    return total_files_images, total_unique_images, total_files_doc, total_files_video, total_files, other_formats

config_order = {
    "order_date": "Año - Mes - Dia",
    "string_date": "Nombre",
    "format_at_root": "Cada fecha",
    "extra_nsfw": False,
    "agrupar_formatos": True,
}

def update_config_order(name, value):
    config_order[name] = value
    return config_order

def start_scan(path1, path2, path3, path4):
    path_to_scan = []
    path_to_scan.append(path1)
    path_to_scan.append(path2)
    path_to_scan.append(path3)
    path_to_scan.append(path4)

    total_files_images, total_unique_images, total_files_doc, total_files_video, total_files, other_formats = scan_images(path_to_scan)
    duplicate_images = total_files_images - total_unique_images
    
    return total_files, total_files_images, duplicate_images, total_unique_images, total_files_doc, total_files_video, other_formats

def create_interface():
    with gr.Blocks() as demo:
        gr.Markdown("# Image Organizer")
        
        # Primera sección: Rutas de origen
        with gr.Row():
            with gr.Column():
                with gr.Group():
                    gr.Markdown("Puede rellenar hasta 4 rutas de origen diferentes, se filtrarás y ordenarán juntas.")
                    src_directory_1 = gr.Textbox(label="Ruta de origen 1", interactive=True)
                    src_directory_2 = gr.Textbox(label="Ruta de origen 2", interactive=True)
                    src_directory_3 = gr.Textbox(label="Ruta de origen 3", interactive=True)
                    src_directory_4 = gr.Textbox(label="Ruta de origen 4", interactive=True)      
            
            with gr.Column():
                info_panel = gr.Column(visible=True)
                with info_panel:
                    with gr.Group():
                        gr.Markdown("Información detectada en el escaneo.")
                        info_total_files = gr.Text(label="Archivos totales", interactive=False)
                        info_total_imgs = gr.Text(label="Imágenes totales", interactive=False)
                        info_duplicate_img = gr.Text(label="Imágenes Repetidas", interactive=False)
                        info_unique_imgs = gr.Text(label="Imágenes Únicas", interactive=False)
                        total_files_video = gr.Text(label="Archivos de video", interactive=False)
                        total_files_doc = gr.Text(label="Archivos de documentos", interactive=False)
                        other_formats = gr.Text(label="Archivos con otros formatos", interactive=False)
        
        scan_button = gr.Button("Escanear")

        # Segunda sección: Opciones de filtrado
        with gr.Row():
            with gr.Column():
                with gr.Group():
                    gr.Markdown("Seleccione tipo de filtrado")
                    order_date = gr.Radio(
                        ["Año - Mes", "Año - Mes - Dia"],
                        label="Organización de carpetas",
                        info="Es la manera de como se distribuirán las carpetas al final.",
                        value="Año - Mes - Dia",
                    )
                    string_date = gr.Radio(
                        ["Nombre", "Numero"],
                        label="Mostrar meses en",
                        info="Mostrar nombres, enero, febrero, etc o número 1, 2, etc.",
                        value="Nombre",
                    )
                    format_at_root = gr.Radio(
                        ["Al inicio", "Cada fecha"],
                        label="Carpetas diferentes formatos",
                        info="Tener carpetas imagen/video/etc o todos unidos en la misma fecha.",
                        value="Cada fecha",
                    )

                    def handle_order_date(value):
                        return update_config_order("order_date", value)

                    order_date.change(
                            fn=handle_order_date,
                            inputs=[order_date]
                        )

                    def handle_string_date(value):
                        return update_config_order("string_date", value)

                    string_date.change(
                            fn=handle_string_date,
                            inputs=[string_date]
                        )

                    def handle_format_at_root(value):
                        return update_config_order("format_at_root", value)
                        
                    format_at_root.change(
                            fn=handle_format_at_root,
                            inputs=[format_at_root]
                        )


            with gr.Column():
                with gr.Group():
                    gr.Markdown("Filtrados extra")
                    extra_nsfw = gr.Checkbox(
                        label="Filtrar NSFW",
                        info="Las imagenes NSFW estarán en carpeta aparte. (Sólo imágenes) (No implementado aún)",
                        value=False,
                        interactive=False,
                    )
                    agrupar_formatos = gr.Checkbox(
                        label="Todos los formatos unidos",
                        info="Formatos de imagen (.jpg, .jpeg, .png..), video (.mp4 , .avi, etc) se agruparán en la misma carpeta /imagenes y /videos",
                        value=True,
                        interactive=True
                    )

                    def handle_extra_nsfw(value):
                        return update_config_order("extra_nsfw", value)
                        
                    extra_nsfw.change(
                            fn=handle_extra_nsfw,
                            inputs=[extra_nsfw]
                        )

                    def handle_agrupar_formatos(value):
                        return update_config_order("agrupar_formatos", value)
                        
                    agrupar_formatos.change(
                            fn=handle_agrupar_formatos,
                            inputs=[agrupar_formatos]
                        )

            with gr.Column():
                with gr.Group():
                    gr.Markdown("Ruta de salida, se crearán las carpetas para organizar los archivos.")
                    dest_folder = gr.Textbox(label="Ruta de salida", interactive=True)

        # Conectar eventos
        scan_button.click(
            fn=start_scan,
            inputs=[src_directory_1, src_directory_2, src_directory_3, src_directory_4],
            outputs=[info_total_files, info_total_imgs, info_duplicate_img, info_unique_imgs, total_files_doc, total_files_video, other_formats]
        )

        start_button = gr.Button("Empezar")
        start_button.click(
            fn=start_organizing,
            inputs=[
                dest_folder,
                order_date,
                string_date,
                format_at_root,
                agrupar_formatos
            ]
    )

    demo.launch(inbrowser=True)

if __name__ == "__main__":
    create_interface()