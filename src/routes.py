
import bluetooth
import usb.core
import usb.util

from flask import Blueprint, jsonify, request
from utils import is_valid_bluetooth_address, get_device_type, is_device_connected

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
        return jsonify({'message': error_message, 'from': 'BluetoothError', 'address': address}), 500
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
