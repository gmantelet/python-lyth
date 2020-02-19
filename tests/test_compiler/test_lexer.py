import pytest

from lyth.compiler.error import LythError
from lyth.compiler.error import LythSyntaxError
from lyth.compiler.lexer import Lexer
from lyth.compiler.scanner import Scanner
from lyth.compiler.token import Literal
from lyth.compiler.token import Symbol


def test_lexer():
    """
    To validate the lexer produces the right tokens from a simple expression.

    If I write this: '1 + 2', I expect to get three tokens, in this order:
    - A Literal.VALUE with a lexeme of '1'
    - A Symbol.ADD with a lexeme of... '+' (but that we do not care)
    - A Literal.VALUE with a lexeme of '2'

    And... is this a good beginning?
    """
    lexer = Lexer(Scanner())
    lexer("1 + 2\n")

    token = next(lexer)

    assert token.column == 0
    assert token.filename == "<stdin>"
    assert token.lexeme == 1
    assert token.lineno == 0
    assert token.symbol == Literal.VALUE
    assert token.text == "1 + 2"

    token = next(lexer)

    assert token.column == 2
    assert token.filename == "<stdin>"
    assert token.lexeme == '+'
    assert token.lineno == 0
    assert token.symbol == Symbol.ADD
    assert token.text == "1 + 2"

    token = next(lexer)

    assert token.column == 4
    assert token.filename == "<stdin>"
    assert token.lexeme == 2
    assert token.lineno == 0
    assert token.symbol == Literal.VALUE
    assert token.text == "1 + 2"

    token = next(lexer)

    assert token.column == -1
    assert token.filename == "<stdin>"
    assert token.lexeme is None
    assert token.lineno == 1
    assert token.symbol == Symbol.EOF
    assert token.text == ""

    with pytest.raises(StopIteration):
        token = next(lexer)

    assert token.column == -1
    assert token.filename == "<stdin>"
    assert token.lexeme is None
    assert token.lineno == 1
    assert token.symbol == Symbol.EOF
    assert token.text == ""


def test_missing_empty_line():
    """
    The script must end up with an empty line.
    """
    lexer = Lexer(Scanner())
    lexer("1 + 2")

    with pytest.raises(LythSyntaxError) as err:
        for i, _ in enumerate(lexer):
            pass

    assert err.value.msg is LythError.MISSING_EMPTY_LINE
    assert err.value.filename == "<stdin>"
    assert err.value.lineno == 0
    assert err.value.offset == -1
    assert err.value.line == "1 + 2"


def test_multiple_spaces():
    """
    Multiple spaces are skipped
    """
    lexer = Lexer(Scanner())
    lexer("1  +=  2  \n")

    token = next(lexer)

    assert token.column == 0
    assert token.filename == "<stdin>"
    assert token.lexeme == 1
    assert token.lineno == 0
    assert token.symbol == Literal.VALUE
    assert token.text == "1  +=  2  "

    token = next(lexer)

    assert token.column == 3
    assert token.filename == "<stdin>"
    assert token.lexeme == '+='
    assert token.lineno == 0
    assert token.symbol == Symbol.ADDAUG
    assert token.text == "1  +=  2  "

    token = next(lexer)

    assert token.column == 7
    assert token.filename == "<stdin>"
    assert token.lexeme == 2
    assert token.lineno == 0
    assert token.symbol == Literal.VALUE
    assert token.text == "1  +=  2  "

    token = next(lexer)

    assert token.column == -1
    assert token.filename == "<stdin>"
    assert token.lexeme is None
    assert token.lineno == 1
    assert token.symbol == Symbol.EOF
    assert token.text == ""

    with pytest.raises(StopIteration):
        token = next(lexer)

    assert token.column == -1
    assert token.filename == "<stdin>"
    assert token.lexeme is None
    assert token.lineno == 1
    assert token.symbol == Symbol.EOF
    assert token.text == ""


def test_missing_space_before_operator():
    """
    A missing space causes the lexer to send an exception.
    """
    token = None
    lexer = Lexer(Scanner())
    lexer("1+  2  \n")

    with pytest.raises(LythSyntaxError) as err:
        token = next(lexer)

    assert token is None
    assert err.value.msg is LythError.MISSING_SPACE_BEFORE_OPERATOR
    assert err.value.filename == "<stdin>"
    assert err.value.lineno == 0
    assert err.value.offset == 0
    assert err.value.line == "1+  2  "


def test_missing_space_after_operator():
    """
    A missing space after an operator causes the lexer to send an exception,
    but tolerates '+' or '-'.

    But it does not tolerate '+=4'
    """
    lexer = Lexer(Scanner())
    lexer("1  +2  \n")

    token = next(lexer)

    assert token.column == 0
    assert token.filename == "<stdin>"
    assert token.lexeme == 1
    assert token.lineno == 0
    assert token.symbol == Literal.VALUE
    assert token.text == "1  +2  "

    token = next(lexer)

    assert token.column == 3
    assert token.filename == "<stdin>"
    assert token.lexeme == '+'
    assert token.lineno == 0
    assert token.symbol == Symbol.ADD
    assert token.text == "1  +2  "

    token = next(lexer)

    assert token.column == 4
    assert token.filename == "<stdin>"
    assert token.lexeme == 2
    assert token.lineno == 0
    assert token.symbol == Literal.VALUE
    assert token.text == "1  +2  "

    lexer("1  +=2  \n")

    token = next(lexer)

    assert token.column == 0
    assert token.filename == "<stdin>"
    assert token.lexeme == 1
    assert token.lineno == 0
    assert token.symbol == Literal.VALUE
    assert token.text == "1  +=2  "

    with pytest.raises(LythSyntaxError) as err:
        token = next(lexer)

    assert err.value.msg is LythError.MISSING_SPACE_AFTER_OPERATOR
    assert err.value.filename == "<stdin>"
    assert err.value.lineno == 0
    assert err.value.offset == 3
    assert err.value.line == "1  +=2  "