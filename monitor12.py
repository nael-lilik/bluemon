import json
from bluepy.btle import Scanner, BTLEException
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

def log_devices(devices, previous_devices, ownership_data):
    current_devices = {dev.addr: dev.rssi for dev in devices}

    # Cari perangkat yang datang (baru muncul)
    new_devices = current_devices.keys() - previous_devices.keys()
    if new_devices:
        log_status("Arrived", new_devices, current_devices, ownership_data)

    # Cari perangkat yang pergi (tidak terdeteksi lagi)
    disappeared_devices = previous_devices.keys() - current_devices.keys()
    if disappeared_devices:
        log_status("Disappeared", disappeared_devices, previous_devices, ownership_data)

    # Cari perangkat yang stay (RSSI kuat antara -60 sampai 0)
    stayed_devices = {addr: rssi for addr, rssi in current_devices.items() if -60 <= rssi <= 0}
    if stayed_devices:
        log_status("Stay", stayed_devices.keys(), stayed_devices, ownership_data)

    # Simpan perangkat saat ini sebagai perangkat sebelumnya
    return current_devices

def log_status(status, device_set, rssi_data, ownership_data):
    with open('bluetooth_log.txt', 'a') as file:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"{timestamp} - {status} BLE devices:\n")
        for addr in device_set:
            try:
                rssi = rssi_data[addr]
                name = "Unknown"
                owner = "Unknown"
                if addr in ownership_data:
                    owner = ownership_data[addr]['owner']
                file.write(f"{timestamp} - Device {addr}, Owner: {owner}, Name: {name}, RSSI: {rssi} dB - {status}\n")
            except BTLEException as e:
                print(f"Error: {e}")
        file.write("--------------------------------------------------\n")

scanner = Scanner()
ownership_data = {}
previous_devices = {}
stay_start_time = {}

# Memuat memori sebelumnya jika ada
previous_devices = load_memory()

while True:
    try:
        devices = scanner.scan(10.0)  # Lakukan pemindaian selama 10 detik

        # Log perangkat yang datang, ada, dan pergi
        previous_devices = log_devices(devices, previous_devices, ownership_data)

        # Update waktu perangkat tinggal (stay) sebelum pergi
        for addr in previous_devices.keys() - stay_start_time.keys():
            stay_start_time[addr] = datetime.datetime.now()

        # Hitung waktu perangkat tinggal (stay) saat stay
        for addr in stay_start_time.keys() & previous_devices.keys():
            if addr in stay_start_time:
                if addr not in stay_start_time:
                    stay_start_time[addr] = datetime.datetime.now()

                stay_duration = datetime.datetime.now() - stay_start_time[addr]
                print(f"Device {addr} stayed for {stay_duration}")

        # Simpan memori ke file JSON
        save_memory(previous_devices)

    except KeyboardInterrupt:
        # Simpan memori terakhir sebelum keluar dari skrip
        save_memory(previous_devices)
        break
