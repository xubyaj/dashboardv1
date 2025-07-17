import numpy as np
import time
import random
import os
import sys

# Set path to shared folder (adjust as needed)
network_share_path = r"/run/user/1000/gvfs/smb-share:server=192.168.20.29,share=data/real time/data"
os.makedirs(network_share_path, exist_ok=True)

user_id = input("Enter your user ID: ").strip()
filename = f"sinewave_{user_id}.txt"
filepath = os.path.join(network_share_path, filename)

sample_rate = 30  # samples per second

def generate_sinewave(freq, amplitude, t):
    return amplitude * np.sin(2 * np.pi * freq * t)

def main():
    print(f"Writing sinewave to {filepath} ... (Press Ctrl+C to stop)")
    try:
        with open(filepath, "a") as f:
            while True:
                freq = random.uniform(0.5, 5.0)
                amplitude = random.uniform(0.5, 2.0)
                t = np.linspace(0, 1, sample_rate, endpoint=False)
                signal = generate_sinewave(freq, amplitude, t)

                for val in signal:
                    f.write(f"{val:.5f}\n")
                    f.flush()          # Flush Python buffer
                    os.fsync(f.fileno())  # Flush OS buffer
                    time.sleep(1 / sample_rate)
    except KeyboardInterrupt:
        print("\nStopped by user.")
        sys.exit(0)

if __name__ == "__main__":
    main()
