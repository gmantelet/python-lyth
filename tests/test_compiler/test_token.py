import pytest

from lyth.compiler.error import LythError
from lyth.compiler.error import LythSyntaxError
from lyth.compiler.token import Literal
from lyth.compiler.token import Symbol
from lyth.compiler.token import Token


def test_integer():
    """
    To validate we get a token catching integers are expected.
    """
    token = Token("1", "<stdin>", 0, 1, " 12+")
    assert token.column == 1
    assert token.filename == "<stdin>"
    assert token.lexeme == "1"
    assert token.lineno == 0
    assert token.symbol == Literal.VALUE
    assert token.text == " 12+"

    token += "2"
    assert token.column == 1
    assert token.filename == "<stdin>"
    assert token.lexeme == "12"
    assert token.lineno == 0
    assert token.symbol == Literal.VALUE
    assert token.text == " 12+"

    with pytest.raises(LythSyntaxError) as err:
        token += "+"

    assert token.column == 1
    assert token.filename == "<stdin>"
    assert token.lexeme == "12"
    assert token.lineno == 0
    assert token.symbol == Literal.VALUE
    assert token.text == " 12+"

    assert err.value.msg is LythError.MISSING_SPACE_BEFORE_OPERATOR
    assert err.value.filename == "<stdin>"
    assert err.value.lineno == 0
    assert err.value.offset == 1
    assert err.value.line == " 12+"

    token = token()
    assert token.column == 1
    assert token.filename == "<stdin>"
    assert token.lexeme == 12
    assert token.lineno == 0
    assert token.symbol == Literal.VALUE
    assert token.text == " 12+"

    assert repr(token) == "Token(VALUE, 12, 0, 1)"
    assert str(token) == "VALUE: 12"


def test_symbol():
    """
    To validate we get a token catching symbols are expected.
    """
    token = Token("+", "<stdin>", 0, 1, " +=")
    assert token.column == 1
    assert token.filename == "<stdin>"
    assert token.lexeme == "+"
    assert token.lineno == 0
    assert token.symbol == Symbol.ADD
    assert token.text == " +="

    token = token()
    assert token.column == 1
    assert token.filename == "<stdin>"
    assert token.lexeme == "+"
    assert token.lineno == 0
    assert token.symbol == Symbol.ADD
    assert token.text == " +="

    token += "="
    assert token.column == 1
    assert token.filename == "<stdin>"
    assert token.lexeme == "+="
    assert token.lineno == 0
    assert token.symbol == Symbol.ADDAUG
    assert token.text == " +="

    token = token()
    assert token.column == 1
    assert token.filename == "<stdin>"
    assert token.lexeme == "+="
    assert token.lineno == 0
    assert token.symbol == Symbol.ADDAUG
    assert token.text == " +="

    with pytest.raises(LythSyntaxError) as err:
        token += "5"

    assert token.column == 1
    assert token.filename == "<stdin>"
    assert token.lexeme == "+="
    assert token.lineno == 0
    assert token.symbol == Symbol.ADDAUG
    assert token.text == " +="

    assert err.value.msg is LythError.MISSING_SPACE_AFTER_OPERATOR
    assert err.value.filename == "<stdin>"
    assert err.value.lineno == 0
    assert err.value.offset == 1
    assert err.value.line == " +="

    assert repr(token) == "Token(ADDAUG, +=, 0, 1)"
    assert str(token) == "ADDAUG: +="


def test_bad_symbol():
    """
    To validate we get a token catching symbols are expected.
    """
    token = None

    with pytest.raises(LythSyntaxError) as err:
        token = Token(";", "<stdin>", 0, 1, ";")

    assert token is None
    assert err.value.msg is LythError.INVALID_CHARACTER
    assert err.value.filename == "<stdin>"
    assert err.value.lineno == 0
    assert err.value.offset == 1
    assert err.value.line == ";"

    token = Token("+", "<stdin>", 0, 1, "+;")
    assert token.column == 1
    assert token.filename == "<stdin>"
    assert token.lexeme == "+"
    assert token.lineno == 0
    assert token.symbol == Symbol.ADD
    assert token.text == "+;"

    with pytest.raises(LythSyntaxError) as err:
        token += ";"

    assert token.column == 1
    assert token.filename == "<stdin>"
    assert token.lexeme == "+"
    assert token.lineno == 0
    assert token.symbol == Symbol.ADD
    assert token.text == "+;"

    assert err.value.msg is LythError.SYNTAX_ERROR
    assert err.value.filename == "<stdin>"
    assert err.value.lineno == 0
    assert err.value.offset == 1
    assert err.value.line == "+;"

    token = Token("6", "<stdin>", 0, 1, "6;")
    assert token.column == 1
    assert token.filename == "<stdin>"
    assert token.lexeme == "6"
    assert token.lineno == 0
    assert token.symbol == Literal.VALUE
    assert token.text == "6;"

    with pytest.raises(LythSyntaxError) as err:
        token += ";"

    assert token.column == 1
    assert token.filename == "<stdin>"
    assert token.lexeme == "6"
    assert token.lineno == 0
    assert token.symbol == Literal.VALUE
    assert token.text == "6;"

    assert err.value.msg is LythError.SYNTAX_ERROR
    assert err.value.filename == "<stdin>"
    assert err.value.lineno == 0
    assert err.value.offset == 1
    assert err.value.line == "6;"

    token = token()
    assert token.column == 1
    assert token.filename == "<stdin>"
    assert token.lexeme == 6
    assert token.lineno == 0
    assert token.symbol == Literal.VALUE
    assert token.text == "6;"
