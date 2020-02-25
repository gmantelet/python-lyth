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
            node = self.addition()

            if self.token is not None and self.token.symbol is Symbol.EOF:
                yield node
                break

            if self.token is not None and self.token.symbol is not Symbol.EOL:
                raise LythSyntaxError(self.token.info, msg=LythError.GARBAGE_CHARACTERS)

            yield node

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
            node = self.numeral()

        except LythSyntaxError as lse:
            if lse.msg is LythError.INCOMPLETE_LINE:
                return Node.noop()

            raise

        while True:
            token = next(self.lexer)

            if token in (Symbol.ADD, Symbol.SUB):
                node = Node(token, node, self.numeral())

            else:
                self.token = token
                break

        return node

    def numeral(self) -> Node:
        """
        Looking for a literal token to make it a numeral.

        Numeral does not expect the line to be terminated, or the source code
        to have an end. If it is the case, then an exception saying that it was
        unsuccessful is raised instead.

        If the token being parsed is not a literal of type value, then it also
        raises an exception saying the symbol is invalid and that it should be
        a numeral instead.
        """
        token = self.lexer()

        if token in (Symbol.EOF, Symbol.EOL):
            raise LythSyntaxError(token.info, msg=LythError.INCOMPLETE_LINE)

        elif token != Literal.VALUE:
            raise LythSyntaxError(token.info, msg=LythError.NUMERAL_EXPECTED)

        return Node(token)
