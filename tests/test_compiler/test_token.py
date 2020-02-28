import pytest

from lyth.compiler.error import LythError
from lyth.compiler.error import LythSyntaxError
from lyth.compiler.token import Keyword
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
    token = Token("+", TokenInfo("<stdin>", 0, 1, " ++"))
    assert token.info.offset == 1
    assert token.info.filename == "<stdin>"
    assert token.lexeme == "+"
    assert token.info.lineno == 0
    assert token.symbol == Symbol.ADD
    assert token.info.line == " ++"

    token = token()
    assert token.info.offset == 1
    assert token.info.filename == "<stdin>"
    assert token.lexeme == "+"
    assert token.info.lineno == 0
    assert token.symbol == Symbol.ADD
    assert token.info.line == " ++"

    token += "+"
    assert token.info.offset == 1
    assert token.info.filename == "<stdin>"
    assert token.lexeme == "++"
    assert token.info.lineno == 0
    assert token.symbol == Symbol.INC
    assert token.info.line == " ++"

    token = token()
    assert token.info.offset == 1
    assert token.info.filename == "<stdin>"
    assert token.lexeme == "++"
    assert token.info.lineno == 0
    assert token.symbol == Symbol.INC
    assert token.info.line == " ++"

    with pytest.raises(LythSyntaxError) as err:
        token += "5"

    assert token.info.offset == 1
    assert token.info.filename == "<stdin>"
    assert token.lexeme == "++"
    assert token.info.lineno == 0
    assert token.symbol == Symbol.INC
    assert token.info.line == " ++"

    assert err.value.msg is LythError.MISSING_SPACE_AFTER_OPERATOR
    assert err.value.filename == "<stdin>"
    assert err.value.lineno == 0
    assert err.value.offset == 1
    assert err.value.line == " ++"

    assert repr(token) == "Token(INC, '++', 0, 1)"
    assert str(token) == "INC: '++'"


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


def test_keyword():
    """
    Are the keywords properly identified?
    """
    token = Token("l", TokenInfo("<stdin>", 0, 1, "let"))
    assert token.info.offset == 1
    assert token.info.filename == "<stdin>"
    assert token.lexeme == "l"
    assert token.info.lineno == 0
    assert token.symbol == Literal.STRING
    assert token.info.line == "let"

    token += 'e'
    assert token.info.offset == 1
    assert token.info.filename == "<stdin>"
    assert token.lexeme == "le"
    assert token.info.lineno == 0
    assert token.symbol == Literal.STRING
    assert token.info.line == "let"

    token += 't'
    assert token.info.offset == 1
    assert token.info.filename == "<stdin>"
    assert token.lexeme == "let"
    assert token.info.lineno == 0
    assert token.symbol == Keyword.LET
    assert token.info.line == "let"

    token = Token("l", TokenInfo("<stdin>", 0, 1, "lett"))
    assert token.info.offset == 1
    assert token.info.filename == "<stdin>"
    assert token.lexeme == "l"
    assert token.info.lineno == 0
    assert token.symbol == Literal.STRING
    assert token.info.line == "lett"

    token += 'e'
    assert token.info.offset == 1
    assert token.info.filename == "<stdin>"
    assert token.lexeme == "le"
    assert token.info.lineno == 0
    assert token.symbol == Literal.STRING
    assert token.info.line == "lett"

    token += 't'
    assert token.info.offset == 1
    assert token.info.filename == "<stdin>"
    assert token.lexeme == "let"
    assert token.info.lineno == 0
    assert token.symbol == Keyword.LET
    assert token.info.line == "lett"

    token += 't'
    assert token.info.offset == 1
    assert token.info.filename == "<stdin>"
    assert token.lexeme == "lett"
    assert token.info.lineno == 0
    assert token.symbol == Literal.STRING
    assert token.info.line == "lett"

    token = Token("a", TokenInfo("<stdin>", 0, 1, "alet"))
    assert token.info.offset == 1
    assert token.info.filename == "<stdin>"
    assert token.lexeme == "a"
    assert token.info.lineno == 0
    assert token.symbol == Literal.STRING
    assert token.info.line == "alet"

    token += 'l'
    assert token.info.offset == 1
    assert token.info.filename == "<stdin>"
    assert token.lexeme == "al"
    assert token.info.lineno == 0
    assert token.symbol == Literal.STRING
    assert token.info.line == "alet"

    token += 'e'
    assert token.info.offset == 1
    assert token.info.filename == "<stdin>"
    assert token.lexeme == "ale"
    assert token.info.lineno == 0
    assert token.symbol == Literal.STRING
    assert token.info.line == "alet"

    token += 't'
    assert token.info.offset == 1
    assert token.info.filename == "<stdin>"
    assert token.lexeme == "alet"
    assert token.info.lineno == 0
    assert token.symbol == Literal.STRING
    assert token.info.line == "alet"
