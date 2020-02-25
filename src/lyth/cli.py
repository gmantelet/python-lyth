"""
Module that contains the command line application.
"""
import sys
import traceback

from lyth.compiler.error import LythSyntaxError
from lyth.compiler.interpreter import Interpreter
from lyth.compiler.lexer import Lexer
from lyth.compiler.parser import Parser
from lyth.compiler.scanner import Scanner
from lyth.usage import fetch


def main(argv=sys.argv):
    """
    The main entry point of the application.
    """
    settings = fetch(argv[1:])
    error = 0

    interpreter = Interpreter()

    count = 0

    while count <= settings.cycle:
        try:
            scanner = Scanner(input('>>> ') + "\n")
            parser = Parser(Lexer(scanner))

            cmd = next(parser)

            if cmd is not None:
                print(interpreter.visit(cmd))

        except LythSyntaxError as e:
            print(e)

        except KeyboardInterrupt:
            break

        except Exception:
            exc_type, exc_value, exc_tb = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_tb)
            error = 1
            break

        if settings.cycle:
            count += 1

    print("Goodbye.")
    return error
