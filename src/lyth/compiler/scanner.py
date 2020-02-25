"""
This module contains the text scanner.

The Scanner is a generator over a string, reading characters one by one so that
the Lexer can build tokens from it.
"""
from __future__ import annotations

from typing import Generator


class Scanner:
    """
    The scanner for the lexer.

    This is a subcomponent of the lexer. In general a scanner returns tokens,
    this one however returns chars one by one, and provides ancillary methods,
    such as keeping track of lines for debug purposes in case an exception is
    raised.
    """
    def __init__(self, data: str, filename: str = "<stdin>") -> None:
        """
        Instantiate the scanner.

        The scanner requires a source of characters, ideally an iterable like a
        string, and optionally, a filename if the source has been retrieved
        from there (but it could be an IP address for example, a urn and so on)
        """
        self.data: str = data
        self.filename: str = filename
        self.index: int = 0
        self.lineno: int = 0
        self.offset: int = -1
        self._stream: Generator[str, None, None] = self.next()

    def __call__(self) -> str:
        """
        Retrieve the next character in source code.

        It fetches the next character in line, and if the end of line is
        reached, it sends "\n" and then it jumps to next line.

        If the end of the source code is reached, the StopIteration exception
        is propagated to the lexer.
        """
        return next(self._stream)

    def __iter__(self) -> Scanner:
        """
        Convenience method to make this instance interable.
        """
        return self

    def __next__(self) -> str:
        """
        Convenience method to retrieve the next character in source code.

        This is used if you really need to use this instance as an iterator as
        I did in some of my test case for convenience. Otherwise, the instance
        is callable because it has practically only one meaning in life which
        is fetching the next character...
        """
        return next(self._stream)

    @property
    def line(self) -> str:
        """
        The current line being scanned.

        This is a convenient property to let the user access the current line
        being parsed. The property looks for enclosing feed line characters,
        before and after the character being scanned. If the character does not
        exist before, it starts from the begining of the source being scanned,
        if it does not exist after, it goes all through the source until its
        end.
        """
        begin = self.data.rfind('\n', 0, self.index - 1)
        end = self.data.find('\n', self.index - 1)
        data = self.data[begin + 1: end] if end >= 0 else self.data[begin + 1:]
        return data.replace('\r', '').replace('\t', '  ')

    def next(self) -> str:
        """
        Shift the scanner to its right, returns the char being read.

        This is a generator yielding a string, character by character. It may
        eventually ignore characters, such as carriage return, or convert
        tabulations automatically.

        When a feed line character is detected, the offset is updated after
        yielding the character, and it is not incremented before, thus, it must
        show that the scanner is still looking at the previous character. This
        helps determine empty lines.

        When the end of the file is reached, next simply leaves, causing the
        generator to raise StopIteration in its lexer parent instance. It also
        flushes the source being scanned to void further scan on that source.

        Raises:
            StopIteration: After the last character of the source has been
                           read, upon IndexError.
        """
        while True:
            try:
                char = self.data[self.index]
                self.index += 1

                if char == '\r':
                    continue

                elif char == '\n':
                    yield char
                    self.lineno += 1
                    self.offset = -1
                    continue

                elif char == '\t':
                    self.offset += 1
                    yield ' '
                    yield ' '

                else:
                    self.offset += 1
                    yield char

            except IndexError:
                self.data = ""
                break

    def __repr__(self) -> str:
        """
        Returns the character being scanned in the corresponding line or source
        code.
        """
        return f"{self!s}:\n\t\"{self.line.replace(chr(13), '').replace(chr(9), '  ')}\"\n\t{' ' * (self.offset + 1)}^"

    def __str__(self) -> str:
        """
        Returns the current position of the character being scanned.
        """
        return f"in line {self.lineno} column {self.offset}"
