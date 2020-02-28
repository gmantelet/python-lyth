"""
This module contains the semantic analyzer.

The semantic analyzer parses an AST tree and maintains a symbol table.
"""
from __future__ import annotations

from enum import Enum
from typing import Any
from typing import Generator
from typing import NoReturn
from typing import Optional
from typing import Union

from lyth.compiler.ast import Node
from lyth.compiler.error import LythError
from lyth.compiler.error import LythSyntaxError
from lyth.compiler.parser import Parser
from lyth.compiler.symbol import Field
from lyth.compiler.symbol import Name
from lyth.compiler.symbol import SymbolType


class Context(Enum):
    """
    Defines the way some data are retrieved from the analyzer.

    In load mode, we consider variables as aliases and retrieve corresponding
    values from the symbol table.

    In store mode, we ask the analyzer to store the target of the AST node into
    the symbol table.
    """
    LOAD = "load"
    STORE = "store"


class Analyzer:
    """
    The semantic analyzer for a given source code.
    """
    def __init__(self, parser: Parser, scope: Optional[str] = None) -> None:
        """
        Instantiate a new analyzer object.

        The analyzer requires an instance of a parser on a source of
        characters. It can be anything that is an iterable, a generator that
        eventually raises StopIteration, as long as it returns AST nodes.

        The analyzer bootstraps its symbol table by placing a root node which
        is the module itself it is exploring.
        """
        self.parser: Parser = parser
        self.scope: str = scope or parser.lexer.scanner.filename
        self.table: Name = Name.root(self.scope, "root", SymbolType())
        self._stream: Generator[Any, None, None] = self._next()

    def __call__(self) -> Any:
        """
        Retrieve the next result from line or block of source code.

        It fetches the next statement or expression from line, or if line ends
        with a colon ':', the block of lines beginning by the same indent. If
        the end of line or block is reached, it returns the result it can
        interpret.

        For instance, if an expression is returned, it may return the result of
        the expression.
        """
        return next(self._stream)

    def __iter__(self) -> Analyzer:
        """
        Convenience method to make this instance interable.
        """
        return self

    def __next__(self) -> Any:
        """
        Convenience method to retrieve the next result in source code.

        This is used if you really need to use this instance as an iterator as
        I did in some of my test case for convenience. Otherwise, the instance
        is callable because it has practically only one meaning in life which
        is fetching the next result from line...
        """
        return next(self._stream)

    def _next(self) -> Any:
        """
        Try to analyze the AST node returned by the parser.
        """
        while True:
            try:
                yield self.visit(self.parser())

            except StopIteration:
                break

    def error(self, node: None, context: Context) -> NoReturn:
        """
        This instance could not process the corresponding AST node.
        """
        raise TypeError(f"Unsupported AST node {node.name.name}")

    def visit(self, node: Node, context: Context = Context.STORE) -> Any:
        """
        The entry point of this instance.

        It visits the root node provided as input by dispatching the call to
        the right method, depending on the name of the node being analyzed, or
        to an error function raising an Exception if the name cannot be handled
        by this instance.
        """
        return getattr(self, "visit_" + node.name.name.lower(), self.error)(node, context)

    def visit_add(self, node: Node, context: Context) -> int:
        """
        A node asking for an addition requires a result
        """
        left = self.visit(node.left, Context.LOAD)
        right = self.visit(node.right, Context.LOAD)
        return left + right

    def visit_div(self, node: Node, context: Context) -> float:
        """
        A node asking for an addition requires a result
        """
        left = self.visit(node.left, Context.LOAD)
        right = self.visit(node.right, Context.LOAD)
        return left / right

    def visit_immutableassign(self, node, context: Context) -> None:
        """
        An assign operator requesting immediate assistance.

        This method raises an exception if we try to reassign a value that is
        already present in the symbol table..
        """
        name = self.visit(node.left, Context.STORE)
        symbol = self.table.get((name, self.scope), None)

        if symbol is not None:
            raise LythSyntaxError(node.info, msg=LythError.REASSIGN_IMMUTABLE)

        else:
            self.table += Name(name, self.scope,
                               SymbolType(Field.UNKNOWN, Field.IMMUTABLE, self.visit(node.right, Context.LOAD)))

    def visit_mul(self, node: Node, context: Context) -> int:
        """
        A node asking for an addition requires a result
        """
        left = self.visit(node.left, Context.LOAD)
        right = self.visit(node.right, Context.LOAD)
        return left * right

    def visit_mutableassign(self, node, context: Context) -> None:
        """
        An assign operator to a mutable variable requests immediate assistance.
        """
        name = self.visit(node.left, Context.STORE)
        symbol = self.table.get((name, self.scope), None)

        if symbol is not None:
            symbol.type.value = self.visit(node.right, Context.LOAD)

        else:
            self.table += Name(name, self.scope,
                               SymbolType(Field.UNKNOWN, Field.MUTABLE, self.visit(node.right, Context.LOAD)))

    def visit_name(self, node: Node, context: Context) -> Union[str, int, Field]:
        """
        A variable requires its name to be returned.

        If the context is to store the result of an expression into a variable,
        usually writing a symbol to the symbol table, then this method returns
        a name.

        If the context is to load the value referenced by this name, usually
        reading a symbol from the symbol table, then this method returns the
        value in the symbol table (or return an error if the variable is
        referenced before it was assigned any value in the symbol table.)
        """
        if context is Context.STORE:
            return node.value

        symbol = self.table.get((node.value, self.scope), None)
        if symbol is None:
            raise LythSyntaxError(node.info, msg=LythError.VARIABLE_REFERENCED_BEFORE_ASSIGNMENT)

        return symbol.type.value

    def visit_noop(self, node: Node, context: Context) -> None:
        """
        No operation node requires no further action.
        """
        return None

    def visit_num(self, node: Node, context: Context) -> int:
        """
        A numeral node storing an integer.
        """
        return node.value

    def visit_sub(self, node: Node, context: Context) -> int:
        """
        A node asking for an addition requires a result
        """
        left = self.visit(node.left, Context.LOAD)
        right = self.visit(node.right, Context.LOAD)
        return left - right
