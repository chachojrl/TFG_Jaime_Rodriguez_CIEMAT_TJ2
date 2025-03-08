import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as signal
import os
import re  # Para extraer el número correcto del nombre del archivo

# ---------------------- CONFIGURACIÓN ---------------------- #
# Define el rango de valores de X
minX = 1050
maxX = 1250

# Nombre del archivo de datos (Modifica esta ruta si es necesario)
file_path = "../utilities/similPatternTool/raw_data/MIR5C_56951_56951.txt"

# Extraer el **primer número de al menos 4 o 5 dígitos** del nombre del archivo
match = re.search(r'\d{4,}', os.path.basename(file_path))  # Busca el primer número de al menos 4 dígitos
if match:
    shot_number = match.group(0)  # Extraer el número completo
else:
    raise ValueError(f"No se encontró un número válido en el nombre del archivo: {file_path}")

# Carpeta donde se guardarán los espectrogramas
output_dir = "../data/spectograms/spectograms_for_try"
os.makedirs(output_dir, exist_ok=True)

# Nombre base de los archivos generados
color_filename = os.path.join(output_dir, f"{shot_number}.png")
heatmap_filename = os.path.join(output_dir, f"{shot_number}_N.png")
bw_filename = os.path.join(output_dir, f"{shot_number}_N_bw.png")

# ---------------------- CARGAR Y PROCESAR DATOS ---------------------- #
# Cargar los datos desde el archivo de texto
data = np.loadtxt(file_path, delimiter=' ', skiprows=1)

# Extraer columnas (Tiempo y Señal)
x = data[:, 0].astype(float)  # Primera columna (Tiempo)
y = data[:, 1].astype(float)  # Segunda columna (Señal)

# Filtrar valores dentro del rango especificado
indices_x = np.where((x >= minX) & (x <= maxX))
x = x[indices_x]
y = y[indices_x]

# ---------------------- CÁLCULO DEL ESPECTROGRAMA ---------------------- #
# Parámetros del espectrograma
nfft = 2**10  # 1024 puntos FFT
overlap = 0.8
ST = 0.001  # Intervalo de muestreo (s)
fs = 1 / ST  # Frecuencia de muestreo

# Calcular el espectrograma
f, t, B = signal.spectrogram(y, fs=fs, window='hann', nperseg=nfft, noverlap=int(overlap * nfft))

# Ajustar el eje temporal
Tin = x[0]
t = t + Tin

# ---------------------- GENERAR Y GUARDAR ESPECTROGRAMAS ---------------------- #
# Convertir a escala logarítmica (dB)
B_dB = 10 * np.log10(np.abs(B))

# Normalizar entre [0,1] para la escala de grises y heatmap
min_dB, max_dB = np.min(B_dB), np.max(B_dB)
B_scaled = (B_dB - min_dB) / (max_dB - min_dB)

# Función auxiliar para guardar imágenes
def save_spectrogram(data, filename, cmap, title, colorbar_label):
    plt.figure(figsize=(10, 6))
    plt.imshow(data, aspect='auto', extent=[t[0], t[-1], f[0], f[-1]], origin='lower', cmap=cmap)
    plt.colorbar(label=colorbar_label)
    plt.xlabel("Time (ms)")
    plt.ylabel("Frequency (kHz)")
    plt.title(title)
    plt.gca().set_facecolor('white')
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()

# Guardar los espectrogramas con los estilos requeridos
save_spectrogram(B_scaled, heatmap_filename, 'turbo', "Spectrogram - Heatmap (Rojo-Amarillo-Azul)", "Normalized Power")
save_spectrogram(B_scaled, bw_filename, 'gray', "Spectrogram - Blanco y Negro", "Normalized Power")
save_spectrogram(B_dB, color_filename, 'jet', "Spectrogram - Plasma (Azul)", "Power (dB)")

print(f"Espectrogramas guardados en {output_dir} con el nombre base: {shot_number}")
