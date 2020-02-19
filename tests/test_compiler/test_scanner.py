import pytest

from lyth.compiler.scanner import Scanner


def test_scanner():
    """
    To validate the scanner retrieves chars one at a time.
    """
    s = """let:
  a := 1 + 2
"""
    scan = Scanner()
    scan(s)

    # Because s is immutable, if I manipulate s after giving it to the scanner
    # I am currently sort of working on a copy of s, and what is given to the
    # scanner is not altered by the following operation:
    s = ''.join(s.replace('\r', '').split('\n'))

    for i, e in enumerate(scan):
        assert e == s[i]
        if i < 4:
            assert scan.lineno == 0
            assert scan.offset == i
            assert f"{scan!s}" == f"in line 0 column {i}"
            assert f"{scan!r}" == f"in line 0 column {i}:\n\tlet:\n\t{' '* i}^"
            assert scan.line == 'let:'
        else:
            assert scan.lineno == 1
            assert scan.offset == i - 4
            assert f"{scan!s}" == f"in line 1 column {i-4}"
            assert f"{scan!r}" == f"in line 1 column {i-4}:\n\t  a := 1 + 2\n\t{' '* (i-4)}^"
            assert scan.line == '  a := 1 + 2'

    assert scan.lineno == 2
    assert scan.offset == -1
    assert f"{scan!s}" == f"in line 2 column -1"
    assert f"{scan!r}" == f"in line 2 column -1:\n\t\n\t^"
    assert scan.line == ''

    with pytest.raises(StopIteration):
        next(scan)
