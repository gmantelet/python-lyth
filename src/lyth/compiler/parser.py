"""
This module contains the parser.

The Parser uses the Lexer to retrieve a series of tokens, and based on these
tokens, it performs syntax analysis. It should give an Abstract Syntax Tree in
the end.
"""
from __future__ import annotations

from typing import Generator

from lyth.compiler.ast import Node
from lyth.compiler.error import LythError
from lyth.compiler.error import LythSyntaxError
from lyth.compiler.lexer import Lexer
from lyth.compiler.token import Literal
from lyth.compiler.token import Symbol
from lyth.compiler.token import Token


class Parser:
    """
    The syntax analyzer for a given source code.
    """
    def __init__(self, lexer: Lexer) -> None:
        """
        Instantiate a new parser object.

        The lexer requires an instance of a lexer on a source of characters.
        It can be anything that is an iterable, a generator that eventually
        raises StopIteration, as long as it returns tokens.
        """
        self.lexer: Lexer = lexer
        self.token: Token = None
        self._stream: Generator[Token, None, None] = self._next()

    def __call__(self) -> Node:
        """
        Retrieve the next AST node from block of source code.

        It fetches the next node from line, or if line ends with a colon ':',
        the block of lines beginning by the same indent. If the end of line or
        block is reached, it returns the node.
        """
        return next(self._stream)

    def __iter__(self) -> Lexer:
        """
        Convenience method to make this instance interable.
        """
        return self

    def __next__(self) -> Node:
        """
        Convenience method to retrieve the next token in source code.

        This is used if you really need to use this instance as an iterator as
        I did in some of my test case for convenience. Otherwise, the instance
        is callable because it has practically only one meaning in life which
        is fetching the next node from line...
        """
        return next(self._stream)

    def _next(self) -> Node:
        """
        Looking for an expression, starting with addition first, which has no
        preemption.
        """
        while True:
            try:
                node = self.expression()

            except StopIteration:
                break

            yield node
            self.token = None

    def addition(self) -> Node:
        """
        Looking for a token that could lead to an addition or a substraction.

        It returns the result of a numeral, or a chain of additions. If an
        unexpected symbol is discovered while itself is fetching the next
        token, then it saves the token and return the current node.

        If the left member is an end of line or an end of file, then it means
        that we are starting with an empty line, and in this case, a Noop node
        is being returned.
        """
        try:
            node = self.multiplication()

        except LythSyntaxError as lse:
            if lse.msg is LythError.INCOMPLETE_LINE:
                return Node.noop()

            raise

        while True:
            token = self.token or next(self.lexer)

            if token in (Symbol.ADD, Symbol.SUB):
                self.token = None
                node = Node(token, node, self.multiplication())

            else:
                self.token = token
                break

        return node

    def expression(self, end: Symbol = Symbol.EOL) -> Node:
        """
        Looking for a line that could lead to an expression, that is, a series
        of operations.

        There should be one expression per line, or one expression per pair of
        parentheses. This is why this method is not a while loop.

        The end parameter determines the token the expression expects to stop.
        In some cases, expression is started by an opening parenthesis, then
        the method should have been called with an expected right parenthesis
        to stop it. The default token otherwise is the end of a line as multi
        line is not yet supported by lyth.
        """
        node = self.addition()

        if self.token is not None and self.token.symbol is not end:
            raise LythSyntaxError(node.info, msg=LythError.GARBAGE_CHARACTERS)

        self.token = None
        return node

    def multiplication(self) -> Node:
        """
        Looking for a token that could lead to a multiplication or a form of
        division.

        It returns the result of a literal, or a chain of multiplication. It
        takes precedence over additions. If an unexpected symbol is discovered,
        as it can be for example an addition which is less prioritary than it,
        then it saves it and return the current node it is working on, that may
        be a literal.
        """
        node = self.literal()

        while True:
            token = self.token or next(self.lexer)

            if token in (Symbol.MUL, Symbol.DIV, Symbol.CEIL):
                self.token = None
                node = Node(token, node, self.literal())

            else:
                self.token = token
                break

        return node

    def literal(self) -> Node:
        """
        Looking for a literal token to make it a numeral, or a name.

        Literal does not expect the line to be terminated, or the source code
        to have an end. If it is the case, then an exception saying that it was
        unsuccessful is raised instead.

        If the token is an opening parenthesis, then the corresponding node to
        return will not be a literal, rather a new expression needs to be
        evaluated.

        If the token being parsed is not a literal of type value, then it also
        raises an exception saying the symbol is invalid and that it should be
        a literal instead.
        """
        token = self.lexer()

        if token in (Symbol.EOF, Symbol.EOL):
            raise LythSyntaxError(token.info, msg=LythError.INCOMPLETE_LINE)

        elif token == Symbol.LPAREN:
            print("Detected left parenthesis")
            return self.expression(end=Symbol.RPAREN)

        elif token not in (Literal.VALUE, Literal.STRING):
            raise LythSyntaxError(token.info, msg=LythError.LITERAL_EXPECTED)

        return Node(token)
