"""
This module defines the interpreter.
"""
from typing import Any
from typing import NoReturn

from lyth.compiler.ast import Node


class Interpreter:
    """
    An interpreter for consoles that works on a list of nodes.

    This is an interpreter for a console emulating some target hardware. It is
    simple debug interpreter to play with code a bit. The real stuff is defined
    in the other class of this module...
    """
    def visit_add(self, node: Node) -> int:
        """
        A node asking for an addition requires a result
        """
        return self.visit(node.left) + self.visit(node.right)

    def visit_mul(self, node: Node) -> int:
        """
        A node asking for a multiplication requires a result
        """
        return self.visit(node.left) * self.visit(node.right)

    def visit_name(self, node: Node) -> str:
        """
        A variable requires its name to be returned.
        """
        return node.value

    def visit_noop(self, node: Node) -> None:
        """
        No operation node requires no further action.
        """
        return None

    def visit_num(self, node: Node) -> int:
        """
        A numeral node storing an integer.
        """
        return node.value

    def visit_sub(self, node: Node) -> int:
        """
        A node asking for a substraction requires a result
        """
        return self.visit(node.left) - self.visit(node.right)

    def visit(self, node: Node) -> Any:
        """
        The entry point of this instance.

        It visits the root node provided as input by dispatching the call to
        the right method, depending on the name of the node being analyzed, or
        to an error function raising an Exception if the name cannot be handled
        by this instance.
        """
        return getattr(self, "visit_" + node.name.name.lower(), self.error)(node)

    def error(self, node: None) -> NoReturn:
        """
        This instance could not process the corresponding AST node.
        """
        raise TypeError(f"Unsupported AST node {node.name.name}")
