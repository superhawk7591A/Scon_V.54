import os
import serial
import serial.tools
import tkinter as tk
from screens.controllerparams import ControllerParameters
from screens.commandsender import CommandSenderScreen
from serialmanager import SerialPortManager
from screens.mainscreen import MainScreen
from screens.positionmanager import PositionManager
from screens.buildload import BuildLoad

#from globalvariables import deviceconnected
import globalvariables

class MyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PScon Servo Controller V")
        self.root.iconbitmap("C:/Users/Orwill/PycharmProjects/SconV.54/screens/Icon1.ICO")
        self.root.geometry('500x500')
        self.root.resizable(False, False)

        # Create a frame for the title
        self.title_frame = tk.Frame(root)
        self.title_frame.pack(side="top", fill="x")
        self.title_label = tk.Label(self.title_frame, text="", font=("Arial", 12, "bold"))
        self.title_label.pack(pady=5)  # Add some vertical padding

        self.watchdog_timer = None

        menubar = tk.Menu()
        root.config(menu=menubar)

        menubar.add_command(label="Main Control", command=self.show_main_screen)


        main_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Script", menu=main_menu)
        main_menu.add_command(label="Position Manager", command=self.show_position_manager_screen)
        main_menu.add_command(label="Build Script", command=self.show_buildload_screen)


        utilities_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Utilities", menu=utilities_menu)
        utilities_menu.add_command(label="Controller Parameters", command=self.show_controller_parameters_screen)
        utilities_menu.add_command(label="Send Manual Command", command=self.show_command_sender_screen)


        # Add Reconnect Device directly to the menubar
        menubar.add_command(label="Connect Controller", command=self.reconnect_device)

        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

        # Initialize the serial port manager
        self.serial_manager = SerialPortManager()
        #Find the controller and get its info
        self.serial_manager.find_device_port()

        # Initialize screens with a reference to `self`
        self.main_screen = MainScreen(self.root, self.serial_manager, self)
        self.command_sender_screen = CommandSenderScreen(self.root, self.serial_manager, self)
        self.position_manager = PositionManager(self.root, self.serial_manager, self)
        self.controller_parameters = ControllerParameters(self.root, self.serial_manager, self)
        self.buildload = BuildLoad(self.root, self.serial_manager, self)

        self.start_watchdog()

        # Hide all screens initially
        self.hide_all_screens()

        # Start with the main screen or navigation screen
        self.show_main_screen()

    def start_watchdog(self):
        self.watchdog_timer = self.root.after(5000, self.on_watchdog_timeout)

    def on_watchdog_timeout(self):
#        print("Watchdog timeout occurred")
        # Handle the timeout (e.g., check connection, attempt reconnect)
        if not self.serial_manager.is_port_accessible():
            globalvariables.deviceconnected=0 #self.update_connection_status(False)
            globalvariables.boarddatastring="No Controller Connected"
            globalvariables.deviceport = "None"
        self.update_ui()
        # Restart the watchdog
        if self.watchdog_timer:
            self.root.after_cancel(self.watchdog_timer)
        self.watchdog_timer = self.root.after(5000, self.on_watchdog_timeout)

    def update_ui(self):
        self.main_screen.label1.config(text=f"Controller: {globalvariables.boarddatastring} on port: {globalvariables.deviceport}")
        self.command_sender_screen.label1.config(text=f"Controller: {globalvariables.boarddatastring} on port: {globalvariables.deviceport}")
        self.position_manager.label1.config(text=f"Controller: {globalvariables.boarddatastring} on port: {globalvariables.deviceport}")
        self.controller_parameters.label1.config(text=f"Controller: {globalvariables.boarddatastring} on port: {globalvariables.deviceport}")
        self.buildload.label1.config(text=f"Controller: {globalvariables.boarddatastring} on port: {globalvariables.deviceport}")

    def show_main_screen(self):
        #        self.flash_screen.pack_forget()  # Hide the flash screen
        self.title_label.config(text="Main Control")
        self.hide_all_screens()
        self.main_screen.pack()  # Show the main screen

    def show_command_sender_screen(self):
        self.hide_all_screens()
        self.title_label.config(text="Send Manual Command")
        self.command_sender_screen.pack()  # Show the flash screen

    def show_position_manager_screen(self):
        self.hide_all_screens()
        self.title_label.config(text="Position Manager")
        self.position_manager.pack()  # Show the position manager

    def show_controller_parameters_screen(self):
        self.hide_all_screens()
        self.title_label.config(text="Controller Parameters")
        self.controller_parameters.pack()  # Show the position manager

    def show_buildload_screen(self):
        self.hide_all_screens()
        self.title_label.config(text="Build and Load Sconscript File")
        self.buildload.pack()  # Show the position manager

    #Hide forget all screens
    def hide_all_screens(self):
        self.main_screen.pack_forget()
        self.command_sender_screen.pack_forget()
        self.position_manager.pack_forget()
        self.controller_parameters.pack_forget()
        self.buildload.pack_forget()

    def on_close(self):
        print(globalvariables.deviceport)
        print(globalvariables.boarddatastring)
        #        print({self.serial_manager.port})
        self.serial_manager.close_port()
        self.root.destroy()

    def show_about(self):
        about_window = tk.Toplevel(self.root)
        about_window.title("About PScon Servo Controller")
        about_window.geometry("300x250")

        about_text = """
        PScon Servo Control Software
        Version 2.24
    
        2005 - 2024
        www.sconcon.com
    
        For use with
        Scon servo controllers
        014, 017, 018, 019, 020, 021, 022
        Firmware versions to 1082
        """

        label = tk.Label(about_window, text=about_text, justify=tk.CENTER, padx=10, pady=10)
        label.pack(expand=True, fill=tk.BOTH)

        ok_button = tk.Button(about_window, text="OK", justify=tk.CENTER, command=about_window.destroy)
        ok_button.pack(pady=10)

    #102624 Adding reconnect capability
    def reconnect_device(self):
        self.serial_manager.close_port()  # Close the current connection if any
        success = self.serial_manager.find_device_port()
        if success:
            #       messagebox.showinfo("Connection Success", f"Connected to {globalvariables.deviceport}")
            self.update_connection_status()
        else:
            globalvariables.boarddatastring ="Connection Error", "Device not found"

    def update_connection_status(self):
        for screen in [self.main_screen, self.command_sender_screen,
                       self.position_manager, self.controller_parameters, self.buildload]:
            if hasattr(screen, 'label1'):
                if globalvariables.deviceconnected == 1:
                    screen.label1.config(
                        text=f"Controller: {globalvariables.boarddatastring} on port: {globalvariables.deviceport}")
                else:
                    screen.label1.config(text="No Controller Connected")

        #end102424 Adf

def get_defaults():
    #   Get or create defaults
    try:
        if not os.path.exists('c:/Irunner/sparams.ovh'):
            with open('c:/Irunner/sparams.ovh', 'w') as f:
                f.write('c:/Irunner' + '\n')
                f.write('scon1\n')
                f.write('sparams.ovh\n')
                f.write('notimplemented\n')
                f.write('notimplemented\n')
                f.write('notimplemented\n')
                f.write('notimplemented\n')
        #            return
        with open('c:/Irunner/sparams.ovh', 'r') as f:
            tokens = [line.strip() for line in f]

        globalvariables.global_path = tokens[0]
        globalvariables.global_project_name = tokens[1]
        globalvariables.interface_version = tokens[3]
        globalvariables.interface_version_1 = tokens[4]
        globalvariables.future_item = tokens[5]
        globalvariables.future_item_1 = tokens[6]
        return

    except Exception as e:
        print(f"Error {e}")
    return

def main():
    root = tk.Tk()
    get_defaults()
    app = MyApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
