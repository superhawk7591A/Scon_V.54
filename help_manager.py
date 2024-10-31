import tkinter as tk
from tkinter import scrolledtext


class HelpManager:
    @staticmethod
    def show_help(parent, title, content):
        help_window = tk.Toplevel(parent)
        help_window.title(title)
        help_window.geometry("600x600")

        # Create a frame to contain the widgets
        frame = tk.Frame(help_window)
        frame.place(x=0, y=0, relwidth=1, relheight=1)

        # Add the scrolled text widget
        help_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD)
        help_text.place(x=10, y=10, relwidth=0.95, relheight=0.8)

        help_text.insert(tk.END, content)
        help_text.config(state='disabled')  # Make text read-only

        # Add a close button
        close_button = tk.Button(frame, text="Close", command=help_window.destroy)
        close_button.place(relx=0.5, rely=0.9, anchor='center')


# Define some standard help content
MAIN_HELP_CONTENT = """
PScon is used to setup and control Scon servo controllers including enabling servos, setting parameters, speed and position information. Scon programs are written with a text editor such as notepad. PScon is then used to build the text into a sconscript file, and download it to the Scon empowered controller.

When a controller is connected, the Main Control screen will show the version and connection. The Run Controls can be used to activate the controller.

The Run / Resume button causes the program to start at line 0 if it is in the stop mode, if the program was pausedm, The Run / Resume button will restart it where it was stipped.

The Stop Button stops the program and resets the active line number

Pause causes the controller to stop running but save the current position.

If a program line number is placed in the Run at line No. box, and the Run button is pressed, the program wil start at that line. The line number can be located in the name.fpass file in the second column.

 
"""
# Define some standard help content


POSITION_MANAGER_HELP_CONTENT = """
Most of these functions require a connected controller.

Scon movements are accomplished by a "move to position" system. Positions are stored in memory, and movemements are created by using a sconscript program that causes the system to move the servos to new positions. 

The speed of movement to the new position is controlled by the rate specification in the Sconscript program or the controllers default rate. 

This screen can be used to:
- Manually move the servos to desired positions, and store the position in the controller memory.
 
- Read the position memory and actuate the servos accordingly.

Controls:
Get Address at Address box:
- Input/Display box: Displays the current address. An address can be placed in this box manually and will be accepted and the controller location read when the Enter Address button is selected. Data is displayed in the Position Memory Servo Values (display only) area.

- Bump Address button increments the address by 1 and retrieves the memory. 
 
- Dec Address button decrements the address by 1 and retrieves the memory. 
 
- Get & Move to Live with yellow as a warning. Causes the servos to move to the values from the selected memory location. Use caution. 

Write Positions to Controller Memory area - Important: Read the information regarding the Use check box in the Live Servos Area 
- Write Position button stores the servos from the "Live Servo Values" area into the specified location, then retrieves the information from the controller and displays it in the Position Memory Servo Values (display only) area.

- Write & bump Pos button performs the same action as the Write Position button, however it then increments the address by 1, so that faster entry can be made.

Live Servo Values area
These controls allow the servos to be manually moved to the required positions. Once the servos are in the desired positions, the values can be stored in a single memory location (or Element). Moving between these positions is how Sconscript causes movements.

Servo1 (or any servo) contains a display box, 6 buttons and a check box. The box for each servo does not accept input  

- The buttons cause servo movement, to expedite movements, the top pair of buttons cause faster movement than the middle pair of buttons. The bottom pair make single numeric changes.

- Once all 8 (or as many as the user is using) are at the desired values, the values are stored as detailed above.

- "Use" Check Box. There may be instances in which a user is using, for example 4 servos, but needs to make a movement that does not cause one or more servos to change. To accommodate this, the movement system ignore values of 65535. 
  If the check box is selected, 65535 will be written into the location for that specific servo and it will be ignored.     
  By Default, the first 4 check boxes are selected, check or uncheck as desired. It is best to uncheck un-used servos. 

"""
CONTROLLER_PARAMETERS_HELP_CONTENT = """
Controller parameters are stored in controller memory. This screen is used to read and change the parameters. 

Clicking “Get Parameters” will re-load the parameters from the connected controller. Once the parameters have been read from the controller, the Save Parameters button will become active and any changes can be saved.

In the  Active Servos box, check the box for each servo that is to be used. All servos will receive a pulse and may be directly controlled; however, the Sconscript program will only update and move the servos that are checked as “Active Servos”. If a servo is selected and not present, movement information will be generated for that servo, this can take time to complete and may cause the user to believe the system is not working properly. For this reason, it is best to un-check the non-present servos in the Active Servos box. 

“Report Controls” should normally be checked. This causes the controller to generate reports that are read by PScon for display on the Main Control as Line number etc. This can be turned off to allow the controller to have more processing resources. The default value of 8 in the “Report Rate” box will cause data to be sent several times per second. 

Run Controls selects the Start/Stop control method. PScon is always able to control the device. If “Run on Power up” is selected, the controller will execute Run at line 0 as soon as power is applied. If “Push Button Control” is selected, the on-board push-button will toggle between run and stop. If “Hardware Control” is selected, Input 1 will start the board and Input 2 will stop the board. Line 0 is the start point for hardware and pushbutton control. Note: any combination of controls may be selected.

The Pulse Width Limits section limits the minimum and maximum pulse width that the controller will generate. This is to protect the hardware and servos. Select the “Use limit controls” box to enable pulse limits. The values are in 10,000 microsecond units. Recommended defaults are 22500 (2.25 Milliseconds) for maximum and 9000 (.9 Milliseconds) for minimum. The same pulse limits apply to all servos.

If a controller has the LCP or Flex I/O connection, it can be configured for use as an Input 4 by selecting Use LCP as Input. This connection does not have any pull down resistors or protection. 

Once all parameters have been set, click “Store Parameters”, this will store the values into the controllers eeprom memory. The controller will continue to run with the old values until the power is cycled.

NOTE: If memory value become damaged or corrupted the controller can be reset to factory defaults. This is discussed in the Scon product manual and is normally accomplished by holding down the on-board pushbutton while the board is powered up.  

Flash memory

When a Scon file is downloaded, the onboard flash memory is overwritten with the new data. Only the elements that are used in the new program will be written. This allows downloading small sections while leaving blocks of subroutines in memory. This may be desirable due to the required flash load time on large programs. 

The entire flash memory may be erased if desired, this includes position memory and scripts. Click the I am sure check box, and the Erase Memory button will become active. Clicking this will erase the entire flash memory.
"""




COMMAND_SENDER_HELP_CONTENT = """
This screen can send a command manually. Scon controllers send and receive several command types. The screen is used to manually send Short commands. This can be used for testing purposes.

Short commands consist of 7 bytes in hexadecimal plus the setup and trailing characters. It is only necessary to include the 7 command bytes since the command send utility adds the other characters. 
- The First byte is the command, followed by 6 bytes of data.  
- Depending upon the command, the meaning of the 6 bytes can vary.

Command O, (O not zero) (Output) Example "O0F1000" (O for Output, followed by 0F (Zero then F) for Output 15, then 1, for the On State, followed by 000 (3 zeros to complete 6 bytes, will activate out 15, normally the onboard LED indicator.  
- Changing the State to zero will turn off Output 15.

Command V (value) - V followed by 4 hexadecimal digits to express the pulse width, followed by two hexadecimal digits for the servo number
- Sets a single servo output to a specific value. The value is expressed in 0.1 microseconds, which means that 15,000 is 1.5ms sets the typical center position.
- To set this value for Servo #1, send V3A9801

Command U (UP/Increase value) - U followed by 4 hexadecimal digits to express the increase in pulse width, followed by two hexadecimal digits for the servo number
- Increases the pulse width value for a single servo. The value and increase are expressed in 0.1 microsecond increments.
- To increase the value for Servo #1 by 250us (.25ms), send U09C401  Note 09C4hex equals 2,500

Command D (Down/Decrease value) - D followed by 4 hexadecimal digits to express the decrease in pulse width, followed by two hexadecimal digits for the servo number
- Decreases the pulse width value for a single servo. The value and decrease are expressed in 0.1 microsecond increments.
- To increase the value for Servo #1 by 250us (.25ms), send U09C401  Note 09C4hex equals 2,500

Commands G and C (Goto and GoSub) 

"""
ASSEMBLER_HELP_CONTENT = """
NEEDS UPDATNG
Most Scon controllers utilize two types of command sequences. Short commands and long commands.
It is important to note that some controllers may utilize different types of commands than listed here.

Note: The return includes the leading O and trailing H that are automatically sent 

Short commands consist of 7 bytes in hexadecimal plus the setup and trailing characters. It is only necessary to include the 7 command bytes since the command send utility adds the other characters. 
- The First byte is the command, followed by 6 bytes of data.  
- Depending upon the command, the meaning of the 6 bytes can vary.

Command O (Output) Example "O0F1000" (O for Output not zero, followed by 0F (Zero then F) for Output 15, then 1, for the On State, followed by 000 (3 zeros to complete 6 bytes, will activate out 15, normally the onboard LED indicator.  
- Changing the State to zero will turn off Output 15.

Command V (value) - V followed by 4 hexadecimal digits to express the pulse width, followed by two hexadecimal digits for the servo number
- Sets a single servo output to a specific value. The value is expressed in 0.1 microseconds, which means that 15,000 is 1.5ms sets the typical center position.
- To set this value for Servo #1, send V3A9801

Command U (UP/Increase value) - U followed by 4 hexadecimal digits to express the increase in pulse width, followed by two hexadecimal digits for the servo number
- Increases the pulse width value for a single servo. The value and increase are expressed in 0.1 microsecond increments.
- To increase the value for Servo #1 by 250us (.25ms), send U09C401  Note 09C4hex equals 2,500

Command D (Down/Decrease value) - D followed by 4 hexadecimal digits to express the decrease in pulse width, followed by two hexadecimal digits for the servo number
- Decreases the pulse width value for a single servo. The value and decrease are expressed in 0.1 microsecond increments.
- To increase the value for Servo #1 by 250us (.25ms), send U09C401  Note 09C4hex equals 2,500

Commands G and C (Goto and GoSub) 

"""

ASSEMBLER_HELP_CONTENT_1 ="""Files are located in Path (set as desired) and titled Project Name (set as desired). The default directory and file names are included. 
Example: Path: c:/Irunner/; Project name: scon1; Source file is scon1.txt (C:/Irunner/scon1.txt)
Path and source file must exist prior to running the build.
Use forward slashes / not back slashes \\\ in path names for compatibility  
 
Source file = Project Name.txt
List file = Project Name.lst
First Pass = Project Name.fpass
Hex output = Project Name.hex

Important note: Comas are not allowed in the source file and will result in errors and/or erroneous actions.

All files are text files that can be viewed in Notepad or similar editors.
Source file can be created in a text editor such as Notepad. If edited or created in another editor, it must be saved as a standard text file with no special characters or formatting.
"""



# Test the HelpManager
if __name__ == "__main__":
    root = tk.Tk()
    test_button = tk.Button(root, text="Test Help",
                            command=lambda: HelpManager.show_help(root, "Test Help", MAIN_HELP_CONTENT))
    test_button.place(relx=0.5, rely=0.5, anchor='center')
    root.geometry("200x200")
    root.mainloop()