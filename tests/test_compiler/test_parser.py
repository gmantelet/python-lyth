import pytest

from lyth.compiler.ast import NodeType
from lyth.compiler.error import LythError
from lyth.compiler.error import LythSyntaxError
from lyth.compiler.lexer import Lexer
from lyth.compiler.parser import Parser
from lyth.compiler.scanner import Scanner


def test_parser_expression():
    """
    To validate the parser iterates properly over an expression.

    The last node on a properly formatted string should be No Op.
    """
    parser = Parser(Lexer(Scanner("1 + 2 + 3 \n")))

    for i in parser:
        pass

    assert i.name == NodeType.Noop
    assert str(i) == "Noop()"


def test_parser_assign():
    """
    To validate the parser iterates properly over a variable being assigned the
    result of an expression.
    """
    parser = Parser(Lexer(Scanner("a <- 1 + 2\n")))

    assign = parser()
    assert assign.name == NodeType.MutableAssign
    assert str(assign) == "MutableAssign(Name(a), Add(Num(1), Num(2)))"

    parser = Parser(Lexer(Scanner("b * 2 -> a\n")))

    assign = parser()
    assert assign.name == NodeType.ImmutableAssign
    assert str(assign) == "ImmutableAssign(Name(a), Mul(Name(b), Num(2)))"


def test_parser_let_assign():
    """
    To validate the parser iterates properly over a variable being assigned the
    result of an expression.
    """
    parser = Parser(Lexer(Scanner("let a <- 1 + 2\n")))

    assign = parser()
    assert assign.name == NodeType.Let
    assert str(assign) == "Let(MutableAssign(Name(a), Add(Num(1), Num(2))))"

    parser = Parser(Lexer(Scanner("let b * 2 -> a\n")))

    assign = parser()
    assert assign.name == NodeType.Let
    assert str(assign) == "Let(ImmutableAssign(Name(a), Mul(Name(b), Num(2))))"


def test_parser_multiple_let_assign():
    """
    To validate the parser iterates properly over a variable being assigned the
    result of an expression.
    """
    parser = Parser(Lexer(Scanner("let:\n  a <- 1 + 2\n  b <- a * 3\n\n")))

    assign = parser()
    assert assign.name == NodeType.Let
    assert str(assign) == "Let(MutableAssign(Name(a), Add(Num(1), Num(2))), MutableAssign(Name(b), Mul(Name(a), Num(3))))"


def test_parser_nested_let_assign():
    """
    To validate the parser solves nested let.
    """
    parser = Parser(Lexer(Scanner("let:\n  let:\n    a <- 1 + 2\n  b <- a * 3\n\n")))

    assign = parser()
    assert assign.name == NodeType.Let
    assert str(assign) == "Let(Let(MutableAssign(Name(a), Add(Num(1), Num(2)))), MutableAssign(Name(b), Mul(Name(a), Num(3))))"

    parser = Parser(Lexer(Scanner("let:\n  let:\n    a <- 1 + 2\n\n  b <- a * 3\n\n")))

    assign = parser()
    assert assign.name == NodeType.Let
    assert str(assign) == "Let(Let(MutableAssign(Name(a), Add(Num(1), Num(2)))), MutableAssign(Name(b), Mul(Name(a), Num(3))))"


def test_parser_invalid_let():
    """
    To validate the parser checks let block statement integrity
    """
    parser = Parser(Lexer(Scanner("let: a <- 1 + 2\n    b <- a * 3\n\n")))

    with pytest.raises(LythSyntaxError) as err:
        next(parser)

    assert err.value.msg is LythError.GARBAGE_CHARACTERS
    assert err.value.filename == "<stdin>"
    assert err.value.lineno == 0
    assert err.value.offset == 5
    assert err.value.line == "let: a <- 1 + 2"

    parser = Parser(Lexer(Scanner("let:\na <- 1 + 2\n  b <- a * 3\n\n")))

    with pytest.raises(LythSyntaxError) as err:
        next(parser)

    assert err.value.msg is LythError.INCONSISTENT_INDENT
    assert err.value.filename == "<stdin>"
    assert err.value.lineno == 1
    assert err.value.offset == 0
    assert err.value.line == "a <- 1 + 2"

    parser = Parser(Lexer(Scanner("let:\n  a <- 1 + 2\n    b <- a * 3\n\n")))

    with pytest.raises(LythSyntaxError) as err:
        next(parser)

    assert err.value.msg is LythError.INCONSISTENT_INDENT
    assert err.value.filename == "<stdin>"
    assert err.value.lineno == 2
    assert err.value.offset == 0
    assert err.value.line == "    b <- a * 3"


def test_parser_let_be():
    """
    To validate the parser iterates properly over a variable being assigned the
    result of an expression.
    """
    parser = Parser(Lexer(Scanner("let b:\n")))

    assign = parser()
    assert assign.name == NodeType.Let
    assert str(assign) == "Let(Class(Name(b), None))"

    parser = Parser(Lexer(Scanner("let bit be attribute:\n")))

    assign = parser()
    assert assign.name == NodeType.Let
    assert str(assign) == "Let(Class(Name(bit), Type(Name(attribute))))"


def test_parser_docstring():
    """
    To validate that the docstring of a class, or a function is not captured in
    this version of the tool, and considered as multiline comment.
    """
    parser = Parser(Lexer(Scanner('"""\nHello you\n"""\n')))
    test = parser()
    assert test.name == NodeType.Noop


def test_parser_addition():
    """
    To validate the parser returns the right AST node.
    """
    parser = Parser(Lexer(Scanner("1 + 2 + 3\n")))

    expr = parser()
    assert expr.name == NodeType.Add
    assert str(expr) == "Add(Add(Num(1), Num(2)), Num(3))"

    expr = next(parser)
    assert expr.name == NodeType.Noop
    assert str(expr) == "Noop()"


def test_parser_multiplication():
    """
    To validate the parser returns the right AST node.
    """
    parser = Parser(Lexer(Scanner("1 * 2 * 3\n")))

    expr = next(parser)
    assert expr.name == NodeType.Mul
    assert str(expr) == "Mul(Mul(Num(1), Num(2)), Num(3))"

    expr = next(parser)
    assert expr.name == NodeType.Noop
    assert str(expr) == "Noop()"


def test_parser_precedence():
    """
    To validate the parser returns the right AST node.
    """
    parser = Parser(Lexer(Scanner("1 + 2 * 3 - 1\n")))

    expr = next(parser)
    assert expr.name == NodeType.Sub
    assert str(expr) == "Sub(Add(Num(1), Mul(Num(2), Num(3))), Num(1))"

    expr = next(parser)
    assert expr.name == NodeType.Noop
    assert str(expr) == "Noop()"


def test_parser_substraction():
    """
    To validate the parser returns the right AST node.
    """
    parser = Parser(Lexer(Scanner("1 + 2 - 3\n")))

    expr = next(parser)
    assert expr.name == NodeType.Sub
    assert str(expr) == "Sub(Add(Num(1), Num(2)), Num(3))"

    expr = next(parser)
    assert expr.name == NodeType.Noop
    assert str(expr) == "Noop()"


def test_parser_parenthesis():
    """
    Parentheses offer the highest precedence and change AST node ordering.
    """
    parser = Parser(Lexer(Scanner("1 + (a - 3) * 5\n")))

    expr = next(parser)
    assert expr.name == NodeType.Add
    assert str(expr) == "Add(Num(1), Mul(Sub(Name(a), Num(3)), Num(5)))"

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

    assert err.value.msg is LythError.LITERAL_EXPECTED
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

    parser = Parser(Lexer(Scanner("1 + 2 *\n")))

    with pytest.raises(LythSyntaxError) as err:
        next(parser)

    assert err.value.msg is LythError.INCOMPLETE_LINE
    assert err.value.filename == "<stdin>"
    assert err.value.lineno == 0
    assert err.value.offset == 6
    assert err.value.line == "1 + 2 *"


def test_parser_wrong_expression():
    """
    To validate the parser complains under various situations:

    1. Expression has too much trailing characters.
    2. Expression has an unexpected let keyword.
    """
    parser = Parser(Lexer(Scanner("1 + 2 + 3 ")))

    with pytest.raises(LythSyntaxError) as err:
        parser()

    assert err.value.msg is LythError.GARBAGE_CHARACTERS

    parser = Parser(Lexer(Scanner("let 1 + 2 + 3\n")))

    with pytest.raises(LythSyntaxError) as err:
        parser()

    assert err.value.msg is LythError.LET_ON_EXPRESSION
