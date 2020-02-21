"""
This module defines Abstract Syntaxt Tree nodes
"""
from enum import Enum

from lyth.compiler.token import Literal
from lyth.compiler.token import Symbol


class NodeType(Enum):
    """
    """
    Add = Symbol.ADD
    Num = Literal.VALUE

    @classmethod
    def as_value(cls, symbol):
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
    def __init__(self, token, *nodes):
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

    def __repr__(self):
        """
        The string representing this node with the type fully spelled.
        """
        return f"{self.name}({', '.join([str(c) for c in self._children])})"

    def __str__(self):
        """
        The string representing this node.
        """
        return f"{self.name.name}({', '.join([str(c) for c in self._children])})"

    @property
    def left(self):
        """
        The left-hand member if this is a binary operator.
        """
        if len(self._children) == 2:
            return self._children[0]

        raise AttributeError("This node is a leaf. Please use 'value'")

    @property
    def right(self):
        """
        The right-hand member if this is a binary operator.
        """
        if len(self._children) == 2:
            return self._children[1]

        raise AttributeError("This node is a leaf. Please use 'value'")

    @property
    def value(self):
        """
        The single child node if this is not a binary operator.
        """
        if len(self._children) == 1:
            return self._children[0]

        raise AttributeError("This node is not a leaf. Please use 'left' and 'right'")
