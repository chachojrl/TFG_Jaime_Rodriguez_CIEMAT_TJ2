import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as signal
import os
import sys

minX = 1050
maxX = 1250

if len(sys.argv) < 2:
    print("ERROR: No shot number provided.")
    sys.exit(1)

shot_number = sys.argv[1]

file_path = f"../utilities/similPatternTool/raw_data/MIR5C_{shot_number}_{shot_number}.txt"

if not os.path.exists(file_path):
    print(f"ERROR: File not found.")
    sys.exit(1)

output_dir = "./spectograms/spectograms_for_try"
os.makedirs(output_dir, exist_ok=True)

color_filename = os.path.join(output_dir, f"{shot_number}.png")
heatmap_filename = os.path.join(output_dir, f"{shot_number}_N.png")
bw_filename = os.path.join(output_dir, f"{shot_number}_N_bw.png")

data = np.loadtxt(file_path, delimiter=' ', skiprows=1)

x = data[:, 0].astype(float)
y = data[:, 1].astype(float)

indices_x = np.where((x >= minX) & (x <= maxX))
x = x[indices_x]
y = y[indices_x]

nfft = 2**10
overlap = 0.8
ST = 0.001
fs = 1 / ST

f, t, B = signal.spectrogram(y, fs=fs, window='hann', nperseg=nfft, noverlap=int(overlap * nfft))

Tin = x[0]
t = t + Tin

B_dB = 10 * np.log10(np.abs(B))

min_dB, max_dB = np.min(B_dB), np.max(B_dB)
B_scaled = (B_dB - min_dB) / (max_dB - min_dB)

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

save_spectrogram(B_scaled, heatmap_filename, 'turbo', "Spectrogram - Heatmap (Red-Yellow-Blue)", "Normalized Power")
save_spectrogram(B_scaled, bw_filename, 'gray', "Spectrogram - Grayscale", "Normalized Power")
save_spectrogram(B_dB, color_filename, 'jet', "Spectrogram - Plasma (Blue)", "Power (dB)")

print(color_filename)
sys.exit(0)