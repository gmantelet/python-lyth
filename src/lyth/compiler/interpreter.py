"""
This module defines the interpreter.

"""


class Interpreter:

    def visit_add(self, node):
        return self.visit(node.left) + self.visit(node.right)

    def visit_noop(self, node):
        return None

    def visit_mul(self, node):
        return self.visit(node.left) * self.visit(node.right)

    def visit_num(self, node):
        return node.value

    def visit_sub(self, node):
        return self.visit(node.left) - self.visit(node.right)

    def visit(self, node):
        return getattr(self, "visit_" + node.name.name.lower(), self.error)(node)

    def error(self, node):
        raise TypeError(f"Unsupported AST node {node.name.name}")
