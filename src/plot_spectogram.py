import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as signal
import os
import sys

# ---------------------- CONFIGURATION ---------------------- #
minX = 1050
maxX = 1250

# Check if a shot number was provided
if len(sys.argv) < 2:
    print("ERROR: No shot number provided.")
    sys.exit(1)

shot_number = sys.argv[1]

# Construct the file path based on the shot number
file_path = f"../utilities/similPatternTool/raw_data/MIR5C_{shot_number}_{shot_number}.txt"

# Check if the file exists
if not os.path.exists(file_path):
    print(f"ERROR: File not found.")
    sys.exit(1)

# Spectrogram storage folder
output_dir = "./spectograms/spectograms_for_try"
os.makedirs(output_dir, exist_ok=True)

# Generate filenames
color_filename = os.path.join(output_dir, f"{shot_number}.png")      # 🔹 Imagen principal
heatmap_filename = os.path.join(output_dir, f"{shot_number}_N.png")  # 🔹 Segunda imagen
bw_filename = os.path.join(output_dir, f"{shot_number}_N_bw.png")    # 🔹 Tercera imagen

# ---------------------- LOAD AND PROCESS DATA ---------------------- #
data = np.loadtxt(file_path, delimiter=' ', skiprows=1)

# Extract columns (Time and Signal)
x = data[:, 0].astype(float)
y = data[:, 1].astype(float)

# Filter values within the specified range
indices_x = np.where((x >= minX) & (x <= maxX))
x = x[indices_x]
y = y[indices_x]

# ---------------------- COMPUTE SPECTROGRAM ---------------------- #
nfft = 2**10
overlap = 0.8
ST = 0.001
fs = 1 / ST

f, t, B = signal.spectrogram(y, fs=fs, window='hann', nperseg=nfft, noverlap=int(overlap * nfft))

Tin = x[0]
t = t + Tin

# Convert to dB scale
B_dB = 10 * np.log10(np.abs(B))

# Normalize for grayscale and heatmap
min_dB, max_dB = np.min(B_dB), np.max(B_dB)
B_scaled = (B_dB - min_dB) / (max_dB - min_dB)

# Function to save spectrograms
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

# Save the spectrograms
save_spectrogram(B_scaled, heatmap_filename, 'turbo', "Spectrogram - Heatmap (Red-Yellow-Blue)", "Normalized Power")
save_spectrogram(B_scaled, bw_filename, 'gray', "Spectrogram - Grayscale", "Normalized Power")
save_spectrogram(B_dB, color_filename, 'jet', "Spectrogram - Plasma (Blue)", "Power (dB)")

# **🔹 Solo imprimimos la imagen principal (`shot_number.png`)**
print(color_filename)
sys.exit(0)
