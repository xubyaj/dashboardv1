import os
import pandas as pd
import matplotlib.pyplot as plt
import time
import shutil
from datetime import datetime
import cups
import re

# Specify your network share directory
directory_to_save = r'/data/post processing/'
directory_to_monitor = r'/data/post processing/new data'
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
    # Extract the number from the filename to use in the title
    file_name = os.path.basename(file_path)
    match = re.search(r'_(\d+)\.txt$', file_name)  # Change regex according to your file naming convention
    number = file_name.split('_')[-1]#match.group(1) if match else "Unknown"

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
        plt.title(f'Signal {i+1} from Participant: {number}')  # Add title with file number
        plt.grid()
        plt.legend()

    # Save the plot to the 'saved plots' directory
    plot_filename = os.path.join(saved_plots_directory, f'{os.path.basename(file_path).replace(".txt", "")}.png')
    
    # Step 2: Save the plot to a file
    plot_path = plot_filename # Ensure this path is writable
    plt.tight_layout()
    plt.savefig(plot_filename)
    plt.close()  # Close the plot to free up memory
    print(f"Plot saved: {plot_filename}")

    # Step 3: Print the plot using CUPS
    def print_image(image_path, printer_name):
        # Connect to CUPS
        conn = cups.Connection()
        
        # Check available printers
        printers = conn.getPrinters()
        for index, (name, details) in enumerate(printers.items()):
            print(f"{index}: {name} - {details}")

        if printer_name not in printers.keys():
            print(f"Printer {printer_name} not found.")
            return

        # Print the image
        print_job_id = conn.printFile(printer_name, image_path, "Sine Wave Plot", {})
        print(f"Print job sent with ID: {print_job_id}")

    # Define the printer name (check if it matches exactly with the output above)
    printer_name = 'Canon_TR8600_series'  # Replace with your configured printer's name

    print_image(plot_path, printer_name)

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