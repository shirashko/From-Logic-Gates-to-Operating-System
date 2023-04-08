"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
import JackTokenizer


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    statement_keywords_list = ["let", "return", "if", "while", "do"]
    op = ['+', '-', '*', '/', "&amp;", '|', "&lt;", "&gt;", '=']

    def __init__(self, input_stream: JackTokenizer, output_stream) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        # Your code goes here!
        self.tokenizer = input_stream
        self.output = output_stream
        self.tab = ""

    def start_compile(self, name):
        self.output.write(self.tab + f"<{name}>\n")  # todo \n
        self.tab += "  "

    def end_compile(self, name):
        self.tab = self.tab[:-2]  # tabbing out
        self.output.write(self.tab + f"</{name}>\n")

    # """    def print(self):
    #         self.output.write('\n')
    #         self.output.write(self.tab + self.tokenizer.line)
    #         self.tokenizer.advance()"""
    def write_and_advance_n_times(self, n):
        for i in range(n):
            self.output.write(self.tab + self.tokenizer.line)
            self.tokenizer.advance()

    def compile_class(self) -> None:
        """Compiles a complete class."""
        # Your code goes here!

        # 'class' className '{' classVarDec* subroutineDec* '}'
        self.start_compile("class")
        for i in range(3):
            self.output.write(self.tab + self.tokenizer.line)
            self.tokenizer.advance()
        while self.tokenizer.current_token == "field" or self.tokenizer.current_token == "static":
            self.compile_class_var_dec()
        while self.tokenizer.current_token == "constructor" or self.tokenizer.current_token == "function" or \
                self.tokenizer.current_token == "method":
            self.compile_subroutine()
        self.write_and_advance_n_times(1)
        # self.output.write(self.tab + self.tokenizer.line)

        self.end_compile("class")

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        # Your code goes here!
        "('static'|'field') type varName (',' varName)* ';'"

        self.start_compile("classVarDec")

        while self.tokenizer.current_token != ";":
            self.output.write(self.tab + self.tokenizer.line)
            self.tokenizer.advance()

        # output ; symbol
        self.output.write(self.tab + self.tokenizer.line)
        self.tokenizer.advance()

        self.end_compile("classVarDec")

    """ we added this function"""

    def compile_subroutine_body(self) -> None:
        # '{' varDec* statements '}'
        self.start_compile("subroutineBody")
        # output '{'
        self.output.write(self.tab + self.tokenizer.line)
        self.tokenizer.advance()
        while self.tokenizer.current_token == "var":
            self.compile_var_dec()
        self.compile_statements()
        # output '}'
        self.output.write(self.tab + self.tokenizer.line)
        self.tokenizer.advance()
        self.end_compile("subroutineBody")

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        # Your code goes here!
        "('constructor'|'function'|'method') ('void'|type) subroutineName '(' parameterList ')' subroutineBody"
        self.start_compile("subroutineDec")
        for i in range(4):
            self.output.write(self.tab + self.tokenizer.line)
            self.tokenizer.advance()
        self.compile_parameter_list()

        # output ) symbol
        self.output.write(self.tab + self.tokenizer.line)
        self.tokenizer.advance()

        self.compile_subroutine_body()

        self.end_compile("subroutineDec")

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the
        enclosing "()".
        """
        "(type varName) (',' type varName)*)?"
        # Your code goes here!
        # todo what to do if ? -> 0 times
        self.start_compile("parameterList")
        # self.output.write("<parameterList>")
        # self.tab += "\t"
        # if self.tokenizer.current_token != ")":
        #     self.output.write('\n')
        while self.tokenizer.current_token != ")":
            self.output.write(self.tab + self.tokenizer.line)
            self.tokenizer.advance()
        self.end_compile("parameterList")

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        # Your code goes here!
        self.start_compile("varDec")

        while self.tokenizer.current_token != ";":
            self.output.write(self.tab + self.tokenizer.line)
            self.tokenizer.advance()

        # output ; symbol
        self.output.write(self.tab + self.tokenizer.line)
        self.tokenizer.advance()

        self.end_compile("varDec")

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing
        "{}".
        """
        "statment*"
        # Your code goes here!
        self.start_compile("statements")
        while self.tokenizer.current_token in self.statement_keywords_list:
            if self.tokenizer.current_token == "if":
                self.compile_if()
            elif self.tokenizer.current_token == "return":
                self.compile_return()
            elif self.tokenizer.current_token == "while":
                self.compile_while()
            elif self.tokenizer.current_token == "do":
                self.compile_do()
            else:  # let
                self.compile_let()

        self.end_compile("statements")

    def compile_do(self) -> None:
        """Compiles a do statement."""
        # Your code goes here!
        "'do' subroutineCall ';'"
        self.start_compile("doStatement")
        self.write_and_advance_n_times(1)
        # subroutineCall:
        "subroutineName '(' expressionList ')' | (className|varName)'.'subroutineName '(' expressionList ')' "
        while self.tokenizer.current_token != "(":
            self.output.write(self.tab + self.tokenizer.line)
            self.tokenizer.advance()
        self.write_and_advance_n_times(1)
        self.compile_expression_list()
        self.write_and_advance_n_times(2)  # output ')' of subroutineCall and ; of compile_do
        self.end_compile("doStatement")

    def compile_let(self) -> None:
        """Compiles a let statement."""
        # Your code goes here!
        "'let' varName ('[' expression ']')? '=' expression ';'"
        self.start_compile("letStatement")
        self.write_and_advance_n_times(2)  # output let varName
        if self.tokenizer.current_token == '[':
            self.write_and_advance_n_times(1)
            self.compile_expression()
            self.write_and_advance_n_times(1)
        self.write_and_advance_n_times(1)
        self.compile_expression()
        self.write_and_advance_n_times(1)
        self.end_compile("letStatement")

    def compile_while(self) -> None:
        """Compiles a while statement."""
        # Your code goes here!
        "'while' '(' expression ')' '{' statements '}'"
        self.start_compile("whileStatement")
        self.write_and_advance_n_times(2)
        self.compile_expression()
        self.write_and_advance_n_times(2)
        self.compile_statements()
        self.write_and_advance_n_times(1)
        self.end_compile("whileStatement")

    def compile_return(self) -> None:
        """Compiles a return statement."""
        # Your code goes here!
        "'return' expression?';'"
        self.start_compile("returnStatement")
        self.write_and_advance_n_times(1)
        if self.tokenizer.current_token != ";":
            self.compile_expression()
        self.write_and_advance_n_times(1)  # output ;
        self.end_compile("returnStatement")

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        # Your code goes here!
        "'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}' )?"
        self.start_compile("ifStatement")
        # output if (
        for i in range(2):
            self.output.write(self.tab + self.tokenizer.line)
            self.tokenizer.advance()
        self.compile_expression()  # todo compile_expression
        for i in range(2):
            self.output.write(self.tab + self.tokenizer.line)
            self.tokenizer.advance()
        self.compile_statements()
        # output '}'
        self.output.write(self.tab + self.tokenizer.line)
        self.tokenizer.advance()
        if self.tokenizer.current_token == "else":
            for i in range(2):  # output else {
                self.output.write(self.tab + self.tokenizer.line)
                self.tokenizer.advance()
            self.compile_statements()
            # output '}'
            self.output.write(self.tab + self.tokenizer.line)
            self.tokenizer.advance()

        self.end_compile("ifStatement")

    def compile_expression(self) -> None:
        """Compiles an expression."""
        """ term (op term)*"""
        self.start_compile("expression")
        self.compile_term()
        while self.tokenizer.current_token in CompilationEngine.op:
            self.write_and_advance_n_times(1)
            self.compile_term()
        self.end_compile("expression")

    def compile_term(self) -> None:
        """Compiles a term.
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """
        """"integerConstant|stringConstant|keywordConstant|varName|varName'['expression']'|subroutineCall|
        '('expression')'| unaryOp term """

        self.start_compile("term")
        if self.tokenizer.current_token == "(":  # '('expression')'
            self.write_and_advance_n_times(1)
            self.compile_expression()
            self.write_and_advance_n_times(1)
        elif self.tokenizer.current_token in ["~", "-", "^", "#"]:  # unaryOp term
            self.write_and_advance_n_times(1)
            self.compile_term()
        else:
            self.write_and_advance_n_times(1)
        if self.tokenizer.current_token == "[":  # varName'['expression']'
            self.write_and_advance_n_times(1)
            self.compile_expression()
            self.write_and_advance_n_times(1)
        elif self.tokenizer.current_token == "(" or self.tokenizer.current_token == ".":  # subroutineCall
            "subroutineName '(' expressionList ')' | (className|varName)'.'subroutineName '(' expressionList ')' "
            while self.tokenizer.current_token != "(":
                self.output.write(self.tab + self.tokenizer.line)
                self.tokenizer.advance()
            self.write_and_advance_n_times(1)
            self.compile_expression_list()
            self.write_and_advance_n_times(1)  # output ')' of subroutineCall

        self.end_compile("term")

    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        # Your code goes here!

        "(expression(',' expression)*)?"
        # check if current token is ')', and if it does it means there isn't an expression so do nothing
        self.start_compile("expressionList")
        if self.tokenizer.current_token != ')':
            self.compile_expression()
            while self.tokenizer.current_token == ',':
                self.write_and_advance_n_times(1)
                self.compile_expression()
        self.end_compile("expressionList")
