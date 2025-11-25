import pandas as pd
import numpy as np
import wfdb
import yaml
import os
from pathlib import Path
from tqdm import tqdm

# Load configuration from YAML file
with open('config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# Get paths and parameters from config
path_to_physionet = config['database']['path_to_physionet']
sample_frequency = config['database']['sample_frequency']
output_path = config['output']

# Determine which records folder to use based on sample frequency
if sample_frequency == 500:
    records_folder = 'records500'
elif sample_frequency == 100:
    records_folder = 'records100'
else:
    raise ValueError(f"Sample frequency {sample_frequency} not supported. Use 100 or 500.")

print(f"Configuration:")
print(f"  - Source: {path_to_physionet}")
print(f"  - Records folder: {records_folder}")
print(f"  - Output: {output_path}")
print(f"  - Sample frequency: {sample_frequency} Hz")

# Create output directory if it doesn't exist
output_dir = Path(output_path) / records_folder
output_dir.mkdir(parents=True, exist_ok=True)
print(f"  - Output directory: {output_dir}")

# Load the PTB-XL database summary file
database_file = os.path.join(path_to_physionet, 'ptbxl_database.csv')
print(f"\nLoading database file: {database_file}")
df_database = pd.read_csv(database_file)

print(f"Total records in database: {len(df_database)}")

# Process each record
successful = 0
failed = 0
errors = []

for idx, row in tqdm(df_database.iterrows(), total=len(df_database), desc="Processing records"):
    try:
        # Get the filename path from the database
        filename_path = row['filename_hr'] if sample_frequency == 500 else row['filename_lr']
        
        # Build full path to record
        record_path = os.path.join(path_to_physionet, filename_path)
        
        # Extract record ID for output filename
        record_id = Path(filename_path).stem
        
        # Load ECG signal
        record = wfdb.rdsamp(record_path)
        signal = record[0]  # Signal data (numpy array)
        meta = record[1]    # Metadata (dict)
        
        # Create DataFrame with signal data
        df_signal = pd.DataFrame(
            signal,
            columns=meta['sig_name']
        )
        
        # Add time column
        df_signal.insert(0, 'time', np.arange(signal.shape[0]) / meta['fs'])
        
        # Save to CSV directly in the records folder
        output_file = output_dir / f"{record_id}.csv"
        df_signal.to_csv(output_file, index=False)
        
        successful += 1
        
    except Exception as e:
        failed += 1
        errors.append({
            'record_id': row.get('ecg_id', 'unknown'),
            'filename': filename_path if 'filename_path' in locals() else 'unknown',
            'error': str(e)
        })
        if failed <= 10:  # Only print first 10 errors to avoid spam
            print(f"\nError processing record {row.get('ecg_id', 'unknown')}: {e}")

# Summary
print("\n" + "="*70)
print("PROCESSING COMPLETE")
print("="*70)
print(f"Successfully processed: {successful}/{len(df_database)} records")
print(f"Failed: {failed}/{len(df_database)} records")
print(f"Output directory: {output_dir}")

# Save error log if there were errors
if errors:
    error_log_file = output_dir / "processing_errors.csv"
    pd.DataFrame(errors).to_csv(error_log_file, index=False)
    print(f"\nError log saved to: {error_log_file}")

print("\nSample output structure:")
print(f"  {output_dir}/")
print(f"    ├── 00001_hr.csv")
print(f"    ├── 00002_hr.csv")
print(f"    ├── 00003_hr.csv")
print(f"    └── ...")
