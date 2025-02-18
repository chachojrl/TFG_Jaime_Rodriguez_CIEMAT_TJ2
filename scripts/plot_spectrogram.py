import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as signal

# Define the range for x values
minX = 1050
maxX = 1250

# Load the data (ignoring the first row as header)
data = np.loadtxt('../Utilities/similPatternTool/raw_data/MIR5C_56938_56938.txt', delimiter=' ', skiprows=1)

x = data[:, 0]  # First column
y = data[:, 1]  # Second column

# Convert to double precision
x = x.astype(float)
y = y.astype(float)

# Filter data within the x range
indices_x = np.where((x >= minX) & (x <= maxX))
x = x[indices_x]
y = y[indices_x]

# Define parameters for spectrogram
nfft = 2**10  # 1024
overlap = 0.8
ST = 0.001  # Sampling time interval
fs = 1 / ST  # Sampling frequency

# Compute spectrogram
f, t, B = signal.spectrogram(y, fs=fs, window='hann', nperseg=nfft, noverlap=int(overlap * nfft))

# Adjust time axis
Tin = x[0]
t = t + Tin

# Plot the spectrogram (in dB scale)
plt.figure()
plt.imshow(10 * np.log10(np.abs(B)), aspect='auto', extent=[t[0], t[-1], f[0], f[-1]], origin='lower', cmap='jet')
plt.clim(0, 40)  # Set color limits
plt.colorbar(label="Power (dB)")
plt.xlabel("Time (ms)")
plt.ylabel("Frequency (kHz)")
plt.title("Spectrogram to forecast\nMIR5C - 10*log10(P) (dB)")
plt.gca().set_facecolor('white')
plt.show()

# Normalized Spectrogram
B_dB = 10 * np.log10(np.abs(B))  # Convert to dB scale
min_dB = np.min(B_dB)
max_dB = np.max(B_dB)
B_scaled = (B_dB - min_dB) / (max_dB - min_dB)  # Normalize to [0,1]

# Plot the normalized spectrogram
plt.figure()
plt.imshow(B_scaled, aspect='auto', extent=[t[0], t[-1], f[0], f[-1]], origin='lower', cmap='jet')
plt.colorbar(label="Normalized Power")
plt.xlabel("Time (ms)")
plt.ylabel("Frequency (kHz)")
plt.title("Spectrogram to forecast\nMIR5C - 10*log10(P) (dB) - Normalized")
plt.gca().set_facecolor('white')
plt.show()
