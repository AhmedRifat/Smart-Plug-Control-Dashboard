from flask import Flask, render_template, jsonify, request, redirect, url_for
from datetime import datetime, timedelta
import json
import os
import atexit
import subprocess
from tuya_control import TuyaDevice

from config import DATA_FILES

app = Flask(__name__)
device = TuyaDevice()

TUYA_MONITOR_DIR = os.path.join(os.path.dirname(__file__), 'tuyapi-node')
TUYA_MONITOR_SCRIPT = 'tuya-monitor.js'

node_process = subprocess.Popen(
    ['node', TUYA_MONITOR_SCRIPT],
    cwd=TUYA_MONITOR_DIR,          # set working directory so 'node' runs in tuyapi-node folder
    stdout=subprocess.PIPE,        # optional: capture stdout
    stderr=subprocess.PIPE         # optional: capture stderr
)
import threading

def print_node_output(stream, prefix=''):
    for line in iter(stream.readline, b''):
        print(prefix + line.decode('utf-8').rstrip())

threading.Thread(target=print_node_output, args=(node_process.stdout, '[NODE stdout] '), daemon=True).start()
threading.Thread(target=print_node_output, args=(node_process.stderr, '[NODE stderr] '), daemon=True).start()
# Initialize data files if they don't exist
if not os.path.exists('data'):
    os.makedirs('data')

if not os.path.exists(DATA_FILES['energy_logs']):
    with open(DATA_FILES['energy_logs'], 'w') as f:
        json.dump([], f)

if not os.path.exists(DATA_FILES['device_status']):
    with open(DATA_FILES['device_status'], 'w') as f:
        json.dump({'status': 'unknown'}, f)

# Replace log_energy_data() with:
def log_energy_data():
    """Log data exactly every 5 minutes"""
    data = device.get_status()
    if not data.get('connected'):
        return

    with open(DATA_FILES['energy_logs'], 'r+') as f:
        logs = json.load(f)
        last_log = logs[-1] if logs else None
        
        # Log if first entry or 5 minutes have passed
        should_log = True  # Default for first entry
        if last_log:
            last_time = datetime.strptime(last_log['timestamp'], '%Y-%m-%d %H:%M:%S')
            should_log = (datetime.now() - last_time).total_seconds() >= 120

        if should_log:
            logs.append({
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'power': round(data['power'], 2),
                'voltage': round(data['voltage'], 1),
                'current': round(data['current'], 3)
            })
            f.seek(0)
            json.dump(logs, f, indent=2)

def get_energy_logs(date=None):
    """Get energy logs, optionally filtered by date"""
    with open(DATA_FILES['energy_logs'], 'r') as f:
        logs = json.load(f)
    
    if date:
        return [log for log in logs if log['timestamp'].startswith(date)]
    return logs

def get_available_dates():
    """Get unique dates with logged data"""
    with open(DATA_FILES['energy_logs'], 'r') as f:
        logs = json.load(f)
    
    dates = set()
    for log in logs:
        date = log['timestamp'].split()[0]
        dates.add(date)
    
    return sorted(dates, reverse=True)[:30]  # Last 30 days

def calculate_total_consumption(logs):
    """Calculate total energy consumption in kWh from logs"""
    if not logs or len(logs) < 2:
        return 0.0
    
    total_wh = 0.0
    
    # Sort logs by timestamp to ensure chronological order
    sorted_logs = sorted(logs, key=lambda x: x['timestamp'])
    
    for i in range(1, len(sorted_logs)):
        prev_log = sorted_logs[i-1]
        current_log = sorted_logs[i]
        
        try:
            # Parse timestamps
            prev_time = datetime.strptime(prev_log['timestamp'], '%Y-%m-%d %H:%M:%S')
            current_time = datetime.strptime(current_log['timestamp'], '%Y-%m-%d %H:%M:%S')
            
            # Calculate time difference in hours
            time_diff_hours = (current_time - prev_time).total_seconds() / 3600.0
            
            # Calculate average power between the two points
            avg_power = (prev_log['power'] + current_log['power']) / 2.0
            
            # Add to total energy (in Wh)
            total_wh += avg_power * time_diff_hours
        except (KeyError, ValueError):
            continue
    
    # Convert to kWh
    return total_wh / 1000.0

def cleanup_node_process():
    print("Shutting down Node.js Tuya monitor...")
    node_process.terminate()
    try:
        node_process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        node_process.kill()

atexit.register(cleanup_node_process)

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/manual')
def manual():
    return render_template('manual.html')


@app.route('/history')
def history():
    date = request.args.get('date')
    dates = get_available_dates()
    
    if date:
        logs = get_energy_logs(date)
        times = [log['timestamp'].split()[1][:5] for log in logs]
        powers = [log['power'] for log in logs]
        volts = [log['voltage'] for log in logs]
        currents = [log['current'] for log in logs]
        total_consumption = calculate_total_consumption(logs)
    else:
        logs = []
        times = powers = volts = currents = []
        total_consumption = None
    
    return render_template('history.html', 
                         dates=dates, 
                         selected_date=date,
                         times=times,
                         powers=powers,
                         volts=volts,
                         currents=currents,
                         total_consumption=total_consumption)

@app.route('/api/status')
def get_status():
    data = device.get_status()
    log_energy_data()  # Log data each time we check status
    return jsonify(data)

@app.route('/api/turn_on', methods=['POST'])
def turn_on():
    result = device.turn_on()
    return jsonify(result)

@app.route('/api/turn_off', methods=['POST'])
def turn_off():
    result = device.turn_off()
    return jsonify(result)

@app.teardown_appcontext
def shutdown(exception=None):
    device.stop_keep_alive()

# Register cleanup
atexit.register(shutdown)

if __name__ == '__main__':
    app.run(debug=True)