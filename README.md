# bluetooth_rpi
Sure! Here's the updated version with an opening sentence and mentioning that the project uses `app.py`:

To run the application and access the API endpoints on your Raspberry Pi, follow these steps:

1. **Install required dependencies:**
   - Open a terminal or SSH into your Raspberry Pi.
   - Update the package lists by running the following command:
     ```
     sudo apt update
     ```
   - Install the required packages by running the following command:
     ```
     sudo apt install python3-pip bluetooth libbluetooth-dev libusb-1.0-0-dev
     ```
   - Install the Python package dependencies by running the following command:
     ```
     sudo pip3 install -r requirements.txt
     ```

2. **Run the app:**
   - Navigate to the project directory where `app.py` is located.
   - Execute the following command to start the Flask application:
     ```
     python3 app.py
     ```
   
   The Flask application will start running, and you should see output similar to the following:
   ```
   * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
   ```

3. **Access the API endpoints:**
   - To get a list of Bluetooth devices, open a web browser and navigate to `http://127.0.0.1:5000/bluetooth/devices`.
   - To connect to a Bluetooth device, send a POST request to `http://127.0.0.1:5000/bluetooth/connect` with the appropriate payload containing the device address.
        - Request body:
     ```json
     {
       "address": "00:11:22:33:44:55"
     }
     ```
     - Replace `"00:11:22:33:44:55"` with the Bluetooth device address you want to connect to.
     - Remember to send the POST requests with the appropriate content type (e.g., `application/json`) in the headers.
   - To get a list of USB devices, open a web browser and navigate to `http://127.0.0.1:5000/usb/devices`.
   - To print a receipt and kick the cash drawer, send a POST request to `http://127.0.0.1:5000/printer/print-receipt` with the appropriate payload containing the receipt data.
        - Request body:

        ```json
        {
        "receipt_data": {
            "items": [
            {
                "name": "Nike Air Balance",
                "price": 100.99,
                "quantity": 3,
                "product_id": "12332423"
            },
            {
                "name": "New Jordan",
                "price": 90.99,
                "quantity": 3,
                "product_id": "12332424"
            },
            {
                "name": "Adinda Yeezy",
                "price": 170.49,
                "quantity": 3,
                "product_id": "12332425"
            },
            {
                "name": "Dior a emon",
                "price": 200.49,
                "quantity": 5,
                "product_id": "12332426"
            }
            ]
        }
        }
        ```
     - Adjust the `"items"` list according to your receipt data. Each item should have a `"name"`, `"product_id"`, `"quantity"`, and `"price"`.
     - Remember to send the POST requests with the appropriate content type (e.g., `application/json`) in the headers.
   - To kick the cash drawer without printing a receipt, send a GET request to `http://127.0.0.1:5000/printer/kick-cashdrawer`.

That's it! By following these steps, you should now be able to run the `app.py` file on your Raspberry Pi and access the different API endpoints. Make sure to adjust the code if you have specific requirements, such as changing the printer interface or modifying the endpoint paths.

