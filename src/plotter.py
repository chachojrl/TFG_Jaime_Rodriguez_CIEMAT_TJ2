import matplotlib.pyplot as plt
import re
import os

# Carpeta donde se guardarán las imágenes temporales
TEMP_IMAGE_FOLDER = "./temp_plots"
os.makedirs(TEMP_IMAGE_FOLDER, exist_ok=True)

def group_signals(signals):
    """Agrupa señales por prefijo común usando expresiones regulares."""
    grouped_signals = {}

    for signal in signals:
        match = re.match(r"([A-Za-z_]+)\d*", signal)
        if match:
            prefix = match.group(1)
            if prefix not in grouped_signals:
                grouped_signals[prefix] = []
            grouped_signals[prefix].append(signal)
        else:
            grouped_signals[signal] = [signal]

    return grouped_signals

def plot_data_per_signal(data_points_dict):
    """
    Genera gráficos por grupos de señales, los guarda en archivos temporales y devuelve las rutas.
    """
    grouped_signals = group_signals(data_points_dict.keys())
    image_paths = []  # Lista para almacenar rutas de imágenes generadas

    for group_name, signal_names in grouped_signals.items():
        fig, ax = plt.subplots(figsize=(10, 6))

        for signal_name in signal_names:
            if signal_name in data_points_dict:
                x_values, y_values = zip(*data_points_dict[signal_name])
                ax.plot(x_values, y_values, label=signal_name, linewidth=1.5)

        ax.set_title(f"Graph for {group_name} signals")
        ax.set_xlabel("Time")
        ax.set_ylabel("Value")
        ax.legend()
        ax.grid()

        # Guardar la imagen en un archivo temporal
        image_path = os.path.join(TEMP_IMAGE_FOLDER, f"{group_name}.png")
        plt.savefig(image_path, format="png")
        plt.close(fig)

        # Agregar la ruta a la lista
        image_paths.append(image_path)

    return image_paths  # Devuelve las rutas de las imágenes
