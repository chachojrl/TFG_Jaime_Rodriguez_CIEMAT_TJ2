import matplotlib.pyplot as plt
import re
import io
from PIL import Image

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
    Genera gráficos por grupos de señales y devuelve una lista de imágenes PIL.
    """
    grouped_signals = group_signals(data_points_dict.keys())
    images = []  # Lista para almacenar imágenes generadas

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

        # Guardar la imagen en un buffer de memoria
        img_buf = io.BytesIO()
        plt.savefig(img_buf, format="png")
        plt.close(fig)
        img_buf.seek(0)  

        # Convertir a PIL.Image y agregar a la lista
        images.append(Image.open(img_buf))

    return images  # Retornar lista de imágenes
