"""
This module defines Abstract Syntaxt Tree nodes
"""
from __future__ import annotations

from enum import Enum
from types import SimpleNamespace
from typing import Optional
from typing import Union

from lyth.compiler.token import Literal
from lyth.compiler.token import Symbol
from lyth.compiler.token import Token
from lyth.compiler.token import TokenInfo


class NodeType(Enum):
    """
    Provides a list of all the valid AST nodes an interpreter must be able to
    visit.
    """
    Add = Symbol.ADD
    Mul = Symbol.MUL
    Num = Literal.VALUE
    Noop = None
    Sub = Symbol.SUB

    @classmethod
    def as_value(cls, symbol: Optional[str]) -> NodeType:
        """
        Return the enumeration type based on the symbol provided or None if the
        symbol is not in the enumeration.
        """
        return cls._value2member_map_.get(symbol)


class Node:
    """
    A generic AST node.

    AST nodes may differ. For the sake of simplicity, we consider that the AST
    node has only two main attributes 'key' and '_children', were _children is
    a list of children nodes, or, if the node is a leaf, like with numerals,
    then this is the lexeme stored in the corresponding token.

    The set of properties help specialize nodes. For example, if the node is a
    leaf, then we expect the use of 'value', when it is a binary operator, then
    usually, it has a left and a right member.

    Last but not least, the AST node stores metadata coming from the token,
    such as the filename, the line number and the column in corresponding
    source code.
    """
    def __init__(self, token: Token, *nodes: Optional[Node]) -> Node:
        """
        Instantiate a new AST Node object.

        Arguments:
            token: The token causing this node to be instantiated
            nodes: A list of children AST nodes.
        """
        self.name = NodeType.as_value(token.symbol)
        self._children = nodes if nodes else (token.lexeme, )

        self.filename = token.info.filename
        self.lineno = token.info.lineno
        self.offset = token.info.offset
        self.line = token.info.line

    @classmethod
    def noop(cls) -> Node:
        """
        A no operation AST node.

        When the parser deciphers an empty line, rather than returning None, it
        returns this AST node instead.
        """
        info = SimpleNamespace(filename='noop', lineno=-1, offset=-1, line='')
        ns = SimpleNamespace(symbol=None, lexeme='', info=info)
        return cls(ns)

    def __repr__(self) -> str:
        """
        The string representing this node with the type fully spelled.
        """
        return f"{self.name}({', '.join([str(c) for c in self._children])})"

    def __str__(self) -> str:
        """
        The string representing this node.
        """
        return f"{self.name.name}({', '.join([str(c) for c in self._children])})"

    @property
    def info(self) -> TokenInfo:
        """
        Returns the original token information.
        """
        return TokenInfo(self.filename, self.lineno, self.offset, self.line)

    @property
    def left(self) -> Union[Node, Union[int, str]]:
        """
        The left-hand member if this is a binary operator.
        """
        if len(self._children) == 2:
            return self._children[0]

        raise AttributeError("This node is a leaf. Please use 'value'")

    @property
    def right(self) -> Union[Node, Union[int, str]]:
        """
        The right-hand member if this is a binary operator.
        """
        if len(self._children) == 2:
            return self._children[1]

        raise AttributeError("This node is a leaf. Please use 'value'")

    @property
    def value(self) -> Union[Node, Union[int, str]]:
        """
        The single child node if this is not a binary operator.
        """
        if len(self._children) == 1:
            return self._children[0]

        raise AttributeError("This node is not a leaf. Please use 'left' and 'right'")
