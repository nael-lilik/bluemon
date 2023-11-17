from bluepy.btle import Scanner, BTLEException
import json
import datetime

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

    for addr, rssi in current_devices.items():
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if addr not in previous_devices:
            previous_devices[addr] = {
                'appeared': timestamp,
                'disappeared': None,
                'last_seen_rssi': rssi,
                'stay_duration': 0,
                'name': device_names.get(addr, 'Unknown')
            }
        else:
            if addr not in memory:
                memory[addr] = {'total_stay_duration': 0}

            if -60 <= rssi <= 0:
                if previous_devices[addr]['disappeared'] is None:
                    previous_devices[addr]['stay_duration'] += 10
                    memory[addr]['total_stay_duration'] += 10
            else:
                if previous_devices[addr]['disappeared'] is None:
                    previous_devices[addr]['disappeared'] = timestamp

    return previous_devices, memory

def log_status(previous_devices):
    with open('bluetooth_log.txt', 'a') as file:
        for addr, data in previous_devices.items():
            appeared = data['appeared']
            disappeared = data['disappeared']
            stay_duration = data['stay_duration']
            name = data['name']
            file.write(f"Device {addr} ({name}) appeared at {appeared}, Stay duration: {stay_duration} seconds")
            if disappeared:
                file.write(f", Disappeared at {disappeared}")
            file.write("\n")
        file.write("--------------------------------------------------\n")

scanner = Scanner()
previous_devices = load_memory()
memory = {}
device_names = load_device_names()

while True:
    try:
        devices = scanner.scan(10.0)  # Lakukan pemindaian selama 10 detik

        # Log perangkat yang datang, ada, dan pergi
        previous_devices, memory = log_devices(devices, previous_devices, memory, device_names)

        # Simpan memori ke file JSON
        save_memory(previous_devices)

        # Log ke file
        log_status(previous_devices)

    except KeyboardInterrupt:
        # Simpan memori terakhir sebelum keluar dari skrip
        save_memory(previous_devices)
        break
