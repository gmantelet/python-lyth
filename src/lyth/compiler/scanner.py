"""
This module contains the text scanner.

The Scanner is an iterator over a string, reading characters one by one so that
the Lexer can provide tokens.
"""


class Scanner:
    """
    The scanner for the lexer.

    This is a subcomponent of the lexer. In general a scanner returns tokens,
    this one however returns chars one by one, and provides ancillary methods,
    such as keeping track of lines for debug purposes in case an exception is
    raised.
    """
    def __init__(self):
        self._line = None
        self.filename = None
        self.lineno = 0
        self.offset = -1  # A clue that the read line is empty.
        self.raw = None
        self.text = None

    def __call__(self, text, source="<stdin>"):
        """
        Calling the scanner makes it work on the piece of source code provided
        as parameter. It makes it available as iterable over the source code.
        """
        self.raw = text.replace('\r', '').split('\n')
        self.text = iter(self.raw)
        self._line = iter(next(self.text))

        self.lineno = 0
        self.offset = -1
        self.filename = source

    def __iter__(self):
        """
        Make this scanner iterable.
        """
        return self

    def __next__(self):
        """
        Retrieve the next character in source code.

        It fetches the next character in line, and if the line is complete,
        then it jumps to next line.
        """
        try:
            char = next(self._line)

        except StopIteration:
            self.offset = -1

        else:
            self.offset += 1
            return char

        # If the end of the source code is reached, the StopIteration exception
        # is propagated to the lexer.
        self._line = iter(next(self.text))
        self.lineno += 1
        return next(self)

    def __repr__(self):
        """
        Returns the character being scanned in the corresponding line or source
        code.
        """
        return f"{self!s}:\n\t{self.raw[self.lineno]}\n\t{' '* self.offset }^"

    def __str__(self):
        """
        Returns the current position of the character being scanned.
        """
        return f"in line {self.lineno} column {self.offset}"

    @property
    def line(self):
        """
        The current line being scanned.

        This is a convenient property to let the user access the current line
        being parsed. _line attribute is an iterator and needs tweaks to be
        displayed properly while doing str(). The user may also use directly
        self.raw[self.lineno].
        """
        return self.raw[self.lineno]
