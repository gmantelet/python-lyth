import pytest

from lyth.compiler.ast import NodeType
from lyth.compiler.error import LythError
from lyth.compiler.error import LythSyntaxError
from lyth.compiler.lexer import Lexer
from lyth.compiler.parser import Parser
from lyth.compiler.scanner import Scanner


def test_parser_addition():
    """
    To validate the parser returns the right AST node.
    """
    parser = Parser(Lexer(Scanner("1 + 2 + 3\n")))

    expr = next(parser)
    assert expr.name == NodeType.Add
    assert str(expr) == "Add(Add(Num(1), Num(2)), Num(3))"

    expr = next(parser)
    assert expr.name == NodeType.Noop
    assert str(expr) == "Noop()"


def test_parser_invalid_expression():
    """
    To validate the parser detects the expression it evaluates is invalid.
    """
    parser = Parser(Lexer(Scanner("1 + 2 + /\n")))

    with pytest.raises(LythSyntaxError) as err:
        next(parser)

    assert err.value.msg is LythError.NUMERAL_EXPECTED
    assert err.value.filename == "<stdin>"
    assert err.value.lineno == 0
    assert err.value.offset == 8
    assert err.value.line == "1 + 2 + /"


def test_parser_invalid_line():
    """
    To validate the parser detects the presence of an missing numeral in
    expression
    """
    parser = Parser(Lexer(Scanner("1 + 2 +\n")))

    with pytest.raises(LythSyntaxError) as err:
        next(parser)

    assert err.value.msg is LythError.INCOMPLETE_LINE
    assert err.value.filename == "<stdin>"
    assert err.value.lineno == 0
    assert err.value.offset == 6
    assert err.value.line == "1 + 2 +"
