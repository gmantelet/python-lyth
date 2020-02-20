"""
This module contains the lexer.

The Lexer is the second stage of the lexical analysis. It uses its first stage,
the Scanner, to get its characters one by one. The scanner keeps track of line
and column numbering. The Lexer produces Tokens from the characters returned by
the Scanner.
"""
from lyth.compiler.error import LythError
from lyth.compiler.error import LythSyntaxError
from lyth.compiler.token import Symbol
from lyth.compiler.token import Token


class Lexer:
    """
    The lexical analyzer for a given source code.
    """
    def __init__(self, scanner):
        """
        Instantiates a new lexer object.

        Attributes:
            scanner (Scanner): An instance of a scanner.
        """
        self.current_token = None
        self.scan = scanner

    def __call__(self, text, source="<stdin>"):
        """
        Starts the lexical analysis on the source code provided as parameter.

        It bootstraps the Scanner, making it an iterable, ready to scan the
        source code character by character. It makes the lexer an iterable,
        ready to call next upon.
        """
        self.scan(text, source)

    def __iter__(self):
        """
        Make this analyzer iterable.
        """
        return self

    def __next__(self):
        """
        Produces the next token from scanned source code.

        Spaces delimit tokens. The Scanner is ran until a space is found, or
        unless an exception is raised from the Scanner.
        """
        try:
            char = next(self.scan)

            if char.isspace():
                return self.handle_space_as_delimiter()

            else:
                return self.handle_char(char)

        except StopIteration:
            return self.handle_eof()

        except LythSyntaxError as lyth_error:
            return self.handle_syntax_error(char, lyth_error)

    def handle_char(self, char):
        """
        Handle the non space character obtained from the Scanner.

        Two options depends on whether we are currently building up a token or
        we need to create a new one:
        1. First character of a new token. Create a new token and move to next
           character.
        2. Successive character of an existing token. Go on building current
           token (aggregate) and get next character from scanner.
                NOTE: This step may raise MISSING_SPACE_AFTER_OPERATOR error.
                      The lexer needs to check if it can ignore the error. For
                      example, '+5' or '-5' are valid cases, and the parser
                      needs to check if it is a sign or an operator.
        """
        if self.current_token is None:
            self.current_token = Token(char, self.scan)

        else:
            self.current_token += char

        return next(self)

    def handle_eof(self):
        """
        The scanner is depleted. We reached end of source code.

        At that point, we have four options:
        1. The last line checked on the scanner was an empty line. If not we
           raise an exception.
        2. There is no current token being processed, we are ready to return an
           End Of File token.
        3. The current token is an end of file, we need to propagate the
           StopIteration exception from the scanner to avoid infinite loops on
           objects using this instance as iterator.
        4. There was a token being processed. We need to return it before we
           send an End Of File token.
        """
        if self.scan.line:
            raise LythSyntaxError(self.scan, msg=LythError.MISSING_EMPTY_LINE) from None

        if self.current_token is None:
            token = Token(None, self.scan)
            self.current_token = token
            return token()

        elif self.current_token.symbol is Symbol.EOF:
            raise

        else:
            token = self.current_token
            self.current_token = None
            return token()

    def handle_space_as_delimiter(self):
        """
        Spaces are token delimitors.

        There are two options depending on whether it is the first time the
        scanner encounters a space:
        1. First space encountered after an existing token is being constructed
           (aggregated). This causes the current token to be returned.
        2. Multiple spaces encountered. Skip, and move to next character
        """
        if self.current_token is not None:
            token = self.current_token
            self.current_token = None
            return token()

        else:
            return next(self)

    def handle_syntax_error(self, char, error):
        """
        We tried to concatenate a token, but there was a LythSyntaxError raised.

        There are a couple of tolerated cases at this stage of the analysis:
        1. The lexical analysis tolerates missing space after '+' or '-' only
           if these symbols represent a sign, and not an operator. The Parser
            would raise such an error at its stage.
        2. In any other LythSyntaxError, the exception is propagated.
        """
        token = self.current_token

        if error.msg is LythError.MISSING_SPACE_AFTER_OPERATOR:
            if token is not None and token.symbol in (Symbol.ADD, Symbol.SUB):
                self.current_token = Token(char, self.scan)
                return token()

        raise
