from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from flask_cors import CORS  # Tambahkan impor untuk Flask-CORS
from threading import Thread
import json
from bluepy.btle import Scanner
import datetime

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")  # Izinkan akses dari semua sumber
CORS(app)  # Menambahkan middleware CORS ke aplikasi Flask

# Definisikan fungsi-fungsi lainnya seperti yang Anda butuhkan

def save_memory(memory):
    with open('bluetooth_memory.json', 'w') as file:
        json.dump(memory, file, indent=4)

def load_memory():
    try:
        with open('bluetooth_memory.json', 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def load_device_names():
    try:
        with open('bluetooth_device_names.json', 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def log_devices(devices, previous_devices, memory, device_names):
    current_devices = {dev.addr: dev.rssi for dev in devices}

    # Load ulang device names setiap kali pemindaian terjadi
    device_names = load_device_names()

    for addr, rssi in current_devices.items():
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if addr not in memory:
            memory[addr] = {}  # Membuat struktur data kosong jika belum ada

        if addr not in previous_devices:
            previous_devices[addr] = {
                'appeared': timestamp,
                'disappeared': None,
                'last_appeared': None,
                'last_seen_rssi': rssi,
                'stay_duration': 0,
                'name': device_names.get(addr, 'Unknown')
            }
            # Tambahkan entri untuk last_appeared ke dalam memory saat perangkat muncul pertama kali
            memory[addr] = {'last_appeared': timestamp}

        else:
            # Perangkat telah tercatat sebagai menghilang sebelumnya, abaikan
            if previous_devices[addr]['disappeared']:
                continue

            if -60 <= rssi <= 0:
                if previous_devices[addr]['disappeared'] is None:
                    # Pastikan 'last_appeared' sudah ada di dalam memory
                    if 'last_appeared' not in memory[addr]:
                        memory[addr]['last_appeared'] = timestamp

                    last_appeared_time = datetime.datetime.strptime(memory[addr]['last_appeared'], "%Y-%m-%d %H:%M:%S")
                    current_time = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                    time_difference = current_time - last_appeared_time
                    memory[addr]['total_stay_duration'] = time_difference.seconds

                    previous_devices[addr]['stay_duration'] = memory[addr]['total_stay_duration']

            else:
                if previous_devices[addr]['disappeared'] is None:
                    previous_devices[addr]['disappeared'] = timestamp
                    memory[addr]['last_appeared'] = None

    return previous_devices, memory, device_names

def log_status(previous_devices, appeared_log, disappeared_log):
    with open('bluetooth_log.txt', 'a') as file:
        for addr, data in previous_devices.items():
            if data['disappeared'] is None and addr not in appeared_log:  # Log untuk perangkat yang masih bertahan (stay)
                appeared = data['appeared']
                stay_duration = data['stay_duration']
                name = data['name']
                file.write(f"Device {addr} ({name}) appeared at {appeared}, Stay duration: {stay_duration} seconds\n")
                appeared_log.add(addr)

            if data['disappeared'] and addr not in disappeared_log:  # Log untuk perangkat yang menghilang
                disappeared = data['disappeared']
                name = data['name']
                file.write(f"Device {addr} ({name}) disappeared at {disappeared}\n")
                disappeared_log.add(addr)

        file.write("--------------------------------------------------\n")

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    memory = load_memory()
    emit('initial_data', {'devices': memory})

def log_devices_and_update():
    appeared_log = set()
    disappeared_log = set()
    previous_devices = {}

    scanner = Scanner()

    while True:
        devices = scanner.scan(10.0)

        previous_devices, memory, device_names = log_devices(devices, previous_devices, {}, {})
        save_memory(previous_devices)
        log_status(previous_devices, appeared_log, disappeared_log)
#        socketio.emit('update', {'devices': previous_devices}, namespace='/update')
        socketio.emit('update', {'devices': previous_devices})
#        socketio.sleep(1)  # Ganti dengan waktu yang sesuai dengan kebutuhan

if __name__ == '__main__':
    # Memulai tugas log_devices_and_update() dalam thread terpisah
    bg_thread = Thread(target=log_devices_and_update)
    bg_thread.daemon = True  # Agar thread berhenti saat aplikasi berhenti
    bg_thread.start()

    socketio.run(app, host='172.16.17.1', debug=True)
