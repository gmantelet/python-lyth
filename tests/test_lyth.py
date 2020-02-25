import builtins
import sys
import unittest.mock
from io import StringIO

import pytest

from lyth.cli import main


@pytest.mark.parametrize("inputs, returns", [('1 + 2', 0), ])
def test_main(inputs, returns):
    """
    Start the main function, activates the console and waits
    """
    with unittest.mock.patch.object(builtins, 'input', lambda x: inputs):
        with unittest.mock.patch('sys.stdout', new_callable=StringIO):
            assert main(["test.py", "-c", "cycle=2"]) == returns
            result = sys.stdout.getvalue()
            assert "Goodbye.\n" in result
            assert "3\n" in result


def test__main__():
    """
    Start the main function, activates the console and waits
    """
    from lyth.__main__ import main
    with unittest.mock.patch.object(builtins, 'input', lambda x: '\n'):
        with unittest.mock.patch('sys.stdout', new_callable=StringIO):
            assert main(["test.py", "-c", "cycle=2"]) == 0


@pytest.mark.parametrize("inputs, returns", [('1 ; 2', 0), ])
def test_lyth_syntax_error(inputs, returns):
    """
    Start the main function, activates the console and waits
    """
    error = f"Invalid character at '<stdin>', line 0:\n\t1 ; 2\n\t  ^"

    with unittest.mock.patch.object(builtins, 'input', lambda x: inputs):
        with unittest.mock.patch('sys.stdout', new_callable=StringIO):
            assert main(["test.py", "-c", "cycle=2"]) == returns
            result = sys.stdout.getvalue()
            assert error in result
