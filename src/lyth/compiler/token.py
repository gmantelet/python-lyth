"""
This module defines a token.

A token is made of a type and a lexeme. The lexeme is considered immutable, and
we use here an Enum to describe the types.
"""
from __future__ import annotations

from enum import Enum
from typing import Optional

from lyth.compiler.error import LythError
from lyth.compiler.error import LythSyntaxError
from lyth.compiler.scanner import Scanner


class _Lexeme(Enum):
    """
    A generic enumeration with a couple of helpers to inherit from.
    """
    @classmethod
    def as_value(cls, value: Optional[str]) -> _Lexeme:
        """
        Return the enumeration type based on the value provided or None if the
        value is not in the enumeration.
        """
        return cls._value2member_map_.get(value)


class Symbol(_Lexeme):
    """
    The enumeration of recognized symbols.

    Symbols are considered here as lexeme that are not keywords, that are not
    names or values, and is the end of file itself.
    """
    ADD = '+'                  # Addition symbol for expressions
    ADDAUG = '+='              # Augmented addition (idiom for a = a + x)
    # AND = '&'                  # Binary mask
    # ANDAUG = '&='              # Augmented assignment (idiom for a = a & x)
    CEIL = '//'                # Also known as integer division
    # CHAR = "'"                 # Desginates an ASCII translation of an integer
    # COLON = ':'                # Beginning of a block of code
    # COMMA = ','                # Delimiter for a set of parameters
    # COMMENT = '#'              # Designates a comment section
    # COMP = '=='                # Testing equality
    # DEC = '--'                 # Decrementing (idiom for a = a - 1)
    # DIFF = '!='                # Different than, not equal than
    DIV = '/'                  # Also known as float division
    # DOC = '"""'                # Docstring
    # DOT = '.'                  # Access to an attribute (or design self)
    EOF = None                 # End of file. StopIteration after this token
    EOL = "\n"                 # End of line.
    # EQ = '='                   # Assigning a mutable value
    # FLIP = '!'                 # Bit flip operator
    # GT = '>'                   # Testing greater than
    # GTE = '>='                 # Testing greater or equal than
    # INC = '++'                 # Incrementing (idiom for a = a + 1)
    # INDENT = '  '              # Multiple of two spaces at column 0
    # MOD = '%'                  # Modulo, the remainder of integer division
    MUL = '*'                  # Multiplication symbol for expressions
    LASSIGN = '<-'              # Assigning a value to its left member
    LPAREN = '('               # Left parenthesis
    # LSHIFT = '<<'              # Left shift operator
    # LSHIFTAUG = '>>='          # Augmented shift (idiom for a = a << x)
    # LT = '<'                   # Testing less than
    # LTE = '<='                 # Testing greater or equal than
    # OR = '|'                   # Binary or operator
    # ORAUG = '|='               # Augmented or (idiom for a = a | x)
    # QUOTE = '"'                # Designates a string
    # RANGE = '..'               # Range operator, or bit space
    RASSIGN = '->'              # Assigning a value to its right member
    RPAREN = ')'               # Right parenthesis
    # RSHIFT = '>>'              # Right shif operator
    # RSHIFTAUG = '>>='          # Augmented shift (idiom for a = a >> x)
    SUB = '-'                  # Substraction symbol for expressions
    # SUBAUG = '-='              # Augmented substraction (idiom for a = a - x)
    # XOR = '^'                  # Exclusive or operator
    # XORAUG = '^='              # Augmented addition (idiom for a = a ^ x)


class Keyword(_Lexeme):
    """
    The enumeration of recognized keywords.

    Use of keywords for naming variables will raise an Exception.
    """
    # AT = 'at'                  # To refer to an address, and not a value
    # AND = 'and'                # A logical and operator
    # FALSE = 'false'            # False value, often equals 0
    # FOR = 'for'                # The for loop
    # FROM = 'from'              # From a module to resolve namespace
    # IF = 'if'                  # The if statement
    # IMPORT = 'import'          # Import a namespace
    # IN = 'in'                  # Check in list
    # IS = 'is'                  # Means the same, for two names, or is at.
    # LET = 'let'                # Public declaration of this namespace
    # NONE = 'none'              # The none address
    # NOT = 'not'                # A logical not operator
    # OF = 'of'                  # The inheritance operator
    # OR = 'or'                  # A logical or operator
    # TRUE = 'true'              # True value, often equals 0
    # WITH = 'with'              # The with statement, using a context


class Literal(_Lexeme):
    """
    The enumeration of meanings.

    Meanings are usually values (integers, floats etc.), or variable naming.
    """
    STRING = 'string'          # A \0 terminsated chain of characters.
    VALUE = 'value'            # A numeral value.


class TokenInfo:
    """
    A unit of data capturing a snapshot of the scanner metadata when a Token
    object is instantiated.
    """
    def __init__(self, filename: str, lineno: int, offset: int, line: str) -> None:
        self.filename = filename
        self.lineno = lineno
        self.offset = offset
        self.line = line


class Token:
    """
    Defines a sequence of characters hopefully carrying some meaning.

    A token can be aggregated. First time a character is scanned, usually after
    a space has been scanned, the token is initialized, then next characters
    are added to the token, unless a space is found in which case a post
    processing may be required, for instance converting the string lexeme into
    an int etc.
    """
    def __init__(self, lexeme: str, scan: Scanner) -> None:
        """
        Instantiate a new Token.

        Instantiates a new Token object if the provided symbol is a _Lexeme. If
        not, it returns an exception to the scanner saying that the symbol is
        invalid.

        Raises:
            LythSyntaxError: The character being scanned could not lead to a
                             token.
        """
        symbol = Symbol.as_value(lexeme)

        if symbol is not None:
            self.symbol = symbol

        elif lexeme.isdigit():
            self.symbol = Literal.VALUE

        elif lexeme.isalpha() or lexeme == '_':
            self.symbol = Literal.STRING

        else:
            raise LythSyntaxError(scan, msg=LythError.INVALID_CHARACTER)

        self.info = TokenInfo(scan.filename, scan.lineno, scan.offset, scan.line)
        self.lexeme = lexeme

    def __call__(self) -> Token:
        """
        Finalizes the token.

        In some cases it is simple to convert the string of the lexeme to the
        right type once it is finished, rather than letting the analyzer does
        it.
        """
        if self.symbol is Literal.VALUE:
            self.lexeme = int(self.lexeme)

        return self

    def __add__(self, lexeme: str) -> Token:
        """
        Add a scanned character to an existing token.

        This method validates that the character appended to the existing token
        keeps the integrity of the token. For example, if the token is made of
        digits, it is important that the next characters are digits as well.
        Sometimes the token type changes as well. The comparator '<' could
        become an assignment if '-' is the next character being scanned.

        The methodology is the following:
        1. If the new lexeme appended to current lexeme leads to a new symbol,
           update symbol and new lexeme, and return this instance.
        2. If the new literal would be a symbol appended to a literal, there is
           clearly a missing space. Exception, such as '5!' will be corrected
           by the lexer.
        3. Appending a digit to a literal leads to appending the lexeme and
           returning current token.
        4. Appending an alphanumerical character, or '_', to a string value
           leads to appending that character to the lexeme and returning
           current token.
        5. Appending an alphanumerical character, or '_', leading to a literal
           right after a symbol, without the presence of a space leads to an
           error. Exception, such as '-5' will be corrected by the lexer.
        """
        symbol = Symbol.as_value(self.lexeme + lexeme)

        if symbol is not None:
            self.symbol = symbol
            self.lexeme += lexeme
            return self

        symbol = Symbol.as_value(lexeme)

        if symbol is not None and self.symbol in Literal:
            raise LythSyntaxError(self.info, msg=LythError.MISSING_SPACE_BEFORE_OPERATOR)

        elif lexeme.isdigit() and self.symbol in Literal:
            self.lexeme += lexeme
            return self

        elif (lexeme.isalnum() or lexeme == '_') and self.symbol is Literal.STRING:
            self.lexeme += lexeme
            return self

        elif (lexeme.isalnum() or lexeme =='_') and self.symbol in Symbol:
            raise LythSyntaxError(self.info, msg=LythError.MISSING_SPACE_AFTER_OPERATOR)

        else:
            raise LythSyntaxError(self.info, msg=LythError.SYNTAX_ERROR)

    def __eq__(self, symbol: _Lexeme) -> bool:
        """
        Testing this token is of provided symbol.
        """
        return self.symbol == symbol

    def __repr__(self) -> str:
        """
        The representation of this instance of the token plus some information.
        """
        return f"Token({self.symbol.name}, {self.lexeme!r}, {self.info.lineno}, {self.info.offset})"

    def __str__(self) -> str:
        """
        A Name Value string representation of this instance of the token.
        """
        return f"{self.symbol.name}: {self.lexeme!r}"
