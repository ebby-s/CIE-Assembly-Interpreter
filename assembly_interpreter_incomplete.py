'''
Input to this program is a text file which has
instuctions following CIE Assembly Language syntax.

Labels are given on one line terminated by a colon, comments are
permitted on any line after the first line and start with an '@'.

Thank you to Stuart Maher for the AQA A level assembler which this
program was based on.
'''

import re

def Assembler():
    '''Runs an assembler based on the CIE Assembly Language specification.'''
    print("CIE Assembler")
    print("="*80)
    again = True
    while again:
        print()
        prog = load_program()
        try: execute_program(prog)
        except:
            print("uh-oh, something's gone wrong...")
            print()
        if input("run again [y/n]? >>> ") == 'n':
            again = False

def load_program():
    '''
    A filename is given as input.
    Program is returned as a list of instructions where
    instructions are a list of strings (each operator/operand
    is a separate entity).
    The file should have the program
    with every instruction on a new line.
    '''
    prog = []
    read_in = False
    while not read_in:
        try:
            filename = input("enter the filename >>> ")
            with open(filename, 'r') as f: program = f.readlines()
            read_in = True
        except: print("Error opening file, check the file exists in the same directory as this program.")
    try:
        # parse instructions
        for x in range(len(program)):
            # create a space-delimited list from the line of code
            # ignore comments
            if program[x][0] != '@':
                line_of_code = list(program[x].split(' '))
                # strip out commas and new lines from each element
                for i in range(len(line_of_code)):
                    line_of_code[i] = re.sub(',', '', line_of_code[i])
                    line_of_code[i] = re.sub('\n', '', line_of_code[i])
                    line_of_code[i] = re.sub('\r', '', line_of_code[i])
                prog.append(line_of_code)
    except:
        print("Error encountered parsing instructions, ensure all instructions",
              "are well-formed and comments start with an '@' symbol.")
        raise Exception
    return prog

def execute_program(prog):
    '''
    Firstly looks ahead through the program to read in labels
    and then executes the instruction line-by-line.  Gives the
    user the option to output the CPU and memory content after each
    instruction has executed.
    '''
    try:
        # scan program for labels and populate dictionary
        labels = {}
        for p in range(len(prog)):
            if prog[p][-1][-1] == ':':
                # checking if last character is a ':' and if so
                # creating the appropriate label with its
                # corresponding line number
                labels[prog[p][-1][:-1]] = p
    except:
        print("Labels are incorrect, ensure they all end with a ':' symbol.")
        raise Exception

    # creates a dictionary of the labels and instantiates all
    # to zero        
    reg_labels = ['ACC','IX']
    regs = {}
    for r in reg_labels: regs[r] = 0

    # creates a dictionary of the comparison bits and instantiates
    # all to False
    comparison_bits = {}    
    comparison_bits['EQ'] = False
    pc = 0
    steps = 0
    
    display_prog(prog)

    # one-time request to step through or just execute in one go
    ask_step = input("would you like to step through the program [y/n]? >>> ")
    if ask_step == 'y': step_through = True
    else: step_through = False
    ask_in_bin = input("would you like the registers and memory to output in binary [y/n]? >>> ")
    if ask_in_bin == 'y': in_bin = True
    else: in_bin = False

    # executes program until HALT or EOF is reached
    halting = False
    while not halting and pc < len(prog):
        steps += 1
        line = prog[pc]
        if step_through:
            # pretty print if user has requested step-through
            print("="*80)
            display_cpu(regs, comparison_bits, pc, in_bin)        
            display_memory(prog)
            print("executing instruction", ' '.join(line))
            inp = input("press enter to step though or 'x' to execute all >>> ")
            if inp == 'x': step_through = False

        # immediate addressing, load number to ACC
        if line[0] == 'LDM':
            regs['ACC'] = int(line[1][1:])

        # direct addressing, load contents of given address to ACC
        if line[0] == 'LDD':
            regs['ACC'] = int(prog[1+labels[line[1]]][0])

        # indirect addressing, address to be used is at given address
        if line[0] == 'LDI':
            address = int(prog[1+labels[line[1]]][0])
            regs['ACC'] = int(prog[1+address][0])

        # indexed addressing, copy contents from calculated address to ACC
        if line[0] == 'LDX':
            while len(prog) < labels[line[1]]+regs['IX']+2: prog.append([str(0)])
            regs['ACC'] = int(prog[1+labels[line[1]]+regs['IX']][0])

        # immediate addressing, load number to IX
        if line[0] == 'LDR':
            regs['IX'] = int(line[1][1:])
        
        # store the contents of ACC at the given address
        elif line[0] == 'STO':
            prog[1+labels[line[1]]][0] = str(regs['ACC'])
        
        # indexed addressing, copy contents of ACC to calculated address
        elif line[0] == 'STX':
            while len(prog) < labels[line[1]]+regs['IX']+2: prog.append([str(0)])
            prog[1+labels[line[1]]+regs['IX']][0] = str(regs['ACC'])
        
        # add register and operand and store in register
        elif line[0] == 'ADD':
            regs['ACC'] += int(prog[1+labels[line[1]]][0])

        # add 1 to the contents of the register
        elif line[0] == 'INC':
            regs[line[1]] += int(1)

        # subtract 1 from the contents of the register
        elif line[0] == 'DEC':
            regs[line[1]] -= int(1)

        # compare register and operand
        elif line[0] == 'CMP':
            if line[1][0] == '#': comparison_bits['EQ'] = regs['ACC'] == int(line[1][1:])
            else: comparison_bits['EQ'] = regs['ACC'] == int(prog[1+labels[line[1]]][0])

        # jump to a label
        elif line[0] == 'JMP':
            pc = labels[line[1]]        
            
        # jump to a label if a stated condition is met
        elif line[0] == 'JPE' and comparison_bits['EQ']:
            pc = labels[line[1]]

        elif line[0] == 'JPN' and not comparison_bits['EQ']:
            pc = labels[line[1]]

        # bit-wise AND between register and operand and stored in register
        elif line[0] == 'AND':
            regs['ACC'] = regs['ACC'] & int(line[1][1:])
        
        # bit-wise OR between register and operand and stored in register
        elif line[0] == 'OR':
            regs['ACC'] = regs['ACC'] | int(line[1][1:])
        
        # bit-wise X-OR between register and operand and stored in register
        elif line[0] == 'XOR':
            regs['ACC'] = regs['ACC'] ^ int(line[1][1:])
        
        # logical left shift between register and operand and stored in register
        elif line[0] == 'LSL':
            regs['ACC'] = regs['ACC'] << int(line[1][1:])
        
        # logical right shift between register and operand and stored in register
        elif line[0] == 'LSR':
            regs['ACC'] = regs['ACC'] >> int(line[1][1:])

        # input character and store its ASCII value in ACC
        elif line[0] == 'IN':
            regs['ACC'] = ord(input("Enter input: "))

        # output ASCII character from ACC
        elif line[0] == 'OUT':
            print(chr(regs['ACC']))

        # terminate execution, old pc is remembered for output
        elif line[0] == 'END':
            halting = True 
        
        # program counter updated (even if jump to label is set)
        pc += 1
        
    print()
    print("="*80)
    print("Program Halted")
    print(steps, "instructions executed")
    display_memory(prog)
    display_cpu(regs, comparison_bits, pc, in_bin)     

def display_memory(prog):
    print("\nMemory:\n")
    for value in prog[prog.index(['END'])+1:]: print(' '.join(value))
    print()

def display_prog(prog):
    '''Pretty prints the program.'''
    print("Program:")
    for line in prog: print(' '.join(line))
    print()
    
def display_cpu(registers, comparison_bits, pc, in_binary=False):
    '''Pretty prints CPU information.'''
    print("Program Counter:", pc)
    print()
    print("Registers:")
    for k in sorted(registers):
        print(k, ":", registers[k]) if not in_binary else print(k, ":", format(registers[k] if registers[k] >= 0 else (1 << 8) + registers[k], '08b'))
    print()
    print("Comparison States:")
    for k in comparison_bits.keys():
        print(k, ":", comparison_bits[k]) if not in_binary else print(k, ":", int(comparison_bits[k]))
    print()

if __name__ == "__main__":
    Assembler()
