

# from flask import Blueprint, jsonify, request
# from escpos import BluetoothConnection
# from escpos.ifusb import USBConnection
# from escpos.impl.epson import GenericESCPOS, CashDrawerException


# app_routes = Blueprint('bluetooth', __name__)

# def connect_to_printer_usb():
#     # USB interface
#     connection = USBConnection.create('04b8:0e20,interface=0,ep_out=0x01,ep_in=0x82')
#     device = GenericESCPOS(connection)
#     device.init()
    
#     return device

# def connect_to_printer_bluetooth(address):
#     # USB interface
#     connection = BluetoothConnection.create(address)
#     device = GenericESCPOS(connection)
#     device.init()
    
#     return device

# connection_functions = {
#     'BLUETOOTH': connect_to_printer_bluetooth(),
#     'USB': connect_to_printer_usb(),
# }

# @app_routes.route('/printer/kick-cashdrawer', methods=['GET'])
# def kick_cash_drawer():
#     conn_type = request.json.get('connection_type')
#     device = connection_functions[conn_type]
    
#     try:
#         device.kick_drawer(port=2)
#         return jsonify({
#             'message': 'Cash drawer kicked successfully!',
#             'status_code': 200
#         }), 200
#     except CashDrawerException as e:
#         # Log or handle the error appropriately
#         return jsonify({
#             'message': f'Failed to kick the cash drawer: {str(e)}',
#             'status_code': 500,
#             }), 500