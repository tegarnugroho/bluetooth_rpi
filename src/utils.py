import bluetooth
from PIL import Image

def is_valid_bluetooth_address(address):
    # Check if a Bluetooth address is valid
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
    # Get the type of a Bluetooth device based on its device class
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
    # Check if a Bluetooth device is connected
    connected_devices = bluetooth.lookup_name(address)
    return address in connected_devices

def get_image(image_path, max_width):
    # Load and resize an image
    image = Image.open(image_path)
    image = image.convert()  # Convert to black and white (monochrome) image

    # Resize the image to fit the paper width (adjust the width as needed)
    width, height = image.size
    if width > max_width:
        ratio = max_width / width
        new_width = max_width
        new_height = int(height * ratio)
        image = image.resize((new_width, new_height), Image.ANTIALIAS)

    return image

def border_line(device, line_width=48, line_character='-'):
    # Print a line of a specified width and character
    line = line_character * line_width
    device.text(line + '\n')
    
def space(length_space):
    # Create a string of spaces with a specified length
    line = ' ' * length_space
    return line
