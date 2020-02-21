import pytest

from lyth.compiler.ast import Node
from lyth.compiler.lexer import Lexer
from lyth.compiler.scanner import Scanner


def test_ast():
    """
    To validate that an AST node can be properly instantiated from a token.
    """
    lexer = Lexer(Scanner())
    lexer("1 + 2\n", source="dummy.txt")

    node_one = Node(next(lexer))
    assert node_one._children == (1, )
    assert node_one.filename == "dummy.txt"
    assert node_one.lineno == 0
    assert node_one.offset == 0
    assert node_one.line == "1 + 2"

    assert node_one.value == 1
    assert str(node_one) == "Num(1)"
    assert repr(node_one) == "NodeType.Num(1)"

    with pytest.raises(AttributeError):
        assert node_one.left == 1

    with pytest.raises(AttributeError):
        assert node_one.right == 2

    token_plus = next(lexer)

    node_two = Node(next(lexer))
    assert node_two._children == (2, )
    assert node_two.filename == "dummy.txt"
    assert node_two.lineno == 0
    assert node_two.offset == 4
    assert node_two.line == "1 + 2"

    assert node_two.value == 2
    assert str(node_two) == "Num(2)"
    assert repr(node_two) == "NodeType.Num(2)"

    node_plus = Node(token_plus, node_one, node_two)

    assert node_plus._children[0] is node_one
    assert node_plus._children[1] is node_two

    with pytest.raises(IndexError):
        assert node_plus._children[2] is node_one

    assert node_plus.filename == "dummy.txt"
    assert node_plus.lineno == 0
    assert node_plus.offset == 2
    assert node_plus.line == "1 + 2"

    with pytest.raises(AttributeError):
        assert node_plus.value == 1

    assert node_plus.left is node_one
    assert node_plus.right is node_two

    assert str(node_plus) == "Add(Num(1), Num(2))"
    assert repr(node_plus) == "NodeType.Add(Num(1), Num(2))"
