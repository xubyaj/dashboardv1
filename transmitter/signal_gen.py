import numpy as np
import pandas as pd
import os
import sys
import time
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
duration_minutes = 20  # Duration in minutes
duration_seconds = duration_minutes * 60  # Convert minutes to seconds

# Time vector
t = np.arange(0, duration_seconds, 1/fs)

# Get the current time
current_time = datetime.now()

# Generate timestamps from the current time
timestamps = [(current_time + timedelta(seconds=i/fs)).timestamp() for i in range(len(t))]

# Generate random sine waves
num_waves = 6
frequencies = np.random.uniform(0.1, 2, num_waves)  # Random frequencies between 0.1 and 2 Hz
sine_waves = np.array([np.sin(2 * np.pi * f * t) for f in frequencies]).T

# Create a DataFrame
data = pd.DataFrame(sine_waves, columns=[f'Sine Wave {i+1}' for i in range(num_waves)])
data['Epoch Time'] = timestamps  # Adding epoch time to the DataFrame

# Ask the user for a user ID
user_id = input("Please enter your user ID: ")

# Save to .txt file
output_directory = r"/run/user/1000/gvfs/smb-share:server=192.168.20.29,share=data/Plots"
output_filename = os.path.join(output_directory, f'sine_waves_{user_id}.txt')

# Simulate file saving with a progress bar
total_steps = 100  # Define total steps for the progress bar
for i in range(total_steps):
    time.sleep(0.05)  # Simulate some processing time
    print_progress_bar(i + 1, total_steps)

# Actually save the DataFrame to the .txt file
data.to_csv(output_filename, index=False, sep='\t')  # Save as .txt file with tab delimiter

# Final progress bar completion
print_progress_bar(total_steps, total_steps)
print("\nSine waves saved successfully to", output_filename)