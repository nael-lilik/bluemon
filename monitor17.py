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

    # Load ulang device names setiap kali pemindaian terjadi
    device_names = load_device_names()

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
            memory[addr] = {'last_appeared': timestamp}  # Menyimpan waktu muncul terakhir

        else:
            # Perangkat telah tercatat sebagai menghilang sebelumnya, abaikan
            if previous_devices[addr]['disappeared']:
                continue

            if -60 <= rssi <= 0:
                if previous_devices[addr]['disappeared'] is None:
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

appeared_log = set()  # Untuk menyimpan perangkat yang sudah muncul dalam log
disappeared_log = set()  # Untuk menyimpan perangkat yang sudah menghilang dalam log

scanner = Scanner()
previous_devices = load_memory()
memory = {}
device_names = load_device_names()

while True:
    try:
        devices = scanner.scan(10.0)  # Lakukan pemindaian selama 10 detik

        # Log perangkat yang datang, ada, dan pergi
        previous_devices, memory, device_names = log_devices(devices, previous_devices, memory, device_names)

        # Simpan memori ke file JSON
        save_memory(previous_devices)

        # Log ke file
        log_status(previous_devices, appeared_log, disappeared_log)

    except KeyboardInterrupt:
        # Simpan memori terakhir sebelum keluar dari skrip
        save_memory(previous_devices)
        break
