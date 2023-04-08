"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class CodeWriter:
    """Translates VM commands into Hack assembly code."""

    advance_sp_and_goto_top = "@SP \nM = M + 1\nA = M - 1\n"
    reduce_sp_and_goto_top = "@SP \nM = M - 1 \nA = M\n"
    save_val = "D = M \n"
    push_D = "M = D\n"
    get_sec = "A = A - 1 \n"  # now A register is contains the address of sec top value on the stack
    pop_one = "@SP \nA = M - 1\n"
    push_true_short = "M = -1\n"
    push_false_short = "M = 0 \n"
    push_false = pop_one + "M = 0 \n"
    push_true = pop_one + "M = -1 \n"

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """
        # Your code goes here!
        self.output_stream = output_stream
        self.file_name = None
        self.current_func_name = ""
        self.label_index = 0
        self.return_index = 0

    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is 
        started.

        Args:
            filename (str): The name of the VM file.
        """
        # Your code goes here!
        # This function is useful when translating code that handles the
        # static segment.
        # To avoid problems with Linux/Windows/MacOS differences with regards
        # to filenames and paths, you are advised to parse the filename in
        # the function "translate_file" in Main.py using python's os library,
        # For example, using code similar to:
        # input_filename, input_extension = os.path.splitext(os.path.basename(input_file.name))
        self.file_name = filename

        # if a new VM file is started, we need to delete all the static segment values of the previous VM file

    # Finally, add the bootstrap code, which initializes the SP to 256, and calls the function "Sys.init
    def bootstrap(self) -> None:
        self.output_stream.write("//bootstrap\n")
        command = "@256 \nD = A \n@SP \nM = D\n"
        self.output_stream.write(command)
        self.write_call("Sys.init", 0)

    def write_arithmetic(self, command: str) -> None:
        """Writes assembly code that is the translation of the given 
        arithmetic command. For the commands eq, lt, gt, you should correctly
        compare between all numbers our computer supports, and we define the
        value "true" to be -1, and "false" to be 0.

        Args:
            command (str): an arithmetic command.
"""
        self.output_stream.write(f"// {command}\n")

        # useful assembly commands
        end_label = f"(END{self.label_index}.{self.file_name}) \n"  # need to self.label_index+=1 when using
        sub_of_top_values = "D = M - D \n"  # M-D is the sub of values that were on top of the stack
        check_if_top_positive = f"@FIRST_POSITIVE{self.label_index}.{self.file_name} \n D;JGE \n"
        sub_without_overflow = f"(SAME_SIGN{self.label_index}.{self.file_name}) \n @SP \n A = M  \n D = M \n A = A - 1 \n {sub_of_top_values}"
        if_D_LE_goto_end = f"@END{self.label_index}.{self.file_name} \n D;JLE \n"
        if_D_LT_goto_end = f"@END{self.label_index}.{self.file_name} \n  D;JLT \n"
        push_true_if_GE = f"@PUSH_TRUE{self.label_index}.{self.file_name} \n D;JGE \n"
        push_false_if_GE = f"@PUSH_FALSE{self.label_index}.{self.file_name} \n D;JGE \n"
        goto_end = f"@END{self.label_index}.{self.file_name} \n 0;JMP \n"
        push_true_full = f"(PUSH_TRUE{self.label_index}.{self.file_name}) \n {self.pop_one} {self.push_true_short} {goto_end}"
        push_false_full = f"(PUSH_FALSE{self.label_index}.{self.file_name}) \n {self.pop_one} {self.push_false_short} {goto_end}"
        first_positive_label = f"(FIRST_POSITIVE{self.label_index}.{self.file_name}) \n"
        if_D_GT_goto_SAME_SIGN = f"@SAME_SIGN{self.label_index}.{self.file_name} \n D;JGE \n"
        first_positive_code = f"{first_positive_label}{self.pop_one}{self.save_val}{if_D_GT_goto_SAME_SIGN}"

        string = None

        if command == "add":
            operation = "D = D + M \n"  # D contains the addition of the 2 top values of the stack
            string = self.reduce_sp_and_goto_top + self.save_val + self.get_sec + operation + self.push_D
        elif command == "sub":
            string = self.reduce_sp_and_goto_top + self.save_val + self.get_sec + sub_of_top_values + self.push_D
        elif command == "neg":
            operation = "M = -M \n"  # negate the top element and put the result as the top value instead of the top value
            string = self.pop_one + operation
        elif command == "eq":
            if_D_false_jump = f"@END{self.label_index}.{self.file_name} \n D;JEQ \n"
            string = self.reduce_sp_and_goto_top + self.save_val + self.get_sec + sub_of_top_values + \
                     self.push_true_short + if_D_false_jump + self.push_false + end_label
        elif command == "gt":  # considering overflow
            string = f"{self.reduce_sp_and_goto_top}{self.save_val}{check_if_top_positive}{self.pop_one}{self.save_val}" \
                     f"{push_true_if_GE}{sub_without_overflow}{self.push_false_short}{if_D_LE_goto_end}{push_true_full}" \
                     f"{first_positive_code}{self.push_false}{end_label}"
        elif command == "lt":  # considering overflow
            string = f"{self.reduce_sp_and_goto_top}{self.save_val}{check_if_top_positive}{self.pop_one}" \
                     f"{self.save_val}{push_false_if_GE}{sub_without_overflow}{self.push_true_short}{if_D_LT_goto_end}" \
                     f"{push_false_full}{first_positive_code}{self.push_true}{end_label}"
        elif command == "and":
            operation_and_push = "M = D & M \n"
            string = self.reduce_sp_and_goto_top + self.save_val + self.get_sec + operation_and_push
        elif command == "or":
            operation_and_push = "M = D | M \n"
            string = self.reduce_sp_and_goto_top + self.save_val + self.get_sec + operation_and_push
        elif command == "not":
            operation_and_push = "M = !M \n"
            string = self.pop_one + operation_and_push
        # support the commands "shiftleft", "shiftright", which perform a left-shift and a right-shift on the last stack value
        elif command == "shiftleft":
            operation = "M = M<< \n"
            string = self.pop_one + operation
        elif command == "shiftright":
            operation = "M = M>> \n"
            string = self.pop_one + operation

        self.output_stream.write(string + "\n")  # print the right string
        self.label_index += 1  # label need to be unique

    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        """Writes assembly code that is the translation of the given 
        command, where command is either C_PUSH or C_POP.

        Args:
            command (str): "C_PUSH" or "C_POP".
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """
        # Your code goes here!
        # Note: each reference to static i appearing in the file Xxx.vm should
        # be translated to the assembly symbol "Xxx.i". In the subsequent
        # assembly process, the Hack assembler will allocate these symbolic
        # variables to the RAM, starting at address 16.

        self.output_stream.write(f"// {command} {segment} {index}\n")
        address_dict = {"local": "@LCL \n", "argument": "@ARG \n", "this": "@THIS \n", "that": "@THAT \n",
                        "static": f"@{self.file_name}.{index}\n", "temp": "@5\n", "pointer": "@3 \n",
                        "free_space": f"@R13\n", "constant": f"@{index} \n"}
        # assembly commands
        save_A = "D = A\n"
        at_index = f"@{index}\n"
        save_index = f"{at_index}{save_A}"
        goto_start_plus_i_A = f"{save_index}{address_dict[segment]}A = D + A \n"
        goto_start_plus_i_M = f"{save_index}{address_dict[segment]}A = D + M \n"
        get_segment_plus_i_M = f"{save_index} {address_dict[segment]}D = D + M \n"
        get_segment_plus_i_A = f"{save_index} {address_dict[segment]}D = D + A \n"
        get_seg_i_and_push = address_dict["free_space"] + "A = M\nM = D \n"
        push_to_free_space = address_dict["free_space"] + self.push_D

        # deciding which assembly commands should be written to the output stream as dependency of the arguments
        # of the function
        if segment == "pointer":  # 0 for this, 1 for that. You should support accessing the pointer segment for
            # all indices (not only 0/1).
            if command == "push":
                assembly_commands = goto_start_plus_i_A + self.save_val + self.advance_sp_and_goto_top + self.push_D
            else:  # command is "pop"
                assembly_commands = get_segment_plus_i_A + push_to_free_space + self.reduce_sp_and_goto_top + \
                                    self.save_val + get_seg_i_and_push
        elif segment == "constant":
            assembly_commands = save_index + self.advance_sp_and_goto_top + self.push_D  # no pop command with constant
            # segment
        elif segment == "static":
            if command == "push":
                assembly_commands = address_dict[segment] + self.save_val + self.advance_sp_and_goto_top + self.push_D
            else:  # command is "pop"
                assembly_commands = self.reduce_sp_and_goto_top + self.save_val + address_dict[segment] + self.push_D
        elif segment == "temp":
            if command == "push":
                assembly_commands = goto_start_plus_i_A + self.save_val + self.advance_sp_and_goto_top + self.push_D
            else:
                assembly_commands = get_segment_plus_i_A + push_to_free_space + self.reduce_sp_and_goto_top + self.save_val + \
                                    get_seg_i_and_push
        else:  # segment == "local" or "argument" or "this" or "that"
            if command == "push":
                assembly_commands = goto_start_plus_i_M + self.save_val + self.advance_sp_and_goto_top + self.push_D
            else:  # command is "pop"
                assembly_commands = get_segment_plus_i_M + push_to_free_space + self.reduce_sp_and_goto_top + \
                                    self.save_val + get_seg_i_and_push

        self.output_stream.write(assembly_commands + "\n")  # write the corresponding assembly commands

    def __initialize_locals(self, n_vars: int) -> None:
        """
        @n_vars
        D = A
        (LOCALS_LOOP)
        @END
        D;JEQ
        D = D - 1
        @SP
        M = M + 1
        A = M - 1
        M = 0
        @LOCALS_LOOP
        0;JMP
        (END)
        """
        # if n_vars > 0:
        # push zero n_vars times for LOCAL segment initialization of the new function scope
        save_num = f"@{n_vars}\nD = A\n"
        frame_for_looping_locals = f"(LOCALS_LOOP{self.label_index}.{self.file_name})\n@END" \
                                   f"{self.label_index}.{self.file_name}\nD;JEQ \nD = D - 1\n"
        goto_loop = f"@LOCALS_LOOP{self.label_index}.{self.file_name} \n0;JMP \n"
        initialize_local_vars = f"{save_num}{frame_for_looping_locals}{self.advance_sp_and_goto_top}" \
                                f"{self.push_false_short}{goto_loop}(END{self.label_index}.{self.file_name})\n"
        self.output_stream.write(initialize_local_vars + "\n")
        self.label_index += 1

    def write_label(self, label: str) -> None:
        """Writes assembly code that affects the label command. 
        Let "foo" be a function within the file Xxx.vm. The handling of
        each "label bar" command within "foo" generates and injects the symbol
        "Xxx.foo$bar" into the assembly code stream.
        When translating "goto bar" and "if-goto bar" commands within "foo",
        the label "Xxx.foo$bar" must be used instead of "bar".

        Args:
            label (str): the label to write.
        """
        self.output_stream.write(f"// label {label} \n")
        assembly_label_command = f"({self.current_func_name}${label}) \n"
        self.output_stream.write(assembly_label_command + "\n")

    def write_goto(self, label: str) -> None:
        """Writes assembly code that affects the goto command.

        Args:
            label (str): the label to go to.
        """
        # goto label -> @label
        #               0;JMP
        self.output_stream.write("// goto label \n")
        assembly_command = f"@{self.current_func_name}${label} \n0;JMP \n"
        self.output_stream.write(assembly_command + "\n")

    def write_if(self, label: str) -> None:
        """Writes assembly code that affects the if-goto command. 

        Args:
            label (str): the label to go to.
        """
        """ if-goto label -> @SP
                            M = M - 1
                            A = M
                            D = M
                            @label
                            D;JNE # if D is true then D = -1   """

        self.output_stream.write("// if-goto label\n")
        check_if_true = "D;JNE \n"
        assembly_command = f"{self.reduce_sp_and_goto_top}{self.save_val}@{self.current_func_name}$" \
                           f"{label}\n{check_if_true}"
        self.output_stream.write(assembly_command + "\n")

    def write_function(self, function_name: str, n_vars: int) -> None:
        """Writes assembly code that affects the function command. 
        The handling of each "function foo" command within the file Xxx.vm
        generates and injects a symbol "Xxx.foo" into the assembly code stream,
        that labels the entry-point to the function's code.
        In the subsequent assembly process, the assembler translates this 
        symbol into the physical address where the function code starts.

        Args:
            function_name (str): the name of the function.
            n_vars (int): the number of local variables of the function.
        """
        """
        @n_vars
        D = A
        (LOCALS_LOOPi)
        @ENDi
        D;JEQ
        @SP
        M = M + 1
        A = M - 1
        M = 0
        D = D - 1
        (ENDi)"""

        self.output_stream.write(f"// function {function_name} {n_vars}\n")  # comment the command
        self.current_func_name = function_name
        # update the class that we enter to a new function
        self.output_stream.write(f"({function_name})\n")
        self.__initialize_locals(n_vars)  # push 0 n_vars times for LOCAL segment initialization

    def __push_return_address(self, func_name) -> None:
        self.output_stream.write("// push return address\n")
        returnAddress = f"{self.file_name}.{func_name}$ret.{self.return_index}\n"  # Xxx.foo$ret.i
        # the assembler implementation makes this label be the address of the next command in the code
        # (after the call command).
        push_returnAddress = f"@{returnAddress}D = A\n{self.advance_sp_and_goto_top}{self.push_D}"
        self.output_stream.write(push_returnAddress)

    def __push_segments(self) -> None:
        """
            push LCL/ ARG/ THIS/ THAT
            @LCL/ ARG/ THIS/ THAT
            D = M
            @SP
            M = M + 1
            A = M - 1
            M = D
        """
        self.output_stream.write("// push segments\n")
        address_list = ["@LCL\n", "@ARG\n", "@THIS\n", "@THAT\n"]
        for at_segment in address_list:
            command = f"{at_segment}{self.save_val}{self.advance_sp_and_goto_top}{self.push_D}"
            self.output_stream.write(command)

    def __reposition_arg(self, n_args: int) -> None:
        # ARG = SP-5-nARGS # initialize the ARG segment of new scope (of the function callee)
        """
            @SP
            D = M
            @5
            D = D - A
            @n_args
            D = D - A
            @ARG
            M = D
        """
        self.output_stream.write("// reposition ARG\n")
        command = f"@SP \n{self.save_val}@5 \nD = D - A \n@{n_args}\nD = D - A \n@ARG \n{self.push_D}"
        self.output_stream.write(command)

    def __reposition_lcl(self) -> None:
        """ LCL = SP:
            @SP
            D = M
            @LCL
            M = D"""
        self.output_stream.write("// reposition LCL\n")
        command = f"@SP \n{self.save_val}@LCL \n{self.push_D}"
        self.output_stream.write(command)

    def __return_address_label(self, func_name) -> None:
        self.output_stream.write("// return address label\n")
        return_address_label = f"({self.file_name}.{func_name}$ret.{self.return_index})\n\n"  # Xxx.foo$ret.i
        # the assembler implementation makes this label be the address of the next command in the code
        # (after the call command).
        self.output_stream.write(return_address_label)

    def __update_function_name_and_goto_func(self, function_name: str) -> None:
        self.output_stream.write("// goto function\n")
        goto_function_command = f"@{function_name}\n 0;JMP \n"
        self.output_stream.write(goto_function_command)

    def write_call(self, function_name: str, n_args: int) -> None:
        """Writes assembly code that affects the call command. 
        Let "foo" be a function within the file Xxx.vm.
        The handling of each "call" command within foo's code generates and
        injects a symbol "Xxx.foo$ret.i" into the assembly code stream, where
        "i" is a running integer (one such symbol is generated for each "call"
        command within "foo").
        This symbol is used to mark the return address within the caller's 
        code. In the subsequent assembly process, the assembler translates this
        symbol into the physical memory address of the command immediately
        following the "call" command.

        Args:
            function_name (str): the name of the function to call.
            n_args (int): the number of arguments of the function.

        My notes:
            push returnAddress
            push LCL
            push ARG
            push THIS
            push THAT
            ARG = SP-5-nARGS
            LCL = SP
            goto functionName
            (returnAddress)
        """
        self.output_stream.write(f"// call {function_name} {n_args}\n")  # comment the vm code to the asm file
        self.__push_return_address(function_name)
        self.__push_segments()  # push local,arguments,this,that
        self.__reposition_arg(n_args)
        self.__reposition_lcl()
        # for example: call Main.fibonacci 1, function SimpleFunction.test 2, function Sys.init 0
        # so we need to change the file name to the one we're going to, and do goto function name
        self.__update_function_name_and_goto_func(function_name)
        self.__return_address_label(function_name)
        self.return_index += 1  # "i" is a running integer (one such symbol is generated for each "call" command within
        # "foo"). this is why when function_name change, we need to initialize return_index to zero

    def __restore_segments(self) -> None:
        """
        @R13
        AM = M - 1 # A == endFrame - i (i=1,2,3,4) every time in the loop is descending in one more, and also A = M-1 so
                   # now A == the address where we saved THAT\THIS\ARG\LCL
        D = M # the value was stored at THAT\THIS\ARG\LCL before the function call
        @THAT\THIS\ARG\LCL
        M = D
        """
        self.output_stream.write("// restore segments\n")
        address_list = ["@THAT\n", "@THIS\n", "@ARG\n", "@LCL\n"]
        for at_seg in address_list:
            command = f"@R13 \nAM = M - 1 \n{self.save_val}{at_seg}{self.push_D}"
            self.output_stream.write(command)

    def __goto_return_address(self) -> None:
        """
        goto retAddr # goes to return address in the caller's code
        @R14
        A = M
        0;JMP
        #todo check it's ok because it feels weird
        """
        self.output_stream.write("// goto return address\n")
        command = f"@R14\nA = M \n0;JMP \n"
        self.output_stream.write(command + "\n")

    def __get_end_frame_and_return_address(self) -> None:
        """
        # endFrame = LCL
        @LCL
        D = M
        @R13 # R13 function as endFrame
        M = D
        # retAddr = *(endFrame - 5) # gets the return address
        @5
        A = D - A // A is the address of the place we saved in the return address
        D = M
        @R14 # saves the return address, function as retAddr variable in the pseudo code
        M = D
        """
        self.output_stream.write("// save endFrame and return address\n")
        command = f"@LCL\n{self.save_val}@R13 \n{self.push_D}@5 \nA=D-A \n{self.save_val}@R14 \n{self.push_D}"
        self.output_stream.write(command)

    def __replace_args_with_return_value(self) -> None:
        """ *ARG = pop() # repositions the return value of caller
         @SP
         M = M - 1
         A = M
         D = M
         @ARG
         A = M
         M = D
        """
        self.output_stream.write("// replace arguments with return value\n")
        command = f"{self.reduce_sp_and_goto_top}{self.save_val}@ARG \nA = M\n{self.push_D}"
        self.output_stream.write(command)

    def __reposition_sp(self) -> None:
        """ SP = ARG + 1 # repositions SP of the caller
         @ARG
         D = M + 1
         @SP
         M = D
        """
        self.output_stream.write("// reposition sp\n")
        command = f"@ARG \nD = M + 1 \n@SP \n{self.push_D}"
        self.output_stream.write(command)

    def write_return(self) -> None:
        """Writes assembly code that affects the return command."""
        """
        endFrame = LCL # endFrame is a temporary variable
        retAddr = *(endFrame - 5) # gets the return address
        *ARG = pop() # repositions the return value of caller
        SP = ARG + 1 # repositions SP of the caller
        THAT = *(endFrame - 1) # restores THAT of the caller
        THIS = = *(endFrame - 2) # restores THIS of the caller
        ARG = = *(endFrame - 3) # restores ARG of the caller
        LCL = = *(endFrame - 4) # restores LCL of the caller
        goto retAddr # goes to return address in the caller's code
        """
        self.output_stream.write(f"// return\n")

        self.__get_end_frame_and_return_address()
        self.__replace_args_with_return_value()
        self.__reposition_sp()
        self.__restore_segments()
        self.__goto_return_address()
