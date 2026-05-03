import os
import shutil

# Ruta a la carpeta que quieres organizar
carpeta_descargas = r"C:\Users\Estudiante\Downloads"

# Mapeo de extensiones a carpetas
extension_map = {
    (".jpg", ".jpeg", ".png"): "Imagenes",
    (".pdf", ".docx", ".txt"): "Documentos",
    (".mp3", ".wav"): "Audio",
    (".zip", ".rar"): "Comprimidos"
}

def organizar_descargas():
    for archivo in os.listdir(carpeta_descargas):
        ruta_archivo = os.path.join(carpeta_descargas, archivo)
        
        # Ignorar directorios
        if os.path.isdir(ruta_archivo):
            continue
            
        for extensiones, carpeta in extension_map.items():
            if archivo.lower().endswith(extensiones):
                # Crear carpeta si no existe
                carpeta_destino = os.path.join(carpeta_descargas, carpeta)
                os.makedirs(carpeta_destino, exist_ok=True)
                
                # Mover archivo
                shutil.move(ruta_archivo, os.path.join(carpeta_destino, archivo))
                print(f"Movido: {archivo} a {carpeta}")

if __name__ == "__main__":
    organizar_descargas()