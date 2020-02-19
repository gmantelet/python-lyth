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
    INVALID_CHARACTER = "Invalid character"
    MISSING_SPACE_BEFORE_OPERATOR = "Missing space before operator"
    MISSING_SPACE_AFTER_OPERATOR = "Missing space after operator"
    MISSING_EMPTY_LINE = "Missing empty line right before end of file"
    SYNTAX_ERROR = "Invalid syntax"


class LythSyntaxError(Exception):
    """
    The SyntaxError with an alias linking it to the lyth code, not the python
    execution itself.
    """
    def __init__(self, filename, lineno, offset, line, msg=LythError.SYNTAX_ERROR):
        super().__init__(f"{msg.value} at '{filename}', line {lineno}:\n\t{line}\n\t{' ' * offset}^")
        self.filename = filename
        self.lineno = lineno
        self.offset = offset
        self.line = line
        self.msg = msg
