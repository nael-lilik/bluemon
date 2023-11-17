from bluepy.btle import Scanner, BTLEException

def log_devices(devices):
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
            except BTLEException as e:
                print(f"Error: {e}")

        file.write("--------------------------------------------------\n")

scanner = Scanner()
while True:
    devices = scanner.scan(10.0)  # Melakukan pemindaian selama 10 detik
    log_devices(devices)
