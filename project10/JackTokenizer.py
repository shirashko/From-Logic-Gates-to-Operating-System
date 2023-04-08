"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

TOKEN = 0
TOKEN_TYPE = 1


class JackTokenizer:
    keyword_list = ["class", "method", "function", "constructor", "int", "boolean", "char", "void", "var", "static",
                    "field", "let", "do", "if", "else", "while", "return", "true", "false", "null", "this"]
    symbol_list = ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~',
                   '^', '#']

    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.
    
    An Xxx .jack file is a stream of characters. If the file represents a
    valid program, it can be tokenized into a stream of valid tokens. The
    tokens may be separated by an arbitrary number of space characters, 
    newline characters, and comments, which are ignored. There are three 
    possible comment formats: /* comment until closing */ , /** API comment 
    until closing */ , and // comment until the line’s end.

    ‘xxx’: quotes are used for tokens that appear verbatim (‘terminals’);
    xxx: regular typeface is used for names of language constructs 
    (‘non-terminals’);
    (): parentheses are used for grouping of language constructs;
    x | y: indicates that either x or y can appear;
    x?: indicates that x appears 0 or 1 times;
    x*: indicates that x appears 0 or more times.

    ** Lexical elements **
    The Jack language includes five types of terminal elements (tokens).
    1. keyword: 'class' | 'constructor' | 'function' | 'method' | 'field' | 
        'static' | 'var' | 'int' | 'char' | 'boolean' | 'void' | 'true' | 'false'
        | 'null' | 'this' | 'let' | 'do' | 'if' | 'else' | 'while' | 'return'
    2. symbol:  '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
        '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
    3. integerConstant: A decimal number in the range 0-32767.
    4. StringConstant: '"' A sequence of Unicode characters not including 
        double quote or newline '"'
    5. identifier: A sequence of letters, digits, and underscore ('_') not 
        starting with a digit.


    ** Program structure **
    A Jack program is a collection of classes, each appearing in a separate 
    file. The compilation unit is a class. A class is a sequence of tokens 
    structured according to the following context free syntax:
    
    class: 'class' className '{' classVarDec* subroutineDec* '}'
    classVarDec: ('static' | 'field') type varName (',' varName)* ';'
    type: 'int' | 'char' | 'boolean' | className
    subroutineDec: ('constructor' | 'function' | 'method') ('void' | type) 
    subroutineName '(' parameterList ')' subroutineBody
    parameterList: ((type varName) (',' type varName)*)?
    subroutineBody: '{' varDec* statements '}'
    varDec: 'var' type varName (',' varName)* ';'
    className: identifier
    subroutineName: identifier
    varName: identifier


    ** Statements **
    statements: statement*
    statement: letStatement | ifStatement | whileStatement | doStatement | 
        returnStatement
    letStatement: 'let' varName ('[' expression ']')? '=' expression ';'
    ifStatement: 'if' '(' expression ')' '{' statements '}' ('else' '{' 
        statements '}')?
    whileStatement: 'while' '(' 'expression' ')' '{' statements '}'
    doStatement: 'do' subroutineCall ';'
    returnStatement: 'return' expression? ';'


    ** Expressions **
    expression: term (op term)*
    term: integerConstant | stringConstant | keywordConstant | varName | 
        varName '['expression']' | subroutineCall | '(' expression ')' | 
        unaryOp term
    subroutineCall: subroutineName '(' expressionList ')' | (className | 
        varName) '.' subroutineName '(' expressionList ')'
    expressionList: (expression (',' expression)* )?
    op: '+' | '-' | '*' | '/' | '&' | '|' | '<' | '>' | '='
    unaryOp: '-' | '~' | '^' | '#'
    keywordConstant: 'true' | 'false' | 'null' | 'this'
    
    If you are wondering whether some Jack program is valid or not, you should
    use the built-in JackCompiler to compiler it. If the compilation fails, it
    is invalid. Otherwise, it is valid.
    """

    @staticmethod
    def is_inline_comment_or_empty_line(arr: list, i: int) -> bool:
        # check if there if the first char that isn't " " isn't "/"
        # line = arr[i].replace(" ", "")  # deleting spaces
        return arr[i] == '' or arr[i][0:2] == "//"

    """There are three possible comment formats: /* comment until closing */ , /** API comment 
    until closing */ , and // comment until the line’s end."""

    @staticmethod
    def drop_white_space_from_command(arr: list, i: int) -> str:
        line_list = arr[i].partition("//")
        if JackTokenizer.not_in_string(line_list):
            line = line_list[0]
        else:
            line = arr[i]
        return line.strip()  # The strip() method removes any leading (spaces at the beginning) and trailing (spaces at
        # the end) characters (space is the default leading character to remove)

    # now drop comments in the formats: /* comment until closing */ , /** API comment until closing */
    @staticmethod
    def not_in_string(line):
        x = 0
        for char in line[0]:
            if char == '"':
                x += 1
        return x % 2 == 0

    def drop_comments(self, input_lines: list) -> list:
        number_of_lines = len(input_lines)
        lines = []
        if number_of_lines > 0:
            flag = True
        else:
            flag = False
        current_line = 0
        while flag:
            if ("/*" in input_lines[current_line] or "/**" in input_lines[current_line]) and \
                    JackTokenizer.not_in_string(input_lines[current_line].partition("/*")):
                temp_line = input_lines[current_line].partition("/*")[0]
                if temp_line != "":
                    lines.append(temp_line)
                # i = current_line
                while "*/" not in input_lines[current_line]:
                    current_line += 1
                # so self.input_lines[i] contains */. check if it has more tokens or should be drop
                temp_line2 = input_lines[current_line].partition("*/")[2]
                # current_line = self.drop_white_space_from_command(line_list[0], 0)
                if temp_line2 != "":
                    lines.append(temp_line2)  # no need to add this line to the final input_line
                # drop the lines which are comments
            # lines = input_lines[0:current_line] + input_lines[i:]
            elif input_lines[current_line] != '':
                lines.append(input_lines[current_line])
            current_line += 1
            if len(input_lines) == current_line:
                flag = False
        return lines

    def delete_white_spaces(self, input_lines_arr: list) -> list:
        # making input_lines contains the lines which are not empty lines, and deleting inline comments from all lines
        number_of_lines = len(input_lines_arr)
        input_lines = []
        for i in range(number_of_lines):
            if i == number_of_lines:
                break
            if not self.is_inline_comment_or_empty_line(input_lines_arr, i):
                input_lines.append(self.drop_white_space_from_command(input_lines_arr, i))
        # drop comments in the formats: /* comment until closing */ , /** API comment */
        return self.drop_comments(input_lines)

    def is_identifier(self, current_token: str) -> bool:
        # check the first char is _ or string
        return current_token[0] == "_" or current_token[0].isalpha()

    def is_string_constant(self, current_token: str) -> bool:
        # it's a string constant if starts and ends with ""
        current_token = current_token.strip()
        return current_token[0] == '"' and current_token[-1] == '"' and len(current_token) >= 2

    def is_int(self, current_token: str) -> bool:
        return current_token[0].isdigit()  # assuming range validity of the number

    def lines_to_tokens(self, input_lines: list) -> list:
        """The tokens may be separated by an arbitrary number of space characters, newline characters, and comments,
        which are ignored."""
        tokens_list = []
        current_token = ""
        for line in input_lines:
            x = 5
            for char in line:
                # if char == '\t':
                #     continue
                """ every token is separate by either a symbol (or a new line, but every line ends with ; - a symbol),
                or a space, so in this cases we add the current_token to the tokens list with it's type, otherwise we 
                add the current char to the current_token because we're still on the same token"""
                if char in self.symbol_list:  # taking care of all the cases which char is symbol
                    if len(current_token) == 0:  # covering the case of symbol-symbol
                        if char == '<':
                            tokens_list.append(("&lt;", "symbol"))
                        elif char == '>':
                            tokens_list.append(("&gt;", "symbol"))
                        elif char == '"':
                            tokens_list.append(("&quot;", "symbol"))
                        elif char == '&':
                            tokens_list.append(("&amp;", "symbol"))
                        else:
                            tokens_list.append((char, "symbol"))
                        continue
                    elif current_token in self.keyword_list:
                        tokens_list.append((current_token, "keyword"))
                    elif self.is_identifier(current_token):
                        tokens_list.append((current_token, "identifier"))
                    elif self.is_string_constant(current_token):
                        # need to omit the " " following the instructions so take the substring written below
                        current_token = current_token.strip()
                        tokens_list.append((current_token[1:- 1], "stringConstant"))
                    elif self.is_int(current_token):
                        tokens_list.append((int(current_token), "integerConstant"))
                    else:
                        current_token += char
                        continue
                    # initializing current_token for finding the next time and adding the symbol to the tokens list
                    current_token = ""
                    if char == '<':
                        tokens_list.append(("&lt;", "symbol"))
                    elif char == '>':
                        tokens_list.append(("&gt;", "symbol"))
                    elif char == '"':
                        tokens_list.append(("&quot;", "symbol"))
                    elif char == '&':
                        tokens_list.append(("&amp;", "symbol"))
                    else:
                        tokens_list.append((char, "symbol"))
                elif char == " " or char == '\t':  # taking care of all the cases which char is a space
                    if current_token in self.keyword_list:
                        tokens_list.append((current_token, "keyword"))
                        current_token = ""
                    elif current_token != "" and self.is_int(current_token):
                        tokens_list.append((int(current_token), "integerConstant"))
                        current_token = ""
                    elif current_token != "" and current_token[0] != '"':
                        tokens_list.append((current_token, "identifier"))
                        current_token = ""
                    elif current_token != "" and current_token[0] == '"':
                        current_token += char
                    # else - ignore the space and move on
                else:
                    # otherwise... we add the current char to the current_token because we're still on the same token
                    current_token += char
        return tokens_list

    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        # Your code goes here!
        # A good place to start is:
        # input_lines = input_stream.read().splitlines()

        input_lines = input_stream.read().splitlines()  # making a list, and every item in the list is a line from the
        # delete all lines which is white space and all comments in the lines which are commands
        input_lines = self.delete_white_spaces(input_lines)
        # making a list of couples in the format of (token,type_of_token)
        self.tokens_list = self.lines_to_tokens(input_lines)  # make a list of tokens in the format (token, token_type)
        self.cur_token_index = 0
        self.line = None
        self.current_token = None
        if len(self.tokens_list) != 0:
            self.line = f"<{self.tokens_list[0][TOKEN_TYPE]}> {self.tokens_list[0][TOKEN]} </{self.tokens_list[0][TOKEN_TYPE]}>\n"
            self.current_token = self.tokens_list[self.cur_token_index][TOKEN]

    def has_more_tokens(self) -> bool:
        """Do  have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        # Your code goes here!
        return len(self.tokens_list) > self.cur_token_index

    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token.
        This method should be called if has_more_tokens() is true.
        Initially there is no current token.
        """
        # Your code goes here!
        self.cur_token_index += 1
        if self.has_more_tokens():
            self.line = f"<{self.tokens_list[self.cur_token_index][TOKEN_TYPE]}> {self.tokens_list[self.cur_token_index][TOKEN]} " \
                        f"</{self.tokens_list[self.cur_token_index][TOKEN_TYPE]}>\n"
            self.current_token = self.tokens_list[self.cur_token_index][TOKEN]

    def token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        # Your code goes here!
        current_token_couple = self.tokens_list[self.cur_token_index]
        return current_token_couple[TOKEN_TYPE]

    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT",
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO",
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        # Your code goes here!
        return self.current_token

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
        """
        # Your code goes here!
        return self.current_token

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
        """
        # Your code goes here!
        return self.current_token

    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
        """
        # Your code goes here!
        return self.current_token

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double
            quotes. Should be called only when token_type() is "STRING_CONST".
        """
        # Your code goes here!
        return self.current_token
