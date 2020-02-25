"""
This module lists all the bad thing that can happen during the execution of a
compiler.
"""
from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lyth.compiler.token import TokenInfo


class LythError(Enum):
    """
    The list of all the error types that can be found during the compilation of
    a lyth script.
    """
    OK = "No error - keep up the good work!"
    GARBAGE_CHARACTERS = "Garbage characters ending line"
    INCOMPLETE_LINE = "Incomplete line"
    INVALID_CHARACTER = "Invalid character"
    MISSING_EMPTY_LINE = "Missing empty line right before end of file"
    MISSING_SPACE_BEFORE_OPERATOR = "Missing space before operator"
    MISSING_SPACE_AFTER_OPERATOR = "Missing space after operator"
    NUMERAL_EXPECTED = "Numeral expected"
    SYNTAX_ERROR = "Invalid syntax"


class LythSyntaxError(Exception):
    """
    The SyntaxError with an alias linking it to the lyth code, not the python
    execution itself.
    """
    def __init__(self, info: TokenInfo, msg: LythError = LythError.SYNTAX_ERROR) -> None:
        super().__init__(f"{msg.value} at '{info.filename}', line {info.lineno}:\n\t"
                         f"{info.line}\n\t{' ' * info.offset}^")

        self.filename = info.filename
        self.lineno = info.lineno
        self.offset = info.offset
        self.line = info.line
        self.msg = msg
