"""
This module contains the lexer.

The Lexer is the second stage of the lexical analysis. It uses its first stage,
the Scanner, to get its characters one by one. The scanner keeps track of line
and column numbering. The Lexer produces Tokens from the characters returned by
the Scanner.
"""
from __future__ import annotations

from typing import Generator

from lyth.compiler.error import LythError
from lyth.compiler.error import LythSyntaxError
from lyth.compiler.scanner import Scanner
from lyth.compiler.token import Symbol
from lyth.compiler.token import Token


class Lexer:
    """
    The lexical analyzer for a given source code.
    """
    def __init__(self, scanner: Scanner) -> None:
        """
        Instantiate the lexer.

        The lexer requires an instance of a scanner on a source of characters.
        It can be anything that is an iterable, a generator that eventually
        raises StopIteration.
        """
        self.scanner: Scanner = scanner
        self._stream: Generator[Token, None, None] = self.next()

    def __call__(self) -> Token:
        """
        Retrieve the next token in source code.

        It fetches the next token in line, and if the end of line is
        reached, it inserts an EOL token.

        If the end of the source code is reached, the StopIteration exception
        is tested. An empty line should be detected or a syntax error is
        raised. Eventually, the end of file is processed as a space, and an EOF
        token is appended.
        """
        return next(self._stream)

    def __iter__(self) -> Lexer:
        """
        Convenience method to make this instance interable.
        """
        return self

    def __next__(self) -> Token:
        """
        Convenience method to retrieve the next token in source code.

        This is used if you really need to use this instance as an iterator as
        I did in some of my test case for convenience. Otherwise, the instance
        is callable because it has practically only one meaning in life which
        is fetching the next token...
        """
        return next(self._stream)

    def next(self) -> Token:
        """
        Get the next token in source being scanned.

        This method assumes spaces as delimiters. Spaces in python comprise
        escape characters (feed line etc.) as well. It yields tokens upon space
        and successive spaces are ignored.

        There are multiple case to consider here.
        1. A space is detected and a token is being built. The generator yields
           the token, effectively stopping its construction.
        2. A space is detected and an indent token is being built. The
           generator appends the space to this indent.
        3. If the space is a feed line character, the generator yields a new
           EOL token right after.
        4. If the space is in first column, this is the beginning of an indent
           and a corresponding token is instantiated.
        5. Other spaces following are ignored, looping through the while loop
           to retrieve another character (and so on)
        6. If it is not a space and it ends an indent, the generator yields
           first the indent.
        7. If it is not a space and no token is present, then we start creating
           one.
        8. If a colon is following directly another token, we stop building the
           token, return it, and generate a colon token.
        9. If it is not a space and a token is present, then we continue the
           construction of the current token.

        When the end of file is reached:
        1. If the scanner reached the end of its source, and the last token is
           not an EOL located at the begining of previous file, then the
           generator pedanticly asks for an empty line.
        2. EOF is treated as an empty space, the generator yields the last
           token, effectively stopping its construction.
        3. The generator then adds an EOF token and leaves the while loop,
           causing the generator to raise StopIteration on future next() calls.

        Exceptions can be ignored:
        1. The scanner pedanticly requires that symbols are separated with
           spaces. However '+5', '-5' and '5!' are examples of valid
           expressions. The generator yields current token and starts a new
           one.
        """
        token = None

        while True:
            try:
                char = self.scanner()

                if char.isspace():
                    #
                    # 1. A space is detected, and a token is being built.
                    #
                    if token is not None and token != Symbol.INDENT:
                        yield token()

                    #
                    # 2. A space is detected, and an indent token is being
                    #    built.
                    #
                    elif token is not None and token == Symbol.INDENT:
                        token += ' '
                        continue

                    #
                    # 3. If the space is a feed line character, the generator
                    #    inserts a new EOL token.
                    #
                    if char == '\n':
                        yield Token('\n', self.scanner)

                    token = None

                    #
                    # 4. If the space is in the first column, this is the
                    #    beginning of an indent.
                    #
                    if self.scanner.offset == 0:
                        token = Token(' ', self.scanner)
                        continue

                    #
                    # 5. Other spaces following are ignored.
                    #
                    continue

                #
                # 6. If it is not a space and it ends an indent, the generator
                #    returns the indent first
                #
                if token is not None and token == Symbol.INDENT:
                    yield token()
                    token = None

                #
                # 7. If it is not a space and no token is present, then we
                #    start defining a new token
                #
                if token is None:
                    token = Token(char, self.scanner)
                    if token == Symbol.COLON:
                        raise LythSyntaxError(token.info, msg=LythError.TOO_MUCH_SPACE_BEFORE)

                #
                # 8. A colon token is following directly another token
                #
                elif token is not None and char == ':':
                    yield token
                    token = Token(char, self.scanner)

                #
                # 9. If it is not a space and a token is present, then we
                #    append the character to the token.
                #
                else:
                    token += char

            except StopIteration:
                if token is not None and (token.symbol is not Symbol.EOL or token.lineno != 0):
                    raise LythSyntaxError(token.info, msg=LythError.MISSING_EMPTY_LINE) from None

                yield Token(None, self.scanner)
                break

            except LythSyntaxError as error:
                if error.msg is LythError.MISSING_SPACE_AFTER_OPERATOR:
                    if token is not None and token.symbol in (Symbol.ADD, Symbol.SUB, Symbol.LPAREN):
                        yield token()
                        token = Token(char, self.scanner)
                        continue

                elif error.msg is LythError.MISSING_SPACE_BEFORE_OPERATOR:
                    new_token = Token(char, self.scanner)
                    if new_token.symbol is Symbol.RPAREN:
                        yield token()
                        token = new_token
                        continue

                raise
