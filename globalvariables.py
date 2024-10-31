deviceconnected = 0   # set to 1 by the serial manager when the board is found
boarddatastring = "No Controller Connected"
deviceport = 0
#servos = [0] * 8

#These are in order of storage in the sprams file
#If changed here is also needs to be changed in the PSmain file where it loads by default
global_path=''
global_project_name=''
global_parameters_file_name='sparams.ovh'
interface_version=""
interface_version_1=""
future_item=""
future_item_1=""
"""
global_path='c:/Irunner/'
global_project_name='scon1'
global_parameters_file_name='sparams.ovh'
interface_version="notimplemented"
interface_version_1="notimplemented"
future_item="notimplemented"
future_item_1="notimplemented"
"""