"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class Parser:
    """
    Handles the parsing of a single .vm file, and encapsulates access to the
    input code. It reads VM commands, parses them, and provides convenient 
    access to their components. 
    In addition, it removes all white space and comments.
    """

    @staticmethod
    def drop_comments(arr: list, i: int) -> str:  # and drop white space from the beginning and the of the string
        line_list = arr[i].partition("//")
        line = line_list[0]
        return line.strip()

    def initialize(self) -> None:
        self.current_command = 0

    @staticmethod
    def is_a_white_space(arr: list, i: int) -> bool:
        # check if there if the first char that isn't " " isn't "/"
        line = arr[i].replace(" ", "")  # deleting spaces
        return line == '' or line[0] == '/'

    def __init__(self, input_file: typing.TextIO) -> None:
        """Opens the input file and gets ready to parse it.
        Args:
            input_file (typing.TextIO): input file.
        """
        # Your code goes here!
        # A good place to start is:
        # input_lines = input_file.read().splitlines()

        arr = input_file.read().splitlines()  # making a list, and every item in the list is a line from the
        # self.input_lines = [i.replace(" ", "") for i in self.input_lines]  # deleting spaces in the strings (lines)
        number_of_lines = len(arr)
        # delete all lines which is white space and all comments in the lines which are commands
        self.input_lines = []
        for i in range(number_of_lines):
            if i == number_of_lines:  # todo WTF?
                break
            if not self.is_a_white_space(arr, i):
                self.input_lines.append(self.drop_comments(arr, i))
        # now self.input_lines contains only commands
        self.current_command = 0

    def has_more_commands(self) -> bool:  # todo remember to consider symbols
        """Are there more commands in the input?
        Returns:
            bool: True if there are more commands, False otherwise.
        """
        # Your code goes here!
        number_of_commands = len(self.input_lines)
        return self.current_command != number_of_commands

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current command.
        Should be called only if has_more_commands() is true.
        """
        # Your code goes here!
        self.current_command += 1

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current VM command.
            "C_ARITHMETIC" is returned for all arithmetic commands.
            For other commands, can return:
            "C_PUSH", "C_POP", "C_LABEL", "C_GOTO", "C_IF", "C_FUNCTION",
            "C_RETURN", "C_CALL".
        """
        # Your code goes here!
        arithmetic = {'add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not', 'shiftleft', 'shiftright'}
        line = self.input_lines[self.current_command]
        if line in arithmetic:
            return "C_ARITHMETIC"
        elif line == "return":
            return "C_RETURN"
        else:
            first_word = line.split(" ")[0]
            if first_word == 'push':
                return "C_PUSH"
            elif first_word == "pop":
                return "C_POP"
            # todo  "C_CALL".
            elif first_word == "label":
                return "C_LABEL"
            elif first_word == "goto":
                return "C_GOTO"
            elif first_word.replace(" ", "") == "if-goto":  # todo if there is space it's valid?
                return "C_IF"
            elif first_word == "function":
                return "C_FUNCTION"
            elif first_word == "call":
                return "C_CALL"

    def arg1(self) -> str:
        """
        Returns:
            str: the first argument of the current command. In case of
            "C_ARITHMETIC", the command itself (add, sub, etc.) is returned.
            Should not be called if the current command is "C_RETURN".
        """
        # Your code goes here!
        line = self.input_lines[self.current_command]
        if self.command_type() == "C_ARITHMETIC":
            return line  # todo - check if it's without \t and likewise
        else:
            second_word = line.split(" ")[1]
            return second_word

    def arg2(self) -> int:
        """
        Returns:
            int: the second argument of the current command. Should be
            called only if the current command is "C_PUSH", "C_POP",
            "C_FUNCTION" or "C_CALL".
        """
        # Your code goes here!
        line = self.input_lines[self.current_command]
        third_word = line.split(" ")[2]
        return int(third_word)
