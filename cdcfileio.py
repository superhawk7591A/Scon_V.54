import os

def write_fixed_length_records(file_path, records, field_lengths):
    with open(file_path, 'wb') as file:
        for record in records:
            for field, length in zip(record, field_lengths):
                # Pad or truncate field to the specified length
                field_data = record[field].ljust(length, '\x00').encode('utf-8')
                file.write(field_data)

def create_default_file(directory='C:/Irunner', filename='scparams.ovh'):
    """Create the file with default content if it doesn't exist."""
    file_path = os.path.join(directory, filename)

    # Define fixed-length records and field lengths
    records = [
        {'Name': 'PScon Version 7.1'},
        {'Parameters': r'00057600n81'+'0000000000'},
        {'Parametersfilepath': r'c:\Irunner\scparams.ovh'},
        {'TempFlashfilepath': r'c:\Irunner\flash.tmp'},
        {'TempFlashfilepath': r'c:\Irunner\flash.tmp'},
        {'Sconfilelocation': r'c:\Irunner\scon.txt'},
        {'Listfilelocation': r'c:\Irunner\scon.txt'},
        {'Flashdatafilelocation': r'c:\Irunner\Flashda.fla'},
        {'filepath': 'file2.txt x' }
    ]
    field_lengths = [64]  # Lengths for 'filename', 'setting1', 'setting2'

    # Create the directory if it does not exist
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Directory '{directory}' created.")

    if not os.path.exists(file_path):
        try:
            # Create default file with fixed-length records
            write_fixed_length_records(file_path, records, field_lengths)
            print(f"File '{file_path}' created with default content.")
        except IOError as e:
            print(f"Error creating file '{file_path}': {e}")
    else:
        print(f"File '{file_path}' already exists.")


def read_file_content(directory='C:/Irunner', filename='scparams.ovh'):
    """Read the content of the file as bytes."""
    file_path = os.path.join(directory, filename)
    try:
        with open(file_path, 'rb') as file:
            content = file.read()
        return content
    except IOError as e:
        print(f"Error reading file '{file_path}': {e}")
        return None



