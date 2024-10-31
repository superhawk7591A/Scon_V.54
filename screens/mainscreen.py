import os.path
# mainscreen.py
import time
import tkinter as tk
import globalvariables
from tkinter import messagebox
from globalvariables import deviceport
from serialmanager import send_command_with_timeout
from help_manager import HelpManager, MAIN_HELP_CONTENT, MAIN_HELP_CONTENT

class MainScreen(tk.Frame):
    def __init__(self, master, serial_manager, app):
        super().__init__(master)
        self.serial_manager = serial_manager
        self.app = app  # Reference to the main application class
        #added124
        self.configure(width=500, height=500)
        self.checking_data = False
        self.run_line=0
        self.create_widgets()
#        command = self.serial_manager.find_device_port()
        # StringVar to hold the current value

        if globalvariables.deviceconnected==1:
            self.label1.config(text= f"Controller: {globalvariables.boarddatastring} on port: {globalvariables.deviceport}")
        else:
            self.label1.config(text="No Controller Connected")


    def run_resume(self):
        command = "$OV0R05000000*************************************************OV~"
        success=self.serial_manager.send_only_long_command(command)

    def stop_con(self):
        command = "$OV0R00*******************************************************OV~"

        print(os.path.dirname(os.path.abspath(__file__)))
        success = self.serial_manager.send_only_long_command(command)

    def pause_con(self):
        command = "$OV0R07*******************************************************OV~"
        success = self.serial_manager.send_only_long_command(command)

    def run_at_line_con(self):
        command = "$OV0R05000000*************************************************OV~"
        try:
            new_value = int(self.ent_line_no.get())
            if 0 <= new_value <= 30000:
                self.run_line = new_value
            else:
                messagebox.showerror("Error", "Invalid input.")
        except:
            messagebox.showerror("Error", "Invalid input.")
        command=command[:7]+f"{self.run_line:06X}"+command[13:]
        success=self.serial_manager.send_only_long_command(command)

    def refresh_status(self):
        if self.serial_manager.serial.in_waiting >= 24:
            data = self.serial_manager.serial.read(24)
            self.process_and_update_ui(data)
        else:
            self.notify_frame_label_v.config(text="Controller not auto sending, press Run, Stop, or Pause")

    def monitor_status_con(self):
        self.checking_data=True
        self.check_for_data()

    def monitor_statoff_con(self):
        self.checking_data=False

#    def check_for_data(self):
#        if not self.checking_data:
#                return
#        if self.serial_manager.serial.in_waiting >= 24:
#            data = self.serial_manager.serial.read(24)
#            self.process_and_update_ui(data)
#        self.after(100, self.check_for_data)  # Schedule next check

    def check_for_data(self):
        if not self.checking_data or not self.serial_manager.is_port_accessible():
            self.checking_data = False
            return
        try:
            if self.serial_manager.serial.in_waiting >= 24:
                data = self.serial_manager.serial.read(24)
                self.process_and_update_ui(data)
            # Schedule the next check only if everything was successful
            self.after(100, self.check_for_data)
        except Exception as e:  # Catch any exception that might occur
            self.checking_data = False
            print(f"Serial communication error: {e}")
            # Handle the error (e.g., show a message to the user, try to reconnect, etc.)


    def process_and_update_ui(self, data):
        self.notify_frame_label_v.config(text="None")
        self.line_num_disp_label_v.config(text=self.parse_24_string_data(data,18,6))
        self.pos_label_v.config(text=self.parse_24_string_data(data,2,4))
        self.stack_label_v.config(text=self.parse_24_string_data(data, 8, 2))
        self.loop_label_v.config(text=self.parse_24_string_data(data, 10, 4))
        self.mode_con_label_v.config(text=self.parse_for_run_outs_data(data,14,2))



    # Process the 24-byte data and update UI elements
    # For example:
    # servo1_pos = int.from_bytes(data[0:2], byteorder='big')
    # self.servo1_label.config(text=str(servo1_pos))
    # ... update other UI elements as needed
    def parse_24_string(self,input_string):
        if len(input_string)==24:
            if input_string.startswith(b'AB'):
               return True, input_string.decode ('ascii')  #f"{int(input_string[2:6],16):05d}"
            else:
                   print("Resync")
                   timeout = time.time() + 1  # 2 second timeout
                   buffer = input_string  # Start with the current input_string
                   while time.time() < timeout:
                       if self.serial_manager.serial.in_waiting:
                           new_byte = self.serial_manager.serial.read(1)
                           buffer += new_byte
                           if len(buffer) >= 24 and buffer[-24:].startswith(b'AB'):
                               print("Resynchronized successfully")
                               synced_data = buffer[-24:]
                               return True, synced_data.decode('ascii')
                   print("Failed to resynchronize within timeout")
                   return False, "YYYYYY" if len(input_string) == 24 else "XXXXXX"

    def parse_24_string_data(self,data,pos,num):
        if len(data)>=24 and data.startswith(b'AB'):
            return f"{int(data[pos:pos+num],16):05d}"          #str(int(data[pos:pos+num],16))

    def parse_for_run_outs_data(self,data,pos,num):
        if len(data)>=24 and data.startswith(b'AB'):
            value = int(data[pos:pos + num], 16)
            bit5 = bool(value & (1 << 4))
            bit6 = bool(value & (1 << 5))
            if bit5 and not bit6:
                return "Running"
            elif bit5 and bit6:
                return "Paused"
            else:
                return "Stopped"




    def show_help(self):
        HelpManager.show_help(self, "Main Screen Help", MAIN_HELP_CONTENT)

# Widgets
    def create_widgets(self):
        # Help Button
        self.help_button = tk.Button(self, text="Help", command=self.show_help)
        self.help_button.place(x=435, y=0)

        # Connection Status label
        self.label1 = tk.Label(self, text="Controller not Connected             ")
        self.label1.place(x=10, y=1)

        self.runcon_frame = tk.LabelFrame(self, text="Run Controls", relief=tk.GROOVE, borderwidth=3, font=("Arial", 11))
        self.runcon_frame.place(x=10, y=30, width=195, height=180)  # Keep place for inner widgets

    # Run/Resume button
        self.run_rusume_button = tk.Button(self.runcon_frame, text="Run\nResume", command=self.run_resume, font=("Arial", 10), bg='yellow', activebackground='#FFFF66')
        self.run_rusume_button.place(x=10, y=10)

        self.stop_button = tk.Button(self.runcon_frame, text="Stop", height=2, command=self.stop_con, font=("Arial", 10))
        self.stop_button.place(x=80, y=10)

        self.pause_button = tk.Button(self.runcon_frame, text="Pause", height=2, command=self.pause_con, font=("Arial", 10))
        self.pause_button.place(x=131, y=10)

        self.run_at_line_frame = tk.LabelFrame(self.runcon_frame, text="Run at line No.", font=("Arial", 11))
        self.run_at_line_frame.place(x=7, y=70, width=170, height=80)  # Keep place for inner widgets

        self.ent_line_no = tk.Entry(self.run_at_line_frame, width= 10,font=("Arial", 10))
        self.ent_line_no.place(x=75, y=17)

        self.run_at_line_button = tk.Button(self.run_at_line_frame, width=6, text="Run", command=self.run_at_line_con, font=("Arial", 10), bg='yellow', activebackground='#FFFF66')
        self.run_at_line_button.place(x=4, y=14)

#---------------------------
        self.status_frame = tk.LabelFrame(self, text="Status", relief=tk.GROOVE, borderwidth=3, font=("Arial", 11))
        self.status_frame.place(x=210, y=30, width=280, height=180)  # Keep place for inner widgets

        self.mode_con_frame = tk.LabelFrame(self.status_frame, text="Mode", relief=tk.GROOVE, font=("Arial", 10))
        self.mode_con_frame.place(x=5, y=5, width=60, height=50)  # Keep place for inner widgets
        self.mode_con_label_v=tk.Label(self.mode_con_frame, text="-------")
        self.mode_con_label_v.place(x=1, y=1)

        self.line_num_disp_frame = tk.LabelFrame(self.status_frame, text="Line Number", relief=tk.GROOVE, font=("Arial", 10))
        self.line_num_disp_frame.place(x=70, y=5, width=85, height=50)  # Keep place for inner widgets
        self.line_num_disp_label_v=tk.Label(self.line_num_disp_frame, text="------")
        self.line_num_disp_label_v.place(x=20, y=1)

        self.pos_label=tk.Label(self.status_frame, text="Position: ")
        self.pos_label.place(x=165, y=0)
        self.pos_label_v=tk.Label(self.status_frame, text="00000")
        self.pos_label_v.place(x=215, y=0)


        self.stack_label=tk.Label(self.status_frame, text="Stack: ")
        self.stack_label.place(x=165, y=20)
        self.stack_label_v=tk.Label(self.status_frame, text="00000")
        self.stack_label_v.place(x=215, y=20)

        self.loop_label=tk.Label(self.status_frame, text="Loop: ")
        self.loop_label.place(x=165, y=40)
        self.loop_label_v=tk.Label(self.status_frame, text="00000")
        self.loop_label_v.place(x=215, y=40)

        self.refresh_status_button = tk.Button(self.status_frame, width=13, text="Refresh status", command=self.refresh_status)
        self.refresh_status_button.place(x=163, y=62)

        self.monitor_status_button = tk.Button(self.status_frame, width=13, text="Monitor status", command=self.monitor_status_con)
        self.monitor_status_button.place(x=163, y=93)

        self.monitor_statoff_button = tk.Button(self.status_frame, width=13, text="Monitor off", command=self.monitor_statoff_con)
        self.monitor_statoff_button.place(x=163, y=123)

        self.notify_frame = tk.LabelFrame(self.status_frame, text="Notifications", relief=tk.GROOVE, font=("Arial", 10))
        self.notify_frame.place(x=5, y=70, width=150, height=80)  # Keep place for inner widgets

        self.notify_frame_label_v = tk.Label(self.notify_frame, text="None", justify='left', wraplength=145)
        self.notify_frame_label_v.place(x=1, y=1)




