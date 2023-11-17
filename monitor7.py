import json
from bluepy.btle import Scanner, BTLEException

def log_devices(devices, previous_devices, ownership_data):
    with open('bluetooth_log.txt', 'a') as file:
        file.write("Found BLE devices:\n")

        # Cek perangkat yang datang
        for dev in devices:
            try:
                if dev.addr not in previous_devices:
                    # Perangkat baru datang
                    name = dev.getValueText(9) if dev.getValueText(9) else "Unknown"
                    file.write(f"Device {dev.addr} ({dev.addrType}), Name: {name}, RSSI={dev.rssi} dB - Arrived\n")

                    # Tambahkan informasi kepemilikan jika tersedia
                    if dev.addr in ownership_data:
                        owner = ownership_data[dev.addr]['owner']
                        file.write(f"Owner: {owner}\n")
                    else:
                        file.write("Owner: Unknown\n")

            except BTLEException as e:
                print(f"Error: {e}")

        # Cek perangkat yang pergi
        for prev_dev in previous_devices:
            if prev_dev not in devices:
                # Perangkat sudah tidak terdeteksi
                file.write(f"Device {prev_dev} - Disappeared\n")

        file.write("--------------------------------------------------\n")

scanner = Scanner()
ownership_data = {}
previous_devices = set()

while True:
    devices = scanner.scan(10.0)  # Melakukan pemindaian selama 10 detik
    log_devices(devices, previous_devices, ownership_data)

    # Memperbarui set perangkat sebelumnya
    previous_devices = set([dev.addr for dev in devices])
