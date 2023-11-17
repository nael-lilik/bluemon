from bluepy.btle import Scanner

def log_devices(devices):
    with open('bluetooth_log.txt', 'a') as file:
        file.write("Found BLE devices:\n")
        for dev in devices:
            file.write(f"Device {dev.addr} ({dev.addrType}), RSSI={dev.rssi} dB\n")
        file.write("--------------------------------------------------\n")

scanner = Scanner()
while True:
    devices = scanner.scan(10.0)  # Melakukan pemindaian selama 10 detik
    log_devices(devices)
