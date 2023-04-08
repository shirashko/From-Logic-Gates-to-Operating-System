"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os
import sys
import typing
from SymbolTable import SymbolTable
from Parser import Parser
from Code import Code


def assemble_file(
        input_file: typing.TextIO, output_file: typing.TextIO) -> None:
    """Assembles a single file.

    Args:
        input_file (typing.TextIO): the file to assemble.
        output_file (typing.TextIO): writes all output to this file.
    """
    """
    You should use the two-pass implementation suggested in the book:
    
    Initialization
    Initialize the symbol table with all the predefined symbols and their
    pre-allocated RAM addresses, according to section 6.2.3 of the book.
    
    First Pass
    Go through the entire assembly program, line by line, and build the symbol
    table without generating any code. As you march through the program lines,
    keep a running number recording the ROM address into which the current
    command will be eventually loaded.
    This number starts at 0 and is incremented by 1 whenever a C-instruction
    or an A-instruction is encountered, but does not change when a label
    pseudo-command or a comment is encountered. Each time a pseudo-command
    (Xxx) is encountered, add a new entry to the symbol table, associating
    Xxx with the ROM address that will eventually store the next command in
    the program.
    This pass results in entering all the program’s labels along with their
    ROM addresses into the symbol table.
    The program’s variables are handled in the second pass.
    
    Second Pass
    Now go again through the entire program, and parse each line.
    Each time a symbolic A-instruction is encountered, namely, @Xxx where Xxx
    is a symbol and not a number, look up Xxx in the symbol table.
    If the symbol is found in the table, replace it with its numeric meaning
    and complete the command’s translation.
    If the symbol is not found in the table, then it must represent a new
    variable. To handle it, add the pair (Xxx,n) to the symbol table, where n
    is the next available RAM address, and complete the command’s translation.
    The allocated RAM addresses are consecutive numbers, starting at address
    16 (just after the addresses allocated to the predefined symbols).
    After the command is translated, write the translation to the output file.
    
    Tools:
    Two useful tools are the supplied Assembler and the supplied CPU
    Emulator, both available in your tools directory. These tools allow
    experimenting with a working assembler before setting out to build one
    yourself. In addition, the supplied assembler provides a visual
    line-level translation GUI, and allows code comparisons with the outputs
    that your assembler will generate. For more information, see the tutorial
    in the lectures and in the submission page.
    
    Testing:
    The supplied ("built-in") Hack Assembler is guaranteed to generate
    correct binary code. This guaranteed performance can be used to test if
    another assembler, say the one written by you, also generates correct code.
    Let Prog.asm be some program written in the symbolic Hack assembly
    language. Suppose we translate this program using the supplied assembler,
    producing a binary file called Prog.hack. Next, we use another assembler
    (e.g. the one that you wrote) to translate the same program into another
    file, say MyProg.hack. Now, if the latter assembler is working correctly,
    it follows that Prog.hack == MyProg.hack. Thus, one way to test a newly
    written assembler is as follows: (i) load into the supplied visual
    assembler Prog.asm as a source program and MyProg.hack as a compare file,
    (ii) translate the source program, and (iii) compare the resulting binary
    code with the compare file (see the figure above). If the comparison
    fails, the assembler that generated MyProg.hack must be buggy; otherwise,
    it may be OK.
    """
    # Your code goes here!

    # add_entry
    # contains
    # get_address

    symbol_table = SymbolTable()  # initialization

    #  First Pass
    address = 0
    parser = Parser(input_file)
    while parser.has_more_commands():
        if parser.command_type() == "L_COMMAND":
            symbol = parser.symbol()  # cutting () from the string
            symbol_table.add_entry(symbol, address)
        else:
            address += 1
        parser.advance()

    parser.initialize()  # prepare for second round

    #  Second Pass
    variable_available_address = 16
    while parser.has_more_commands():
        if parser.command_type() == "A_COMMAND":
            symbol = parser.symbol()
            if not symbol.isdigit():
                if not symbol_table.contains(symbol):  # it's a variable
                    symbol_table.add_entry(symbol, variable_available_address)
                    variable_available_address += 1

                decimal_address = symbol_table.get_address(symbol)
                # we have decimal number that we will convert into binary number
                command = bin(int(decimal_address)).replace("0b", "")
                output_file.write("0" * (16 - len(command)) + command + "\n")
            else:
                command = bin(int(symbol)).replace("0b", "")
                while len(command) != 15:
                    command = "0" + command
                output_file.write("0" + command + "\n")  # check what is up with the first binary digit
        elif parser.command_type() == "C_COMMAND":
            dest = parser.dest()
            comp = parser.comp()
            is_shift = False
            if ">>" in comp or "<<" in comp:
                is_shift = True
            jump = parser.jump()
            dest = Code.dest(dest)
            comp = Code.comp(comp)
            jump = Code.jump(jump)
            # if it's a shift - 101
            if is_shift:
                command = f"101{comp}{dest}{jump}"
            else:
                command = f"111{comp}{dest}{jump}"
            output_file.write(command + "\n")
        parser.advance()


def main():
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: Assembler <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_assemble = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
    else:
        files_to_assemble = [argument_path]
    for input_path in files_to_assemble:
        filename, extension = os.path.splitext(input_path)
        if extension.lower() != ".asm":
            continue
        output_path = filename + ".hack"
        with open(input_path, 'r') as input_file, \
                open(output_path, 'w') as output_file:
            assemble_file(input_file, output_file)


if "__main__" == __name__:
    main()
    # Parses the input path and calls assemble_file on each input file.
    # This opens both the input and the output files!
    # Both are closed automatically when the code finishes running.
    # If the output file does not exist, it is created automatically in the
    # correct path, using the correct filename.
