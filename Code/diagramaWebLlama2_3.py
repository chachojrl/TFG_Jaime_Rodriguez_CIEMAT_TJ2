import requests
import matplotlib.pyplot as plt
import urllib3
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)



#Generar una URL para realizar una solicitud basada en los parámetros proporcionados.
def generate_url(base_url, shot, nsignal, signals, factors, tstart, tstop):

    url = f"{base_url}?shot={shot}&nsignal={nsignal}"
    for i in range(1, nsignal + 1):
        signal = signals[i - 1] if i - 1 < len(signals) else ""
        factor = factors[i - 1] if i - 1 < len(factors) else "1.00"
        url += f"&signal{i:02}={signal}&fact{i:02}={factor}"
    url += f"&tstart={tstart:.2f}&tstop={tstop:.2f}"
    return url

#Realizar una solicitud HTTP GET al enlace generado y devolver la respuesta.
def fetch_data(url):

    response = requests.get(url, verify=False)
    if response.status_code == 200:
        return response.text
    else:
        raise ValueError(f"Error al conectar con el servidor: {response.status_code}")

#Extrae los datos contenidos en `dataXX` desde el HTML recibido para múltiples señales.
def extract_data_points(html_content, signals):

    data_points_dict = {}
    matches = re.finditer(r"var data(\d{2}) = \[(.*?)\];", html_content, re.DOTALL)
    for match, signal_name in zip(matches, signals):
        data_block = match.group(2)
        data_points = []
        for line in data_block.split('],['):
            values = line.strip('[]').split(',')
            x, y = map(float, values)
            data_points.append((x, y))
        data_points_dict[signal_name] = data_points
    if not data_points_dict:
        raise ValueError("No se encontraron datos en las señales `dataXX`.")
    return data_points_dict

#Genera una gráfica combinada a partir de los puntos de datos extraídos.
def plot_data(data_points_dict):

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

# Función principal para el chatbot
#Pipeline completo para integrar en un chatbot.
def process_data_for_chatbot(base_url, shot, nsignal, signals, factors, tstart, tstop):

    try:
        # Generar URL
        url = generate_url(base_url, shot, nsignal, signals, factors, tstart, tstop)
        print("URL generada:", url)

        # Obtener y procesar datos
        raw_html = fetch_data(url)
        data_points_dict = extract_data_points(raw_html, signals)
        print("Datos extraídos:", {k: v[:5] for k, v in data_points_dict.items()})  # Mostrar los primeros 5 puntos

        # Graficar los datos
        plot_data(data_points_dict)
        return "Gráfica generada exitosamente."
    except Exception as e:
        return f"Error: {e}"
