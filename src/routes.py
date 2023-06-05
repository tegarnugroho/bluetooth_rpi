from flask import Blueprint, jsonify, request
import bluetooth
import usb.core
import pywinusb.hid as hid
from utils import is_valid_bluetooth_address, get_device_type, is_device_connected

bluetooth_routes = Blueprint('bluetooth', __name__)


@bluetooth_routes.route('/bluetooth/devices', methods=['GET'])
def get_bluetooth_devices():
    nearby_devices = bluetooth.discover_devices(lookup_names=True, lookup_class=True)
    devices = []

    for device_address, device_name, device_class in nearby_devices:
        device_data = {
            'bluetooth_address': device_address,
            'bluetooth_name': device_name,
            'bluetooth_class': device_class,
            'bluetooth_type': get_device_type(device_class),
            'is_connected': is_device_connected(device_address)
        }
        devices.append(device_data)

    return jsonify({
        'data': devices, 
        'length': len(devices),
        'status_code': 200,
        'message': 'ok!'
        }), 200

@bluetooth_routes.route('/bluetooth/connect', methods=['POST'])
def connect_bluetooth_device():
    address = request.json.get('address')  # Get the Bluetooth device address from the request

    if not is_valid_bluetooth_address(address):
        return jsonify({'message': 'Invalid Bluetooth address'}), 400

    try:
        socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        socket.connect((address, 1))  # Connect to the Bluetooth device

        # Perform any necessary operations with the connected Bluetooth device

        socket.close()  # Close the Bluetooth connection

        return jsonify({'message': 'Bluetooth device connected successfully'})
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@bluetooth_routes.route('/bluetooth/ble/connect', methods=['POST'])
def connect_ble_device():
    address = request.json.get('address')  # Get the Bluetooth device address from the request

    if not is_valid_bluetooth_address(address):
        return jsonify({'message': 'Invalid Bluetooth address'}), 400

    try:
        socket = bluetooth.BluetoothSocket(bluetooth.LE)
        socket.connect((address, bluetooth.ADDR_TYPE_PUBLIC))  # Connect to the BLE device

        # Perform any necessary operations with the connected BLE device

        socket.close()  # Close the Bluetooth connection

        return jsonify({'message': 'BLE device connected successfully'})
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    
@bluetooth_routes.route('/usb/rapsberry', methods=['GET'])
def get_usb_devices():
    usb_devices = []
    
    for device in usb.core.find(find_all=True):
        manufacturer = usb.util.get_string(device, device.iManufacturer)
        product = usb.util.get_string(device, device.iProduct)
        serial_number = usb.util.get_string(device, device.iSerialNumber)
        
        device_data = {
            'name': product,
            'vendor': manufacturer,
            'serial_number': serial_number,
            'connected': True
        }
        usb_devices.append(device_data)
    
    return jsonify({'devices': usb_devices, 'count': len(usb_devices)}) 

@bluetooth_routes.route('/usb/windows', methods=['GET'])
def get_windows_usb():
    devices = []
    
    # Find all USB devices
    all_devices = hid.HidDeviceFilter().get_devices()
    
    # Extract relevant information from each device
    for device in all_devices:
        device_info = {
            'vendor_id': device.vendor_id,
            'product_id': device.product_id,
            'vendor_name': device.vendor_name,
            'product_name': device.product_name
        }
        devices.append(device_info)
    
    return jsonify(devices)