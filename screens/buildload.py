from dbm import error

import globalvariables
import tkinter as tk
import os
from contextlib import nullcontext
from operator import truediv
from tkinter import messagebox

from globalvariables import deviceconnected
from tkinter import scrolledtext
from help_manager import HelpManager, MAIN_HELP_CONTENT, ASSEMBLER_HELP_CONTENT, ASSEMBLER_HELP_CONTENT_1

class BuildLoad(tk.Frame):
    def __init__(self, master, serial_manager, app):
        super().__init__(master)
        self.serial_manager = serial_manager
        self.app = app
        self.create_widgets()
        self.configure(width=500, height=500)
        self.report=""
#        self.path_name_entry = tk.Entry(self)
#        self.path_name_entry.insert(0,globalvariables.global_path)
#       self.project_name_entry = tk.Entry(self)
#       self.project_name_entry.insert(0,globalvariables.global_path)
        self.command=""
        self.symbol_table = {}
        self.references = {}
        self.pass_number=1

        self.help_button = tk.Button(self, text="Help", command=self.show_help)
        self.help_button.place(x=435, y=0)

        self.label1 = tk.Label(self, text="Controller not Connected")
        self.label1.place(x=10,y=1)


        if globalvariables.deviceconnected==1:
            self.label1.config(text= f"Controller: {globalvariables.boarddatastring} on port: {globalvariables.deviceport}")
        else:
            self.label1.config(text="No Controller Connected")

    def start_assemble(self):
        self.report = ""   # Clear the screen
        self.symbol_table = {}
        self.references = {}
        self.update_summary(self.report)
        for pass_number in [1, 2]:
            self.pass_number = pass_number
            xerrors = self.all_passes()
            self.report += (f"Pass {pass_number} Errors: {xerrors}\n")
            self.update_summary(self.report)
#            print(f"Pass {pass_number} Errors: {xerrors}")
            if xerrors != 0:
                self.report += (f"Assembly failed during pass {pass_number}\n")
                self.update_summary(self.report)
                self.report += (
                    f"Generated lising file: {globalvariables.global_path + globalvariables.global_project_name + '.fpass'}\n")
                self.update_summary(self.report)
#                print(f"Assembly failed during pass {pass_number}")
                return False
            if pass_number == 1:
                self.report += ("First pass successfully. Starting second pass...\n")
                self.update_summary(self.report)
 #               print("First pass completed successfully. Starting second pass...")
        self.report += ("Assembly completed successfully\n")
        self.update_summary(self.report)
 #       print("Assembly completed successfully")
#now reconfigure the optput
        self.generate_hex_flash_file()
#        print("done")
        return True

    def generate_hex_flash_file(self):
        with open(globalvariables.global_path+globalvariables.global_project_name+'.hex', 'r') as hex_file:
            hex_content = hex_file.readlines()

        data_dict = {}
        for line in hex_content:
            parts = line.strip().split(' ')
            if len(parts) == 2:
                address, content = parts
                data_dict[int(address, 16)] = content

        # Sort data by address
        sorted_data = sorted(data_dict.items())

        # Reconfigure data into pages
        pages = {}
        for address, content in sorted_data:
            page_number = address // 16
            element_in_page = address % 16
            if page_number not in pages:
                pages[page_number] = ['F' * 32] * 16
            pages[page_number][element_in_page] = content.ljust(32, 'F')

        # Write reconfigured data to new file
        with open(globalvariables.global_path+globalvariables.global_project_name+'.fhex', 'w') as new_hex_file:
            for page_num in sorted(pages.keys()):
                if any(element != 'F' * 32 for element in pages[page_num]):
                    page_data = ''.join(pages[page_num])
                    new_hex_file.write(f"{page_num:05d}{page_data}{'F' * 16}\n")

        self.report += (f"Generated file: {globalvariables.global_path+globalvariables.global_project_name+'.fhex'}\n")
        self.update_summary(self.report)
        self.report += (f"Generated lising file: {globalvariables.global_path+globalvariables.global_project_name+'.fpass'}\n")
        self.update_summary(self.report)

        print(f"Generated file: {globalvariables.global_path+globalvariables.global_project_name+'.fhex'}")

    def fix_up_hex(self):
        strung_out="F"*528
        page_number=0
        try:
            with open(globalvariables.global_path+globalvariables.global_project_name+'.hex', 'r') as infile, \
            open(globalvariables.global_path+globalvariables.global_project_name+'.fhex', 'w') as outfile:
                for line_num, line in enumerate(infile, 1):
                    tokens = line.strip().split()

                    if not tokens:
                        continue
                    print(line_num, tokens)
                    outfile.write(strung_out+"\n")
    # If not a valid decimal, treat it as a label


        except ValueError:
            pass
        return

    def all_passes(self):
        error_count=0
        code_address = 0
#        lone_o_type = 0 # this is a valid line indicator to be used to determine if strungout
        errors=[]
        tokens=[]
#element is 1 16 byte block of flash memory, used for either an instruction, a position or special data.
#flash page = 16 Elements of 16 bytes = 256 total bytes even though the actual flash page is 264 bytes 256-264 are unused
        strung_out="FF"*269 #flash write buffer = 5 address definers plus 264 data bytes of which 256 are used
        element_counter=0 # element flash write line counter
#writing flash page consists of using R16 Write Flash page
#reading a flash page uses R15
        so_vl_counter=0 #counter for valid lines inside strunt_out

        try:
            with open(globalvariables.global_path+globalvariables.global_project_name+'.txt', 'r') as infile,\
            open(globalvariables.global_path+globalvariables.global_project_name+'.fpass', 'w') as outfile,\
            open(globalvariables.global_path+globalvariables.global_project_name+'.hex', 'w') as writefile:
#            open(globalvariables.global_path+globalvariables.global_project_name+'.lst', 'w') as listfile:
                address = 0
                for line_num, line in enumerate(infile, 1):
                    tokens = line.strip().split()
                    if not tokens:
                        continue

                    # Start of pacing check for remark
                    if tokens[0].startswith('/'):
                        if len(tokens) > 0:
                            outfile.write(f"{line_num} {line}\n")
                            # No bump in line no

                    elif tokens[0].lower() == 'move':
                        if len(tokens) <= 1:
                            outfile.write(f"{line_num} {code_address:04X} Move: ERROR Insufficient arguments\n")
                            error_count += 1
                        else:
                            target = tokens[1]
                            if self.pass_number == 1:
                                outfile.write(f"{line_num} {code_address:04X} Move {target}\n")
                            else:  # pass_number == 2
                                try:
                                    # Check if the target is a valid decimal address
                                    explicit_address = int(target)  # Parse as decimal
                                    if 0 <= explicit_address <= 32000:
                                        success, philcode=self.super_simple_phil('00',explicit_address,None)
                                        success, philcode=self.super_simple_rate(tokens,philcode)
                                        #Handle the speed / rate specifications if any
                                        if success:
                                            outfile.write(f"{line_num} {code_address:04X} Move: {target} {explicit_address:04X}\n")
                                            writefile.write(f"{code_address:04x} {philcode}\n")
                                        else:
                                            outfile.write(f"{line_num} {code_address:04X} Move: ERROR {philcode}\n")
                                            error_count += 1
                                    else:
                                        outfile.write(
                                            f"{line_num} {code_address:04X} Move: ERROR Address out of range (0-32000)\n")
                                        error_count += 1

                                except ValueError:
                                    # If not a valid decimal, treat it as a label
                                    if target in self.symbol_table:
                                        label_address = self.symbol_table[target]
                                        if 0 <= label_address <= 32000:
                                            outfile.write(
                                                f"{line_num} {code_address:04X} Move: {target} {label_address:04X}\n")
                                        else:
                                            outfile.write(
                                                f"{line_num} {code_address:04X} Move: ERROR Label address out of range (0-32000)\n")
                                            error_count += 1
                                    else:
                                        outfile.write(
                                            f"{line_num} {code_address:04X} Move: {target} ERROR Label not found\n")
                                        error_count += 1
                        code_address += 1

                    elif tokens[0].lower() == 'if':   #if input 32h
                        if len(tokens) < 3:
                            outfile.write(f"{line_num} {code_address:04X} If: ERROR Insufficient arguments\n")
                            error_count += 1
                        else:
                            if tokens[1].lower() == 'input':  # Only current value to input from
                                try:
                                    success, ifin_test, dest_is_label = self.interrogate_ifin(tokens, '32')
                                    if success:
                                        if self.pass_number==2 and dest_is_label== True:
                                            if tokens[4] in self.symbol_table:
                                                value = self.symbol_table[tokens[4]]
                                                ifin_test=ifin_test[:10]+f'{int(value):04X}'+ifin_test[14:]
                                            else:
                                                error_count +=1
                                        writefile.write(f"{code_address:04X} {ifin_test}\n")
                                        outfile.write(f"{line_num} {code_address:04X} If Input {tokens[2]} {tokens[3]} {tokens[4]}\n")
                                    else:
                                        outfile.write(f"{line_num} {code_address:04X} If Input: ERROR Invalid statement\n")
                                        error_count += 1
#                                    print(ifin_test, dest_is_label)
                                except ValueError as e:
                                    outfile.write(f"{line_num} {code_address:04X} If Input: ERROR {str(e)}\n")
                                    error_count += 1
                            else:
                                outfile.write(f"{line_num} {code_address:04X} If: ERROR Incorrect source\n")
                                error_count += 1
                        code_address += 1

                    elif tokens[0].lower() == 'output':
                        if len(tokens) < 3:
                            outfile.write(f"{line_num} {code_address:04X} Output: ERROR Insufficient arguments\n")
                            error_count += 1
                        else:
                            try:
                                value = int(tokens[1])
                                if 0 <= value <= 255:
                                    if tokens[2].lower() == 'on':
                                        opcode = '40'
                                    elif tokens[2].lower() == 'off':
                                        opcode = '41'
                                    else:
                                        raise ValueError("Invalid on/off specifier")
                                    success, philcode = self.super_simple_phil(opcode, value, None )
                                    outfile.write(f"{line_num} {code_address:04X} Output {value:03d} {opcode}\n")
                                    writefile.write(f"{code_address:04X} {philcode}\n")
                                else:
                                    raise ValueError("Value out of range")
                            except ValueError as e:
                                outfile.write(f"{line_num} {code_address:04X} Output: ERROR {str(e)}\n")
                                error_count += 1
                        code_address += 1

                    elif tokens[0].lower() == 'do':
                        if len(tokens) <= 1:
                            outfile.write(f"{line_num} {code_address:04X} Do: ERROR Insufficient arguments\n")
                            error_count += 1
                        else:
                            try:
                                value = int(tokens[1])
                                if 0 <= value <= 32000:
                                    success,philcode=self.super_simple_phil('1E',value,None)
                                    outfile.write(f"{line_num} {code_address:04X} Do {tokens[1]}\n")
                                    writefile.write(f"{code_address:04x} {philcode}\n")
                                else:
                                    outfile.write(f"{line_num} {code_address:04X} Do: ERROR Out of range\n")
                                    error_count+=1
                            except ValueError:
                                outfile.write(f"{line_num} {code_address:04X} Do: ERROR Not a number\n")
                                error_count+=1
                        code_address += 1

                    elif tokens[0].lower() == 'speed':
                        if len(tokens) < 2:
                            outfile.write(f"{line_num} {code_address:04X} Speed: ERROR Insufficient arguments\n")
                            error_count += 1
                        else:
                            success,ocode=self.super_snum_check(tokens)
                            if success:
                                if code_address<32000:
                                    outfile.write(f"{line_num} Warning set code address before Speed statement recommended location 32000 to 32200\n")
                                    outfile.write(f"{line_num} Warning verify/set code address after Speed. Recommended it to be last statement\n")
                                outfile.write(f"{line_num} {code_address:04X} Place Speed Values {tokens}\n")
#                                writefile.write(f"{code_address:04x} E3\n")
                                writefile.write(f"{code_address:04x} {ocode}\n")
                            else:
                                outfile.write(f"{line_num} {code_address:04X} Speed: ERROR\n")
                                error_count += 1
                        code_address += 1

                    elif tokens[0].lower() == 'position':
                        if len(tokens) < 2:
                            outfile.write(f"{line_num} {code_address:04X} Position: ERROR Insufficient arguments\n")
                            error_count += 1
                        else:
                            success,ocode=self.super_snum_check(tokens)
                            if success:
                                outfile.write(f"{line_num} {code_address:04X} Place Position Values {tokens}\n")
                                #writefile.write(f"{code_address:04x} E1\n")
                                writefile.write(f"{code_address:04x} {ocode}\n")
                            else:
                                outfile.write(f"{line_num} {code_address:04X} Position: ERROR\n")
                                error_count += 1
                        code_address += 1

                    elif tokens[0].lower() == 'goto':
                        if len(tokens) <= 1:
                            outfile.write(f"{line_num} {code_address:04X} Goto: ERROR Insufficient arguments\n")
                            error_count += 1
                        else:
                            if self.pass_number == 1:
                                outfile.write(f"{line_num} {code_address:04X} Goto {tokens[1]}\n")
                            else:
                                try:
                                    if tokens[1] in self.symbol_table:
                                        value = self.symbol_table[tokens[1]]
                                    else:
                                        value = int(tokens[1])

                                    if 0 <= value <= 32000:
                                        success, philcode = self.super_simple_phil('0A', value, None)
                                        if success:
                                            outfile.write(
                                                f"{line_num} {code_address:04X} Goto: {tokens[1]} {value:04X}\n")
                                            writefile.write(f"{code_address:04x} {philcode}\n")
                                        else:
                                            outfile.write(
                                                f"{line_num} {code_address:04X} Goto: ERROR Failed to generate code\n")
                                            error_count += 1
                                    else:
                                        outfile.write(f"{line_num} {code_address:04X} Goto: ERROR Out of range\n")
                                        error_count += 1
                                except ValueError:
                                    outfile.write(
                                        f"{line_num} {code_address:04X} Goto: ERROR Not a number or valid label\n")
                                    error_count += 1
                        code_address += 1

                    elif tokens[0].lower() == 'gosub':
                        if len(tokens) <= 1:
                            outfile.write(f"{line_num} {code_address:04X} Gosub: ERROR Insufficient arguments\n")
                            error_count += 1
                        else:
                            if self.pass_number == 1:
                                outfile.write(f"{line_num} {code_address:04X} Gosub {tokens[1]}\n")
                            else:
                                try:
                                    if tokens[1] in self.symbol_table:
                                        value = self.symbol_table[tokens[1]]
                                    else:
                                        value = int(tokens[1])

                                    if 0 <= value <= 32000:
                                        success, philcode = self.super_simple_phil('14', value, None)
                                        if success:
                                            outfile.write(
                                                f"{line_num} {code_address:04X} Gosub: {tokens[1]} {value:04X}\n")
                                            writefile.write(f"{code_address:04x} {philcode}\n")
                                        else:
                                            outfile.write(
                                                f"{line_num} {code_address:04X} Gosub: ERROR Failed to generate code\n")
                                            error_count += 1
                                    else:
                                        outfile.write(f"{line_num} {code_address:04X} Gosub: ERROR Out of range\n")
                                        error_count += 1
                                except ValueError:
                                    outfile.write(
                                        f"{line_num} {code_address:04X} Gosub: ERROR Not a number or valid label\n")
                                    error_count += 1
                        code_address += 1

                    elif tokens[0].lower() == 'return':              #'return': '22-16h',
                        if len(tokens) >= 1:
                            success, philcode=self.super_simple_phil('16',None,None)
                            outfile.write(f"{line_num} {code_address:04X} Return\n")
                            writefile.write(f"{code_address:04x} {philcode}\n")
                            code_address += 1

                    elif tokens[0].lower() == 'stop':              #'stop': '128-80h',
                        if len(tokens) >= 1:
                            success, philcode=self.super_simple_phil('80',None,None)
                            outfile.write(f"{line_num} {code_address:04X} Stop\n")
                            writefile.write(f"{code_address:04x} {philcode}\n")
                            code_address += 1

                    elif tokens[0].lower() == 'nop':              #No operation : '255-0ffh',
                        if len(tokens) >= 1:
                            success, philcode=self.super_simple_phil('FF',None,None)
                            outfile.write(f"{line_num} {code_address:04X} No Operation\n")
                            writefile.write(f"{code_address:04x} {philcode}\n")
                            code_address += 1

                    elif tokens[0].lower()=='address':
                        if len(tokens) <= 1:
                            outfile.write(f"{line_num} {"XXXX"} Address: ERROR Insufficient arguments\n")
                            error_count += 1
                        else:
                            try:
                                value = int(tokens[1])
                                if 0 <= value <= 32767:
                                    outfile.write(f"{line_num} {"XXXX"} Address: Placement to {tokens[1]}\n")
                                    code_address = value  # Set the code_address to the new value
                                    #writefile.write(f"{"E0"}{code_address:04X}\n")
                                else:
                                    outfile.write(f"{line_num} {"XXXX"} Address: ERROR Out of range\n")
                                    error_count += 1
                            except ValueError:
                                outfile.write(f"{line_num} {"XXXX"} Address: ERROR Invalid integer\n")
                                error_count += 1

                    elif tokens[0].lower() == 'wait':
                        if len(tokens) <= 1:
                            outfile.write(f"{line_num} {code_address:04X} Wait: ERROR Insufficient arguments\n")
                            error_count += 1
                        else:
                            try:
                                value = int(tokens[1])
                                if 0 <= value <= 255:
                                    success, philcode = self.super_simple_phil('28', value, None)
                                    outfile.write(f"{line_num} {code_address:04X} Wait {tokens[1]}\n")
                                    writefile.write(f"{code_address:04X} {philcode}\n")
                                    #writefile.write(f"{code_address:04x} 1E{value:02x}\n")
                                else:
                                    outfile.write(f"{line_num} {code_address:04X} Wait: ERROR Out of range\n")
                                    error_count += 1
                            except ValueError:
                                outfile.write(f"{line_num} {code_address:04X} Wait: ERROR Not a number\n")
                                error_count += 1
                        code_address += 1

                    elif tokens[0].lower() == 'loop':
                        if len(tokens) >= 1:
                            success, philcode=self.super_simple_phil('20',None,None)
                            outfile.write(f"{line_num} {code_address:04X} Loop back from Do\n")
                            writefile.write(f"{code_address:04x} {philcode}\n")
                            code_address += 1

# region servo =; +; - & DSR's
#Now handle the the set absolute and +/- variable items

                    elif (tokens[0].lower()[0] =='s' and
                         tokens[0][1].isdigit() and
                         tokens[0][2] in ('=', '+', '-')):
                        try:
                            success, hex_str_all=self.super_check(tokens)
                            if success:
                                outfile.write(f"{line_num} {code_address:04X} {tokens[0]}\n")
                                writefile.write(f"{code_address:04x} {hex_str_all}\n")
                            else:
                                outfile.write(f"{line_num} {code_address:04X} {tokens[0]} Invalid value\n")
                                error_count += 1
                        except:
                            outfile.write(f"{line_num} {code_address:04X} {tokens[0]} Error  ********\n")
                            error_count += 1
                        code_address+=1
#now the DSRs
                    elif (tokens[0].lower()[:3] =='dsr' and tokens[0][3].isdigit()):
                        try:
                            success, hex_str_all=self.super_dsr_check(tokens)
                            if success:
                                outfile.write(f"{line_num} {code_address:04X} {tokens[0]}\n")
                                writefile.write(f"{code_address:04x} {hex_str_all}\n")
                            else:
                                outfile.write(f"{line_num} {code_address:04X} {tokens[0]} Invalid value\n")
                                error_count += 1
                        except:
                            outfile.write(f"{line_num} {code_address:04X} {tokens[0]} Error  ********\n")
                            error_count += 1
                        code_address+=1
#endregion

# check for remark last check. If it is here it will become a label
                    elif not len(tokens)==0:
                        lalabel=tokens[0]
                        self.symbol_table[lalabel.lower()]=code_address
                        outfile.write(f"{line_num} {code_address:04X} {lalabel} (label)\n")
                                   #No bump in line no
                    if not tokens:
                        continue
                #writefile.write(strung_out)
                if error_count>0:
                    writefile.close()
                    os.remove(globalvariables.global_path+globalvariables.global_project_name+'.hex')

                return(error_count)

        except FileNotFoundError as e:
            error_message = f"Error: File not found - {e}\n\n"
            error_message += f"Current working directory:  {globalvariables.global_path}\n\n"  #{os.getcwd()}\n\n
            error_message += f"Attempting to access file: {globalvariables.global_project_name}"
            #messagebox.showerror("Error", error_message)
        return error_message

#    def add_to_strung_out(indata):
 #       if len(indata)>0:

# This is check and fill opcode for the variable commands
    def super_check(self, tokens):
        ocode = 'FF' * 16  # the empty (unused to be FF) write string
        opcode='FF'
        if 0 < int(tokens[0][3:]) < 65535:
            value=int(tokens[0][3:])
            hexvalue=f'{value:04X}'
            snumber='0'+tokens[0][1]
            if tokens[0][2]=='=':
                opcode='50'+snumber+hexvalue
            elif tokens[0][2]=='+':
                opcode='52'+snumber+hexvalue
            elif tokens[0][2]=='-':
                opcode='54'+snumber+hexvalue
            success = True
            ocode=opcode+ocode[8:]
        else:
            success = False
        return success, ocode

        # This is check and fill opcode for the variable commands

    def super_dsr_check(self, tokens):
        ocode = 'FF' * 16  # the empty (unused to be FF) write string
        opcode='FF'
        if 0 < int(tokens[0][5:]) < 65535:
            value = int(tokens[0][5:])
            hexvalue = f'{value:04X}'
            dsrnumber = f'{(int(tokens[0][3])+31):02X}'
            if tokens[0][4] == '=':
                opcode = '50' + dsrnumber + hexvalue
            elif tokens[0][4] == '+':
                opcode = '52' + dsrnumber + hexvalue
            elif tokens[0][4] == '-':
                opcode = '54' + dsrnumber + hexvalue
            success = True
            ocode=opcode+ocode[8:]
        else:
            success = False
        return success, ocode

    def super_snum_check(self, tokens):
        success=False
        ocode='FF'*16 # the empty (unused to be FF) write string
        for token in tokens:
            l_token=token.lower()
            if (l_token.startswith('s') and
                len(l_token) >= 4 and
                l_token[1].isdigit() and
                l_token[2] == '=' and
                1 <= int(l_token[1]) <= 8 and
                l_token[3:].isdigit()):
                servo_num = int(l_token[1])
                placement = (servo_num - 1) * 4
                hex_value = f'{int(l_token[3:]):04X}'
                ocode=(ocode[:placement]+hex_value+ocode[placement+4:])
                success = True
        return success, ocode

    def super_simple_phil(self, opcode, data4h=None, data2h=None):
        ocode = 'FF' * 16  # Initialize with all 'F's
        # Ensure opcode is a valid 2-digit hex string
        if len(opcode) != 2 or not all(c in '0123456789ABCDEFabcdef' for c in opcode):
            return False, ocode  # Return failure if opcode is invalid
        opcode = opcode.upper()  # Convert to uppercase for consistency
        try:
            if data2h is not None:
                data1 = f'{int(data2h):02X}'
            else:
                data1 = 'FF'
            if data4h is not None:
                data2 = f'{int(data4h):04X}'
            else:
                data2 = 'FFFF'
            ocode = opcode + data1 + data2 + ocode[8:]
            return True, ocode
        except ValueError:
            return False, ocode

    def super_simple_rate(self, tokens, philcode):
        rate_found = False
        for token in tokens:
            token = token.lower()
            if token.startswith("rate="):
                rate_found = True
                rate_value = token[5:]
                if rate_value == "dsr1":
                    philcode = philcode[:8] + "02" + philcode[10:]
                elif rate_value == "dsr2":
                    philcode = philcode[:8] + "03" + philcode[10:]
                elif rate_value == "dsr3":
                    philcode = philcode[:8] + "04" + philcode[10:]
                else:
                    try:
                        numeric_value = int(rate_value)
                        if 0 <= numeric_value <= 65535:
                            philcode = philcode[:8] + f"{numeric_value:04X}" + philcode[12:]
                        else:
                            return False, "RATE value out of range (0-65535)"
                    except ValueError:
                        return False, "Invalid RATE value"
                break  # Exit the loop after processing the first RATE token

        if not rate_found:
            # Default to DSR1 if no RATE is specified
            philcode = philcode[:8] + "02" + philcode[10:]

        return True, philcode

    def interrogate_ifin(self, tokens, opcode):
        success = False
        destination='FFFF'
        ocode = 'FF' * 16

        # Check if we have enough tokens
        if len(tokens) < 5:
            return False, ocode, False

        # Check the format of the third token (index 2)
        if '=' not in tokens[2]:
            return False, ocode, False

        insel_str, compsel_str = tokens[2].split('=')

        # Check if insel is a single digit
        if not insel_str.isdigit() or len(insel_str) != 1:
            return False, ocode, False

        insel = int(insel_str)

        # Check if compsel is a valid integer between 0 and 65535
        try:
            compsel = int(compsel_str)
            if not 0 <= compsel <= 32767:
                return False, ocode, ''
        except ValueError:
            return False, ocode, False

        # Check the command (fourth token, index 3)
        command_map = {'goto': '0A', 'gosub': '14', 'stop': '80'}
        command = command_map.get(tokens[3].lower())
        if not command:
            return False, ocode, False

        if tokens[4].isdigit():
            dest=int(tokens[4])
            if not 0 <= dest <= 65535:
                return False, ocode, False
            destination = f'{int(tokens[4]):04X}'
            dest_is_label = False
        else:
            dest_is_label=True
        ocode = opcode + f'{insel:02X}' + f'{compsel:04X}' + command + destination + ocode[:18]
        return True, ocode, dest_is_label

    def update_summary(self, text):
        self.asmbl_report.config(state=tk.NORMAL)  # Allow editing
        self.asmbl_report.delete('1.0', tk.END)  # Clear existing text
        self.asmbl_report.insert(tk.END, text)  # Insert new text
        self.asmbl_report.config(state=tk.DISABLED)  # Make it read-only again

    def get_write(self):
        #   def get_default_stuff(self):
        try:
            with open('c:/Irunner/sparams.ovh', 'r') as f:
                tokens = [line.strip() for line in f]
            globalvariables.global_path = tokens[0]
            globalvariables.global_project_name = tokens[1]
            with open('c:/Irunner/sparams.ovh', 'w') as f:
                tokens[0]=self.path_name_entry.get()
                tokens[1]=self.project_name_entry.get()
                for token in tokens:
                    f.write(token+'\n')
#read them back
            with open('c:/Irunner/sparams.ovh', 'r') as f:
                tokens = [line.strip() for line in f]
            globalvariables.global_path = tokens[0]
            self.path_name_entry.delete(0, tk.END)
            self.path_name_entry.insert(0, globalvariables.global_path)
            globalvariables.global_project_name = tokens[1]
            self.project_name_entry.delete(0, tk.END)
            self.project_name_entry.insert(0, globalvariables.global_project_name)
#            self.asmbl_report="Updated"
            self.update_summary("Saved")
        except Exception as e:
            print(f"Error {e}")
        return

    def read_pagef(self):
        try:
            #get the page number from the user
            pagenu = f"{int(self.page_number_entry.get()):05d}"
            # Check if page number is within valid range
            if not 0 <= int(pagenu) <= 2048:
                raise ValueError
            comsend1 = "$OV0R14"+pagenu+"**************************************************OV~"
            #Note on original version controllers, the first
            success, response = self.serial_manager.send_long_receive_528(comsend1)
            if not success:
               raise ConnectionError
            elements = self.get_elements_from_pg(response)
            self.report=""
            self.report+= f'Elements in Page {pagenu} \n'
            for i in range(len(elements)):
                self.report += (elements[i]+'\n')
                self.update_summary(self.report)
        except ConnectionError:
            self.report = "Controller not ready or communication error"
            self.update_summary(self.report)
        except ValueError:
            self.report = "Page number must be between 0 and 2048"
            self.update_summary(self.report)

    @staticmethod
    def get_elements_from_pg(indat):
        return [indat[i:i + 32] for i in range(0, len(indat), 32)]

    def write_pagef(self):
        self.report = ""
        self.update_summary(self.report)
        file_path = os.path.join(globalvariables.global_path, f"{globalvariables.global_project_name}.fhex")
        try:
            with open(file_path, 'r') as infile:
                for line_number, line in enumerate(infile, 1):
                    # Remove newline character and any leading/trailing whitespace
                    line = line.strip()
                    page_number = line[:5]
                    status, response = self.serial_manager.write_528_byte_fpage(line)
                    if status:
                        self.report += f"Successfully wrote page {page_number}\n"
                    else:
                        self.report += f"Error writing page from line {line_number}: {response}\n"
                    self.update_summary(self.report)
                self.report += "Finished writing all pages\n"
                self.update_summary(self.report)
        except FileNotFoundError:
            self.report += f"Error: File not found - {file_path}\n"
            self.update_summary(self.report)
        except IOError as e:
            self.report += f"Error reading file: {e}\n"
            self.update_summary(self.report)
        except Exception as e:
            self.report += f"An unexpected error occurred: {e}\n"
            self.update_summary(self.report)

    def create_widgets(self):
        # File management frame
        self.input_frame = tk.LabelFrame(self, text="File Information")
        self.input_frame.place(x=10, y=40, width=305, height=175)  # Keep place for inner widgets
        self.fpath_frame = tk.LabelFrame(self.input_frame, text="Path")
        self.fpath_frame.place(x=5, y=5, width=290, height=55)  # Keep place for inner widgets
        self.path_name_entry = tk.Entry(self.fpath_frame, width=45,)
        self.path_name_entry.insert(0,globalvariables.global_path)
        self.path_name_entry.place(x=5, y=2, height=25)  # Adjust x and y as needed
        self.fproject_frame = tk.LabelFrame(self.input_frame, text="Project Name")
        self.fproject_frame.place(x=5, y=60, width=290, height=55)  # Keep place for inner widgets
        self.project_name_entry = tk.Entry(self.fproject_frame, width=45)
        self.project_name_entry.insert(0,globalvariables.global_project_name)
        self.project_name_entry.place(x=5, y=2, height=25)  # Adjust x and y as needed
        self.save_both_button = tk.Button(self.input_frame, text="Save/Change", command=self.get_write)
        self.save_both_button.place(x=195, y=120, width=100)
        self.help_button1 = tk.Button(self.input_frame, text="Project, File, Path Help", command=self.show_help_1)
        self.help_button1.place(x=5, y=120)


        # Build functions frame
        self.build_frame = tk.LabelFrame(self, text="Assemble / Build Control")
        self.build_frame.place(x=323, y=40, width=165, height=175)  # Keep place for inner widgets

        self.build_button = tk.Button(self.build_frame, text="Build Project", command=self.start_assemble)
        self.build_button.place(x=5, y=8, width=100)

        self.write_controller_button = tk.Button(self.build_frame, text="Write Controller", command=self.write_pagef)
        self.write_controller_button.place(x=5, y=42, width=100)

        self.read_frame = tk.LabelFrame(self.build_frame, text="Read Controller Page")
        self.read_frame.place(x=4, y=72, width=155, height=75)  # Keep place for inner widgets

        self.read_controller_mem_page_button = tk.Button(self.read_frame, text="Read", command=self.read_pagef)
        self.read_controller_mem_page_button.place(x=100, y=10, width=40, height=40)

        self.read_frame = tk.LabelFrame(self.read_frame, text="Page #")
        self.read_frame.place(x=4, y=2, width=90, height=50)  # Keep place for inner widgets
        self.page_number_entry = tk.Entry(self.read_frame, width=10)
        self.page_number_entry.insert(0,0)
        self.page_number_entry.place(x=5, y=2, height=22)  # Adjust x and y as needed

        #Output frame
        self.build_frame = tk.LabelFrame(self, text="Report / Output")
        self.build_frame.place(x=10, y=225, width=478, height=210)  # Keep place for inner widgets
        self.asmbl_report =tk.Text(self.build_frame, wrap=tk.WORD, width=57, height=11)
        self.asmbl_report.place(x=5, y=5)
        self.asmbl_report.config(state=tk.DISABLED)

    allowed_variables = set()  # You can add allowed variables here if needed

    def show_help(self):
        HelpManager.show_help(self, "Command Sender Help", ASSEMBLER_HELP_CONTENT)

    def show_help_1(self):
        HelpManager.show_help(self, "Command Sender Help", ASSEMBLER_HELP_CONTENT_1)
