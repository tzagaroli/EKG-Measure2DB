import pandas as pd
import numpy as np
import wfdb
import matplotlib.pyplot as plt

# Path to the file (without extension)
path = '.local/ptb-xl/'
record_path = path + 'records500/00000/00001_hr'

# Load ECG signal
record = wfdb.rdsamp(record_path)
signal = record[0]  # Signal data
meta = record[1]    # Metadata

# Display information
print(f"Sampling frequency: {meta['fs']} Hz")
print(f"Number of leads: {signal.shape[1]}")
print(f"Number of samples: {signal.shape[0]}")
print(f"Lead names: {meta['sig_name']}")

# Create time axis
time = np.arange(signal.shape[0]) / meta['fs']

# Display all leads
plt.figure(figsize=(15, 10))
for i in range(signal.shape[1]):
    plt.subplot(signal.shape[1], 1, i+1)
    plt.plot(time, signal[:, i])
    plt.ylabel(meta['sig_name'][i])
    plt.grid(True)
    if i == 0:
        plt.title('ECG - Record 00001_hr')
    if i == signal.shape[1] - 1:
        plt.xlabel('Time (s)')

plt.tight_layout()
plt.show()