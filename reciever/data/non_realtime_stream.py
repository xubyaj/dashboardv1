import os
import pandas as pd
import matplotlib.pyplot as plt
import time
import shutil
from datetime import datetime

# Specify your network share directory
directory_to_save = r'/data/Post_Processing/'
directory_to_monitor = r'/data/Post_Processing/Plots'
saved_data_directory = os.path.join(directory_to_save, 'saved data')
saved_plots_directory = os.path.join(directory_to_save, 'saved plots')

# Create directories if they do not exist
os.makedirs(saved_data_directory, exist_ok=True)
os.makedirs(saved_plots_directory, exist_ok=True)

processed_files = set()  # To keep track of processed files

def is_file_ready(file_path, wait_time=5, check_interval=0.5):
    """Check if the file upload is complete by monitoring its size."""
    initial_size = os.path.getsize(file_path)
    time.sleep(wait_time)  # Wait for the file write operation to potentially complete

    # Check the size multiple times
    for _ in range(int(wait_time / check_interval)):
        time.sleep(check_interval)
        final_size = os.path.getsize(file_path)
        if final_size != initial_size:
            initial_size = final_size  # Update the size if it changed
        else:
            return True  # File is ready if the size hasn't changed
    return False  # File is still being written

def plot_signals(file_path):
    try:
        # Load the data from the specified file path
        data = pd.read_csv(file_path, sep='\t')
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return

    # Plot each signal in a separate subplot
    num_signals = data.shape[1] - 1  # Exclude the 'Epoch Time' column
    plt.figure(figsize=(15, 2 * num_signals))
    
    duration = data['Epoch Time'].iloc[-1] - data['Epoch Time'].iloc[0]  # Compute duration based on timestamps
    for i in range(num_signals):
        plt.subplot(num_signals, 1, i + 1)
        # Normalize time for the plot between 0 and duration
        normalized_time = data['Epoch Time'] - data['Epoch Time'].iloc[0]
        plt.plot(normalized_time, data.iloc[:, i], label=data.columns[i], linewidth=1)
        plt.xlim(0, duration)  # Set x-axis limits from 0 to duration
        plt.xlabel('Time (seconds)')
        plt.ylabel(data.columns[i])
        plt.title(f'Signal: {data.columns[i]}')
        plt.grid()
        plt.legend()

    # Save the plot to the 'saved plots' directory
    plot_filename = os.path.join(saved_plots_directory, f'{os.path.basename(file_path).replace(".txt", "")}.png')
    plt.tight_layout()
    plt.savefig(plot_filename)
    plt.close()  # Close the plot to free up memory
    print(f"Plot saved: {plot_filename}")

def monitor_directory():
    print("Monitoring directory for new files...")
    print(f"Looking in: {directory_to_monitor} for .txt files.")
    while True:
        try:
            # List all files in the specified directory
            files_in_directory = os.listdir(directory_to_monitor)

            for filename in files_in_directory:
                file_path = os.path.join(directory_to_monitor, filename)
                
                # Check if the file has already been processed
                if filename.endswith('.txt') and filename not in processed_files:
                    print(f"Detected new file: {filename}")
                    
                    # Wait until the file is fully uploaded
                    if is_file_ready(file_path):
                        print(f"Processing new file: {filename}")
                        plot_signals(file_path)
                        processed_files.add(filename)
                        
                        # Move processed file to the 'saved data' directory
                        shutil.move(file_path, os.path.join(saved_data_directory, filename))
                        print(f"Moved file to: {saved_data_directory}")
                    else:
                        print(f"File {filename} is still being uploaded.")

            print("Waiting for new files...")  # Indicate it's actively running

        except Exception as e:
            print(f"Error in monitoring directory: {e}")

        time.sleep(5)  # Check for new files every 5 seconds

if __name__ == "__main__":
    monitor_directory()