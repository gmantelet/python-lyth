"""
This module contains the parser.

The Parser uses the Lexer to retrieve a series of tokens, and based on these
tokens, it performs syntax analysis. It should give an Abstract Syntax Tree in
the end.
"""
from lyth.compiler.ast import Node
from lyth.compiler.error import LythError
from lyth.compiler.error import LythSyntaxError
from lyth.compiler.token import Literal
from lyth.compiler.token import Symbol


class Parser:
    """
    The syntax analyzer for a given source code.
    """
    def __init__(self, lexer):
        """
        Instantiates a new parser object.

        Attributes:
            lexer   (Lexer)  : An instance of a lexer.
            tokens  (list)   : Keeping track of past tokens when a miss is
                               detected.
        """
        self.lexer = lexer
        self.tokens = []

    def __call__(self, text, source="<stdin>"):
        """
        Starts the syntax analysis on the source code provided as parameter.

        It bootstraps the Lexer, making it an iterable, ready to use its
        scanner and produce a series of tokens. It also makes the parser an
        iterable, ready to call next upon.
        """
        self.lexer(text, source)

    def __iter__(self):
        """
        Make this analyzer iterable.
        """
        return self

    def __next__(self):
        """
        Produces the next AST node from analyzed source code.

        Each iteration is a line or a block of code. A block of code is started
        with ':' and ended when the indent decreases.
        """
        return self.expression()

    def addition(self):
        """
        Looking for a plus or a minus sign.

        It returns the result of a numeral, or a chain of additions and
        multiplication nodes.
        """
        return self.binaryop(self.multiplication(), Symbol.ADD, Symbol.SUB)

    def expression(self):
        """
        Looking for an expression, starting with addition first, which has no
        preemption.
        """
        return self.addition()

    def multiplication(self):
        """
        Looking for a multiplier or a divider sign.

        It returns the result of a numeral, or a chain of multiplication nodes.
        """
        return self.binaryop(self.numeral(), Symbol.MUL, Symbol.DIV, Symbol.CEIL)

    def numeral(self):
        """
        Looking for a numeral.

        A numeral can be of the following form: '5', '+5', '-5'.
        1. If a sign is found while looking for a value, then next token should
           be a numeral. Affect its lexeme if it is a minus sign.
        2. End of file has been encountered while looking for a value. This is
           a syntax error.
        3. Non value tokens means we deal with something that is not a numeral.
        """
        token = next(self.lexer)

        if token == Symbol.EOF:
            raise LythSyntaxError(token.info, msg=LythError.INCOMPLETE_LINE)

        elif token != Literal.VALUE:
            raise LythSyntaxError(token.info, msg=LythError.NUMERAL_EXPECTED)

        return Node(token)

    def binaryop(self, node, *operators):
        """
        Looking for a specific set of operators.

        The method follows this recipe:
        1. Fetch the next token
        2. If the token is the expected one: for example, '*', '/', '//', then
           process and look for a right member, which should be a numeral, and
           go back to step 1.
        2. If it this is "something else", for instance a '+', an '=', an '=='
           operator, push it to the stack, and return the left member instead.
        """
        while True:
            try:
                token = self.tokens.pop()

            except IndexError:
                self.tokens.append(next(self.lexer))
                continue

            if token in operators:
                node = Node(token, node, self.numeral())

            else:
                self.tokens.append(token)
                break

        return node
