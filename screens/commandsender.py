import tkinter as tk
from tkinter import messagebox
import globalvariables
from globalvariables import deviceconnected
from tkinter import scrolledtext
from help_manager import HelpManager, MAIN_HELP_CONTENT, COMMAND_SENDER_HELP_CONTENT

class CommandSenderScreen(tk.Frame):
    def __init__(self, master, serial_manager, app):
        super().__init__(master)
        self.serial_manager = serial_manager
        self.app = app
        self.create_widgets()
        # Removed place(), use pack() when the screen is selected in the main app.
        self.configure(width=500, height=500)

        self.help_button = tk.Button(self, text="Help", command=self.show_help)
        self.help_button.place(x=300, y=1)

        self.label1 = tk.Label(self, text="Controller not Connected")
        self.label1.place(x=10,y=1)

        if globalvariables.deviceconnected==1:
            self.label1.config(text= f"Controller: {globalvariables.boarddatastring} on port: {globalvariables.deviceport}")
        else:
            self.label1.config(text="No Controller Connected")

    def create_widgets(self):
        # Input frame
        self.input_frame = tk.LabelFrame(self, text="Send Command - Using short commands")
        self.input_frame.place(x=10, y=40, width=440, height=90)  # Keep place for inner widgets

        # Label
        self.input_label = tk.Label(self.input_frame, text="Command:")
        self.input_label.place(x=5, y=10)

        self.input_label2 = tk.Label(self.input_frame, text="Return:")
        self.input_label2.place(x=18, y=37)

        # Entry widget
        self.input_entry = tk.Entry(self.input_frame, width=20)
        self.input_entry.place(x=75, y=10, width=60)

        # Return data
        self.input_label2 = tk.Label(self.input_frame, text="None")
        self.input_label2.place(x=75, y=37)

        # Send button
        self.submit_button = tk.Button(self.input_frame, text="Send", command=self.submit_data)
        self.submit_button.place(x=145, y=7, width=60)

    def show_help(self):
        HelpManager.show_help(self, "Command Sender Help", COMMAND_SENDER_HELP_CONTENT)

    def submit_data(self):
        input_string = self.input_entry.get()

        # Check if the input is exactly 7 ASCII characters
        if len(input_string) != 7 or not input_string.isascii():
            messagebox.showerror("Error", "Input must be exactly 7 characters.")
            return  # Exit the function if the input is invalid
        try:
            # Process the input string here
 #           print(f"Received input: {input_string}")
 #           messagebox.showinfo("Success", f"Received: {input_string}")
            x1="-O"+input_string+"H" #"-OO0F1000H"
 #           print(x1)
            success, response=self.serial_manager.send_short_command(x1)
            self.input_label2.config(text=response)

#            self.input_entry.delete(0, "end")
        except ValueError:
            messagebox.showerror("Error", "Invalid input.")
