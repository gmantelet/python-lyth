"""
This module contains the parser.

The Parser uses the Lexer to retrieve a series of tokens, and based on these
tokens, it performs syntax analysis. It should give an Abstract Syntax Tree in
the end.
"""
from __future__ import annotations

from typing import Generator
from typing import List
from typing import Optional
from typing import Tuple

from lyth.compiler.ast import Node
from lyth.compiler.ast import NodeType
from lyth.compiler.error import LythError
from lyth.compiler.error import LythSyntaxError
from lyth.compiler.lexer import Lexer
from lyth.compiler.token import Keyword
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
        self.indent = 0
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
        Looking for an assignment, starting with an expression first.
        """
        while True:
            try:
                node = self.assign()

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

    def assign(self) -> Node:
        """
        Based on a left-member expression, check that we are dealing with an
        assign, be mutable or immutable.

        This method first looks for an expression. If the expressions exits,
        then it has likely stored a token. We match this token against an
        assign operator ('<-' or '->'). If the token does not match, then we
        return the expression node.

        The expression expects to fill out the line, so the next token should
        be something like EOL. If it is not, but it is an assign operator,
        either '<-' or '->' then this method evaluates an assignment instead.

        If the operator is a left assign, a variable, that must be a name, and
        not an expressed is being assigned an expression (or a literal).

        If the operator is a right assign, then an expression (or a literal) is
        assigned to an immutable name. If name fails, for instance there is an
        expression, or if the token after is not an end of line, then an error
        is returned.

        If there is no assign operator, this method makes sure that there is no
        let keyword leading the orphan expression.
        """
        node, let = self.let()  # There can be an optional let in assign statement.

        if self.token is not None and self.token == Symbol.LASSIGN:
            if node.name not in (NodeType.Name, NodeType.Let):
                raise LythSyntaxError(node.info, msg=LythError.LEFT_MEMBER_IS_EXPRESSION)

            else:
                token = self.token
                self.token = None
                node = Node(token, node, self.expression())

        elif self.token is not None and self.token == Symbol.RASSIGN:
            token = self.token
            self.token = None
            node = Node(token, self.name(), node)

            if next(self.lexer) != Symbol.EOL:
                raise LythSyntaxError(node.info, msg=LythError.GARBAGE_CHARACTERS)

        elif let and node.name != NodeType.Class:
            raise LythSyntaxError(let.info, msg=LythError.LET_ON_EXPRESSION)

        return Node(let, node) if let is not None else node

    def block(self) -> List[Node]:
        """
        Processing a list of indented statements following a colon.

        Original token is provided as parameter to help this method wraps the
        node around the token, fill its statement attribute and return it. For
        this, the block method requires the node constructor, and the token.
        """
        statements = []
        self.indent += 1

        while True:
            new_token = self.token or self.lexer()

            if new_token == Symbol.EOL:
                self.token = None
                continue

            if new_token == Symbol.EOF:
                self.token = new_token
                return statements

            if new_token != Symbol.INDENT:
                raise LythSyntaxError(new_token.info, msg=LythError.INCONSISTENT_INDENT)

            if new_token.lexeme <= self.indent - 1:
                self.indent = new_token.lexeme
                self.token = new_token
                return statements

            if new_token.lexeme != self.indent:
                raise LythSyntaxError(new_token.info, msg=LythError.INCONSISTENT_INDENT)

            statements.append(self.assign())


    def classdef(self, name: Node, end: Symbol = Symbol.EOL) -> Node:
        """
        Looking for a class definition.

        Causes to fetch the block and append to the class node that is built
        subsequent lines of codes until the next dedent.
        """
        token = self.token or next(self.lexer)

        if token == Keyword.BE:
            self.token = next(self.lexer)
            type_node = Node.typedef(self.name())
            token = next(self.lexer)

        else:
            # node = Node.classdef(name)
            type_node = None

        if token != Symbol.COLON:
            raise LythSyntaxError(node_type.info, msg=LythError.GARBAGE_CHARACTERS)

        self.token = None
        try:
            node = Node.classdef(name, type_node, *self.block())

        except StopIteration:
            raise

        return node

    def docstring(self) -> None:
        """
        This version does not do anything with docstrings.
        """
        token = self.lexer()

        while token != Symbol.DOC:
            token = self.lexer()

    def expression(self, end: Symbol = Symbol.EOL) -> Node:
        """
        Looking for a line that could lead to an expression, that is, a series
        of operations.

        There should be one expression per line, or one expression per pair of
        parentheses. This is why this method is not a while loop.

        Expression raises an Exception if it detects trailing characters. The
        exception however, is bypassed in case of an assignment. In this case,
        the expression returns the node, and the current assignment token for
        the assign method to run.

        The end parameter determines the token the expression expects to stop.
        In some cases, expression is started by an opening parenthesis, then
        the method should have been called with an expected right parenthesis
        to stop it. The default token otherwise is the end of a line as multi
        line is not yet supported by lyth.
        """
        node = self.addition()

        if self.token in (Symbol.LASSIGN, Symbol.RASSIGN):
            return node

        elif node.name == NodeType.Name and self.token in (Symbol.COLON, Keyword.BE):
            return self.classdef(node)

        elif self.token is not None and self.token.symbol is not end:
            print(node)
            print(self.token)
            raise LythSyntaxError(node.info, msg=LythError.GARBAGE_CHARACTERS)

        self.token = None
        return node

    def let(self) -> Tuple[Node, Optional[Token]]:
        """
        Is there any let keyword that wants to come out?

        Let keyword declares a node to be declared publicly in our tree of
        symbol. It can be an assign, a class, an enum, a struct etc. or even a
        list of them.
        """
        token = self.lexer()
        if token == Keyword.LET:

            next_token = self.lexer()

            #
            # 1. Multiple statements let
            #
            if next_token == Symbol.COLON:
                eol = self.lexer()

                if eol != Symbol.EOL:
                    raise LythSyntaxError(eol.info, msg=LythError.GARBAGE_CHARACTERS)

                return Node(token, *self.block()), None

            #
            # 2. Single statement let
            #
            self.token = next_token
            return self.expression(), token

        #
        # 3. No let detected
        #
        self.token = token
        return self.expression(), None

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

        The token may already have been scanned by let. In all cases the
        current token, even if none, must be consumed, otherwise the expression
        will evaluate with a literal token.
        """
        token = self.token or self.lexer()
        self.token = None
        if token in (Symbol.EOF, Symbol.EOL):
            raise LythSyntaxError(token.info, msg=LythError.INCOMPLETE_LINE)

        elif token == Symbol.LPAREN:
            return self.expression(end=Symbol.RPAREN)

        elif token == Symbol.DOC:
            self.docstring()
            return self.literal()

        elif token not in (Literal.VALUE, Literal.STRING):
            raise LythSyntaxError(token.info, msg=LythError.LITERAL_EXPECTED)

        return Node(token)

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

            if token in (Symbol.MUL, Symbol.DIV, Symbol.FLOOR):
                self.token = None
                node = Node(token, node, self.literal())

            else:
                self.token = token
                break

        return node

    def name(self) -> Node:
        """
        Looking for a name token.

        Literal does not expect the line to be terminated, or the source code
        to have an end. If it is the case, then an exception saying that it was
        unsuccessful is raised instead.
        """
        token = self.token or self.lexer()

        if token in (Symbol.EOF, Symbol.EOL):
            raise LythSyntaxError(token.info, msg=LythError.INCOMPLETE_LINE)

        elif token != Literal.STRING:
            raise LythSyntaxError(token.info, msg=LythError.NAME_EXPECTED)

        return Node(token)
