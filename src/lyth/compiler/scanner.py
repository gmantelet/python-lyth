"""
This module contains the text scanner.

The Scanner is nothing more than an iterator over a string, returning the
current character being read, and providing ancillary functions such as keeping
track of line and column numbers when it becomes important to raise an
Exception.
"""


class Scanner:
    """
    The scanner for the Lexer.

    An input text is iterated over, providing characters on demand to the
    lexer. The scanner could provide a couple of ancillary functions, and could
    also acts as a linter in future versions of this tool, warning the user
    about syntax errors.

    Attributes:
        _line  (iterable): Current line to scan characters for.
        _raw   (list)    : The source code, line by line.
        _text  (iterable): An iterator on the lines of the source code.
        column (integer) : The position of the caret in the line of code.
        line   (integer) : The line of code being scanned.
    """
    def __init__(self, text):
        """
        Instantiates a new scanner.

        The scanner is instantiated and starts fetching the source code
        provided.

        Parameters:
            text: The source code to scan

        Raises:
            StopIteration: If the source code is empty.
        """
        self._raw = text.replace('\r', '').split('\n')
        self._text = iter(self._raw)
        self._line = iter(next(self._text))
        self.column = -1  # Voluntarily placing the caret at -1.
        self.line = 0

    def __getitem__(self, line):
        """
        Return the line of source code being scanned.
        """
        if line >= len(self._raw):
            return "EOF"

        return self._raw[line]

    def __iter__(self):
        """
        Make this scanner iterable.
        """
        return self

    def __next__(self):
        """
        Retrieve the next character in source code.
        """
        try:
            self.column += 1
            return next(self._line)

        except StopIteration:
            self.column = -1
            self.line += 1

        # If the end of the source code is reached, the StopIteration exception
        # is propagated to the lexer.
        self._line = iter(next(self._text))
        return next(self)

    def __repr__(self):
        """
        Returns the character being scanned in the corresponding line or source
        code.
        """
        if self.line >= len(self._raw):
            return f"{self!s}:\n\tEOF"

        return f"{self!s}:\n\t{self[self.line]}\n\t{' '* self.column }^"

    def __str__(self):
        """
        Returns the current position of the character being scanned.
        """
        return f"in line {self.line} column {self.column}"
