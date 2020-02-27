"""
This module defines the symbol table.
"""
from __future__ import annotations

from enum import Enum
from typing import Generator
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union


class Field(Enum):
    """
    An enumeration storing extra keywords.

    This is important to precisely identify an unknown value. Otherwise, how
    could the analyzer, and the interpreter, know that None is a known value of
    None and not an unknown value?
    """
    IMMUTABLE = 'immutable'
    MUTABLE = 'mutable'
    NONE = 'none'
    UNKNOWN = 'unknown'


class TraversalMode(Enum):
    """
    An enumeration defining the options to traverse the binary tree.
    """
    IN_ORDER = "in-order"
    PRE_ORDER = "pre-order"
    POST_ORDER = "post-order"


class SymbolType:
    """
    The data type of a symbol, and optional information such as its mutability.
    """
    def __init__(self, type: Field = Field.UNKNOWN, mutable: Field = Field.UNKNOWN,
                 value: Field = Field.UNKNOWN) -> None:
        """
        Instantiates this object.

        The type determines if operations are allowed. For example, when an
        integer, and a string are summed up, this may be incompatible and the
        semantic analyzer may raise an exception. The type will ultimately help
        the interpreter determine how much space it requires on memory for the
        associated object.

        The second important attribute is the object mutability. The
        interpreter may take different decisions based on object mutability.

        The third option is the initial value to provide to this symbol.
        Classes are a bit different, and none may be provided only for them.
        """
        self.type = type
        self.mutable = mutable
        self.value = value


class Name:
    """
    A symbol maintained in the table by the analyzer and exposed to the
    interpreter.
    """
    roots = set()

    def __init__(self, name: str, scope: str, type: SymbolType) -> None:
        """
        Instantiate a new symbol.

        Attributes:
            name:    The name is the identifier of the symbol, it comes from
                     the Name AST node, and stores the lexeme of the associated
                     token.
            type:    The type of the symbol validates its integrity when
                     operations are applied on. For example can we reassign an
                     immutable variable? Can we add up two different types?
            scope:   The scope determines validity of a symbol and helps solve
                     naming conflicts. It is the name of another symbol, and as
                     such the interpreter must be able to find that symbol.
            address: The address in target memory this symbol will be assigned
                     to.
            size:    The address space required by this symbol in memory based
                     on its type.
            left:    Left child node for this binary tree.
            right:   Right child node for this binary tree.
        """
        self.__name = name
        self.__scope = scope
        self.type = type
        self.address: Union[Field, int] = Field.UNKNOWN
        self.size: Union[Field, int] = Field.UNKNOWN
        self.left: Optional[Name] = None
        self.right: Optional[Name] = None

    def __add__(self, other: Name) -> Name:
        """
        Insert a name to this instance.
        """
        if self < other:
            if self.right:
                self.right += other

            else:
                self.right = other

        elif self > other:
            if self.left:
                self.left += other

            else:
                self.left = other

        return self

    def __call__(self, mode: TraversalMode = TraversalMode.PRE_ORDER) -> Generator[Name]:
        """
        Begining the traversal of the node, collecting its generator.

        When traversing the node, the traversal mode needs to be defined:
        """
        return self.next(mode)

    def __contains__(self, other: Name) -> bool:
        """
        Check that this instance stores the name specified is in this branch.
        """
        if self == other:
            return True

        elif self < other and self.right:
            return other in self.right

        elif self > other and self.left:
            return other in self.left

        else:
            return False

    def __eq__(self, other: Name) -> bool:
        """
        Are the two objects equivalent?

        To be considered equal, the objects must bare the same name, and the
        same scope.
        """
        if not isinstance(other, self.__class__):
            raise ValueError(f"Cannot compare {self.__class__.__name__} with {type(other)}")

        return self.__name == other.__name and self.__scope == other.__scope

    def __ge__(self, other: Name) -> bool:
        """
        Comparing keys to determine which one is on the right of the other one.
        """
        if not isinstance(other, self.__class__):
            raise ValueError(f"Cannot compare {self.__class__.__name__} with {type(other)}")

        if self.__name == other.__name:
            return self.__scope >= other.__scope

        return self.__name > other.__name

    def __getitem__(self, info: Union[str, Tuple[str, str]]) -> Union[Name, List[Name]]:
        """
        Retrieves an instance of Name based on its information.

        If the information is only a name, then it returns all the names in the
        symbol table regardless of their scope. If a scope is provided as well,
        then it returns only
        """
        if isinstance(info, tuple):
            other = self.__class__(*info, SymbolType())
            if other == self:
                return self

            elif other == self.right:
                return self.right

            elif other == self.left:
                return self.left

            elif other in self.right:
                return self.right[info]

            elif other in self.left:
                return self.left[info]

            else:
                raise KeyError(f"({''.join(info)}) not in this node ({self})")

        elif isinstance(info, str):
            return [child for child in self() if child.name == info]

        else:
            raise ValueError(f"__getitem__ accepts info as name of 'str', or "
                             f"<name, info> as tuple of 'str', not {type(info)}")

    def __gt__(self, other: Name) -> bool:
        """
        Comparing keys to determine which one is on the right of the other one.
        """
        if not isinstance(other, self.__class__):
            raise ValueError(f"Cannot compare {self.__class__.__name__} with {type(other)}")

        if self.__name == other.__name:
            return self.__scope > other.__scope

        return self.__name > other.__name

    def __hash__(self):
        """
        Return the hash value of the name and the scope of this instance.
        """
        return hash((self.__name, self.__scope))

    def __le__(self, other: Name) -> bool:
        """
        Comparing keys to determine which one is on the right of the other one.
        """
        if not isinstance(other, self.__class__):
            raise ValueError(f"Cannot compare {self.__class__.__name__} with {type(other)}")

        if self.__name == other.__name:
            return self.__scope <= other.__scope

        return self.__name < other.__name

    def __lt__(self, other: Name) -> bool:
        """
        Comparing keys to determine which one is on the left of the other one.
        """
        if not isinstance(other, self.__class__):
            raise ValueError(f"Cannot compare {self.__class__.__name__} with {type(other)}")

        if self.__name == other.__name:
            return self.__scope < other.__scope

        return self.__name < other.__name

    def __ne__(self, other: Name) -> bool:
        """
        Are the two objects equivalent?

        To be considered unequal, the objects must bare different names or
        different scopes
        """
        if not isinstance(other, self.__class__):
            raise ValueError(f"Cannot compare {self.__class__.__name__} with {type(other)}")

        return self.__name != other.__name or self.__scope != other.__scope

    @property
    def name(self):
        """
        Returns the read only name attribute
        """
        return self.__name

    def next(self, mode: TraversalMode = TraversalMode.PRE_ORDER) -> Name:
        """
        Retrieves the next node in tree.

        The three modes are covered by this generator method, naming pre-order,
        in-order, and post-order.
        """
        if mode is TraversalMode.PRE_ORDER:
            yield self

        if self.left:
            for child in self.left(mode):
                yield child

        if mode is TraversalMode.IN_ORDER:
            yield self

        if self.right:
            for child in self.right(mode):
                yield child

        if mode is TraversalMode.POST_ORDER:
            yield self

    @classmethod
    def root(cls, name: str, scope: str, type: SymbolType) -> Name:
        """
        Create a new node object and register as root, or return root if it
        exists.
        """
        obj = cls(name, scope, type)
        for r in cls.roots:
            if r == obj:
                return r

        cls.roots.add(obj)
        return obj

    @property
    def scope(self):
        """
        Returns the read only scope attribute
        """
        return self.__scope
