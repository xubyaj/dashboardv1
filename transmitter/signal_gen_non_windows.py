import numpy as np
import pandas as pd
import os
import sys
from datetime import datetime, timedelta

# Function to display a simple progress bar
def print_progress_bar(iteration, total, length=40):
    percent = (iteration / total) * 100
    filled_length = int(length * iteration // total)
    bar = '█' * filled_length + '-' * (length - filled_length)
    sys.stdout.write(f'\rProgress: |{bar}| {percent:.2f}% Complete')
    sys.stdout.flush()

# Parameters
fs = 100  # Sampling frequency in Hz
duration_minutes = 2  # Duration in minutes
duration_seconds = duration_minutes * 60  # Convert minutes to seconds

# Time vector
t = np.arange(0, duration_seconds, 1/fs)

# Get the current time and generate timestamps
current_time = datetime.now()
timestamps = [(current_time + timedelta(seconds=i/fs)).timestamp() for i in range(len(t))]

# Generate random sine waves with variable noise
num_waves = 6
frequencies = np.random.uniform(0.1, 2, num_waves)  # Random frequencies between 0.1 and 2 Hz
amplitudes = np.random.uniform(0.5, 1.5, num_waves)  # Random amplitudes for more variation

# Create sine waves with spikes and flat zones
sine_waves = []
for f, a in zip(frequencies, amplitudes):
    wave = np.sin(2 * np.pi * f * t) * a  # Basic sine wave
    
    # Add random spikes
    noise = np.random.normal(0, 0.1, t.shape)  # Add slight noise
    spikes = np.random.choice([0, 1], size=t.shape, p=[0.95, 0.05])  # 5% chance for a spike
    spike_values = np.random.normal(5, 2, size=t.shape) * spikes  # Spikes with a random value
    wave += noise + spike_values
    
    # Introduce flat zones
    flat_zones = np.random.choice([0, 1], size=t.shape, p=[0.85, 0.15])  # 15% chance for flat zones
    wave = np.where(flat_zones == 1, 0, wave)  # Set flat zones to 0
    
    sine_waves.append(wave)

# Convert list to array
sine_waves = np.array(sine_waves).T  # Make it 2D array with shape (time, wave)

# Create a DataFrame
data = pd.DataFrame(sine_waves, columns=[f'Sine Wave {i+1}' for i in range(num_waves)])
data['Epoch Time'] = timestamps  # Adding epoch time to the DataFrame

# Ask the user for a user ID
user_id = input("Please enter your user ID: ")

# Save to .txt file
output_directory = r"/run/user/1000/gvfs/smb-share:server=192.168.20.29,share=data/post processing/new data"
os.makedirs(output_directory, exist_ok=True)  # Ensure the output directory exists
output_filename = os.path.join(output_directory, f'sine_waves_{user_id}.txt')

try:
    # Determine the total number of rows to save
    total_rows = data.shape[0]
    chunk_size = 1000  # Number of rows per chunk
    total_chunks = (total_rows + chunk_size - 1) // chunk_size  # Calculate total chunks

    # Start saving and display the progress bar
    print(f"\nSaving to {output_filename}...")
    with open(output_filename, 'w') as f:
        data.iloc[0:0].to_csv(f, index=False, sep='\t')  # Write the header
        
        for chunk in range(total_chunks):
            start_idx = chunk * chunk_size
            end_idx = min((chunk + 1) * chunk_size, total_rows)
            
            # Save the chunk to the file
            data.iloc[start_idx:end_idx].to_csv(f, index=False, sep='\t', header=False)
            
            # Update the progress bar
            print_progress_bar(chunk + 1, total_chunks)

    # Final progress bar completion
    print_progress_bar(total_chunks, total_chunks)
    print("\nSine waves saved successfully to", output_filename)

except Exception as e:
    print(f"\nAn error occurred while saving the file: {e}")