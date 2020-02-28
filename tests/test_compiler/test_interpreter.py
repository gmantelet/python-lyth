import enum

import pytest

from lyth.compiler.ast import Node
from lyth.compiler.interpreter import Interpreter
from lyth.compiler.lexer import Lexer
from lyth.compiler.parser import Parser
from lyth.compiler.scanner import Scanner
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


def test_interpreter():
    """
    Basic set of visiting nodes
    """
    interpreter = Interpreter()

    cmd = next(Parser(Lexer(Scanner("1 + 2\n"))))
    assert interpreter.visit(cmd) == 3

    cmd = next(Parser(Lexer(Scanner("1 * 2\n"))))
    assert interpreter.visit(cmd) == 2

    cmd = next(Parser(Lexer(Scanner("1 - 2\n"))))
    assert interpreter.visit(cmd) == -1

    cmd = next(Parser(Lexer(Scanner("\n"))))
    assert interpreter.visit(cmd) is None

    cmd = next(Parser(Lexer(Scanner("a\n"))))
    assert interpreter.visit(cmd) == 'a'
