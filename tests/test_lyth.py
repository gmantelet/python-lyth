
from lyth.cli import main


def test_main():
    assert main([]) == 0


def test__main__():
    from lyth.__main__ import main
    assert main([]) == 0
