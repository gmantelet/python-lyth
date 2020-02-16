import pytest

from lyth.compiler.scanner import Scanner


def test_scanner():
    """
    To validate the scanner retrieves chars one at a time.
    """
    s = """let:
  a := 1 + 2
"""
    scanner = Scanner(s)

    # Because s is immutable, if I manipulate s after giving it to the scanner
    # I am currently sort of working on a copy of s, and what is given to the
    # scanner is not altered by the following operation:
    s = ''.join(s.replace('\r', '').split('\n'))

    for i, e in enumerate(scanner):
        assert e == s[i]
        if i < 4:
            assert scanner.line == 0
            assert scanner.column == i
            assert f"{scanner!s}" == f"in line 0 column {i}"
            assert f"{scanner!r}" == f"in line 0 column {i}:\n\tlet:\n\t{' '* i}^"
        else:
            assert scanner.line == 1
            assert scanner.column == i - 4
            assert f"{scanner!s}" == f"in line 1 column {i-4}"
            assert f"{scanner!r}" == f"in line 1 column {i-4}:\n\t  a := 1 + 2\n\t{' '* (i-4)}^"

    # Why does it move to 3? It is because we have an empty line right after
    # a := 1 + 2 that produces no token.
    # By convention, I also place the caret at -1 every time the scanner moves
    # to next line. So, when the scanner raises StopIteration, I always expect
    # it to stay stuck to -1.
    assert scanner.line == 3
    assert scanner.column == -1
    assert f"{scanner!s}" == f"in line 3 column -1"
    assert f"{scanner!r}" == f"in line 3 column -1:\n\tEOF"

    with pytest.raises(StopIteration):
        next(scanner)


def test_scanner_getitem():
    """
    To validate the scanner returns us the line it is scanning.
    """
    s = """let:
  a := 1 + 2
"""
    scanner = Scanner(s)
    assert scanner[0] == 'let:'
    assert scanner[1] == '  a := 1 + 2'
    assert scanner[2] == ''
    assert scanner[3] == 'EOF'
