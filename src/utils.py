import bluetooth
from PIL import Image

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

def get_image(image_path):

    # Load and convert the image
    image = Image.open(image_path)
    image = image.convert()  # Convert to black and white (monochrome) image

    # Resize the image to fit the paper width (adjust the width as needed)
    max_width = 512  # Maximum width for an 80mm paper (80mm = 3.15 inches = 3.15 * 72 dpi = 226.8 pixels)
    width, height = image.size
    if width > max_width:
        ratio = max_width / width
        new_width = max_width
        new_height = int(height * ratio)
        image = image.resize((new_width, new_height), Image.ANTIALIAS)

    return image
