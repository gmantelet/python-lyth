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
    LEFT_MEMBER_IS_EXPRESSION = "Left member of assignment should not be an expression"
    LET_ON_EXPRESSION = "Let keyword unexpected on expression"
    LITERAL_EXPECTED = "Literal expected"
    MISSING_EMPTY_LINE = "Missing empty line right before end of file"
    MISSING_SPACE_BEFORE_OPERATOR = "Missing space before operator"
    MISSING_SPACE_AFTER_OPERATOR = "Missing space after operator"
    NAME_EXPECTED = "Variable name expected"
    REASSIGN_IMMUTABLE = "Reassigning an immutable variable"
    SYNTAX_ERROR = "Invalid syntax"
    UNEVEN_INDENT = "Uneven indent"
    VARIABLE_REFERENCED_BEFORE_ASSIGNMENT = "Variable referenced before assignment"


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
