import bluetooth
import usb.core
import usb.util
import subprocess

from flask import Blueprint, jsonify, request
from utils import is_valid_bluetooth_address, get_device_type, is_device_connected, get_image, border_line, space, detect_usb_device_type
from escpos import printer, exceptions as printer_exceptions

app_routes = Blueprint('bluetooth', __name__)

@app_routes.route('/bluetooth/devices', methods=['GET'])
def get_bluetooth_devices():
    try:
        # Discover nearby Bluetooth devices
        nearby_devices = bluetooth.discover_devices(lookup_names=True, flush_cache=True, lookup_class=True)
        devices = []

        for device_address, device_name, device_class in nearby_devices:
            try:
                # Create device data
                device_data = {
                    'address': device_address,
                    'name': device_name,
                    'class': device_class,
                    'type': get_device_type(device_class),
                    'is_connected': is_device_connected(device_address)
                }

                devices.append(device_data)
            except Exception as e:
                print(f"Error processing device: {e}")
                # Handle the error as needed

        return jsonify({
            'data': devices,
            'status_code': 200,
            'message': 'ok!'
        }), 200
    except Exception as e:
        print(f"Error discovering Bluetooth devices: {e}")
        # Handle the error as needed
        return jsonify({
            'error': 'Failed to retrieve Bluetooth devices',
            'status_code': 500,
            'message': 'error'
        }), 500
    
@app_routes.route('/bluetooth/pair', methods=['POST'])
def pair_bluetooth_device():
    # Retrieve the Bluetooth device address from the request
    device_address = request.json.get('device_address')

    # Check if the provided device address is valid
    if not is_valid_bluetooth_address(device_address):
        return jsonify({'error': 'Invalid Bluetooth device address'})

    try:
        # Run the bluetoothctl command to initiate pairing
        command = f"bluetoothctl -- pair {device_address}"
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()

        if process.returncode == 0:
            message = "Successfully paired with the Bluetooth device."
        else:
            error_message = error.decode().strip() if error else "Pairing failed."
            return jsonify({'error': error_message})

        return jsonify({'message': message})

    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        return jsonify({'error': error_message})


@app_routes.route('/bluetooth/connect', methods=['POST'])
def connect_to_bluetooth():
    # Retrieve the Bluetooth device address from the request
    device_address = request.json.get('device_address')

    # Check if the provided device address is valid
    if not is_valid_bluetooth_address(device_address):
        return jsonify({'error': 'Invalid Bluetooth device address'})

    try:
        # Run the bluetoothctl command to initiate connection
        command = f"bluetoothctl -- connect {device_address}"
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()

        if process.returncode == 0:
            message = "Successfully connected to the Bluetooth device."
        else:
            error_message = error.decode().strip() if error else "Connection failed."
            return jsonify({'error': error_message})

        return jsonify({'message': message})

    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        return jsonify({'error': error_message})
    
@app_routes.route('/bluetooth/disconnect-and-remove', methods=['POST'])
def disconnect_and_remove_bluetooth():
    # Retrieve the Bluetooth device address from the request
    device_address = request.json.get('device_address')

    # Check if the provided device address is valid
    if not is_valid_bluetooth_address(device_address):
        return jsonify({'error': 'Invalid Bluetooth device address'})

    try:
        # Run the bluetoothctl command to disconnect and remove the device
        command_disconnect = f"bluetoothctl -- disconnect {device_address}"
        process_disconnect = subprocess.Popen(command_disconnect, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output_disconnect, error_disconnect = process_disconnect.communicate()

        command_remove = f"bluetoothctl -- remove {device_address}"
        process_remove = subprocess.Popen(command_remove, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output_remove, error_remove = process_remove.communicate()

        if process_disconnect.returncode == 0 and process_remove.returncode == 0:
            message = "Successfully disconnected and removed the Bluetooth device."
        else:
            error_message = f"Disconnect error: {error_disconnect.decode().strip() if error_disconnect else 'Unknown'}\n" \
                           f"Remove error: {error_remove.decode().strip() if error_remove else 'Unknown'}"
            return jsonify({'error': error_message})

        return jsonify({'message': message})

    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        return jsonify({'error': error_message})

@app_routes.route('/usb/devices', methods=['GET'])
def get_usb_devices():
    usb_devices = []

    try:
        for device in usb.core.find(find_all=True):
            # Get USB device information
            manufacturer = usb.util.get_string(device, device.iManufacturer) if device.iManufacturer else None
            product = usb.util.get_string(device, device.iProduct) if device.iProduct else None
            serial_number = usb.util.get_string(device, device.iSerialNumber) if device.iSerialNumber else None
            vendor_id = device.idVendor
            product_id = device.idProduct
            type = detect_usb_device_type(device)

            device_data = {
                'name': product,
                'vendor': manufacturer,
                'serial_number': serial_number,
                'vendor_id': vendor_id,
                'product_id': product_id,
                'is_connected': True,
                'type': type,
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
@app_routes.route('printer/print-receipt', methods=['POST'])
def print_receipt():
    # Retrieve the receipt data from the request
    receipt_data = request.json.get('receipt_data')

    try:
        # Connect to the printer
        device = connect_to_printer()
        
        device.set(align='center')
        # Set the print width to 80mm (ESC/POS command)
        device._raw(b'\x1B\x57\x40\x50')

        # Print receipt content
        device.set(align='center')
        device.image(get_image('static/images/pnc-logo.bmp', 324))
        device.text('\n***** das POS-Unternehmen *****\n\n')
        
        device.text('Beleg-Nr. 10052/013/0001   31.08.2022 11:33:37\n')
        device.set(align='left')
        device.text('Frau Tamara (Cashier) served you at Station 1\n')
        device.set(align='center')
        border_line(device)
        
        # Define the column titles
        column_titles = ["Art-Nr", "Anz", "E-Preis", "Betrag"]

        # Set the items sections
        for index, item in enumerate(receipt_data['items'], start=1):
            number = str(index)
            name = item['name']
            product_id = item['product_id']
            quantity = item['quantity']
            price = f"{item['price']:.2f}"
            total = f"{item['price'] * item['quantity']:.2f}"

            # Calculate the space counts
            number_space_count = len(number)
            name_space_count = 44 - len(name)  # Adjust the space count as needed
            product_id_space_count = 18 - len(product_id)
            
            title_line = f"{space(3)}{column_titles[0]}{space(product_id_space_count + 4)}" \
                   f"{column_titles[1]}{space(3)}" \
                   f"{column_titles[2]}{space(3)}" \
                   f"{column_titles[3]}{space(3)}"

            if index == 1:
                device.text(title_line + '\n')
                border_line(device)

            name_line = f"{name}{space(name_space_count)}"
            qty_line = f"{quantity}{space(4)}"
            price_line = f"{price}{space(4)}"
            total_line = f"{total}"
            line = f"{number}{space(number_space_count)}" \
                   f"{name_line}"

            device.text(line + '\n')
            device.set(align='left')
            device.text(f"{space(3)}{product_id}{space(product_id_space_count + 3)}{qty_line}{price_line}{total_line}\n")  # Print the product ID, quantity, price, and total below the name
            device.set(align='center')
            
        # Accumulate the total amount 
        total_amount = sum(item['price'] * item['quantity'] for item in receipt_data['items'])
        total_amount = round(total_amount, 2)
        
        # Set total amount section
        border_line(device)
        device.set(text_type='B', font='A', width=2, height=2)  # Set larger size and bold format
        spaces_before_total = max(0, 24 - len(f"Gesamtbetrag {total_amount}"))  # Calculate the remaining spaces
        device.text(f"Gesamtbetrag {space(spaces_before_total)}{total_amount}\n")
        device.set(text_type='NORMAL', font='A', width=1, height=1) 
        border_line(device)
        
        # Set the tax, net section
        task_rate = 19  # Task rate in percentage
        net_price = total_amount / (1 + (task_rate / 100))  # Calculate the net price
        task_amount = total_amount - net_price  # Calculate the task amount
        task_line = f"{space(10)}{task_rate:.1f}%: {task_amount:.2f}\n"
        net_price_line = f'Netto-Warenwert: {net_price:.2f}\n'
        device.text(task_line)
        device.text(net_price_line)
        border_line(device)
        
        # Footer of the receipt
        device.text('\n')
        device.barcode("123456", "CODE39", pos='OFF', width=2, height=100)  # Generate the barcode without a number
        device.text('\n\n\n***** Thank you for your purchase *****\n')
        device.text('www.aks-anker.de/')

        # Cut the paper
        device.cut()

        # Close the printer connection
        device.close()
        
        # Kick the cash drawer
        kick_cash_drawer()

        return 'Receipt printed and cash drawer kicked successfully!'

    except printer_exceptions.Error as e:
        return f'Printing failed: {str(e)}'


def connect_to_printer():
    # Connect to the printer based on the selected interface
    # Replace the following lines with the desired connection logic
    vendor_id = 0x0e20
    product_id = 0x04b8
    in_ep = 0x82  # Input endpoint address
    out_ep = 0x01  # Output endpoint address
    # USB interface
    device = printer.Usb(product_id, vendor_id, in_ep=in_ep, out_ep=out_ep)

    # Serial interface (RS232)
    # printer = Serial(devfile='/dev/ttyUSB0', baudrate=9600)

    # Network interface (Ethernet)
    # printer = Network(host='192.168.1.100', port=9100)

    # Bluetooth interface
    # printer = Bluetooth(mac='00:11:22:33:44:55')
    
    return device

@app_routes.route('/printer/kick-cashdrawer', methods=['GET'])
def kick_cash_drawer():
    device = connect_to_printer()
    # Send command to open the cash drawer (specific to your printer model)
    # Replace the following line with the appropriate command for your printer
    try:
        device.cashdraw(2)
        device.close()
        return 'Cash drawer kicked successfully!'
    except printer_exceptions.Error as e:
        # Log or handle the error appropriately
        return f'Failed to kick the cash drawer: {str(e)}'
