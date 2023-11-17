import json
from bluepy.btle import Scanner, BTLEException

def log_devices(devices, ownership_data):
    with open('bluetooth_log.txt', 'a') as file:
        file.write("Found BLE devices:\n")
        for dev in devices:
            try:
                # Mendapatkan nama perangkat jika tersedia
                name = dev.getValueText(9)  # Nilai 9 adalah untuk nama perangkat
                if name is not None:
                    file.write(f"Device {dev.addr} ({dev.addrType}), Name: {name}, RSSI={dev.rssi} dB\n")
                else:
                    file.write(f"Device {dev.addr} ({dev.addrType}), Name: Unknown, RSSI={dev.rssi} dB\n")

                # Mendapatkan jenis perangkat jika tersedia
                for (adtype, desc, value) in dev.getScanData():
                    if desc == 'Complete Local Name' and value.lower().startswith('type'):
                        file.write(f"Type: {value}\n")
                        break

                # Menambahkan informasi kepemilikan MAC ke dalam file JSON terpisah
                if dev.addr in ownership_data:
                    ownership_data[dev.addr]['last_seen'] = str(dev.scanData)
                else:
                    ownership_data[dev.addr] = {
                        'last_seen': str(dev.scanData),
                        'owner': 'Your_Name_or_ID'  # Ganti dengan informasi kepemilikan Anda
                    }

            except BTLEException as e:
                print(f"Error: {e}")

        file.write("--------------------------------------------------\n")

        # Menyimpan informasi kepemilikan MAC ke dalam file JSON terpisah
        with open('mac_ownership.json', 'w') as json_file:
            json.dump(ownership_data, json_file, indent=4)

scanner = Scanner()
ownership_data = {}

while True:
    devices = scanner.scan(10.0)  # Melakukan pemindaian selama 10 detik
    log_devices(devices, ownership_data)
