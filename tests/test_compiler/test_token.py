import pytest

from lyth.compiler.error import LythError
from lyth.compiler.error import LythSyntaxError
from lyth.compiler.token import Literal
from lyth.compiler.token import Symbol
from lyth.compiler.token import Token
from lyth.compiler.token import TokenInfo


def test_integer():
    """
    To validate we get a token catching integers are expected.
    """
    token = Token("1", TokenInfo("<stdin>", 0, 1, " 12+"))
    assert token.info.offset == 1
    assert token.info.filename == "<stdin>"
    assert token.lexeme == "1"
    assert token.info.lineno == 0
    assert token.symbol == Literal.VALUE
    assert token.info.line == " 12+"

    token += "2"
    assert token.info.offset == 1
    assert token.info.filename == "<stdin>"
    assert token.lexeme == "12"
    assert token.info.lineno == 0
    assert token.symbol == Literal.VALUE
    assert token.info.line == " 12+"

    with pytest.raises(LythSyntaxError) as err:
        token += "+"

    assert token.info.offset == 1
    assert token.info.filename == "<stdin>"
    assert token.lexeme == "12"
    assert token.info.lineno == 0
    assert token.symbol == Literal.VALUE
    assert token.info.line == " 12+"

    assert err.value.msg is LythError.MISSING_SPACE_BEFORE_OPERATOR
    assert err.value.filename == "<stdin>"
    assert err.value.lineno == 0
    assert err.value.offset == 1
    assert err.value.line == " 12+"

    token = token()
    assert token.info.offset == 1
    assert token.info.filename == "<stdin>"
    assert token.lexeme == 12
    assert token.info.lineno == 0
    assert token.symbol == Literal.VALUE
    assert token.info.line == " 12+"

    assert repr(token) == "Token(VALUE, 12, 0, 1)"
    assert str(token) == "VALUE: 12"


def test_symbol():
    """
    To validate we get a token catching symbols are expected.
    """
    token = Token("+", TokenInfo("<stdin>", 0, 1, " +="))
    assert token.info.offset == 1
    assert token.info.filename == "<stdin>"
    assert token.lexeme == "+"
    assert token.info.lineno == 0
    assert token.symbol == Symbol.ADD
    assert token.info.line == " +="

    token = token()
    assert token.info.offset == 1
    assert token.info.filename == "<stdin>"
    assert token.lexeme == "+"
    assert token.info.lineno == 0
    assert token.symbol == Symbol.ADD
    assert token.info.line == " +="

    token += "="
    assert token.info.offset == 1
    assert token.info.filename == "<stdin>"
    assert token.lexeme == "+="
    assert token.info.lineno == 0
    assert token.symbol == Symbol.ADDAUG
    assert token.info.line == " +="

    token = token()
    assert token.info.offset == 1
    assert token.info.filename == "<stdin>"
    assert token.lexeme == "+="
    assert token.info.lineno == 0
    assert token.symbol == Symbol.ADDAUG
    assert token.info.line == " +="

    with pytest.raises(LythSyntaxError) as err:
        token += "5"

    assert token.info.offset == 1
    assert token.info.filename == "<stdin>"
    assert token.lexeme == "+="
    assert token.info.lineno == 0
    assert token.symbol == Symbol.ADDAUG
    assert token.info.line == " +="

    assert err.value.msg is LythError.MISSING_SPACE_AFTER_OPERATOR
    assert err.value.filename == "<stdin>"
    assert err.value.lineno == 0
    assert err.value.offset == 1
    assert err.value.line == " +="

    assert repr(token) == "Token(ADDAUG, '+=', 0, 1)"
    assert str(token) == "ADDAUG: '+='"


def test_bad_symbol():
    """
    To validate we get a token catching symbols are expected.
    """
    token = None

    with pytest.raises(LythSyntaxError) as err:
        token = Token(";", TokenInfo("<stdin>", 0, 1, ";"))

    assert token is None
    assert err.value.msg is LythError.INVALID_CHARACTER
    assert err.value.filename == "<stdin>"
    assert err.value.lineno == 0
    assert err.value.offset == 1
    assert err.value.line == ";"

    token = Token("+", TokenInfo("<stdin>", 0, 1, "+;"))
    assert token.info.offset == 1
    assert token.info.filename == "<stdin>"
    assert token.lexeme == "+"
    assert token.info.lineno == 0
    assert token.symbol == Symbol.ADD
    assert token.info.line == "+;"

    with pytest.raises(LythSyntaxError) as err:
        token += ";"

    assert token.info.offset == 1
    assert token.info.filename == "<stdin>"
    assert token.lexeme == "+"
    assert token.info.lineno == 0
    assert token.symbol == Symbol.ADD
    assert token.info.line == "+;"

    assert err.value.msg is LythError.SYNTAX_ERROR
    assert err.value.filename == "<stdin>"
    assert err.value.lineno == 0
    assert err.value.offset == 1
    assert err.value.line == "+;"

    token = Token("6", TokenInfo("<stdin>", 0, 1, "6;"))
    assert token.info.offset == 1
    assert token.info.filename == "<stdin>"
    assert token.lexeme == "6"
    assert token.info.lineno == 0
    assert token.symbol == Literal.VALUE
    assert token.info.line == "6;"

    with pytest.raises(LythSyntaxError) as err:
        token += ";"

    assert token.info.offset == 1
    assert token.info.filename == "<stdin>"
    assert token.lexeme == "6"
    assert token.info.lineno == 0
    assert token.symbol == Literal.VALUE
    assert token.info.line == "6;"

    assert err.value.msg is LythError.SYNTAX_ERROR
    assert err.value.filename == "<stdin>"
    assert err.value.lineno == 0
    assert err.value.offset == 1
    assert err.value.line == "6;"

    token = token()
    assert token.info.offset == 1
    assert token.info.filename == "<stdin>"
    assert token.lexeme == 6
    assert token.info.lineno == 0
    assert token.symbol == Literal.VALUE
    assert token.info.line == "6;"


def test_missing_space_before_symbol():
    """
    To validate we get an exception saying the token wants a space to be
    inserted before the symbol
    """
    token = Token("5", TokenInfo("<stdin>", 0, 1, "5+"))
    assert token.info.offset == 1
    assert token.info.filename == "<stdin>"
    assert token.lexeme == "5"
    assert token.info.lineno == 0
    assert token.symbol == Literal.VALUE
    assert token.info.line == "5+"

    with pytest.raises(LythSyntaxError) as err:
        token += "+"

    assert token.lexeme == "5"
    assert err.value.msg is LythError.MISSING_SPACE_BEFORE_OPERATOR
    assert err.value.filename == "<stdin>"
    assert err.value.lineno == 0
    assert err.value.offset == 1
    assert err.value.line == "5+"



def test_literal():
    """
    To test various conditions on strings that name a variable.
    """
    token = Token("h", TokenInfo("<stdin>", 0, 1, "he"))
    assert token.info.offset == 1
    assert token.info.filename == "<stdin>"
    assert token.lexeme == "h"
    assert token.info.lineno == 0
    assert token.symbol == Literal.STRING
    assert token.info.line == "he"

    token += 'e'
    assert token.info.offset == 1
    assert token.info.filename == "<stdin>"
    assert token.lexeme == "he"
    assert token.info.lineno == 0
    assert token.symbol == Literal.STRING
    assert token.info.line == "he"

    token = Token("_", TokenInfo("<stdin>", 0, 1, "_e_12__"))
    assert token.info.offset == 1
    assert token.info.filename == "<stdin>"
    assert token.lexeme == "_"
    assert token.info.lineno == 0
    assert token.symbol == Literal.STRING
    assert token.info.line == "_e_12__"

    token += 'e'
    assert token.info.offset == 1
    assert token.info.filename == "<stdin>"
    assert token.lexeme == "_e"
    assert token.info.lineno == 0
    assert token.symbol == Literal.STRING
    assert token.info.line == "_e_12__"

    token += '_'
    assert token.info.offset == 1
    assert token.info.filename == "<stdin>"
    assert token.lexeme == "_e_"
    assert token.info.lineno == 0
    assert token.symbol == Literal.STRING
    assert token.info.line == "_e_12__"

    token += '1'
    assert token.info.offset == 1
    assert token.info.filename == "<stdin>"
    assert token.lexeme == "_e_1"
    assert token.info.lineno == 0
    assert token.symbol == Literal.STRING
    assert token.info.line == "_e_12__"

    token += '2'
    assert token.info.offset == 1
    assert token.info.filename == "<stdin>"
    assert token.lexeme == "_e_12"
    assert token.info.lineno == 0
    assert token.symbol == Literal.STRING
    assert token.info.line == "_e_12__"

    token += '_'
    assert token.info.offset == 1
    assert token.info.filename == "<stdin>"
    assert token.lexeme == "_e_12_"
    assert token.info.lineno == 0
    assert token.symbol == Literal.STRING
    assert token.info.line == "_e_12__"

    token += '_'
    assert token.info.offset == 1
    assert token.info.filename == "<stdin>"
    assert token.lexeme == "_e_12__"
    assert token.info.lineno == 0
    assert token.symbol == Literal.STRING
    assert token.info.line == "_e_12__"

    token = Token("h", TokenInfo("<stdin>", 0, 1, "h+"))
    assert token.info.offset == 1
    assert token.info.filename == "<stdin>"
    assert token.lexeme == "h"
    assert token.info.lineno == 0
    assert token.symbol == Literal.STRING
    assert token.info.line == "h+"

    with pytest.raises(LythSyntaxError) as err:
        token += "+"

    assert token.lexeme == "h"
    assert err.value.msg is LythError.MISSING_SPACE_BEFORE_OPERATOR
    assert err.value.filename == "<stdin>"
    assert err.value.lineno == 0
    assert err.value.offset == 1
    assert err.value.line == "h+"

    token = Token("_", TokenInfo("<stdin>", 0, 1, "_+"))
    assert token.info.offset == 1
    assert token.info.filename == "<stdin>"
    assert token.lexeme == "_"
    assert token.info.lineno == 0
    assert token.symbol == Literal.STRING
    assert token.info.line == "_+"

    with pytest.raises(LythSyntaxError) as err:
        token += "+"

    assert token.lexeme == "_"
    assert err.value.msg is LythError.MISSING_SPACE_BEFORE_OPERATOR
    assert err.value.filename == "<stdin>"
    assert err.value.lineno == 0
    assert err.value.offset == 1
    assert err.value.line == "_+"

    token = Token("_", TokenInfo("<stdin>", 0, 1, "_1+"))
    assert token.info.offset == 1
    assert token.info.filename == "<stdin>"
    assert token.lexeme == "_"
    assert token.info.lineno == 0
    assert token.symbol == Literal.STRING
    assert token.info.line == "_1+"

    token += "1"
    assert token.info.offset == 1
    assert token.info.filename == "<stdin>"
    assert token.lexeme == "_1"
    assert token.info.lineno == 0
    assert token.symbol == Literal.STRING
    assert token.info.line == "_1+"

    with pytest.raises(LythSyntaxError) as err:
        token += "+"

    assert token.lexeme == "_1"
    assert err.value.msg is LythError.MISSING_SPACE_BEFORE_OPERATOR
    assert err.value.filename == "<stdin>"
    assert err.value.lineno == 0
    assert err.value.offset == 1
    assert err.value.line == "_1+"
