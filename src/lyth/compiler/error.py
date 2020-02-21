"""
This module lists all the bad thing that can happen during the execution of a
compiler.
"""
from enum import Enum


class LythError(Enum):
    """
    The list of all the error types that can be found during the compilation of
    a lyth script.
    """
    OK = "No error - keep up the good work!"
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
    def __init__(self, info, msg=LythError.SYNTAX_ERROR):
        super().__init__(f"{msg.value} at '{info.filename}', line {info.lineno}:\n\t"
                         f"{info.line}\n\t{' ' * info.offset}^")

        self.filename = info.filename
        self.lineno = info.lineno
        self.offset = info.offset
        self.line = info.line
        self.msg = msg
