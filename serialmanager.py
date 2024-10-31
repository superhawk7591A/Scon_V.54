import serial
import serial.tools.list_ports
import threading
import queue

import time
import globalvariables
from globalvariables import deviceconnected


class SerialPortManager:
    def __init__(self, baudrate=57600, timeout=1):
        self.serial = None
        self.device_port = None
        self.baudrate = baudrate
        self.timeout = timeout
#9/23 continuous monitoring
        self.monitoring = False
        self.data_queue = queue.Queue()
        # Scan for the correct port

    # added to prevent crashing if board disconnected  modified 10/27/2024
    def is_port_accessible(self):
        if not hasattr(self, 'serial') or self.serial is None:
            return False
        try:
            return self.serial.is_open and self.serial.in_waiting >= 0
        except serial.SerialException:
            return False

    def find_device_port(self):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            try:
#                print(f"Trying {port.device}...")
                test_serial = serial.Serial(port.device, self.baudrate, timeout=self.timeout)
                # Debugging: Check if the port opened successfully
#                if test_serial.is_open:
#                    print(f"Successfully opened {port.device}")
 #               else:
#                    print(f"Failed to open {port.device}")
                # Store the serial object temporarily
                self.serial = test_serial
                # Now attempt to send the command and check the response
                if self.wait_for_ready():           #this sends attn and waits for a response or times out
                    self.device_port = port.device
                    command= "$OVXR02*******************************************************OV~"
                    success, response=self.send_and_receive_long(command)
#                    print(len(response))
#                    print (response)
                    if success:
                        globalvariables.boarddatastring=(self.scan_untilsaterisk(6,response))
                        globalvariables.deviceport=port.device
                        globalvariables.deviceconnected = 1  # set to 1 when the board is found
                        return True
#                        print(response)
                    else:
                        globalvariables.boarddatastring="No Cotroller Connected"
#                        print (response, "fail1")
                else:
 #                       print(f"No valid response from {port.device}")
                        test_serial.close()
                        self.serial = None
            except serial.SerialException as e:
                globalvariables.deviceport = "None"
                globalvariables.deviceconnected = 0  # set to 1 when the board is found


    def reconnect_device(self):
        if self.serial and self.serial.is_open:
            self.serial.close()
        port = self.find_device_port()
        if port:
            try:
                self.serial = serial.Serial(port, 57600, timeout=1)
                globalvariables.deviceconnected = 1
                globalvariables.deviceport = port
                return True, f"Connected to {port}"
            except serial.SerialException as e:
                globalvariables.deviceconnected = 0
                return False, str(e)
        else:
            globalvariables.deviceconnected = 0
            return False, "Device not found"

    def close_port(self):
        if self.serial and self.serial.is_open:
            self.serial.close()


    def send_command_with_timeout(self, command, expected_response, timeout=0.25):
        if not self.serial or not self.serial.is_open:
            return False, None
        self.serial.write(command.encode('ascii'))
        self.serial.flush()  # Ensure the command is sent immediately
        start_time = time.time()
        response = ""
        while time.time() - start_time < timeout:
            if self.serial.in_waiting > 0:
                new_data = self.serial.read(self.serial.in_waiting).decode('ascii', errors='ignore')
                response += new_data
                if expected_response in response:
                    return True, response
            time.sleep(0.01)  # Slightly longer sleep to reduce CPU usage
        return False, response


    # Extra New New 9/11
    def send_long_command(self, command):
        try:
            if self.wait_for_ready():
                return self.send_and_receive_long(command)
            else:
                return False, "Device not ready"
        except Exception as e:
#           print(f"Error in send_long_command: {e}")
            return False, "Error occurred"

    def send_and_receive_long(self, command, timeout=0.5):
        if len(command) != 65:
            return False, "Invalid command length"
        try:
            self.serial.write(command.encode('ascii'))
            start_time = time.time()
            response = b""
            while time.time() - start_time < timeout:
                if self.serial.in_waiting > 0:
                    response += self.serial.read(self.serial.in_waiting)
                    if len(response) >= 64:
                        return True, response.decode('ascii', errors='ignore')
                time.sleep(0.001)
            return False, "Timeout: Incomplete response"
        except Exception as e:
#            print(f"Error in send_and_receive_short: {e}")
            return False, str(e)

    # Extra New New 9/23
    def send_only_long_command(self, command):
        try:
            if self.wait_for_ready():
                return self.send_no_receive_long(command)
            else:
                return False, "Device not ready"
        except Exception as e:
#            print(f"Error in send_long_command: {e}")
            return False, "Error occurred"

    def send_no_receive_long(self, command, timeout=0.5):
        if len(command) != 65:
            return False, "Invalid command length"
        try:
            self.serial.write(command.encode('ascii'))
            time.sleep(0.001)
            return True
        except Exception as e:
            globalvariables.deviceconnected = 0

#9/23 Continuous 24 byte

#New New
    def send_short_command(self, command):
        try:
            if self.wait_for_ready():
                return self.send_and_receive_short(command)
            else:
                return False, "Device not ready"
        except Exception as e:
#            print(f"Error in send_short_command: {e}")
            return False, "Error occurred"

    def wait_for_ready(self, timeout=0.5):
        try:
            self.serial.write("&".encode('ascii'))
            start_time = time.time()
            while time.time() - start_time < timeout:
                if self.serial.in_waiting > 0:
                    response = self.serial.read(self.serial.in_waiting).decode('ascii', errors='ignore')
                    if ":" in response:
                        return True
                time.sleep(0.001)
            return False
        except Exception as e:
            globalvariables.deviceconnected=0  #(f"Error in wait_for_ready: {e}")
            return False



    def send_and_receive_short(self, command, timeout=0.5):
        if len(command) != 10:
            return False, "Invalid command length"
        try:
            self.serial.write(command.encode('ascii'))
            start_time = time.time()
            response = b""
            while time.time() - start_time < timeout:
                if self.serial.in_waiting > 0:
                    response += self.serial.read(self.serial.in_waiting)
                    if len(response) >= 9:
                        return True, response[:9].decode('ascii', errors='ignore')
                time.sleep(0.001)
            return False, "Timeout: Incomplete response"
        except Exception as e:
            print(f"Error in send_and_receive_short: {e}")
            return False, str(e)


    # Extra New New 10/24
    def send_long_receive_528(self, command):
        try:
            if self.wait_for_ready():
                return self.send_long_rec_528(command)
            else:
                return False, "Device not ready"
        except Exception as e:
            #           print(f"Error in send_long_command: {e}")
            return False, "Error occurred"

    def send_long_rec_528(self, command, timeout=1):
        if len(command) != 65:
            return False, "Invalid command length"
        try:
            self.serial.write(command.encode('ascii'))
            start_time = time.time()
            response = b""
            while time.time() - start_time < timeout:
                if self.serial.in_waiting > 0:
                    response += self.serial.read(self.serial.in_waiting)
                    if len(response) >= 528:
                        return True, response.decode('ascii', errors='ignore')
                time.sleep(0.001)
            return False, "Timeout: Incomplete response"
        except Exception as e:
            #            print(f"Error in send_and_receive_short: {e}")
            return False, str(e)

#Sends stream write attn character(#) and waits for the stream write ready response(!) - for writing a page to flash
#use in conjunction with stream write flash page. After receiving immideatly (<ms) send stream
    def send_528_wait_for_ready(self, timeout=0.5):
        try:
            self.serial.write("#".encode('ascii'))
            start_time = time.time()
            while time.time() - start_time < timeout:
                if self.serial.in_waiting > 0:
                    response = self.serial.read(self.serial.in_waiting).decode('ascii', errors='ignore')
                    if "!" in response:
                        return True
                time.sleep(0.001)
            return False
        except Exception as e:
            globalvariables.deviceconnected=0  #(f"Error in wait_for_ready: {e}")
            return False

    def write_528_byte_fpage(self, stream, timeout=5):
        if len(stream) != 533:
            return False, "Error: Input data must be 533 bytes (5 bytes address + 528 bytes data)"
        command = '$' + stream  # Add '$' prefix to the data
        print(command)
        try:
            if self.send_528_wait_for_ready():
                self.serial.write(command.encode('ascii'))
                start_time = time.time()
                response = b""
                while time.time() - start_time < timeout:
                    if self.serial.in_waiting > 0:
                        response += self.serial.read(self.serial.in_waiting)
                        if len(response) >= 64:
                            # Trim to exactly 64 bytes if we received more
                            response = response[:64]
                            decoded_response = response.decode('ascii', errors='ignore')
                            # Check for "OK" in the correct position
                            if decoded_response[3:5] == "OK":
                                return True, "Write successful: " + decoded_response
                            else:
                                return False, "Write failed: " + decoded_response
                    time.sleep(0.001)
                return False, "Timeout: Incomplete response"
            else:
                return False, "Device not ready"
        except Exception as e:
            globalvariables.deviceconnected = 0
            return False, f"Error in write_528_byte_fpage: {str(e)}"

    def receive_data(self):
        if self.serial and self.serial.is_open:
            data = self.serial.readline().decode('utf-8').strip()
            print(f"Received: {data}")
            return data
        else:
            print("Serial port not open.")
            return None

    def read_serial(self):
        if self.serial and self.serial.is_open:
            if self.serial.in_waiting:
                try:
                    data = self.serial.readline()
                    print(f"Received: {data}")

                    # Here you can process the data as needed
                except UnicodeDecodeError:
                    print("Received data couldn't be decoded")
        else:
            print("Serial port not open.")

    def close_port(self):
        if self.serial and self.serial.is_open:
            self.serial.close()

#This routine is used to look through the long command string and stop when the first asterisk is reached
    def scan_untilsaterisk(self,start,input_string):
        result=""
        # Start scanning from the 6th character (index 5)
        for char in input_string[start:]:
            if char == '*':
                break
            result += char
        return result
# Moved in
#sends a long command with standard instruction and additional data, back with return
    def long_command_encode(self, instruction, edata, more=None):
        command = "$OV0xxx*******************************************************OV~"
        instruction=instruction.zfill(3)[:3]
        edata=str(edata).zfill(6)[:6]
        command=command[:4]+instruction+edata+command[13:]
        if more is not None:
            more=str(more).zfill(40)[:40]
            command=command[:13]+more+command[53:]
        success, response=self.send_long_command(command)
        return success, response


def send_command_with_timeout(serial_port, command, expected_response, timeout=5):
    # Send the attention character or command
    serial_port.write(command.encode())

    start_time = time.time()

    while time.time() - start_time < timeout:
        if serial_port.in_waiting > 0:  # Check if there's any data available to read
            response = serial_port.read(serial_port.in_waiting).decode()
            if expected_response in response:
                print("Expected response received:", response)
                return True
        time.sleep(0.1)  # Small delay to avoid busy-waiting

    print("Timeout waiting for response")
    return False
