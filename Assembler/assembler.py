class Assembler:
    def __init__(self, input_file):
        self.input_file = input_file
        self.list_file = input_file.rsplit('.', 1)[0] + '.lst'
        self.first_pass_file = input_file.rsplit('.', 1)[0] + '.fpass'
        self.hex_file = input_file.rsplit('.', 1)[0] + '.hex'
        self.symbols = {}
        self.references = {}

    def first_pass(self):
        with open(self.input_file, 'r') as infile, open(self.first_pass_file, 'w') as outfile, open(self.list_file, 'w') as listfile:
            address = 0
            for line_num, line in enumerate(infile, 1):
                # Process each line
                # Identify labels, store in self.symbols
                # Identify references, store in self.references
                # Write to first_pass_file and list_file
                pass

    def second_pass(self):
        with open(self.first_pass_file, 'r') as infile, open(self.hex_file, 'w') as hexfile, open(self.list_file, 'a') as listfile:
            for line in infile:
                # Process each line
                # Resolve references using self.symbols
                # Generate machine code
                # Write to hex_file and update list_file
                pass

    def assemble(self):
        self.first_pass()
        self.second_pass()

# Usage
assembler = Assembler('input.asm')
assembler.assemble()