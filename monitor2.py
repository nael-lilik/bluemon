import bluetooth
import datetime

def log_devices(devices):
    with open('bluetooth_log.txt', 'a') as file:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"Timestamp: {timestamp}\n")
        for addr, name in devices.items():
            file.write(f"Found device: {name} with address {addr}\n")
        file.write("--------------------------------------------------\n")

def device_discovered(address, device_name):
    print(f"Found device with address {address} and name {device_name}")
    log_devices({address: device_name})  # Menyimpan data ke dalam log

def discover_ble_devices():
    nearby_devices = bluetooth.discover_devices(duration=8, lookup_names=True, lookup_lue=True)
    return nearby_devices

while True:
    ble_devices = discover_ble_devices()
    for addr, name in ble_devices:
        device_discovered(addr, name)

