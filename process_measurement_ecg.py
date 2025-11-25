"""
ECG Measurement File Processor
Reads ECG_X.txt files, splits them into 10-second segments, and saves as CSV
"""

import os
import yaml
import pandas as pd
from pathlib import Path


def load_config(config_file='config.yaml'):
    """Load configuration from YAML file"""
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config


def read_ecg_file(filepath):
    """
    Read ECG file in format:
    0;4095
    1;1583
    ...
    
    Returns DataFrame with 'index' and 'value' columns
    """
    data = []
    
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    # Remove last line if it's empty (just newline)
    if lines and lines[-1].strip() == '':
        lines = lines[:-1]
    
    # Parse lines
    for line in lines:
        line = line.strip()
        if line and ';' in line:
            parts = line.split(';')
            if len(parts) == 2:
                try:
                    idx = int(parts[0])
                    value = int(parts[1])
                    data.append({'index': idx, 'value': value})
                except ValueError:
                    print(f"Warning: Skipping invalid line: {line}")
    
    return pd.DataFrame(data)


def split_into_segments(df, sample_frequency=500, segment_duration=10):
    """
    Split ECG data into segments of specified duration
    
    Args:
        df: DataFrame with 'index' and 'value' columns
        sample_frequency: Sampling frequency in Hz (default: 500)
        segment_duration: Duration of each segment in seconds (default: 10)
    
    Returns:
        List of DataFrames, each representing one segment
    """
    samples_per_segment = sample_frequency * segment_duration
    total_samples = len(df)
    num_complete_segments = total_samples // samples_per_segment
    
    segments = []
    
    for i in range(num_complete_segments):
        start_idx = i * samples_per_segment
        end_idx = start_idx + samples_per_segment
        
        segment_df = df.iloc[start_idx:end_idx].copy()
        
        # Calculate time from index
        T_sample = 1.0 / sample_frequency
        segment_df['time'] = segment_df['index'] * T_sample
        
        # Reset time to start at 0 for each segment
        segment_df['time'] = segment_df['time'] - segment_df['time'].iloc[0]
        
        # Keep only time and value columns
        segment_df = segment_df[['time', 'value']]
        
        segments.append(segment_df)
    
    # Log discarded samples
    remaining_samples = total_samples - (num_complete_segments * samples_per_segment)
    if remaining_samples > 0:
        print(f"  Discarded {remaining_samples} remaining samples (incomplete segment)")
    
    return segments


def process_ecg_files(config):
    """Process all ECG_X.txt files from input directory"""
    
    # Extract paths from config
    input_dir = Path(config['database']['path_to_measure'])
    output_dir = Path(config['measure']['output'])
    sample_frequency = config['database']['sample_frequency']
    
    print("="*70)
    print("ECG Measurement File Processor")
    print("="*70)
    print(f"Input directory: {input_dir}")
    print(f"Output directory: {output_dir}")
    print(f"Sample frequency: {sample_frequency} Hz")
    print(f"Segment duration: 10 seconds ({sample_frequency * 10} samples)")
    print("="*70)
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all ECG_X.txt files
    ecg_files = sorted(input_dir.glob('ECG_*.txt'))
    
    if not ecg_files:
        print(f"\nNo ECG_*.txt files found in {input_dir}")
        return
    
    print(f"\nFound {len(ecg_files)} ECG file(s) to process\n")
    
    # Global counter for output files
    global_segment_counter = 0
    
    # Statistics
    total_segments = 0
    total_files_processed = 0
    
    # Process each file
    for ecg_file in ecg_files:
        print(f"Processing: {ecg_file.name}")
        
        try:
            # Read ECG file
            df = read_ecg_file(ecg_file)
            
            if df.empty:
                print(f"  Warning: File is empty or invalid, skipping")
                continue
            
            print(f"  Loaded {len(df)} samples")
            
            # Split into 10-second segments
            segments = split_into_segments(df, sample_frequency, segment_duration=10)
            
            if not segments:
                print(f"  Warning: Not enough samples for a complete 10s segment, skipping")
                continue
            
            print(f"  Created {len(segments)} segment(s)")
            
            # Save each segment
            for segment in segments:
                output_filename = f"ecg_{global_segment_counter:05d}.csv"
                output_path = output_dir / output_filename
                
                # Save as CSV
                segment.to_csv(output_path, index=False)
                
                global_segment_counter += 1
            
            print(f"  ✓ Saved segments: ecg_{global_segment_counter-len(segments):05d}.csv to ecg_{global_segment_counter-1:05d}.csv")
            
            total_segments += len(segments)
            total_files_processed += 1
            
        except Exception as e:
            print(f"  ✗ Error processing {ecg_file.name}: {e}")
    
    # Summary
    print("\n" + "="*70)
    print("PROCESSING COMPLETE")
    print("="*70)
    print(f"Files processed: {total_files_processed}/{len(ecg_files)}")
    print(f"Total segments created: {total_segments}")
    print(f"Output directory: {output_dir}")
    print(f"Output files: ecg_00000.csv to ecg_{global_segment_counter-1:05d}.csv")
    print("="*70)


def main():
    # Load configuration
    config = load_config('config.yaml')
    
    # Process files
    process_ecg_files(config)


if __name__ == '__main__':
    main()