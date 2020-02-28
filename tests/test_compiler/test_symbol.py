import pytest

from lyth.compiler.symbol import Field
from lyth.compiler.symbol import Name
from lyth.compiler.symbol import SymbolType
from lyth.compiler.symbol import TraversalMode


@pytest.fixture
def clean_namespace(scope='module'):
    while Name.roots:
        root = Name.roots.pop()
        del root[(root.name, root.scope)]


def test_symbol_integrity(clean_namespace):
    """
    To validate I am warned that I try to change immutable attributes on
    symbols
    """
    sym = Name('test', 'test_module', SymbolType())
    assert sym.name == 'test'
    assert sym.scope == 'test_module'
    assert sym.type.type is Field.UNKNOWN
    assert sym.type.mutable is Field.UNKNOWN
    assert sym.type.value is Field.UNKNOWN
    assert sym.address is Field.UNKNOWN
    assert sym.size is Field.UNKNOWN
    assert sym.left is None
    assert sym.right is None

    sym.type.mutable = Field.MUTABLE
    assert sym.type.mutable is Field.MUTABLE

    with pytest.raises(AttributeError):
        sym.name = "Fail"

    with pytest.raises(AttributeError):
        sym.scope = "Fail Again"

    with pytest.raises(ValueError):
        sym == 1

    with pytest.raises(ValueError):
        sym != 1

    with pytest.raises(ValueError):
        sym > 1

    with pytest.raises(ValueError):
        sym >= 1

    with pytest.raises(ValueError):
        sym < 1

    with pytest.raises(ValueError):
        sym <= 1


def test_rich_comparison(clean_namespace):
    """
    To validate comparison operators acts on the name and scope of symbols as
    expected.
    """
    sym1 = Name('a', 'b', SymbolType())
    sym2 = Name('a', 'c', SymbolType())
    sym3 = Name('b', 'a', SymbolType())
    sym4 = Name('b', 'b', SymbolType())
    sym5 = Name('a', 'b', SymbolType())
    sym6 = Name('b', 'b', SymbolType())

    assert sym1 is not sym5
    assert sym1 == sym5
    assert sym1 != sym2
    assert sym1 < sym2
    assert sym1 < sym3
    assert sym4 > sym2
    assert sym4 > sym3
    assert sym3 <= sym6
    assert sym1 <= sym6
    assert sym5 >= sym1
    assert sym6 >= sym5


def test_symbol_roots(clean_namespace):
    """
    To validate the analyzer can handle its root node as expected
    """
    sym = Name('test', 'test_module', SymbolType())
    assert sym not in Name.roots

    sym = Name.root('test', 'test_module', SymbolType())
    assert sym in Name.roots

    sym2 = Name.root('test', 'test_module', SymbolType())
    assert sym2 is sym
    assert sym2 in Name.roots

    sym3 = Name.root('test', 'test_module2', SymbolType())
    assert sym3 is not sym
    assert sym3 in Name.roots


def test_symbol_add(clean_namespace):
    """
    To validate binary tree insertion and traversal work as expected.
    """
    sym1 = Name('b', 'b', SymbolType())
    sym1 += Name('b', 'd', SymbolType())
    sym1 += Name('c', 'a', SymbolType())

    assert sym1.left is None
    assert sym1.right.name == 'b'
    assert sym1.right.scope == 'd'
    assert sym1.right.left is None
    assert sym1.right.right.name == 'c'
    assert sym1.right.right.scope == 'a'
    assert str(sym1) == "b, b"
    assert repr(sym1) == "b, b: unknown (unknown, unknown)"

    sym1 += Name('b', 'b', SymbolType())
    assert sym1.left is None
    assert sym1.right.name == 'b'
    assert sym1.right.scope == 'd'
    assert sym1.right.left is None
    assert sym1.right.right.name == 'c'
    assert sym1.right.right.scope == 'a'

    sym1 += Name('b', 'c', SymbolType())
    assert sym1.left is None
    assert sym1.right.name == 'b'
    assert sym1.right.scope == 'd'
    assert sym1.right.left.name == 'b'
    assert sym1.right.left.scope == 'c'
    assert sym1.right.right.name == 'c'
    assert sym1.right.right.scope == 'a'

    sym1 += Name('b', 'a', SymbolType())
    assert sym1.left.name == 'b'
    assert sym1.left.scope == 'a'
    assert sym1.right.name == 'b'
    assert sym1.right.scope == 'd'
    assert sym1.right.left.name == 'b'
    assert sym1.right.left.scope == 'c'
    assert sym1.right.right.name == 'c'
    assert sym1.right.right.scope == 'a'

    tree = sym1(TraversalMode.PRE_ORDER)
    node = next(tree)
    assert node.name == 'b'
    assert node.scope == 'b'
    node = next(tree)
    assert node.name == 'b'
    assert node.scope == 'a'
    node = next(tree)
    assert node.name == 'b'
    assert node.scope == 'd'
    node = next(tree)
    assert node.name == 'b'
    assert node.scope == 'c'
    node = next(tree)
    assert node.name == 'c'
    assert node.scope == 'a'

    tree = sym1(TraversalMode.IN_ORDER)
    node = next(tree)
    assert node.name == 'b'
    assert node.scope == 'a'
    node = next(tree)
    assert node.name == 'b'
    assert node.scope == 'b'
    node = next(tree)
    assert node.name == 'b'
    assert node.scope == 'c'
    node = next(tree)
    assert node.name == 'b'
    assert node.scope == 'd'
    node = next(tree)
    assert node.name == 'c'
    assert node.scope == 'a'

    tree = sym1(TraversalMode.POST_ORDER)
    node = next(tree)
    assert node.name == 'b'
    assert node.scope == 'a'
    node = next(tree)
    assert node.name == 'b'
    assert node.scope == 'c'
    node = next(tree)
    assert node.name == 'c'
    assert node.scope == 'a'
    node = next(tree)
    assert node.name == 'b'
    assert node.scope == 'd'
    node = next(tree)
    assert node.name == 'b'
    assert node.scope == 'b'

    sym1 += Name('b', 'ab', SymbolType())
    assert sym1.left.name == 'b'
    assert sym1.left.scope == 'a'
    assert sym1.left.left is None
    assert sym1.left.right.name == 'b'
    assert sym1.left.right.scope == 'ab'
    assert sym1.right.name == 'b'
    assert sym1.right.scope == 'd'
    assert sym1.right.left.name == 'b'
    assert sym1.right.left.scope == 'c'
    assert sym1.right.right.name == 'c'
    assert sym1.right.right.scope == 'a'

    assert (Name('b', 'b', SymbolType()) in sym1) is True
    assert (Name('b', 'a', SymbolType()) in sym1) is True
    assert (Name('c', 'a', SymbolType()) in sym1) is True
    assert (Name('c', 'a', SymbolType()) in sym1.right) is True
    assert (Name('c', 'a', SymbolType()) in sym1.left) is False

    assert sym1[('b', 'b')] is sym1
    assert sym1[('b', 'c')] is sym1.right.left
    assert sym1[('c', 'a')] is sym1.right.right

    with pytest.raises(KeyError):
        _ = sym1[('a', 'e')]

    assert sym1['d'] == []
    assert sym1['c'] == [sym1.right.right]
    assert sym1['b'] == [sym1, sym1.left, sym1.left.right, sym1.right, sym1.right.left]

    with pytest.raises(ValueError):
        _ = sym1[1]

    sym1 += Name('a', 'a', SymbolType())
    assert sym1[('a', 'a')] is sym1.left.left


def test_symbol_as_dict(clean_namespace):
    """
    To validate the use of __getitem__, __setitem__, __delitem__
    """
    sym1 = Name.root('a', 'a', SymbolType())

    assert sym1[('a', 'a')] is sym1
    assert sym1[('a')] == [sym1]

    with pytest.raises(KeyError):
        _ = sym1[('a', 'e')]

    assert sym1[('b')] == []

    with pytest.raises(ValueError):
        _ = sym1[1]

    sym1[('a', 'b')] = SymbolType()
    assert sym1[('a', 'b')].name == 'a'
    assert sym1[('a', 'b')].scope == 'b'

    with pytest.raises(ValueError):
        sym1['a'] = SymbolType()

    with pytest.raises(ValueError):
        sym1[1] = SymbolType()

    sym1[('a', 'c')] = SymbolType()
    assert sym1[('a', 'c')].name == 'a'
    assert sym1[('a', 'c')].scope == 'c'

    sym1[('a', 'ab')] = SymbolType()
    del sym1[('a', 'ab')]

    del sym1[('a', 'b')]

    with pytest.raises(KeyError):
        _ = sym1[('a', 'b')]

    with pytest.raises(KeyError):
        _ = sym1[('a', 'c')]

    with pytest.raises(ValueError):
        del sym1['a']

    with pytest.raises(ValueError):
        del sym1[1]

    del sym1[('a', 'a')]
    assert Name.roots == set()

    sym2 = Name('b', 'b', SymbolType())
    sym2[('a', 'b')] = SymbolType()
    sym2[('a', 'a')] = SymbolType()
    sym2[('a', 'c')] = SymbolType()

    del sym2[('a', 'b')]
    with pytest.raises(KeyError):
        _ = sym1[('a', 'c')]


def test_get_parent(clean_namespace):
    """
    To test we get the right parent node.
    """
    sym1 = Name('b', 'b', SymbolType())
    sym1 += Name('a', 'b', SymbolType())
    sym1 += Name('a', 'a', SymbolType())
    sym1 += Name('a', 'c', SymbolType())
    sym1 += Name('b', 'd', SymbolType())
    sym1 += Name('b', 'c', SymbolType())
    sym1 += Name('b', 'e', SymbolType())

    assert sym1.get_parent(sym1[('b', 'e')]) == sym1[('b', 'd')]
    assert sym1.get_parent(sym1[('b', 'c')]) == sym1[('b', 'd')]
    assert sym1.get_parent(sym1[('b', 'd')]) == sym1[('b', 'b')]
    assert sym1.get_parent(sym1[('a', 'a')]) == sym1[('a', 'b')]
    assert sym1.get_parent(sym1[('a', 'c')]) == sym1[('a', 'b')]
    assert sym1.get_parent(sym1[('a', 'b')]) == sym1[('b', 'b')]
    assert sym1.get_parent(sym1) is None
    assert sym1.get_parent(Name('c', 'c', SymbolType())) is None
