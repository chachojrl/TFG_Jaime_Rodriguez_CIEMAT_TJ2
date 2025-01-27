import requests
import matplotlib.pyplot as plt
import urllib3
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

# Deshabilitar advertencias por SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def generate_url(base_url, shot, nsignal, signals, factors, tstart, tstop):
    """
    Genera una URL para realizar una solicitud basada en los parámetros proporcionados.
    """
    url = f"{base_url}?shot={shot}&nsignal={nsignal}"
    
    for i in range(1, nsignal + 1):
        signal = signals[i - 1] if i - 1 < len(signals) else ""
        factor = factors[i - 1] if i - 1 < len(factors) else "1.00"
        url += f"&signal{i:02}={signal}&fact{i:02}={factor}"

    url += f"&tstart={tstart:.2f}&tstop={tstop:.2f}"
    return url

def fetch_data(url):
    """
    Realiza una solicitud HTTP GET al enlace generado y devuelve la respuesta.
    """
    response = requests.get(url, verify=False)
    if response.status_code == 200:
        print("Respuesta completa del servidor:")
        print(response.text[:1000])  # Muestra los primeros 1000 caracteres
        return response.text
    else:
        raise ValueError(f"Error al conectar con el servidor: {response.status_code}")

def extract_data_points(html_content, signals):
    """
    Extrae los datos contenidos en `dataXX` desde el HTML recibido para múltiples señales.
    """
    data_points_dict = {}
    matches = re.finditer(r"var data(\d{2}) = \[(.*?)\];", html_content, re.DOTALL)
    for match, signal_name in zip(matches, signals):
        data_block = match.group(2)
        # Parsear los datos en una lista de tuplas
        data_points = []
        for line in data_block.split('],['):
            values = line.strip('[]').split(',')
            x, y = map(float, values)
            data_points.append((x, y))
        data_points_dict[signal_name] = data_points
    
    if not data_points_dict:
        raise ValueError("No se encontraron datos en las señales `dataXX`.")

    return data_points_dict

def plot_data(data_points_dict):
    """
    Genera una gráfica combinada a partir de los puntos de datos extraídos.
    """
    plt.figure(figsize=(10, 6))

    for signal_name, data_points in data_points_dict.items():
        x_values = [point[0] for point in data_points]
        y_values = [point[1] for point in data_points]
        plt.plot(x_values, y_values, label=signal_name, linewidth=1.5)

    plt.title("Gráfica de los datos extraídos de múltiples señales")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.legend()
    plt.grid()
    plt.show()

# Configuración inicial
base_url = "https://info.fusion.ciemat.es/cgi-bin/TJII_data.cgi"

shot = int(input("Ingrese el valor de 'shot': "))
nsignal = int(input("Ingrese el número de señales (entre 5 y 30): "))

if nsignal < 5 or nsignal > 30:
    raise ValueError("El número de señales debe estar entre 5 y 30.")

signals = []
factors = []

for i in range(1, nsignal + 1):
    signal = input(f"Ingrese el nombre de la señal {i} (deje vacío si no aplica): ")
    factor = input(f"Ingrese el factor para la señal {i} (por defecto 1.00): ") or "1.00"
    signals.append(signal)
    factors.append(factor)

tstart = float(input("Ingrese el tiempo inicial (tstart) [por defecto 0.00]: ") or 0.00)
tstop = float(input("Ingrese el tiempo final (tstop) [por defecto 2000.00]: ") or 2000.00)

# Generar URL
generated_url = generate_url(base_url, shot, nsignal, signals, factors, tstart, tstop)
print("URL generada:", generated_url)

# Obtener datos y procesar
try:
    raw_html = fetch_data(generated_url)
    data_points_dict = extract_data_points(raw_html, signals)
    print("Datos extraídos:", {k: v[:5] for k, v in data_points_dict.items()})  # Muestra los primeros 5 puntos de cada señal
    plot_data(data_points_dict)

except Exception as e:
    print("Error al procesar el diagrama:", e)
