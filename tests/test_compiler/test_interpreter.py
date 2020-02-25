import enum

import pytest

from lyth.compiler.ast import Node
from lyth.compiler.interpreter import Interpreter
from lyth.compiler.token import Token
from lyth.compiler.token import TokenInfo


class Dummy(enum.Enum):
    DUMMY = "!!!"


def test_wrong_node():
    """
    """
    node = Node(Token("+", TokenInfo("test_interpreter.py", 0, 0, "!!!")))
    node.name = Dummy.DUMMY

    interpreter = Interpreter()

    with pytest.raises(TypeError) as err:
        interpreter.visit(node)

    assert str(err.value) == "Unsupported AST node DUMMY"
