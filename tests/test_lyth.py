import builtins
import sys
import unittest.mock
from io import StringIO

import pytest

from lyth.cli import main


@pytest.mark.parametrize("inputs, returns", [('1 + 2', 0), ('1 * 2 + 1', 0), ('2 * 2 - 1', 0)])
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


def test_keyboard_interrupt():
    """
    Start the main function, activates the console and send ctrl-c to it
    """
    from lyth.__main__ import main
    with unittest.mock.patch.object(builtins, 'input', lambda x: (_ for _ in ()).throw(KeyboardInterrupt())):
        with unittest.mock.patch('sys.stdout', new_callable=StringIO):
            assert main(["test.py", "-c", "cycle=2"]) == 0
            assert "Keyboard interrupt" in sys.stdout.getvalue()
            assert "Goodbye.\n" in sys.stdout.getvalue()


def test_exception():
    """
    Start the main function, activates the console and send ctrl-c to it
    """
    from lyth.__main__ import main
    with unittest.mock.patch.object(builtins, 'input', lambda x: (_ for _ in ()).throw(Exception("exception from test"))):
        with unittest.mock.patch('sys.stdout', new_callable=StringIO):
            with unittest.mock.patch('sys.stderr', new_callable=StringIO):
                assert main(["test.py", "-c", "cycle=2"]) == 1
                assert "Exception: exception from test" in sys.stderr.getvalue()
                assert "Goodbye.\n" in sys.stdout.getvalue()


countdown = 0


def _delayed_interrupt(inp):
    """
    This function is used to mock input(). It returns 5 empty lines before
    mocking a ctrl-c command from a user.
    """
    global countdown

    if countdown < 5:
        countdown += 1
        return '\n'

    countdown = 0
    raise KeyboardInterrupt()


def test_idle():
    """
    Testing an idle console.
    """
    from lyth.__main__ import main
    with unittest.mock.patch.object(builtins, 'input', _delayed_interrupt):
        with unittest.mock.patch('sys.stdout', new_callable=StringIO):
            assert main([]) == 0
            assert "Goodbye.\n" in sys.stdout.getvalue()


def test__main__():
    """
    Start the main function, activates the console and waits
    """
    from lyth.__main__ import main
    with unittest.mock.patch.object(builtins, 'input', lambda x: (_ for _ in ()).throw(KeyboardInterrupt())):
        with unittest.mock.patch('sys.stdout', new_callable=StringIO):
            assert main(["test.py", "-c", "cycle=2"]) == 0
            assert "Keyboard interrupt" in sys.stdout.getvalue()
            assert "Goodbye.\n" in sys.stdout.getvalue()


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
