"""
import serial
import time

class SerialPortManager:
    def __init__(self, port='COM5', baudrate=57600, timeout=1):
        try:
            self.serial = serial.Serial(port, baudrate, timeout=timeout)
            print(f"Connected to {port} at {baudrate} baud.")
        except serial.SerialException as e:
            print(f"Failed to connect: {e}")
            self.serial = None






    def send_command_with_timeout(self, command, expected_response, timeout=5):
        if self.serial and self.serial.is_open:
            self.serial.write(command.encode())
            start_time = time.time()
            while time.time() - start_time < timeout:
                if self.serial.in_waiting > 0:
                    response = self.serial.read(self.serial.in_waiting).decode()
                    if expected_response in response:
                        print("Expected response received:", response)
                        return True
                time.sleep(0.1)
            print("Timeout waiting for response")
            return False
        else:
            print("Serial port not open.")
            return False

    def send_data(self, data):
        if self.serial and self.serial.is_open:
            self.serial.write(data.encode('utf-8'))
            print(f"Sent: {data}")
        else:
            print("Serial port not open.")

    def receive_data(self):
        if self.serial and self.serial.is_open:
            data = self.serial.readline().decode('utf-8').strip()
            print(f"Received: {data}")
            return data
        else:
            print("Serial port not open.")
            return None

    def close_port(self):
        if self.serial:
            self.serial.close()
            print("Serial port closed.")

    def cdc_test_this(self):
        print("Testing This")

    def send_command_with_timeout(self, command, expected_response, timeout=2):
        print("Entering send_command_with_timeout")
        if self.serial and self.serial.is_open:
            print("Serial port is open, sending command...")
            self.serial.write(command.encode('ascii'))
            print(command)
            start_time = time.time()
            while time.time() - start_time < timeout:
                if self.serial.in_waiting > 0:
                    response = self.serial.read(self.serial.in_waiting).decode()
                    if expected_response in response:
  #                      command="$OVXR02*******************************************************OV~"
  #                      self.serial.write(command.encode('ascii'))
  #                      print("Expected response received:", response)
                        return True
                time.sleep(0.001)
            print("Timeout waiting for response")
            return False
        else:
            print("Serial port not open.")
            return False






"""