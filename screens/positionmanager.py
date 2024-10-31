# positionmanager.py

import tkinter as tk
import time
from http.client import responses
from tkinter import messagebox
import globalvariables
from globalvariables import deviceport
from serialmanager import send_command_with_timeout
from help_manager import HelpManager, MAIN_HELP_CONTENT, POSITION_MANAGER_HELP_CONTENT

class PositionManager(tk.Frame):
    def __init__(self, master, serial_manager, app):
        super().__init__(master)
        self.servos = [0] * 8
        self.live_servos =["00000"] *8
        self.cur_addr = 10000
        self.serial_manager = serial_manager
        self.app = app  # Reference to the main application class
        self.configure(width=500, height=500)
#        self.label = tk.Label(self, text="Position Manager Screen")
#        self.label.place(relx=.5,rely=.5, anchor=tk.CENTER)

        self.help_button = tk.Button(self, text="Help", command=self.show_help)
        self.help_button.place(x=440, y=1)

        self.label1 = tk.Label(self, text="Controller not Connected")
        self.label1.place(x=10,y=1)

        if globalvariables.deviceconnected==1:
            self.label1.config(text= f"Controller: {globalvariables.boarddatastring} on port: {globalvariables.deviceport}")
        else:
            self.label1.config(text="No Controller Connected")


        self.screen_selected = False
#Cont
        self.cur_adr_val = 10000

        self.continuous_actions = {}
        self.create_widgets()

        # StringVar to hold the current value
    def show_help(self):
        HelpManager.show_help(self, "Position Manager Help", POSITION_MANAGER_HELP_CONTENT)

    def load_fill_servals(self):
        self.load_servals()
        self.servo1_label.config (text=self.live_servos[0])
        self.servo2_label.config (text=self.live_servos[1])
        self.servo3_label.config(text=self.live_servos[2])
        self.servo4_label.config(text=self.live_servos[3])
        self.servo5_label.config(text=self.live_servos[4])
        self.servo6_label.config(text=self.live_servos[5])
        self.servo7_label.config(text=self.live_servos[6])
        self.servo8_label.config(text=self.live_servos[7])

    def load_servals(self):
        success, response=self.get_serv_values()
        if success:
            self.big_parse_string(response)

#following convrts the input return string to servo positions
    def big_parse_string(self, input_string):
        if len(input_string) >= 38:
            start_index=6
            for i in range(8):
                ascii_hex_part=input_string[start_index:start_index+4]
                dval=str(int(ascii_hex_part,16))
                self.live_servos[i]=dval
                start_index +=4
            return          #f"{int(input_string[2:6], 16):05d}"
        else:
            messagebox.showerror("Error", "Invalid input.")
            return "XXXXXX"

# Show that a device is connected
        self.label1 = tk.Label(self, text="Controller not Connected")
        self.label1.place(x=10,y=1)
        if globalvariables.deviceconnected==1:
            self.label1.config(text= f"Controller: {globalvariables.boarddatastring} on port: {globalvariables.deviceport}")
        else:
            self.label1.config(text="No Controller Connected                     ")

    def get_serv_values(self):
        command = "$OVXR01*******************************************************OV~"
        success, response=self.serial_manager.send_long_command(command)
        return success, response

    def parse_string(self,input_string):
        if len(input_string)>=7:
             return f"{int(input_string[2:6],16):05d}"
        else:
            messagebox.showerror("Error", "Invalid input.")
            return "XXXXXX"

    def get_mem_loc_servals(self,cur_addr):
        # Inc addr& send the command and address using the sender
        success, response = self.serial_manager.long_command_encode("R18",f"{self.cur_addr:06X}")
        #Now write the current memory location to the display, indicate the values ar not current but are memory values
        self.insert_serv_vals(response)

    def fill40_servo_string(self):
        filbe = ""
        for i in range(8):
            if getattr(self, f'uses{i + 1}').get():  # Check if the servo is selected
                filbe += str(self.live_servos[i]).zfill(5)
            else:
                filbe += "FFFF"  # Use "FFFF" for unselected servos
        return filbe.ljust(40, '0')

    def put_mem_loc_servals(self, cur_addr):
        # Write the servo values into controller flash
        success, response = self.serial_manager.long_command_encode("R19",f"{self.cur_addr:06X}",self.fill40_servo_string())
        #Now write the current memory location to the display, indicate the values ar not current but are memory values
        self.insert_serv_vals(response)

    def put_then_bump_servals(self, cur_addr):
        self.put_mem_loc_servals(self.cur_addr)
        self.cur_addr+=1
        self.address_entry.delete(0, tk.END)
        self.address_entry.insert(0, str(self.cur_addr))

    def insert_serv_vals(self, response):
        start_index = 12
        for i in range(8):
            sv_0 = response[start_index:start_index + 5]
            label_name = f"pm_{i + 1}_label"
            if hasattr(self, label_name):
                label = getattr(self, label_name)
                label.config(text=sv_0)
            start_index += 5

# region servo buttons etc
# Cont
    def start_continuous(self, action):
        if action not in self.continuous_actions:
            self.continuous_actions[action] = self.after(0, lambda: self.continuous_action(action))

    def stop_continuous(self, action):
        if action in self.continuous_actions:
            self.after_cancel(self.continuous_actions[action])
            del self.continuous_actions[action]

    def continuous_action(self, action):
        # Perform the action
        if action == 's1_up':
            self.s1_up()
        elif action == 's1_dn':
            self.s1_dn()
        elif action == 's1_upp':
            self.s1_upp()
        elif action == 's1_dnn':
            self.s1_dnn()
        elif action == 's2_up':
            self.s2_up()
        elif action == 's2_dn':
            self.s2_dn()
        elif action == 's2_upp':
            self.s2_upp()
        elif action == 's2_dnn':
            self.s2_dnn()
        elif action == 's3_up':
            self.s3_up()
        elif action == 's3_dn':
            self.s3_dn()
        elif action == 's3_upp':
            self.s3_upp()
        elif action == 's3_dnn':
            self.s3_dnn()
        elif action == 's4_up':
            self.s4_up()
        elif action == 's4_dn':
            self.s4_dn()
        elif action == 's4_upp':
            self.s4_upp()
        elif action == 's4_dnn':
            self.s4_dnn()
        elif action == 's5_up':
            self.s5_up()
        elif action == 's5_dn':
            self.s5_dn()
        elif action == 's5_upp':
            self.s5_upp()
        elif action == 's5_dnn':
            self.s5_dnn()
        elif action == 's6_up':
            self.s6_up()
        elif action == 's6_dn':
            self.s6_dn()
        elif action == 's6_upp':
            self.s6_upp()
        elif action == 's6_dnn':
            self.s6_dnn()

        elif action == 's7_up':
            self.s7_up()
        elif action == 's7_dn':
            self.s7_dn()
        elif action == 's7_upp':
            self.s7_upp()
        elif action == 's7_dnn':
            self.s7_dnn()

        elif action == 's8_up':
            self.s8_up()
        elif action == 's8_dn':
            self.s8_dn()
        elif action == 's8_upp':
            self.s8_upp()
        elif action == 's8_dnn':
            self.s8_dnn()


        # Schedule the next action if it's still in continuous_actions
        if action in self.continuous_actions:
            self.continuous_actions[action] = self.after(10, lambda: self.continuous_action(action))

    #end new cont
#      replace = command [:3] + "0201" +command[:3]
    def s1_up1(self):
        success, response = self.serial_manager.send_short_command("-OU000101H")
        s_get=text=self.parse_string(response)
        self.servo1_label.config(text=s_get)
        self.live_servos[0]=s_get

    def s1_dn1(self):
        success, response = self.serial_manager.send_short_command("-OD000101H")
        s_get=text=self.parse_string(response)
        self.servo1_label.config(text=s_get)
        self.live_servos[0]=s_get


    def s1_up(self):
        success, response = self.serial_manager.send_short_command("-OU000401H")
        s_get=text=self.parse_string(response)
        self.servo1_label.config(text=s_get)
        self.live_servos[0]=s_get

    def s1_dn(self):
        success, response = self.serial_manager.send_short_command("-OD000401H")
        s_get=text=self.parse_string(response)
        self.servo1_label.config(text=s_get)
        self.live_servos[0]=s_get

    def s1_upp(self):
        success, response = self.serial_manager.send_short_command("-OU004001H")
        s_get=text=self.parse_string(response)
        self.servo1_label.config(text=s_get)
        self.live_servos[0]=s_get

    def s1_dnn(self):
        success, response = self.serial_manager.send_short_command("-OD004001H")
        s_get=text=self.parse_string(response)
        self.servo1_label.config(text=s_get)
        self.live_servos[0]=s_get

    def s2_up1(self):
        success, response = self.serial_manager.send_short_command("-OU000102H")
        s_get=text=self.parse_string(response)
        self.servo2_label.config(text=s_get)
        self.live_servos[1]=s_get
    def s2_dn1(self):
        success, response = self.serial_manager.send_short_command("-OD000102H")
        s_get=text=self.parse_string(response)
        self.servo2_label.config(text=s_get)
        self.live_servos[1]=s_get
    def s2_up(self):
        success, response = self.serial_manager.send_short_command("-OU000402H")
        s_get=text=self.parse_string(response)
        self.servo2_label.config(text=s_get)
        self.live_servos[1]=s_get
    def s2_dn(self):
        success, response = self.serial_manager.send_short_command("-OD000402H")
        s_get=text=self.parse_string(response)
        self.servo2_label.config(text=s_get)
        self.live_servos[1]=s_get
    def s2_upp(self):
        success, response = self.serial_manager.send_short_command("-OU004002H")
        s_get=text=self.parse_string(response)
        self.servo2_label.config(text=s_get)
        self.live_servos[1]=s_get
    def s2_dnn(self):
        success, response = self.serial_manager.send_short_command("-OD004002H")
        s_get=text=self.parse_string(response)
        self.servo2_label.config(text=s_get)
        self.live_servos[1]=s_get
    def s3_up1(self):
        success, response = self.serial_manager.send_short_command("-OU000103H")
        s_get=text=self.parse_string(response)
        self.servo3_label.config(text=s_get)
        self.live_servos[2]=s_get
    def s3_dn1(self):
        success, response = self.serial_manager.send_short_command("-OD000103H")
        s_get=text=self.parse_string(response)
        self.servo3_label.config(text=s_get)
        self.live_servos[2]=s_get
    def s3_up(self):
        success, response = self.serial_manager.send_short_command("-OU000403H")
        s_get=text=self.parse_string(response)
        self.servo3_label.config(text=s_get)
        self.live_servos[2]=s_get
    def s3_dn(self):
        success, response = self.serial_manager.send_short_command("-OD000403H")
        s_get=text=self.parse_string(response)
        self.servo3_label.config(text=s_get)
        self.live_servos[2]=s_get
    def s3_upp(self):
        success, response = self.serial_manager.send_short_command("-OU004003H")
        s_get=text=self.parse_string(response)
        self.servo3_label.config(text=s_get)
        self.live_servos[2]=s_get
    def s3_dnn(self):
        success, response = self.serial_manager.send_short_command("-OD004003H")
        s_get=text=self.parse_string(response)
        self.servo3_label.config(text=s_get)
        self.live_servos[2]=s_get
    def s4_up1(self):
        success, response = self.serial_manager.send_short_command("-OU000104H")
        s_get=text=self.parse_string(response)
        self.servo4_label.config(text=s_get)
        self.live_servos[3]=s_get
    def s4_dn1(self):
        success, response = self.serial_manager.send_short_command("-OD000104H")
        s_get=text=self.parse_string(response)
        self.servo4_label.config(text=s_get)
        self.live_servos[3]=s_get
    def s4_up(self):
        success, response = self.serial_manager.send_short_command("-OU000204H")
        s_get=text=self.parse_string(response)
        self.servo4_label.config(text=s_get)
        self.live_servos[3]=s_get
    def s4_dn(self):
        success, response = self.serial_manager.send_short_command("-OD000204H")
        s_get=text=self.parse_string(response)
        self.servo4_label.config(text=s_get)
        self.live_servos[3]=s_get
    def s4_upp(self):
        success, response = self.serial_manager.send_short_command("-OU004004H")
        s_get=text=self.parse_string(response)
        self.servo4_label.config(text=s_get)
        self.live_servos[3]=s_get
    def s4_dnn(self):
        success, response = self.serial_manager.send_short_command("-OD004004H")
        s_get=text=self.parse_string(response)
        self.servo4_label.config(text=s_get)
        self.live_servos[3]=s_get

    def s5_up1(self):
        success, response = self.serial_manager.send_short_command("-OU000105H")
        s_get=text=self.parse_string(response)
        self.servo5_label.config(text=s_get)
        self.live_servos[4]=s_get
    def s5_dn1(self):
        success, response = self.serial_manager.send_short_command("-OD000105H")
        s_get=text=self.parse_string(response)
        self.servo5_label.config(text=s_get)
        self.live_servos[4]=s_get
    def s5_up(self):
        success, response = self.serial_manager.send_short_command("-OU000205H")
        s_get=text=self.parse_string(response)
        self.servo5_label.config(text=s_get)
        self.live_servos[4]=s_get
    def s5_dn(self):
        success, response = self.serial_manager.send_short_command("-OD000205H")
        s_get=text=self.parse_string(response)
        self.servo5_label.config(text=s_get)
        self.live_servos[4]=s_get
    def s5_upp(self):
        success, response = self.serial_manager.send_short_command("-OU004005H")
        s_get=text=self.parse_string(response)
        self.servo5_label.config(text=s_get)
        self.live_servos[4]=s_get
    def s5_dnn(self):
        success, response = self.serial_manager.send_short_command("-OD004005H")
        s_get=text=self.parse_string(response)
        self.servo5_label.config(text=s_get)
        self.live_servos[4]=s_get

    def s6_up1(self):
        success, response = self.serial_manager.send_short_command("-OU000106H")
        s_get=text=self.parse_string(response)
        self.servo6_label.config(text=s_get)
        self.live_servos[5]=s_get
    def s6_dn1(self):
        success, response = self.serial_manager.send_short_command("-OD000106H")
        s_get=text=self.parse_string(response)
        self.servo6_label.config(text=s_get)
        self.live_servos[5]=s_get
    def s6_up(self):
        success, response = self.serial_manager.send_short_command("-OU000206H")
        s_get=text=self.parse_string(response)
        self.servo6_label.config(text=s_get)
        self.live_servos[5]=s_get
    def s6_dn(self):
        success, response = self.serial_manager.send_short_command("-OD000206H")
        s_get=text=self.parse_string(response)
        self.servo6_label.config(text=s_get)
        self.live_servos[5]=s_get
    def s6_upp(self):
        success, response = self.serial_manager.send_short_command("-OU004006H")
        s_get=text=self.parse_string(response)
        self.servo6_label.config(text=s_get)
        self.live_servos[5]=s_get
    def s6_dnn(self):
        success, response = self.serial_manager.send_short_command("-OD004006H")
        s_get=text=self.parse_string(response)
        self.servo6_label.config(text=s_get)
        self.live_servos[5]=s_get

    def s7_up1(self):
        success, response = self.serial_manager.send_short_command("-OU000107H")
        s_get=text=self.parse_string(response)
        self.servo7_label.config(text=s_get)
        self.live_servos[6]=s_get
    def s7_dn1(self):
        success, response = self.serial_manager.send_short_command("-OD000107H")
        s_get=text=self.parse_string(response)
        self.servo7_label.config(text=s_get)
        self.live_servos[6]=s_get
    def s7_up(self):
        success, response = self.serial_manager.send_short_command("-OU000207H")
        s_get=text=self.parse_string(response)
        self.servo7_label.config(text=s_get)
        self.live_servos[6]=s_get
    def s7_dn(self):
        success, response = self.serial_manager.send_short_command("-OD000207H")
        s_get=text=self.parse_string(response)
        self.servo7_label.config(text=s_get)
        self.live_servos[6]=s_get
    def s7_upp(self):
        success, response = self.serial_manager.send_short_command("-OU004007H")
        s_get=text=self.parse_string(response)
        self.servo7_label.config(text=s_get)
        self.live_servos[6]=s_get
    def s7_dnn(self):
        success, response = self.serial_manager.send_short_command("-OD004007H")
        s_get=text=self.parse_string(response)
        self.servo7_label.config(text=s_get)
        self.live_servos[6]=s_get

    def s8_up1(self):
        success, response = self.serial_manager.send_short_command("-OU000108H")
        s_get=text=self.parse_string(response)
        self.servo8_label.config(text=s_get)
        self.live_servos[7]=s_get
    def s8_dn1(self):
        success, response = self.serial_manager.send_short_command("-OD000108H")
        s_get=text=self.parse_string(response)
        self.servo8_label.config(text=s_get)
        self.live_servos[7]=s_get
    def s8_up(self):
        success, response = self.serial_manager.send_short_command("-OU000208H")
        s_get=text=self.parse_string(response)
        self.servo8_label.config(text=s_get)
        self.live_servos[7]=s_get
    def s8_dn(self):
        success, response = self.serial_manager.send_short_command("-OD000208H")
        s_get=text=self.parse_string(response)
        self.servo8_label.config(text=s_get)
        self.live_servos[7]=s_get
    def s8_upp(self):
        success, response = self.serial_manager.send_short_command("-OU004008H")
        s_get=text=self.parse_string(response)
        self.servo8_label.config(text=s_get)
        self.live_servos[7]=s_get
    def s8_dnn(self):
        success, response = self.serial_manager.send_short_command("-OD004008H")
        s_get=text=self.parse_string(response)
        self.servo8_label.config(text=s_get)
        self.live_servos[7]=s_get
#endregion

    # Testing here
    def update_adr_value(self):
        try:
            new_value = int(self.address_entry.get())
            if 0 <= new_value <= 65535:
                self.cur_addr = new_value
            else:
                messagebox.showerror("Error", "Invalid input.")
        except:
            messagebox.showerror("Error", "Invalid input.")
        self.address_entry.delete(0, tk.END)
        self.address_entry.insert(0, str(self.cur_addr))
        self.get_mem_loc_servals(self.cur_addr)
            #end of tesitng

    def bump_adr_value(self):
        self.cur_addr += 1
        self.address_entry.delete(0, tk.END)
        self.address_entry.insert(0, str(self.cur_addr))
        self.get_mem_loc_servals(self.cur_addr)

    def dec_adr_value(self):
        self.cur_addr -= 1
        self.address_entry.delete(0, tk.END)
        self.address_entry.insert(0, str(self.cur_addr))
        self.get_mem_loc_servals(self.cur_addr)

    def get_mem_moveset_to_live(self):
 # Send the command and address using the sender
        success, response = self.serial_manager.send_short_command("-OT" + f"{self.cur_addr:06X}" + "H")
 # Show wait label
        self.wait_label = tk.Label(self, text="Wait", fg="red", font=("Arial", 16, "bold"))
        self.wait_label.place(x=350, y=13, anchor="center")
 # Force update to show the wait label
        self.update()
 # Schedule the finish method after 2500ms
        self.after(2500, self.finish_mem_moveset_to_live)

    def finish_mem_moveset_to_live(self):
        # Remove wait label
        if hasattr(self, 'wait_label'):
            self.wait_label.destroy()
        # Load servo values
        self.load_fill_servals()


    def create_widgets(self):
        button_style = {
            'font': ('Aerial', 8),
            'width': 2,
            'height': 1,
            'padx': 0,
            'pady': 0,
            'borderwidth': 1,
            'relief': 'raised'
        }

# region Init Widgets
# Widgets for the position address management
        self.help_button = tk.Button(self, text="Help", command=self.show_help)
        self.help_button.place(x=440, y=1)
        self.label1 = tk.Label(self, text="Controller not Connected             ")
        self.label1.place(x=10, y=1)


#---------------------------------------------------------------------------------------------------------

#Position Memory Controls
    #Main frame for memory activity
        self.pm_frame = tk.LabelFrame(self, text="Position Memory Editor")
        self.pm_frame.place(x=5, y=30, width=480, height=200)  # Keep place for inner widgets

    #Address frame
        self.pm_label_frame = tk.LabelFrame(self.pm_frame, text="Get Values at Address")
        self.pm_label_frame.place(x=7, y=0, width=465, height=50)  # Keep place for inner widgets

    #Address Label & Input area

        # Address entry widget for both input and display
#        self.cur_addr = tk.IntVar(value=10000)  # Initialize with default value
        self.address_entry = tk.Entry(self.pm_label_frame, width=6, font=12)   #textvariable=self.cur_addr,
        self.address_entry.place(x=5, y=2)
        self.address_entry.insert(0, str(self.cur_adr_val))

    # Set Address Button to update the display
        self.update_address_button = tk.Button(self.pm_label_frame, text="Enter Address", command=self.update_adr_value)
        self.update_address_button.place(x=70, y=0)

    # Bump Address
        self.bump_address_button = tk.Button(self.pm_label_frame, text="Bump Address", command=self.bump_adr_value)
        self.bump_address_button.place(x=159, y=0)

        # dec Address
        self.dec_address_button = tk.Button(self.pm_label_frame, text="Dec Address", command=self.dec_adr_value)
        self.dec_address_button.place(x=253, y=0)

        # Set Address Button to update the display
        self.update_address_button = tk.Button(self.pm_label_frame, text="Get & Move to Live", command=self.get_mem_moveset_to_live, bg='yellow', activebackground='#FFFF66')
        self.update_address_button.place(x=336, y=0)



#----------------------------------------------------------------------------------
    # Read Write Controls
        self.pm_rw_controls_frame = tk.LabelFrame(self.pm_frame, text="Write Positions to Controller Memory")
        self.pm_rw_controls_frame.place(x=7, y=50, width=220, height=55)  # Keep place for inner widgets

        self.putmem_button = tk.Button(self.pm_rw_controls_frame, text="Write Position", command=lambda: self.put_mem_loc_servals(self.cur_addr))
        self.putmem_button.place(x=5, y=2)

        self.putmem_bump_button = tk.Button(self.pm_rw_controls_frame, text="Write & Bump Pos", command=lambda: self.put_then_bump_servals(self.cur_addr))
        self.putmem_bump_button.place(x=96, y=2)

# Memory servo value display frame
        self.pm_servo_display_frame = tk.LabelFrame(self.pm_frame, text="Postion Memory Servo Values (display only)")
        self.pm_servo_display_frame.place(x=7, y=110, width=465, height=65)  # Keep place for inner widgets

        self.pm_1_frame = tk.LabelFrame(self.pm_servo_display_frame, text="S1")
        self.pm_1_frame.place(x=2, y=0, width=52, height=44)
        self.pm_1_label=tk.Label(self.pm_1_frame, text="-----", anchor="n", font=('Arial', 11), padx=1, pady=1)
        self.pm_1_label.place(x=0, y=0)

        self.pm_2_frame = tk.LabelFrame(self.pm_servo_display_frame, text="S2")
        self.pm_2_frame.place(x=60, y=0, width=52, height=45)
        self.pm_2_label=tk.Label(self.pm_2_frame, text="-----", anchor="n", font=('Arial', 11), padx=1, pady=1)
        self.pm_2_label.place(x=0, y=0)

        self.pm_3_frame = tk.LabelFrame(self.pm_servo_display_frame, text="S3")
        self.pm_3_frame.place(x=118, y=0, width=52, height=45)
        self.pm_3_label=tk.Label(self.pm_3_frame, text="-----", anchor="n", font=('Arial', 11), padx=1, pady=1)
        self.pm_3_label.place(x=0, y=0)

        self.pm_4_frame = tk.LabelFrame(self.pm_servo_display_frame, text="S4")
        self.pm_4_frame.place(x=176, y=0, width=52, height=44)
        self.pm_4_label=tk.Label(self.pm_4_frame, text="-----", anchor="n", font=('Arial', 11), padx=1, pady=1)
        self.pm_4_label.place(x=0, y=0)

        self.pm_5_frame = tk.LabelFrame(self.pm_servo_display_frame, text="S5")
        self.pm_5_frame.place(x=234, y=0, width=52, height=45)
        self.pm_5_label=tk.Label(self.pm_5_frame, text="-----", anchor="n", font=('Arial', 11), padx=1, pady=1)
        self.pm_5_label.place(x=0, y=0)

        self.pm_6_frame = tk.LabelFrame(self.pm_servo_display_frame, text="S6")
        self.pm_6_frame.place(x=292, y=0, width=52, height=45)
        self.pm_6_label=tk.Label(self.pm_6_frame, text="-----", anchor="n", font=('Arial', 11), padx=1, pady=1)
        self.pm_6_label.place(x=0, y=0)

        self.pm_7_frame = tk.LabelFrame(self.pm_servo_display_frame, text="S7")
        self.pm_7_frame.place(x=350, y=0, width=52, height=45)
        self.pm_7_label=tk.Label(self.pm_7_frame, text="-----", anchor="n", font=('Arial', 11), padx=1, pady=1)
        self.pm_7_label.place(x=0, y=0)

        self.pm_8_frame = tk.LabelFrame(self.pm_servo_display_frame, text="S8")
        self.pm_8_frame.place(x=408, y=0, width=52, height=45)
        self.pm_8_label=tk.Label(self.pm_8_frame, text="-----", anchor="n", font=('Arial', 11), padx=1, pady=1)
        self.pm_8_label.place(x=0, y=0)




#----------------------------
#Main Live servos frame
        # Create the live_servos_frame
        self.live_servos_frame = tk.LabelFrame(self, text="Live Servo Values")
        self.live_servos_frame.place(x=5, y=230, width=480, height=225)

#Servo Widgets
# Input frame for servo 1
        self.servo1_frame = tk.LabelFrame(self.live_servos_frame, text="Servo 1")
        self.servo1_frame.place(x=7, y=0, width=55, height=165)  # Keep place for inner widgets
# Label
        self.servo1_label = tk.Label(self.servo1_frame, text="00000", anchor="n", borderwidth=2,relief="groove", padx=3, pady=2)
        self.servo1_label.place(x=5, y=0)
#Buttons
        # Buttons
        self.s1aup = tk.Button(self.servo1_frame, text="+", **button_style)
        self.s1aup.place(x=12, y=40, anchor="center")
        self.s1aup.bind('<ButtonPress-1>', lambda e: self.start_continuous('s1_upp'))
        self.s1aup.bind('<ButtonRelease-1>', lambda e: self.stop_continuous('s1_upp'))
        self.s1cup = tk.Button(self.servo1_frame, text="+", **button_style)
        self.s1cup.place(x=12, y=70, anchor="center")
        self.s1cup.bind('<ButtonPress-1>', lambda e: self.start_continuous('s1_up'))
        self.s1cup.bind('<ButtonRelease-1>', lambda e: self.stop_continuous('s1_up'))
        self.s1caup=tk.Button(self.servo1_frame,text="1", **button_style)
        self.s1caup.place(x=12, y=100, anchor="center")
        self.s1caup.bind('<Button-1>', lambda e: self.s1_up1())

        self.s1ddn=tk.Button(self.servo1_frame,text="-", **button_style)
        self.s1ddn.place(x=35, y=40, anchor="center")
        self.s1ddn.bind('<ButtonPress-1>', lambda e: self.start_continuous('s1_dnn'))
        self.s1ddn.bind('<ButtonRelease-1>', lambda e: self.stop_continuous('s1_dnn'))
        self.s1bdn=tk.Button(self.servo1_frame,text="-", **button_style)
        self.s1bdn.place(x=35, y=70, anchor="center")
        self.s1bdn.bind('<ButtonPress-1>', lambda e: self.start_continuous('s1_dn'))
        self.s1bdn.bind('<ButtonRelease-1>', lambda e: self.stop_continuous('s1_dn'))
        self.s1dadn=tk.Button(self.servo1_frame,text="1", **button_style)
        self.s1dadn.place(x=35, y=100, anchor="center")
        self.s1dadn.bind('<Button-1>', lambda e: self.s1_dn1())
#check Box
        self.uses1=tk.BooleanVar(value=True)
        cbuses1=tk.Checkbutton(self.servo1_frame, text="Use", variable=self.uses1)
        cbuses1.place(x=22, y=130, anchor="center")


 #Input frame for servo 2
        self.servo2_frame = tk.LabelFrame(self.live_servos_frame, text="Servo 2")
        self.servo2_frame.place(x=65, y=0, width=55, height=165)  # Keep place for inner widgets
# Label
        self.servo2_label = tk.Label(self.servo2_frame, text="00000", anchor="n", borderwidth=2,relief="groove", padx=3, pady=2)
        self.servo2_label.place(x=5, y=0)
#Buttons
        self.s2cup = tk.Button(self.servo2_frame, text="+", **button_style)
        self.s2cup.place(x=12, y=40, anchor="center")
        self.s2cup.bind('<ButtonPress-1>', lambda e: self.start_continuous('s2_upp'))
        self.s2cup.bind('<ButtonRelease-1>', lambda e: self.stop_continuous('s2_upp'))
        self.s2aup = tk.Button(self.servo2_frame, text="+", **button_style)
        self.s2aup.place(x=12, y=70, anchor="center")
        self.s2aup.bind('<ButtonPress-1>', lambda e: self.start_continuous('s2_up'))
        self.s2aup.bind('<ButtonRelease-1>', lambda e: self.stop_continuous('s2_up'))
        self.s2aup = tk.Button(self.servo2_frame, text="1", **button_style)
        self.s2aup.place(x=12, y=100, anchor="center")
        self.s2aup.bind('<Button-1>', lambda e: self.s2_up1())
        self.s2ddn=tk.Button(self.servo2_frame,text="-", **button_style)
        self.s2ddn.place(x=35, y=40, anchor="center")
        self.s2ddn.bind('<ButtonPress-1>', lambda e: self.start_continuous('s2_dnn'))
        self.s2ddn.bind('<ButtonRelease-1>', lambda e: self.stop_continuous('s2_dnn'))
        self.s2bdn=tk.Button(self.servo2_frame,text="-", **button_style)
        self.s2bdn.place(x=35, y=70, anchor="center")
        self.s2bdn.bind('<ButtonPress-1>', lambda e: self.start_continuous('s2_dn'))
        self.s2bdn.bind('<ButtonRelease-1>', lambda e: self.stop_continuous('s2_dn'))
        self.s2bdn=tk.Button(self.servo2_frame,text="1", **button_style)
        self.s2bdn.place(x=35, y=100, anchor="center")
        self.s2bdn.bind('<Button-1>', lambda e: self.s2_dn1())

#check Box
        self.uses2=tk.BooleanVar(value=True)
        cbuses2=tk.Checkbutton(self.servo2_frame, text="Use", variable=self.uses2)
        cbuses2.place(x=24, y=130, anchor="center")

 #Input frame for servo 3
        self.servo3_frame = tk.LabelFrame(self.live_servos_frame, text="Servo 3")
        self.servo3_frame.place(x=123, y=0, width=55, height=165)  # Keep place for inner widgets
# Label
        self.servo3_label = tk.Label(self.servo3_frame, text="00000", anchor="n", borderwidth=2,relief="groove", padx=3, pady=2)
        self.servo3_label.place(x=5, y=0)
#Buttons
        self.s3cup = tk.Button(self.servo3_frame, text="+", **button_style)
        self.s3cup.place(x=12, y=40, anchor="center")
        self.s3cup.bind('<ButtonPress-1>', lambda e: self.start_continuous('s3_upp'))
        self.s3cup.bind('<ButtonRelease-1>', lambda e: self.stop_continuous('s3_upp'))
        self.s3aup = tk.Button(self.servo3_frame, text="+", **button_style)
        self.s3aup.place(x=12, y=70, anchor="center")
        self.s3aup.bind('<ButtonPress-1>', lambda e: self.start_continuous('s3_up'))
        self.s3aup.bind('<ButtonRelease-1>', lambda e: self.stop_continuous('s3_up'))
        self.s3aup = tk.Button(self.servo3_frame, text="1", **button_style)
        self.s3aup.place(x=12, y=100, anchor="center")
        self.s3aup.bind('<Button-1>', lambda e: self.s3_up1())
        self.s3ddn=tk.Button(self.servo3_frame,text="-", **button_style)
        self.s3ddn.place(x=35, y=40, anchor="center")
        self.s3ddn.bind('<ButtonPress-1>', lambda e: self.start_continuous('s3_dnn'))
        self.s3ddn.bind('<ButtonRelease-1>', lambda e: self.stop_continuous('s3_dnn'))
        self.s3bdn=tk.Button(self.servo3_frame,text="-", **button_style)
        self.s3bdn.place(x=35, y=70, anchor="center")
        self.s3bdn.bind('<ButtonPress-1>', lambda e: self.start_continuous('s3_dn'))
        self.s3bdn.bind('<ButtonRelease-1>', lambda e: self.stop_continuous('s3_dn'))
        self.s3bdn=tk.Button(self.servo3_frame,text="1", **button_style)
        self.s3bdn.place(x=35, y=100, anchor="center")
        self.s3bdn.bind('<Button-1>', lambda e: self.s3_dn1())
#check Box
        self.uses3=tk.BooleanVar(value=True)
        cbuses3=tk.Checkbutton(self.servo3_frame, text="Use", variable=self.uses3)
        cbuses3.place(x=24, y=130, anchor="center")

# Input frame for servo 4
        self.servo4_frame = tk.LabelFrame(self.live_servos_frame, text="Servo 4")
        self.servo4_frame.place(x=181, y=0, width=55, height=165)  # Keep place for inner widgets
        # Label
        self.servo4_label = tk.Label(self.servo4_frame, text="00000", anchor="n", borderwidth=2, relief="groove",
                                     padx=3, pady=2)
        self.servo4_label.place(x=5, y=0)
        # Buttons
        self.s4cup = tk.Button(self.servo4_frame, text="+", **button_style)
        self.s4cup.place(x=12, y=40, anchor="center")
        self.s4cup.bind('<ButtonPress-1>', lambda e: self.start_continuous('s4_upp'))
        self.s4cup.bind('<ButtonRelease-1>', lambda e: self.stop_continuous('s4_upp'))
        self.s4aup = tk.Button(self.servo4_frame, text="+", **button_style)
        self.s4aup.place(x=12, y=70, anchor="center")
        self.s4aup.bind('<ButtonPress-1>', lambda e: self.start_continuous('s4_up'))
        self.s4aup.bind('<ButtonRelease-1>', lambda e: self.stop_continuous('s4_up'))
        self.s4aup = tk.Button(self.servo4_frame, text="1", **button_style)
        self.s4aup.place(x=12, y=100, anchor="center")
        self.s4aup.bind('<Button-1>', lambda e: self.s4_up1())
        self.s4ddn = tk.Button(self.servo4_frame, text="-", **button_style)
        self.s4ddn.place(x=35, y=40, anchor="center")
        self.s4ddn.bind('<ButtonPress-1>', lambda e: self.start_continuous('s4_dnn'))
        self.s4ddn.bind('<ButtonRelease-1>', lambda e: self.stop_continuous('s4_dnn'))
        self.s4bdn = tk.Button(self.servo4_frame, text="-", **button_style)
        self.s4bdn.place(x=35, y=70, anchor="center")
        self.s4bdn.bind('<ButtonPress-1>', lambda e: self.start_continuous('s4_dn'))
        self.s4bdn.bind('<ButtonRelease-1>', lambda e: self.stop_continuous('s4_dn'))
        self.s4bdn = tk.Button(self.servo4_frame, text="1", **button_style)
        self.s4bdn.place(x=35, y=100, anchor="center")
        self.s4bdn.bind('<Button-1>', lambda e: self.s4_dn1())

        # check Box
        self.uses4 = tk.BooleanVar(value=True)
        cbuses4 = tk.Checkbutton(self.servo4_frame, text="Use", variable=self.uses4)
        cbuses4.place(x=24, y=130, anchor="center")

        # Input frame for servo 5
        self.servo5_frame = tk.LabelFrame(self.live_servos_frame, text="Servo 5")
        self.servo5_frame.place(x=239, y=0, width=55, height=165)  # Keep place for inner widgets
        # Label
        self.servo5_label = tk.Label(self.servo5_frame, text="00000", anchor="n", borderwidth=2, relief="groove",
                                     padx=3, pady=2)
        self.servo5_label.place(x=5, y=0)
        # Buttons
        self.s5cup = tk.Button(self.servo5_frame, text="+", **button_style)
        self.s5cup.place(x=12, y=40, anchor="center")
        self.s5cup.bind('<ButtonPress-1>', lambda e: self.start_continuous('s5_upp'))
        self.s5cup.bind('<ButtonRelease-1>', lambda e: self.stop_continuous('s5_upp'))
        self.s5aup = tk.Button(self.servo5_frame, text="+", **button_style)
        self.s5aup.place(x=12, y=70, anchor="center")
        self.s5aup.bind('<ButtonPress-1>', lambda e: self.start_continuous('s5_up'))
        self.s5aup.bind('<ButtonRelease-1>', lambda e: self.stop_continuous('s5_up'))
        self.s5a1up = tk.Button(self.servo5_frame, text="1", **button_style)
        self.s5a1up.place(x=12, y=100, anchor="center")
        self.s5a1up.bind('<Button-1>', lambda e: self.s5_up1())

        self.s5ddn = tk.Button(self.servo5_frame, text="-", **button_style)
        self.s5ddn.place(x=35, y=40, anchor="center")
        self.s5ddn.bind('<ButtonPress-1>', lambda e: self.start_continuous('s5_dnn'))
        self.s5ddn.bind('<ButtonRelease-1>', lambda e: self.stop_continuous('s5_dnn'))
        self.s5bdn = tk.Button(self.servo5_frame, text="-", **button_style)
        self.s5bdn.place(x=35, y=70, anchor="center")
        self.s5bdn.bind('<ButtonPress-1>', lambda e: self.start_continuous('s5_dn'))
        self.s5bdn.bind('<ButtonRelease-1>', lambda e: self.stop_continuous('s5_dn'))
        self.s5b1dn = tk.Button(self.servo5_frame, text="1", **button_style)
        self.s5b1dn.place(x=35, y=100, anchor="center")
        self.s5b1dn.bind('<ButtonPress-1>', lambda e: self.s5_dn1())


        # check Box
        self.uses5 = tk.BooleanVar()
        cbuses5 = tk.Checkbutton(self.servo5_frame, text="Use", variable=self.uses5)
        cbuses5.place(x=24, y=130, anchor="center")


        # Input frame for servo 6
        self.servo6_frame = tk.LabelFrame(self.live_servos_frame, text="Servo 6")
        self.servo6_frame.place(x=297, y=0, width=55, height=165)  # Keep place for inner widgets
        # Label
        self.servo6_label = tk.Label(self.servo6_frame, text="00000", anchor="n", borderwidth=2, relief="groove",
                                     padx=3, pady=2)
        self.servo6_label.place(x=5, y=0)
        # Buttons
        self.s6cup = tk.Button(self.servo6_frame, text="+", **button_style)
        self.s6cup.place(x=12, y=40, anchor="center")
        self.s6cup.bind('<ButtonPress-1>', lambda e: self.start_continuous('s6_upp'))
        self.s6cup.bind('<ButtonRelease-1>', lambda e: self.stop_continuous('s6_upp'))
        self.s6aup = tk.Button(self.servo6_frame, text="+", **button_style)
        self.s6aup.place(x=12, y=70, anchor="center")
        self.s6aup.bind('<ButtonPress-1>', lambda e: self.start_continuous('s6_up'))
        self.s6aup.bind('<ButtonRelease-1>', lambda e: self.stop_continuous('s6_up'))
        self.s6aaup = tk.Button(self.servo6_frame, text="+", **button_style)
        self.s6aaup.place(x=12, y=100, anchor="center")
        self.s6aaup.bind('<Button-1>', lambda e: self.s6_up1())
        self.s6ddn = tk.Button(self.servo6_frame, text="-", **button_style)
        self.s6ddn.place(x=35, y=40, anchor="center")
        self.s6ddn.bind('<ButtonPress-1>', lambda e: self.start_continuous('s6_dnn'))
        self.s6ddn.bind('<ButtonRelease-1>', lambda e: self.stop_continuous('s6_dnn'))
        self.s6bdn = tk.Button(self.servo6_frame, text="1", **button_style)
        self.s6bdn.place(x=35, y=70, anchor="center")
        self.s6bdn.bind('<ButtonPress-1>', lambda e: self.start_continuous('s6_dn'))
        self.s6bdn.bind('<ButtonRelease-1>', lambda e: self.stop_continuous('s6_dn'))
        self.s6bdn = tk.Button(self.servo6_frame, text="1", **button_style)
        self.s6bdn.place(x=35, y=100, anchor="center")
        self.s6bdn.bind('<Button-1>', lambda e: self.s6_dn1())
        # check Box
        self.uses6 = tk.BooleanVar()
        cbuses6 = tk.Checkbutton(self.servo6_frame, text="Use", variable=self.uses6)
        cbuses6.place(x=24, y=130, anchor="center")

        # Input frame for servo 7
        self.servo7_frame = tk.LabelFrame(self.live_servos_frame, text="Servo 7")
        self.servo7_frame.place(x=355, y=0, width=55, height=165)  # Keep place for inner widgets
        # Label
        self.servo7_label = tk.Label(self.servo7_frame, text="00000", anchor="n", borderwidth=2, relief="groove",
                                     padx=3, pady=2)
        self.servo7_label.place(x=5, y=0)
        # Buttons
        self.s7cup = tk.Button(self.servo7_frame, text="+", **button_style)
        self.s7cup.place(x=12, y=40, anchor="center")
        self.s7cup.bind('<ButtonPress-1>', lambda e: self.start_continuous('s7_upp'))
        self.s7cup.bind('<ButtonRelease-1>', lambda e: self.stop_continuous('s7_upp'))
        self.s7aup = tk.Button(self.servo7_frame, text="+", **button_style)
        self.s7aup.place(x=12, y=70, anchor="center")
        self.s7aup.bind('<ButtonPress-1>', lambda e: self.start_continuous('s7_up'))
        self.s7aup.bind('<ButtonRelease-1>', lambda e: self.stop_continuous('s7_up'))
        self.s7a1up = tk.Button(self.servo7_frame, text="1", **button_style)
        self.s7a1up.place(x=12, y=100, anchor="center")
        self.s7a1up.bind('<Button-1>', lambda e: self.s7_up1())

        self.s7ddn = tk.Button(self.servo7_frame, text="-", **button_style)
        self.s7ddn.place(x=35, y=40, anchor="center")
        self.s7ddn.bind('<ButtonPress-1>', lambda e: self.start_continuous('s7_dnn'))
        self.s7ddn.bind('<ButtonRelease-1>', lambda e: self.stop_continuous('s7_dnn'))
        self.s7bdn = tk.Button(self.servo7_frame, text="-", **button_style)
        self.s7bdn.place(x=35, y=70, anchor="center")
        self.s7bdn.bind('<ButtonPress-1>', lambda e: self.start_continuous('s7_dn'))
        self.s7bdn.bind('<ButtonRelease-1>', lambda e: self.stop_continuous('s7_dn'))
        self.s7b1dn = tk.Button(self.servo7_frame, text="1", **button_style)
        self.s7b1dn.place(x=35, y=100, anchor="center")
        self.s7b1dn.bind('<Button-1>', lambda e: self.s7_dn1())

        # check Box
        self.uses7 = tk.BooleanVar()
        cbuses7 = tk.Checkbutton(self.servo7_frame, text="Use", variable=self.uses7)
        cbuses7.place(x=24, y=130, anchor="center")

        # Input frame for servo 7
        self.servo8_frame = tk.LabelFrame(self.live_servos_frame, text="Servo 8")
        self.servo8_frame.place(x=413, y=0, width=55, height=165)  # Keep place for inner widgets
        # Label
        self.servo8_label = tk.Label(self.servo8_frame, text="00000", anchor="n", borderwidth=2, relief="groove",
                                     padx=3, pady=2)
        self.servo8_label.place(x=5, y=0)
        # Buttons
        self.s8cup = tk.Button(self.servo8_frame, text="+", **button_style)
        self.s8cup.place(x=12, y=40, anchor="center")
        self.s8cup.bind('<ButtonPress-1>', lambda e: self.start_continuous('s8_upp'))
        self.s8cup.bind('<ButtonRelease-1>', lambda e: self.stop_continuous('s8_upp'))


        self.s8aup = tk.Button(self.servo8_frame, text="+", **button_style)
        self.s8aup.place(x=12, y=70, anchor="center")
        self.s8aup.bind('<ButtonPress-1>', lambda e: self.start_continuous('s8_up'))
        self.s8aup.bind('<ButtonRelease-1>', lambda e: self.stop_continuous('s8_up'))

        self.s8a1up = tk.Button(self.servo8_frame, text="1", **button_style)
        self.s8a1up.place(x=12, y=100, anchor="center")
        self.s8a1up.bind('<Button-1>', lambda e: self.s8_up1())

        self.s8ddn = tk.Button(self.servo8_frame, text="-", **button_style)
        self.s8ddn.place(x=35, y=40, anchor="center")
        self.s8ddn.bind('<ButtonPress-1>', lambda e: self.start_continuous('s8_dnn'))
        self.s8ddn.bind('<ButtonRelease-1>', lambda e: self.stop_continuous('s8_dnn'))

        self.s8bdn = tk.Button(self.servo8_frame, text="-", **button_style)
        self.s8bdn.place(x=35, y=70, anchor="center")
        self.s8bdn.bind('<ButtonPress-1>', lambda e: self.start_continuous('s8_dn'))
        self.s8bdn.bind('<ButtonRelease-1>', lambda e: self.stop_continuous('s8_dn'))

        self.s8b1dn = tk.Button(self.servo8_frame, text="1", **button_style)
        self.s8b1dn.place(x=35, y=100, anchor="center")
        self.s8b1dn.bind('<Button-1>', lambda e: self.s8_dn1())
        # check Box
        self.uses8 = tk.BooleanVar()
        cbuses8 = tk.Checkbutton(self.servo8_frame, text="Use", variable=self.uses8)
        cbuses8.place(x=24, y=130, anchor="center")

        self.getall_button = tk.Button(self.live_servos_frame, text="Manually Load Live Value All Servos from Controller", command=self.load_fill_servals)
        self.getall_button.place(x=7, y=172)

#endregion

        self.load_fill_servals()