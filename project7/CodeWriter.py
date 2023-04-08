"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class CodeWriter:
    """Translates VM commands into Hack assembly code."""

    i = 0  # static variable ?

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """
        # Your code goes here!
        self.output_stream = output_stream
        self.file_name = None

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
        pop_first = " @SP \n M = M - 1 \n A = M \n"  # sp--, now A points to address of top value
        save_val = "D = M \n"
        get_sec = "A = A - 1 \n"  # now A register is contains the address of sec top value on the stack
        push_result = "M = D \n"
        pop_one = "@SP \n A = M - 1 \n"
        push_true_short = "M = -1 \n"
        push_false_short = "M = 0 \n"
        push_false = pop_one + "M = 0 \n"
        push_true = pop_one + "M = -1 \n"
        end_label = f"(END{self.i}) \n"  # need to self.i+=1 when using
        sub_of_top_values = "D = M - D \n"  # M-D is the sub of values that were on top of the stack
        check_if_top_positive = f"@FIRST_POSITIVE{self.i} \n D;JGE \n"
        sub_without_overflow = f"(SAME_SIGN{self.i}) \n @SP \n A = M  \n D = M \n A = A - 1 \n {sub_of_top_values}"
        if_D_LE_goto_end = f"@END{self.i} \n D;JLE \n"
        if_D_LT_goto_end = f"@END{self.i} \n  D;JLT \n"
        push_true_if_GE = f"@PUSH_TRUE{self.i} \n D;JGE \n"
        push_false_if_GE = f"@PUSH_FALSE{self.i} \n D;JGE \n"
        goto_end = f"@END{self.i} \n 0;JMP \n"
        push_true_full = f"(PUSH_TRUE{self.i}) \n {pop_one} {push_true_short} {goto_end}"
        push_false_full = f"(PUSH_FALSE{self.i}) \n {pop_one} {push_false_short} {goto_end}"
        first_positive_label = f"(FIRST_POSITIVE{self.i}) \n"
        if_D_GT_goto_SAME_SIGN = f"@SAME_SIGN{self.i} \n D;JGE \n"
        first_positive_code = f"{first_positive_label}{pop_one}{save_val}{if_D_GT_goto_SAME_SIGN}"

        string = None

        if command == "add":
            operation = "D = D + M \n"  # D contains the addition of the 2 top values of the stack
            string = pop_first + save_val + get_sec + operation + push_result
        elif command == "sub":
            string = pop_first + save_val + get_sec + sub_of_top_values + push_result
        elif command == "neg":
            operation = "M = -M \n"  # negate the top element and put the result as the top value instead of the top value
            string = pop_one + operation
        elif command == "eq":
            if_D_false_jump = f"@END{self.i} \n D;JEQ \n"
            string = pop_first + save_val + get_sec + sub_of_top_values + push_true_short + if_D_false_jump + push_false \
                     + end_label
        elif command == "gt":  # considering overflow
            string = f"{pop_first}{save_val}{check_if_top_positive}{pop_one}{save_val}{push_true_if_GE}" \
                     f"{sub_without_overflow} {push_false_short}{if_D_LE_goto_end}{push_true_full}" \
                     f"{first_positive_code}{push_false}{end_label}"
        elif command == "lt":  # considering overflow
            string = f"{pop_first}{save_val}{check_if_top_positive}{pop_one}{save_val}{push_false_if_GE}" \
                     f"{sub_without_overflow}{push_true_short}{if_D_LT_goto_end}{push_false_full}{first_positive_code}" \
                     f"{push_true}{end_label}"
        elif command == "and":
            operation_and_push = "M = D & M \n"
            string = pop_first + save_val + get_sec + operation_and_push
        elif command == "or":
            operation_and_push = "M = D | M \n"
            string = pop_first + save_val + get_sec + operation_and_push
        elif command == "not":
            operation_and_push = "M = !M \n"
            string = pop_one + operation_and_push
        # support the commands "shiftleft", "shiftright", which perform a left-shift and a right-shift on the last stack value
        elif command == "shiftleft":  # todo make sure it's ok
            operation = "M = M<< \n"
            string = pop_one + operation
        elif command == "shiftright":  # todo make sure it's ok
            operation = "M = M>> \n"
            string = pop_one + operation

        self.output_stream.write(string + "\n")  # print the right string
        self.i += 1  # label need to ve unique

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
                        "free_space": f"@segment_plus_i{self.i}\n", "constant": f"@{index} \n"}
        # assembly commands
        save_A = " D = A \n"
        save_index = f"@{str(index)} \n {save_A}"
        get_segment_plus_i_M = f"{save_index} {address_dict[segment]} D = D + M \n"
        get_segment_plus_i_A = f" {save_index} {address_dict[segment]} D = D + A \n"
        at_index = f"@{index}\n"
        save_index = f"{at_index}{save_A}"
        goto_start_plus_i_A = f"{save_index}{address_dict[segment]} A = D + A \n"
        goto_start_plus_i_M = f"{save_index}{address_dict[segment]} A = D + M \n"
        advance_sp_and_goto_top = "@SP \n M = M + 1 \n A = M - 1 \n "
        push_D = "M = D \n"
        reduce_sp_and_goto_top = "@SP \n M = M - 1 \n A = M \n"  # sp--, , A is the address of the top value of the stack
        save_val = "D = M \n"
        get_seg_i_and_push = address_dict["free_space"] + "A = M \n M = D \n"
        push_to_free_space = address_dict["free_space"] + push_D

        assembly_commands = None
        # deciding which assembly commands should be written to the output stream as dependency of the arguments
        # of the function
        if segment == "pointer":  # 0 for this, 1 for that. You should support accessing the pointer segment for
            # all indices (not only 0/1).
            if command == "push":
                assembly_commands = goto_start_plus_i_A + save_val + advance_sp_and_goto_top + push_D
            else:  # command is "pop"
                assembly_commands = get_segment_plus_i_A + push_to_free_space + reduce_sp_and_goto_top + save_val + \
                                    get_seg_i_and_push  # todo
        elif segment == "constant":
            assembly_commands = save_index + advance_sp_and_goto_top + push_D  # no pop command with constant segment

        elif segment == "static":
            if command == "push":
                assembly_commands = address_dict[segment] + save_val + advance_sp_and_goto_top + push_D
            else:  # command is "pop"
                assembly_commands = reduce_sp_and_goto_top + save_val + address_dict[segment] + push_D
        elif segment == "temp":
            if command == "push":
                assembly_commands = goto_start_plus_i_A + save_val + advance_sp_and_goto_top + push_D
            else:
                assembly_commands = get_segment_plus_i_A + push_to_free_space + reduce_sp_and_goto_top + save_val + \
                                    get_seg_i_and_push
        else:  # segment == "local" or "argument" or "this" or "that"
            if command == "push":
                assembly_commands = goto_start_plus_i_M + save_val + advance_sp_and_goto_top + push_D
            else:  # command is "pop"
                assembly_commands = get_segment_plus_i_M + push_to_free_space + reduce_sp_and_goto_top + save_val + \
                                    get_seg_i_and_push

        self.output_stream.write(
            assembly_commands + "\n")  # write the corresponding assembly commands (for the given args)
        self.i += 1

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
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        pass

    def write_goto(self, label: str) -> None:
        """Writes assembly code that affects the goto command.

        Args:
            label (str): the label to go to.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        pass

    def write_if(self, label: str) -> None:
        """Writes assembly code that affects the if-goto command. 

        Args:
            label (str): the label to go to.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        pass

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
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        pass

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
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        pass

    def write_return(self) -> None:
        """Writes assembly code that affects the return command."""
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        pass
