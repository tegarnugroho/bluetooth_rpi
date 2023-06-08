import bluetooth
import subprocess

def is_valid_bluetooth_address(address):
    parts = address.split(':')
    if len(parts) != 6:
        return False
    for part in parts:
        try:
            int(part, 16)
        except ValueError:
            return False
    return True

def get_device_type(device_class):
    major_class = (device_class >> 8) & 0xFF

    device_types = {
        0x01: 'Computer',
        0x02: 'Phone',
        0x03: 'Network Access Point',
        0x04: 'Audio/Video',
        0x05: 'Peripheral',
        0x06: 'Imaging',
        0x07: 'Wearable',
        0x08: 'Toy',
        0x09: 'Health',
        0x1F: 'Uncategorized'
    }
    
    if major_class == 0x05:  # Peripheral class
        if (device_class >> 2) & 0x01 == 1:  # Check if the device is a BLE device
            return 'BLE Device'
        else:
            return 'Peripheral'
    elif major_class == 0x01:  # Computer class
        # Check if the device is a tablet
        if (device_class >> 2) & 0x02 == 1:
            return 'Tablet'
        else:
            return device_types.get(major_class, 'Unknown')
    else:
        return device_types.get(major_class, 'Unknown')

def is_device_connected(address):
    connected_devices = bluetooth.lookup_name(address)
    return address in connected_devices