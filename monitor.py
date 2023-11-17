import bluetooth
import datetime

def log_devices(devices):
    with open('bluetooth_log.txt', 'a') as file:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"Timestamp: {timestamp}\n")
        for addr, name, device_class in devices:
            file.write(f"Found device: {name} with address {addr} and class {device_class}\n")
        file.write("--------------------------------------------------\n")

def device_discovered(address, device_class):
    print(f"Found device with address {address} and class {device_class}")
    log_devices([(address, "Unknown", device_class)])  # Menyimpan data ke dalam log

# Callback function yang akan dipanggil ketika perangkat ditemukan
bluetooth.bluez.hci_enable_le_scan()
bluetooth.bluez.hci_enable_classic_discovery()
bluetooth.bluez.hci_filter_all()
bt_sock = bluetooth.bluez.hci_open_dev(0)

def event_loop():
    while True:
        pkt = bt_sock.recv(255)
        ptype, event, plen = bluetooth.bluez.hci_acl_packet_type(pkt)
        if event == bluetooth.bluez.EVT_INQUIRY_RESULT_WITH_RSSI or event == bluetooth.bluez.EVT_LE_META_EVENT:
            pkt_offset = 0
            subevent, = bluetooth.bluez.get_le_meta_subevent(pkt)
            if subevent == bluetooth.bluez.EVT_LE_ADVERTISING_REPORT:
                pkt_offset, addr_type, addr, _, length, adv_data = bluetooth.bluez.parse_le_advertising_packet(pkt, pkt_offset)
                device_class = "Unknown"
                if len(adv_data) > 2:
                    device_class = adv_data[1]
                device_discovered(addr, device_class)

event_loop()
