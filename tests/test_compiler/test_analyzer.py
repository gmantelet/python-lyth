import pytest

from lyth.compiler.analyzer import Analyzer
from lyth.compiler.error import LythError
from lyth.compiler.error import LythSyntaxError
from lyth.compiler.lexer import Lexer
from lyth.compiler.parser import Parser
from lyth.compiler.scanner import Scanner
from lyth.compiler.symbol import Field
from lyth.compiler.symbol import Name


@pytest.fixture
def clean_namespace(scope='module'):
    while Name.roots:
        root = Name.roots.pop()
        del root[(root.name, root.scope)]


def test_analyzer_mutable_assign(clean_namespace):
    """
    To validate that the analyzer is able to produce a symbol table.

    We test store and load context, that is, a value is stored with the result
    of an expression, and then we use the alias to store another value into
    another variable.
    """
    analyzer = Analyzer(Parser(Lexer(Scanner('a <- 1 + 2\n', '__test__'))))

    assert str(analyzer.table) == "__test__, root"

    analyzer()
    assert analyzer.table[('a', '__test__')].type.value == 3
    assert analyzer.table[('a', '__test__')].type.mutable == Field.MUTABLE
    assert analyzer.table[('a', '__test__')].type.type == Field.UNKNOWN
    assert analyzer.table.left is None
    assert str(analyzer.table.right) == "a, __test__"

    analyzer.parser.lexer.scanner += '__a <- a + 2\n'
    assert str(analyzer.table) == "__test__, root"

    analyzer()
    assert analyzer.table[('a', '__test__')].type.value == 3
    assert analyzer.table[('a', '__test__')].type.mutable == Field.MUTABLE
    assert analyzer.table[('a', '__test__')].type.type == Field.UNKNOWN
    assert analyzer.table[('__a', '__test__')].type.value == 5
    assert analyzer.table[('__a', '__test__')].type.mutable == Field.MUTABLE
    assert analyzer.table[('__a', '__test__')].type.type == Field.UNKNOWN

    assert str(analyzer.table.left) == "__a, __test__"
    assert str(analyzer.table.right) == "a, __test__"

    analyzer.parser.lexer.scanner += 'a <- 5\n'
    analyzer()
    assert analyzer.table[('a', '__test__')].type.value == 5
    assert analyzer.table[('a', '__test__')].type.mutable == Field.MUTABLE
    assert analyzer.table[('a', '__test__')].type.type == Field.UNKNOWN
    assert analyzer.table[('__a', '__test__')].type.value == 5
    assert analyzer.table[('__a', '__test__')].type.mutable == Field.MUTABLE
    assert analyzer.table[('__a', '__test__')].type.type == Field.UNKNOWN

    analyzer.parser.lexer.scanner += 'c <- b + 2\n'
    with pytest.raises(LythSyntaxError) as err:
        analyzer()

    assert err.value.msg is LythError.VARIABLE_REFERENCED_BEFORE_ASSIGNMENT
    assert err.value.filename == "__test__"
    assert err.value.lineno == 3
    assert err.value.offset == 5
    assert err.value.line == "c <- b + 2"

    analyzer = Analyzer(Parser(Lexer(Scanner('a <- 1 - 2\n', '__test__'))))
    analyzer()
    assert analyzer.table[('a', '__test__')].type.value == -1
    assert analyzer.table[('a', '__test__')].type.mutable == Field.MUTABLE
    assert analyzer.table[('a', '__test__')].type.type == Field.UNKNOWN

    analyzer = Analyzer(Parser(Lexer(Scanner('4 / 2 -> d\n', '__test__'))))
    analyzer()
    assert analyzer.table[('d', '__test__')].type.value == 2
    assert analyzer.table[('d', '__test__')].type.mutable == Field.IMMUTABLE
    assert analyzer.table[('d', '__test__')].type.type == Field.UNKNOWN


def test_analyzer_immutable_assign(clean_namespace):
    """
    To validate that the analyzer is able to produce a symbol table.

    We test store and load context, that is, a value is stored with the result
    of an expression, and then we use the alias to store another value into
    another variable.
    """

    analyzer = Analyzer(Parser(Lexer(Scanner('7 + 4 -> b\n', '__test__'))))

    assert str(analyzer.table) == "__test__, root"

    analyzer()
    assert analyzer.table[('b', '__test__')].type.value == 11
    assert analyzer.table[('b', '__test__')].type.mutable == Field.IMMUTABLE
    assert analyzer.table[('b', '__test__')].type.type == Field.UNKNOWN

    analyzer.parser.lexer.scanner += '12 -> b\n'
    with pytest.raises(LythSyntaxError) as err:
        analyzer()

    assert err.value.msg is LythError.REASSIGN_IMMUTABLE
    assert err.value.filename == "__test__"
    assert err.value.lineno == 1
    assert err.value.offset == 3
    assert err.value.line == "12 -> b"


def test_analyzer_wrong_assign(clean_namespace):
    """
    To validate that the analyzer generates exceptions when the assign operator
    is not properly written.
    """
    analyzer = Analyzer(Parser(Lexer(Scanner('7 + 4 -> b + 1\n', '__test__'))))

    assert str(analyzer.table) == "__test__, root"

    with pytest.raises(LythSyntaxError) as err:
        analyzer()

    assert err.value.msg is LythError.GARBAGE_CHARACTERS
    assert err.value.filename == "__test__"
    assert err.value.lineno == 0
    assert err.value.offset == 6
    assert err.value.line == "7 + 4 -> b + 1"

    analyzer = Analyzer(Parser(Lexer(Scanner('7 + 4 <- 1 + 2\n', '__test__'))))

    assert str(analyzer.table) == "__test__, root"

    with pytest.raises(LythSyntaxError) as err:
        analyzer()

    assert err.value.msg is LythError.LEFT_MEMBER_IS_EXPRESSION
    assert err.value.filename == "__test__"
    assert err.value.lineno == 0
    assert err.value.offset == 2
    assert err.value.line == "7 + 4 <- 1 + 2"

    analyzer = Analyzer(Parser(Lexer(Scanner('7 + 4 -> \n', '__test__'))))

    assert str(analyzer.table) == "__test__, root"

    with pytest.raises(LythSyntaxError) as err:
        analyzer()

    assert err.value.msg is LythError.INCOMPLETE_LINE
    assert err.value.filename == "__test__"
    assert err.value.lineno == 0
    assert err.value.offset == 8
    assert err.value.line == "7 + 4 -> "

    analyzer = Analyzer(Parser(Lexer(Scanner('7 + 4 -> 6\n', '__test__'))))

    assert str(analyzer.table) == "__test__, root"

    with pytest.raises(LythSyntaxError) as err:
        analyzer()

    assert err.value.msg is LythError.NAME_EXPECTED
    assert err.value.filename == "__test__"
    assert err.value.lineno == 0
    assert err.value.offset == 9
    assert err.value.line == "7 + 4 -> 6"


def test_analyzer_iterator(clean_namespace):
    """
    To validate the ability to analyze multiple lines on the fly
    """
    analyzer = Analyzer(Parser(Lexer(Scanner('a <- 1 + 2\na * 5 -> b\n', '__test__'))))

    assert str(analyzer.table) == "__test__, root"
    assert analyzer.table.left is None
    assert analyzer.table.right is None

    for _ in analyzer:
        print(f"TEST: left node of root is {analyzer.table.left}")
        print(f"TEST: right node of root is {analyzer.table.right}")

    assert analyzer.table[('a', '__test__')].type.value == 3
    assert analyzer.table[('a', '__test__')].type.mutable == Field.MUTABLE
    assert analyzer.table[('b', '__test__')].type.value == 15
    assert analyzer.table[('b', '__test__')].type.mutable == Field.IMMUTABLE


def test_analyzer_unknown_ast_node(clean_namespace):
    """
    To validate we get a dedicated error message when the AST node is not valid
    """
    parser = Parser(Lexer(Scanner('a <- 1 + 2\na * 5 -> b\n', '__test__')))

    node = next(parser)

    from enum import Enum

    class Dummy(Enum):
        DUMMY = "dummy"

    node.name = Dummy.DUMMY

    analyzer = Analyzer(None, "__dummy__.py")

    with pytest.raises(TypeError):
        analyzer.visit(node)


def test_analyzer_let(clean_namespace):
    """
    To validate that for now the analyzer is not doing anything upon let
    keyword
    """
    analyzer = Analyzer(Parser(Lexer(Scanner('let a <- 1 + 2\n', '__test__'))))

    assert str(analyzer.table) == "__test__, root"

    analyzer()
    assert analyzer.table[('a', '__test__')].type.value == 3
    assert analyzer.table[('a', '__test__')].type.mutable == Field.MUTABLE
    assert analyzer.table[('a', '__test__')].type.type == Field.UNKNOWN
    assert analyzer.table.left is None
    assert str(analyzer.table.right) == "a, __test__"
