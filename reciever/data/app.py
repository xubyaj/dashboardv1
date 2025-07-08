from flask import Flask, jsonify, render_template_string
import os
import glob
import socket
from contextlib import closing
import plotly

app = Flask(__name__)

# Path to "Plots" directory
network_share_path = os.path.join(os.getcwd(), "Plots")

# HTML with extra console logs & window.onload
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Live Sinewave Plot - Most Recent File</title>
    <script src="/static/plotly.min.js"></script>
</head>
<body>
    <h2>Live Sinewave Plot (Most Recent File)</h2>
    <div id="plot" style="width:90vw; height:70vh;"></div>
    <p id="filename"></p>

    <script>
    window.onload = function() {
        console.log("JavaScript Loaded. Initializing Plot...");

        let lastIndex = 0;
        let lastFile = "";

        const trace = {
            x: [],
            y: [],
            mode: 'lines+markers',
            name: 'Sinewave'
        };

        const layout = {
            margin: { t: 20 },
            xaxis: { title: 'Sample Index' },
            yaxis: { title: 'Amplitude' }
        };

        Plotly.newPlot('plot', [trace], layout);
        console.log("Initial empty plot created.");

        async function fetchData() {
            console.log("Fetching /data...");
            try {
                const response = await fetch('/data');
                const result = await response.json();
                console.log("Data received:", result);
                return result;
            } catch (error) {
                console.error("Error fetching data:", error);
                return { values: [], filename: "Error fetching data" };
            }
        }

        async function updatePlot() {
            const data = await fetchData();
            const yData = data.values;
            const fileName = data.filename;

            if (fileName !== lastFile || yData.length < lastIndex) {
                console.log("Resetting plot due to new file or data reset.");
                Plotly.react('plot', [{
                    x: [],
                    y: [],
                    mode: 'lines+markers',
                    name: 'Sinewave'
                }], layout);
                lastIndex = 0;
                lastFile = fileName;
            }

            if (yData.length > lastIndex) {
                const newY = yData.slice(lastIndex);
                const newX = Array.from({length: newY.length}, (_, i) => lastIndex + i);

                Plotly.extendTraces('plot', {
                    x: [newX],
                    y: [newY]
                }, [0]);

                lastIndex = yData.length;

                const maxPoints = 1000;
                const minX = Math.max(0, lastIndex - maxPoints);
                Plotly.relayout('plot', {
                    'xaxis.range': [minX, lastIndex]
                });
            }

            document.getElementById('filename').textContent = 'Current file: ' + fileName;
        }

        setInterval(updatePlot, 500);  // update every 500ms
    };
    </script>
</body>
</html>
"""

def get_most_recent_txt_file(folder):
    files = glob.glob(os.path.join(folder, "*.txt"))
    return max(files, key=os.path.getmtime) if files else None

def list_txt_files(folder):
    print(f"Listing .txt files in {folder}")
    for f in glob.glob(os.path.join(folder, "*.txt")):
        print(f" - {os.path.basename(f)}")

def find_open_port(start=5000, end=5100):
    for port in range(start, end):
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            if s.connect_ex(('0.0.0.0', port)) != 0:
                return port
    raise RuntimeError("No open ports found.")

def get_local_ip():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as s:
        try:
            s.connect(('10.255.255.255', 1))
            return s.getsockname()[0]
        except Exception:
            return '127.0.0.1'

@app.route("/")
def index():
    return render_template_string(HTML_PAGE)

@app.route("/data")
def data():
    file = get_most_recent_txt_file(network_share_path)
    if file:
        try:
            with open(file, "r") as f:
                lines = [line.strip() for line in f if line.strip()]
            values = list(map(float, lines))
            filename = os.path.basename(file)
        except Exception as e:
            print(f"Error reading file: {e}")
            values = []
            filename = "Error reading file"
    else:
        values = []
        filename = "No .txt files found"
    return jsonify({"values": values, "filename": filename})

if __name__ == "__main__":
    list_txt_files(network_share_path)
    port = find_open_port()
    local_ip = get_local_ip()
    print(f"Starting server at http://{local_ip}:{port}")
    app.run(host="0.0.0.0", port=port)
