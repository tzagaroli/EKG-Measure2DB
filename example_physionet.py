import pandas as pd
import numpy as np
import wfdb
import matplotlib.pyplot as plt
import yaml
import os

# Load configuration from YAML file
with open('config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# Get the path from config
path_to_physionet = config['database']['path_to_physionet']

# Build the complete record path
# Note: Use os.path.join for proper path handling across OS
record_path = os.path.join(path_to_physionet, 'records500', '00000', '00001_hr')

print(f"Loading record from: {record_path}")

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
