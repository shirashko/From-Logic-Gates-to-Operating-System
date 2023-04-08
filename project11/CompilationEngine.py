"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
from JackTokenizer import JackTokenizer
from SymbolTable import SymbolTable
from VMWriter import VMWriter


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    statement_keywords_list = ["let", "return", "if", "while", "do"]
    binary_op = ['+', '-', '*', '/', "&amp;", '|', "&lt;", "&gt;", '=']
    unary_op = ['~', '-', '#', '^']
    subroutines = ['method', 'function', 'constructor']
    class_scope_var = ['static', 'field']
    os_op_dict = {'*': 'Math.multiply', '/': 'Math.divide'}
    primitive_binary_op_dict = {'+': 'ADD', '-': 'SUB', '&amp': 'AND', '|': 'OR', "&lt": 'LT', "&gt": "GT", "=": "EQ"}
    primitive_unary_op_dict = {"~": "NOT", "-": "NEG", "^": "SHIFTLEFT", "#": "SHIFTRIGHT"}

    def __init__(self, input_stream: JackTokenizer, output_stream) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        # Your code goes here!
        self.input = input_stream
        self.vm_writer = VMWriter(output_stream)
        self.symbol_table = SymbolTable()
        self.class_name = None
        self.cur_subroutine_name = None
        self.cur_subroutine_type = None
        self.n_locals_cur_subroutine = None
        self.labels_index = 0
        self.num_of_arguments_in_cur_call = 0

    def compile_class(self) -> None:
        """Compiles a complete class."""
        # Your code goes here!
        # 'class' className '{' classVarDec* subroutineDec* '}'
        self.input.advance()  # skip 'class'
        self.class_name = self.input.current_token
        self.input.advance()  # skip 'className'
        self.input.advance()  # skip '{'
        while self.input.current_token in self.class_scope_var:
            self.compile_class_var_dec()
        while self.input.current_token in self.subroutines:
            self.compile_subroutine()
        self.input.advance()  # skip '}'

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        # Your code goes here!
        "('static'|'field') type varName (',' varName)* ';'"
        # no need to emit anything, just add to the symbol table
        kind = self.input.current_token
        self.input.advance()
        _type = self.input.current_token
        self.input.advance()
        name = self.input.current_token
        self.input.advance()
        self.symbol_table.define(name, _type, kind)
        while self.input.current_token == ",":
            self.input.advance()  # skip ','
            name = self.input.current_token
            self.input.advance()
            self.symbol_table.define(name, _type, kind)
        self.input.advance()  # skip ';'

    """ we added this function"""

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        # Your code goes here!
        "('constructor'|'function'|'method') ('void'|type) subroutineName '(' parameterList ')' subroutineBody"

        self.cur_subroutine_type = self.input.current_token
        self.input.advance()
        self.input.advance()
        self.cur_subroutine_name = self.input.current_token
        self.input.advance()
        self.input.advance()  # skip '(
        self.compile_parameter_list()
        self.input.advance()  # skip ')'
        # subroutineBody - '{' varDec* statements '}'
        self.input.advance()  # skip '{'
        while self.input.current_token == "var":
            self.compile_var_dec()
        self.vm_writer.write_function(f"{self.class_name}.{self.cur_subroutine_name}", self.n_locals_cur_subroutine)
        if self.cur_subroutine_type == 'constructor':
            self.vm_writer.write_push("CONST", self.symbol_table.var_counter("FIELD"))
            self.vm_writer.write_call("Memory.alloc", 1)
            self.vm_writer.write_pop("POINTER", 0)
        elif self.cur_subroutine_type == 'method':
            self.symbol_table.define('this', self.class_name, "ARG")
            self.vm_writer.write_push("ARG", 0)
            self.vm_writer.write_pop("POINTER", 0)
        self.compile_statements()
        self.input.advance()  # skip '}'

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the
        enclosing "()".
        """
        "( (type varName) (',' type varName)* )?"
        # Your code goes here!
        # add arguments to the symbol table
        if self.input.current_token == ')':
            return
        flag_for_first_entry = True
        while flag_for_first_entry or self.input.current_token == ',':
            if flag_for_first_entry:
                flag_for_first_entry = False
            else:
                self.input.advance()  # skip ','
            _type = self.input.current_token
            self.input.advance()
            name = self.input.current_token
            self.input.advance()
            self.symbol_table.define(name, _type, 'ARG')

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        # Your code goes here!
        # 'var' type varName (',' varName)*';'

        self.input.advance()  # skip 'var'
        _type = self.input.current_token
        self.input.advance()
        name = self.input.current_token
        self.input.advance()
        self.symbol_table.define(name, _type, 'VAR')
        self.n_locals_cur_subroutine += 1
        while self.input.current_token == ',':
            self.input.advance()  # skip ','
            name = self.input.current_token
            self.input.advance()
            self.symbol_table.define(name, _type, 'VAR')
            self.n_locals_cur_subroutine += 1
        self.input.advance()  # skip ';'

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing
        "{}".
        """
        "statment*"
        # Your code goes here!
        while self.input.current_token in self.statement_keywords_list:
            if self.input.current_token == "if":
                self.compile_if()
            elif self.input.current_token == "return":
                self.compile_return()
            elif self.input.current_token == "while":
                self.compile_while()
            elif self.input.current_token == "do":
                self.compile_do()
            else:  # let
                self.compile_let()

    def subroutineCall(self) -> None:
        # subroutineName '(' expressionList ')' | (className|varName)'.'subroutineName '(' expressionList ')'
        name = self.input.current_token
        self.input.advance()  # skip 'name'
        if self.input.symbol() == '(':  # compiling the first case
            self.input.advance()  # skip '('
            self.compile_expression_list()
            self.input.advance()  # skip ')'
            self.vm_writer.write_call(self.class_name + '.' + name, self.num_of_arguments_in_cur_call)
            self.num_of_arguments_in_cur_call = 0
        else:  # we are in the second case
            self.input.advance()  # skip '.'
            if self.symbol_table.kind_of(name) is not None:  # it's a varName so it's a method
                self.num_of_arguments_in_cur_call = 1  # for passing the object address
                self.vm_writer.write_push(self.symbol_table.kind_of(name), self.symbol_table.index_of(name))
                sub_name = self.symbol_table.type_of(name) + '.' + self.input.current_token  # self.symbol_table.type
            else:  # it's a className
                sub_name = name + '.' + self.input.current_token
            self.input.advance()  # skip 'subroutineName'
            self.input.advance()  # skip '('
            self.compile_expression_list()
            self.input.advance()  # skip ')'
            self.vm_writer.write_call(sub_name, self.num_of_arguments_in_cur_call)
            self.num_of_arguments_in_cur_call = 0

    def compile_do(self) -> None:  # todo
        """Compiles a do statement."""
        # Your code goes here!
        "'do' subroutineCall ';'"
        self.input.advance()  # skip 'do'
        self.subroutineCall()
        self.input.advance()  # skip ';
        self.vm_writer.write_pop('TEMP', 0)

    def compile_let(self) -> None:
        """Compiles a let statement."""
        # Your code goes here!
        "'let' varName ('[' expression ']')? '=' expression ';'"

        self.input.advance()  # skip 'let'
        varName = self.input.current_token
        self.input.advance()  # skip 'varName'
        if self.input.current_token == '[':
            self.input.advance()  # skip '['
            self.vm_writer.write_push(self.symbol_table.kind_of(varName), self.symbol_table.index_of(varName))
            self.compile_expression()
            self.input.advance()  # skip ']'
            self.vm_writer.write_arithmetic("ADD")
            self.input.advance()  # skip '='
            self.compile_expression()
            self.input.advance()  # skip ';'
            self.vm_writer.write_pop("TEMP", 0)
            self.vm_writer.write_pop("POINTER", 1)
            self.vm_writer.write_push("TEMP", 0)
            self.vm_writer.write_pop("THAT", 0)
        else:
            self.input.advance()  # skip '='
            self.compile_expression()
            self.vm_writer.write_pop(self.symbol_table.kind_of(varName), self.symbol_table.index_of(varName))
            self.input.advance()  # skip ';'

    def compile_while(self) -> None:
        """Compiles a while statement."""
        # Your code goes here!
        "'while' '(' expression ')' '{' statements '}'"
        self.input.advance()  # skip 'while'
        self.input.advance()  # skip '('
        while_label = f"L{self.labels_index}"
        self.labels_index += 1
        after_loop_label = f"L{self.labels_index}"
        self.labels_index += 1
        self.vm_writer.write_label(while_label)
        self.compile_expression()
        self.input.advance()  # skip ')'
        self.vm_writer.write_arithmetic('NEG')
        self.vm_writer.write_if(after_loop_label)
        self.input.advance()  # skip '{'
        self.compile_statements()
        self.input.advance()  # skip '}'
        self.vm_writer.write_goto(while_label)
        self.vm_writer.write_label(after_loop_label)

    def compile_return(self) -> None:
        """Compiles a return statement."""
        # Your code goes here!
        "'return' expression?';'"
        # if it's a void method, it will have only 'return;'
        self.input.advance()  # skip 'return'
        if self.input.current_token == ";":  # it's a void function so we need to push constant zero #todo so need to
            # save that it's a void function like I did or it's redundant?
            self.vm_writer.write_push('CONST', 0)
        else:
            self.compile_expression()

        self.input.advance()  # skip ';'
        self.vm_writer.write_return()

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        # Your code goes here!
        "'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}' )?"
        # self.vm_writer.write_if()

        self.input.advance()  # skip 'if'
        self.input.advance()  # skip '('
        self.compile_expression()  # now the top value of the stack is true or false
        self.input.advance()  # skip ')'
        self.input.advance()  # skip '{'
        self.vm_writer.write_arithmetic('NEG')
        else_label = f"L{self.labels_index}"  # there isn't else for sure but doing it in case...
        self.labels_index += 1
        after_else_label = f"L{self.labels_index}"
        self.labels_index += 1
        self.vm_writer.write_if(else_label)
        self.compile_statements()
        self.input.advance()  # skip '}'
        self.vm_writer.write_goto(after_else_label)
        self.vm_writer.write_label(else_label)
        # if there is an else so do it here, else just goto after_else_label
        if self.input.current_token == "else":
            self.input.advance()  # skip 'else'
            self.input.advance()  # skip '{'
            self.compile_statements()
            self.input.advance()  # skip '}'
        self.vm_writer.write_label(after_else_label)
        # check if there is an else statements

    def compile_string_const_term(self, str) -> None:
        # create an object of type string
        self.vm_writer.write_push("CONST", len(str))
        self.vm_writer.write_call("String.new", 1)  # String.new takes as argument the number of memory blocks
        # needed to be allocated - one for each char. now the base address of the string object is on the top of the
        # stack
        for char in str:
            self.vm_writer.write_push("CONST", ord(char))
            self.vm_writer.write_call("String.appendChar", 2)  # taking the char (ascii) we want to add and the
            # string object we want to add it to. it returns the string address (I think)

    def compile_expression(self) -> None:
        """Compiles an expression."""
        """ term (op term)*"""
        self.compile_term()
        while self.input.current_token in self.binary_op:
            op = self.input.current_token
            self.input.advance()  # skip 'op'
            self.compile_term()
            if op in self.primitive_binary_op_dict:  # write arithmetic
                self.vm_writer.write_arithmetic(self.primitive_binary_op_dict[op])
            else:  # write call
                self.vm_writer.write_call(self.os_op_dict[op], 2)

    def compile_array_val_term(self, varName) -> None:
        self.input.advance()  # skip '['
        self.vm_writer.write_push(self.symbol_table.kind_of(varName), self.symbol_table.index_of(varName))  # push arr
        self.compile_expression()
        self.vm_writer.write_arithmetic('ADD')
        self.vm_writer.write_pop('POINTER', 1)
        self.vm_writer.write_push('THAT', 0)
        self.input.advance()  # skip ']'

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
        """"integerConstant|stringConstant|keywordConstant|varName|varName'['expression']'| '('expression')'| 
        unaryOp term | subroutineCall"""
        if self.input.token_type() == "INT_CONST":
            self.vm_writer.write_push("CONST", self.input.current_token)
            self.input.advance()
        elif self.input.token_type() == "STRING_CONST":
            self.compile_string_const_term(self.input.current_token)
            self.input.advance()
        elif self.input.token_type() in ['true', 'false', 'null', 'this']:
            if self.input.current_token == 'true':
                self.vm_writer.write_push("CONST", 1)
                self.vm_writer.write_arithmetic('NEG')
            elif self.input.current_token == 'this':
                self.vm_writer.write_push('POINTER', 0)
            else:  # null or false
                self.vm_writer.write_push("CONST", 0)
            self.input.advance()
        elif self.symbol_table.kind_of(self.input.current_token) is not None:  # it's a varName
            varName = self.input.current_token
            self.input.advance()
            if self.input.current_token == '[':  # it's an varName'['expression']'
                self.compile_array_val_term(varName)
            else:  # we are in the case of varName
                self.vm_writer.write_push(self.symbol_table.kind_of(varName), self.symbol_table.index_of(varName))
        elif self.input.current_token == '(':  # '('expression')'
            self.input.advance()  # skip '('
            self.compile_expression()
            self.input.advance()  # skip ')'
        elif self.input.current_token in self.unary_op:  # unaryOp term
            unary_op = self.input.current_token
            self.input.advance()
            self.compile_term()
            self.vm_writer.write_arithmetic(self.primitive_unary_op_dict[unary_op])
        else:  # subroutineCall
            self.subroutineCall()

    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        # Your code goes here!

        "(expression(',' expression)*)?"
        # check if current token is ')', and if it does it means there isn't an expression so do nothing
        if self.input.current_token != ')':
            self.num_of_arguments_in_cur_call += 1
            self.compile_expression()
            while self.input.current_token == ',':
                self.num_of_arguments_in_cur_call += 1
                self.input.advance()  # skip ','
                self.compile_expression()
