
import bluetooth
import usb.core
import usb.util

from flask import Blueprint, jsonify, request
from utils import is_valid_bluetooth_address, get_device_type, is_device_connected
from escpos import printer, exceptions as printer_exceptions

bluetooth_routes = Blueprint('bluetooth', __name__)



@bluetooth_routes.route('/bluetooth/devices', methods=['GET'])
def get_bluetooth_devices():
    nearby_devices = bluetooth.discover_devices(lookup_names=True, flush_cache=True, lookup_class=True)
    devices = []

    for device_address, device_name, device_class in nearby_devices:
        device_data = {
            'address': device_address,
            'name': device_name,
            'class': device_class,
            'type': get_device_type(device_class),
            'is_connected': is_device_connected(device_address),
            'services': []
        }

        # Search for services for the current device
        services = bluetooth.find_service(address=device_address)

        for service in services:
            port = service['port']
            name = service['name']
            host = service['host']
            protocol = service["protocol"]
            service_classes = service["service-classes"]
            service_id = service["service-id"]

            service_data = {
                'port': port,
                'name': name,
                'host': host,
                'protocol': protocol,
                'service-classes': service_classes,
                'service-id': service_id,
                # Include any other service-related information if needed
            }

            device_data['services'].append(service_data)

        devices.append(device_data)

    return jsonify({
        'data': devices,
        'status_code': 200,
        'message': 'ok!'
    }), 200
    
@bluetooth_routes.route('/bluetooth/connected-devices', methods=['GET'])
def get_connected_devices():
    connected_devices = bluetooth.discover_devices(lookup_names=True)

    devices = []
    for device_address, device_name in connected_devices:
        devices.append({
            'address': device_address,
            'name': device_name
        })

    return jsonify({
        'data': devices,
        'status_code': 200,
        'message': 'ok!'
    }), 200 

@bluetooth_routes.route('/bluetooth/connect', methods=['POST'])
def connect_bluetooth_device():
    address = str(request.json.get('address'))  # Convert the Bluetooth device address to a string
    status = {
        0: 'ok',
        1: 'communication timeout',
        3: 'checksum error',
        4: 'unknown command',
        5: 'invalid access level',
        8: 'hardware error',
        10: 'device not ready',
    }

    if not is_valid_bluetooth_address(address):
        return jsonify({'message': 'Invalid Bluetooth address'}), 400

    try:
        socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        socket.connect((address, 1))  # Connect to the Bluetooth device using the discovered port and RFCOMM protocol

        # Perform any necessary operations with the connected Bluetooth device

        return jsonify({'message': 'Bluetooth device connected successfully', 'address': address})
    except bluetooth.BluetoothError as e:
        error_code = e.args[0]
        error_message = status.get(error_code, str(e))
        return jsonify({'message': error_message, 'from': 'BluetoothError', 'address': address, 'error_code': error_code}), 500
    except Exception as e:
        return jsonify({'message': str(e), 'from': 'Exception', 'address': address}), 500


@bluetooth_routes.route('/usb/devices', methods=['GET'])
def get_usb_devices():
    usb_devices = []

    try:
        for device in usb.core.find(find_all=True):
            manufacturer = usb.util.get_string(device, device.iManufacturer) if device.iManufacturer else None
            product = usb.util.get_string(device, device.iProduct) if device.iProduct else None
            serial_number = usb.util.get_string(device, device.iSerialNumber) if device.iSerialNumber else None

            device_data = {
                'name': product,
                'vendor': manufacturer,
                'serial_number': serial_number,
                'is_connected': True
            }
            usb_devices.append(device_data)

        return jsonify({
            'data': usb_devices, 
            'status_code': 200,
            'message': 'ok!'
            },), 200
    except usb.core.USBError as e:
        error_message = f"USBError: {str(e)}"
        print(error_message)
        return jsonify({'error': error_message})
    except Exception as e:
        error_message = f"An error occurred while retrieving USB devices: {str(e)}"
        print(error_message)
        return jsonify({'error': error_message})

# API route to print a receipt and kick the cash drawer
@bluetooth_routes.route('printer/print-receipt', methods=['POST'])
def print_receipt():
    # Retrieve the receipt data from the request
    receipt_data = request.json.get('receipt_data')

    try:
        # Connect to the printer
        device = connect_to_printer()
        
        device.set(align='center')
        # Set the print width to 80mm (ESC/POS command)
        device._raw(b'\x1B\x57\x40\x32')

        # Print receipt content
        device.set(align='center', text_type='B')
        device.text("P&C POS App\n")
        device.set(align='center', text_type='NORMAL')
        device.text("\n-------------------------------\n")
        
        for item in receipt_data['items']:
            name = item['name']
            price = f"${item['price']}"

            # Calculate the space count
            space_count = 30 - len(name) - len(price)  # Adjust the space count as needed

            line = f"{name}{' ' * space_count}{price}"
            device.text(line + '\n')
        
        device.text("-------------------------------\n\n")
        device.line_spacing()
        device.line_spacing()
        device.barcode("123456", "CODE39")

        # Cut the paper
        device.cut()

        # Close the printer connection
        device.close()
        
        #Kick the cash drawer
        kick_cash_drawer()

        return 'Receipt printed and cash drawer kicked successfully!'
    
    except printer_exceptions.Error as e:
        return f'Printing failed: {str(e)}'


def connect_to_printer():
    # Connect to the printer based on the chosen interface
    # Replace the following lines with your desired connection logic
    vendor_id = 0x0e20
    product_id = 0x04b8
    in_ep = 0x82  # Input endpoint address
    out_ep = 0x01  # Output endpoint address
    # USB interface
    device = printer.Usb(product_id, vendor_id, in_ep=in_ep, out_ep=out_ep)

    # Serial (RS232) interface
    # printer = Serial(devfile='/dev/ttyUSB0', baudrate=9600)

    # Network (Ethernet) interface
    # printer = Network(host='192.168.1.100', port=9100)

    # Bluetooth interface
    # printer = Bluetooth(mac='00:11:22:33:44:55')
    
    return device

@bluetooth_routes.route('printer/kick-cashdrawer', methods=['GET'])
def kick_cash_drawer():
    device = connect_to_printer()
    # Send the command to kick the cash drawer (specific to your printer model)
    # Replace the following line with the appropriate command for your printer
    try:
        device.cashdraw(2)
        device.close()
        return 'Cash drawer kicked successfully!'
    except printer_exceptions.Error as e:
        # Log or handle the error appropriately
        return f'Failed to kick the cash drawer: {str(e)}'