import json
from bluepy.btle import Scanner, BTLEException
import datetime

def log_devices(devices, previous_devices, ownership_data):
    current_devices = {dev.addr for dev in devices}

    # Cari perangkat yang datang (baru muncul)
    new_devices = current_devices - previous_devices
    if new_devices:
        log_status("Arrived", new_devices, ownership_data)

    # Cari perangkat yang pergi (tidak terdeteksi lagi)
    disappeared_devices = previous_devices - current_devices
    if disappeared_devices:
        log_status("Disappeared", disappeared_devices, ownership_data)

    # Simpan perangkat saat ini sebagai perangkat sebelumnya
    return current_devices

def log_status(status, device_set, ownership_data):
    with open('bluetooth_log.txt', 'a') as file:
        file.write(f"{status} BLE devices at {datetime.datetime.now()}:\n")
        for addr in device_set:
            try:
                # Cari informasi nama dan kepemilikan perangkat jika tersedia
                name = "Unknown"
                owner = "Unknown"
                if addr in ownership_data:
                    owner = ownership_data[addr]['owner']
                file.write(f"Device {addr}, Owner: {owner}, Name: {name} - {status}\n")
            except BTLEException as e:
                print(f"Error: {e}")
        file.write("--------------------------------------------------\n")

scanner = Scanner()
ownership_data = {}
previous_devices = set()

while True:
    try:
        devices = scanner.scan(10.0)  # Lakukan pemindaian selama 10 detik

        # Log perangkat yang datang dan pergi
        previous_devices = log_devices(devices, previous_devices, ownership_data)

    except KeyboardInterrupt:
        break
