# Controller_parameters.py

import tkinter as tk
import time
from http.client import responses
from tkinter import messagebox
import globalvariables
from globalvariables import deviceport
#from serialtest import send_command_with_timeout

from help_manager import HelpManager, MAIN_HELP_CONTENT, CONTROLLER_PARAMETERS_HELP_CONTENT

class ControllerParameters(tk.Frame):
    def __init__(self, master, serial_manager, app):
        super().__init__(master)
        self.save_me=None
        self.serial_manager = serial_manager
        self.app = app  # Reference to the main application class
        self.configure(width=500, height=500)
        self.data_ready = False  # Add this line
        self.create_widgets()

        # StringVar to hold the current value
    def show_help(self):
        HelpManager.show_help(self, "Controller Parameters Help", CONTROLLER_PARAMETERS_HELP_CONTENT)

 #   def get_bit_status(self, hex_string, byte_index, bit_index):
 #       # Extract the hex pair at the given byte index
  #      hex_pair = hex_string[byte_index * 2: byte_index * 2 + 2]
   #     # Convert the hex pair to an integer
    #    byte_value = int(hex_pair, 16)
    #    # Check if the specified bit is set
     #   return bool(byte_value & (1 << bit_index))

    def get_bit_status(self, byte_index, bit_index):
        # Extract the hex pair at the given byte index
        hex_pair = self.save_me[byte_index * 2: byte_index * 2 + 2]
        # Convert the hex pair to an integer
        byte_value = int(hex_pair, 16)
        # Check if the specified bit is set
        return bool(byte_value & (1 << bit_index))

    def get_dec_valbit(self, byte_index):
        # Extract 0-65535 from the string return dec numeric
        hex_quad = self.save_me[byte_index * 2: byte_index * 2 + 4]
        dec16_val=int(hex_quad,16)
        return dec16_val

    def get_dec_valbit_2(self, byte_index):
        # Extract 0-256 from the string return dec numeric
        hex_pair = self.save_me[byte_index * 2: byte_index * 2 + 2]
        return int(hex_pair,16)

    def pac2_save_me_hex(self, index, decnum):
        # Convert the decimal number to a 2-byte hex string
        hex_string = f"{int(decnum):04X}"
        # Ensure self.save_me is initialized and long enough
        if not hasattr(self, 'save_me') or len(self.save_me) < index + 4:
            raise ValueError("self.save_me is not properly initialized or is too short")
        # Replace the 4 bytes at the specified index in self.save_me
        self.save_me = self.save_me[:index] + hex_string + self.save_me[index + 4:]
        return hex_string  # Return the hex string for convenience

    def pac1_save_me_hex(self, index, decnum):
        # Convert the decimal number to a 1-byte hex string
        hex_string = f"{int(decnum):02X}"
        # Ensure self.save_me is initialized and long enough
        if not hasattr(self, 'save_me') or len(self.save_me) < index + 2:
            raise ValueError("self.save_me is not properly initialized or is too short")
        # Replace the 2 bytes at the specified index in self.save_me
        self.save_me = self.save_me[:index] + hex_string + self.save_me[index + 2:]
        return hex_string  # Return the hex string for convenience


    def get_params(self):
        #Return Data is in Hex
        #First 2 bytes of save_me
            # Move separation (bit 0 & 1 ) 00=separate, 01=Common, 02&03=Other
            # Report on = bit 2
            # Use servo pulse limits bit 3
            # Rest unused
        # Run Modes are in 2 bytes starting at 2 (0 ref) of save_me. Only the lower 3 bits are used
            # Run on Power up bit 0 true, run on push button bit 1 true, run on hardware bit 3, Only 1 other combos invalid


        command = "$OV0R1R00000**************************************************OV~"
        #Note on original version controllers, the first
        success, response = self.serial_manager.send_long_command(command)
        self.save_me = response[11:43]
        if success:
            self.data_ready = True
            self.put_params_button.config(state=tk.NORMAL)  # Enable the Save

# Run Params & pulse limits----------------------------------
        if self.get_bit_status(byte_index=1, bit_index=0):
           self.ronpu.set(True)
        else:
           self.ronpu.set(False)

        if self.get_bit_status(byte_index=1, bit_index=1):
           self.pbcont.set(True)
        else:
           self.pbcont.set(False)

        if self.get_bit_status(byte_index=1, bit_index=2):
           self.hwcont.set(True)
        else:
           self.hwcont.set(False)

        if self.get_bit_status(byte_index=0, bit_index=2):
           self.reportcon.set(True)
        else:
           self.reportcon.set(False)

        if self.get_bit_status(byte_index=0, bit_index=3):
           self.use_limits_con.set(True)
        else:
            self.use_limits_con.set(False)

        if self.get_bit_status(byte_index=4, bit_index=0):
           self.use_lcp_con.set(True)
        else:
            self.use_lcp_con.set(False)


# Active Servos ----------------------------------
        if self.get_bit_status(byte_index=12, bit_index=0):
           self.use_s1_con.set(True)
        else:
            self.use_s1_con.set(False)
        if self.get_bit_status(byte_index=12, bit_index=1):
           self.use_s2_con.set(True)
        else:
            self.use_s2_con.set(False)
        if self.get_bit_status(byte_index=12, bit_index=2):
            self.use_s3_con.set(True)
        else:
            self.use_s3_con.set(False)
        if self.get_bit_status(byte_index=12, bit_index=3):
            self.use_s4_con.set(True)
        else:
            self.use_s4_con.set(False)

        if self.get_bit_status(byte_index=12, bit_index=4):
           self.use_s5_con.set(True)
        else:
            self.use_s5_con.set(False)
        if self.get_bit_status(byte_index=12, bit_index=5):
           self.use_s6_con.set(True)
        else:
            self.use_s6_con.set(False)
        if self.get_bit_status(byte_index=12, bit_index=6):
            self.use_s7_con.set(True)
        else:
            self.use_s7_con.set(False)
        if self.get_bit_status(byte_index=12, bit_index=7):
            self.use_s8_con.set(True)
        else:
            self.use_s8_con.set(False)

        self.pwmax_limit_entry.delete(0, tk.END)  # Clear existing content
        self.pwmax_limit_entry.insert(0, str(self.get_dec_valbit(byte_index=8)))  # Insert new value

        self.pwmin_limit_entry.delete(0, tk.END)  # Clear existing content
        self.pwmin_limit_entry.insert(0, str(self.get_dec_valbit(byte_index=10)))  # Insert new value

        self.report_rate_entry.delete(0, tk.END)  # Clear existing content
        self.report_rate_entry.insert(0, str(self.get_dec_valbit_2(byte_index=7)))  # Insert new value



    def save_params(self):

         command = "$OV0R1W00000**************************************************OV~"
#        #Note on original version controllers, the first

         command = command[:11] + self.save_me + command[43:65]
         hex_string=self.pac2_save_me_hex(16,self.pwmax_limit_entry.get())
         hex_string=self.pac2_save_me_hex(20,self.pwmin_limit_entry.get())
         hex_string=self.pac1_save_me_hex(14,self.report_rate_entry.get())

         # byte pair 0
         injectee = 0
         if self.reportcon.get(): injectee += 4  # bit 0
         if self.use_limits_con.get(): injectee += 8  # bit 1
         self.pac1_save_me_hex(0, injectee)

        #byte pair 1
         injectee = 0
         if self.ronpu.get(): injectee += 1   #bit 0
         if self.pbcont.get(): injectee += 2   #bit 1
         if self.hwcont.get(): injectee += 4  #bit 2
         self.pac1_save_me_hex(2, injectee)

        #byte pair 3
         injectee = 0
         if self.use_lcp_con.get(): injectee += 1   #bit 0
         self.pac1_save_me_hex(8, injectee)


         injectee = 0
         if self.use_s1_con.get(): injectee += 1
         if self.use_s2_con.get(): injectee += 2
         if self.use_s3_con.get(): injectee += 4
         if self.use_s4_con.get(): injectee += 8
         if self.use_s5_con.get(): injectee += 16
         if self.use_s6_con.get(): injectee += 32
         if self.use_s7_con.get(): injectee += 64
         if self.use_s8_con.get(): injectee += 128
         self.pac1_save_me_hex(24, injectee)

         command = command[:12] + self.save_me + command[44:65]
         success, response = self.serial_manager.send_long_command(command)
#10272024
    def update_erase_button_state(self):
        if self.im_sure_con.get():
            self.erase_flash_button.config(state=tk.NORMAL)
        else:
            self.erase_flash_button.config(state=tk.DISABLED)

    def erase_entire_flash(self):
        print("erasing")
 #       command = "$OV0R1W00000**************************************************OV~"

    #        #Note on original version controllers, the first
#    command = command[:12] + self.save_me + command[44:65]
#    success, response = self.serial_manager.send_long_command(command)



# region Widget Creation
    def create_widgets(self):
# Help Button
        self.help_button = tk.Button(self, text="Help", command=self.show_help)
        self.help_button.place(x=435, y=0)
 # Connection Status label
        self.label1 = tk.Label(self, text="Controller not Connected             ")
        self.label1.place(x=10, y=1)
        self.update_connection_status()

#------------------------------------------------
    #Run Controls Frame
        self.runcon_label_frame = tk.LabelFrame(self, text="Run Controls")
        self.runcon_label_frame.place(x=20, y=30, width=150, height=120)

        self.ronpu = tk.BooleanVar(value=False)
        ronpu1 = tk.Checkbutton(self.runcon_label_frame, text="Run on Power up", variable=self.ronpu)
        ronpu1.place(x=0, y=0)
        self.pbcont = tk.BooleanVar(value=False)
        pbcont1 = tk.Checkbutton(self.runcon_label_frame, text="Push Button Control", variable=self.pbcont)
        pbcont1.place(x=0, y=20)
        self.hwcont = tk.BooleanVar(value=False)
        hwcont1 = tk.Checkbutton(self.runcon_label_frame, text="Hardware Control", variable=self.hwcont)
        hwcont1.place(x=0, y=40)

#--------------------------------------------------------------
        self.othercon_label_frame = tk.LabelFrame(self, text="Other Controls")
        self.othercon_label_frame.place(x=195, y=30, width=150, height=200)

        self.use_limits_con = tk.BooleanVar(value=False)
        use_limits_button = tk.Checkbutton(self.othercon_label_frame, text="Use Pules Limits", variable=self.use_limits_con)
        use_limits_button.place(x=0, y=0)

        self.pwmax_label = tk.Label(self.othercon_label_frame, text="Maximum:")
        self.pwmax_label.place(x=0, y=25)
        self.pwmax_limit_entry = tk.Entry(self.othercon_label_frame, width=9)
        self.pwmax_limit_entry.place(x=72, y=25)  # Adjust x and y as needed


        self.pwmin_label = tk.Label(self.othercon_label_frame, text="Minimum:")
        self.pwmin_label.place(x=0, y=50)
        self.pwmin_limit_entry = tk.Entry(self.othercon_label_frame, width=9)
        self.pwmin_limit_entry.place(x=72, y=50)  # Adjust x and y as needed


        self.use_lcp_con = tk.BooleanVar(value=False)
        use_lcp_button = tk.Checkbutton(self.othercon_label_frame, text="Use LCP as Input", variable=self.use_lcp_con)
        use_lcp_button.place(x=0, y=75)


#--------------------------------------------------------------------------
        self.reprate_label_frame = tk.LabelFrame(self, text="Report Controls")
        self.reprate_label_frame.place(x=20, y=155, width=150, height=75)

        self.reportcon = tk.BooleanVar(value=False)
        report_button = tk.Checkbutton(self.reprate_label_frame, text="Live Reports", variable=self.reportcon)
        report_button.place(x=0, y=0)

        self.reprate_label=tk.Label(self.reprate_label_frame, text="Report Rate:")
        self.reprate_label.place(x=0, y=27)

        self.report_rate_entry = tk.Entry(self.reprate_label_frame, width=9)
        self.report_rate_entry.place(x=72, y=27)  # Adjust x and y as needed

#--------------------------------------------------------------------------
        self.active_servos_label_frame = tk.LabelFrame(self, text="Active Servos")
        self.active_servos_label_frame.place(x=375, y=30, width=100, height=200)

        self.use_s1_con = tk.BooleanVar(value=False)
        self.use_s1_con_button = tk.Checkbutton(self.active_servos_label_frame, text="Servo 1",variable=self.use_s1_con)
        self.use_s1_con_button.place(x=0, y=0)

        self.use_s2_con = tk.BooleanVar(value=False)
        self.use_s2_con_button = tk.Checkbutton(self.active_servos_label_frame, text="Servo 2",variable=self.use_s2_con)
        self.use_s2_con_button.place(x=0, y=20)

        self.use_s3_con = tk.BooleanVar(value=False)
        self.use_s3_con_button = tk.Checkbutton(self.active_servos_label_frame, text="Servo 3",variable=self.use_s3_con)
        self.use_s3_con_button.place(x=0, y=40)

        self.use_s4_con = tk.BooleanVar(value=False)
        self.use_s4_con_button = tk.Checkbutton(self.active_servos_label_frame, text="Servo 4",variable=self.use_s4_con)
        self.use_s4_con_button.place(x=0, y=60)

        self.use_s5_con = tk.BooleanVar(value=False)
        self.use_s5_con_button = tk.Checkbutton(self.active_servos_label_frame, text="Servo 5",variable=self.use_s5_con)
        self.use_s5_con_button.place(x=0, y=90)

        self.use_s6_con = tk.BooleanVar(value=False)
        self.use_s6_con_button = tk.Checkbutton(self.active_servos_label_frame, text="Servo 6",variable=self.use_s6_con)
        self.use_s6_con_button.place(x=0, y=110)

        self.use_s7_con = tk.BooleanVar(value=False)
        self.use_s7_con_button = tk.Checkbutton(self.active_servos_label_frame, text="Servo 7",variable=self.use_s7_con)
        self.use_s7_con_button.place(x=0, y=130)

        self.use_s8_con = tk.BooleanVar(value=False)
        self.use_s8_con_button = tk.Checkbutton(self.active_servos_label_frame, text="Servo 8",variable=self.use_s8_con)
        self.use_s8_con_button.place(x=0, y=150)

        self.get_params_button = tk.Button(self, text="Get Parameters", height=2, command=self.get_params)
        self.get_params_button.place(x=20, y=242)
        self.put_params_button = tk.Button(self, text="Save Parameters",  height=2,command=self.save_params, state=tk.DISABLED)
        self.put_params_button.place(x=120, y=242)

        self.erase_flash_frame = tk.LabelFrame(self, text="Erase Controller Script & Position Memory")
        self.erase_flash_frame.place(x=227, y=235, width=250, height=50)

        self.im_sure_con = tk.BooleanVar(value=False)
        self.im_sure_con_button = tk.Checkbutton(self.erase_flash_frame, text="I am sure", font=('hlvecta', 10,'bold'), variable=self.im_sure_con, command=self.update_erase_button_state)
        self.im_sure_con_button.place(x=0, y=0)

        self.erase_flash_button = tk.Button(self.erase_flash_frame, text="Erase Memory", command=self.erase_entire_flash, state=tk.DISABLED)
        self.erase_flash_button.place(x=120, y=0)









#endregion

# Show that a device is connected
    def update_connection_status(self):
        if globalvariables.deviceconnected==1:
            self.label1.config(text= f"Controller: {globalvariables.boarddatastring} on port: {globalvariables.deviceport}")
        else:
            self.label1.config(text="No Controller Connected            ")
