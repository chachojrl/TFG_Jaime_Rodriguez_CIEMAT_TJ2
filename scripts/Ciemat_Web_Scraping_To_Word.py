import os
import requests
from bs4 import BeautifulSoup

# URL de la página web objetivo
url = 'https://www.fusion.ciemat.es/inicio/recursos/tesis-doctorales/'

# Realizar la solicitud HTTP con SSL deshabilitado temporalmente
response = requests.get(url, verify=False)
response.raise_for_status()  # Verificar si la solicitud fue exitosa

# Analizar el contenido HTML
soup = BeautifulSoup(response.text, 'html.parser')

# Encontrar todos los elementos con la clase 'bibitem'
bibitems = soup.find_all(class_='bibitem')

# Crear la carpeta 'extracted_web_data' si no existe
os.makedirs('extracted_web_data', exist_ok=True)

# Función para descargar y guardar archivos
def download_file(file_url, dest_folder):
    local_filename = file_url.split('/')[-1]
    file_path = os.path.join(dest_folder, local_filename)

    print(f"Descargando {file_url}...")  # Para depuración

    try:
        with requests.get(file_url, stream=True, verify=False) as r:
            r.raise_for_status()
            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"Archivo guardado: {file_path}")
    except Exception as e:
        print(f"Error descargando {file_url}: {e}")

    return file_path

# Recorrer los elementos 'bibitem' y extraer los enlaces
for bibitem in bibitems:
    link = bibitem.find('a', href=True)
    if link:
        href = link['href']
        if href.startswith('http'):  # Asegurar que sea un enlace absoluto
            download_file(href, 'extracted_web_data')
