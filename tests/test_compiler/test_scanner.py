import pytest

from lyth.compiler.scanner import Scanner


def test_scanner():
    """
    To validate the scanner retrieves chars one at a time.
    """
    s = """let:
  a := 1 + 2
""".replace('\r', '')
    scan = Scanner(s)
    # scan(s)

    # Because s is immutable, if I manipulate s after giving it to the scanner
    # I am currently sort of working on a copy of s, and what is given to the
    # scanner is not altered by the following operation:
    s = ''.join(s.replace('\r', '').split('\n'))

    for i, e in enumerate(scan):

        if i < 4:
            print(f"char {i}: reading '{e}', expecting '{s[i]}'")
            print(f"{scan!r}")

            assert e == s[i]
            assert scan.lineno == 0
            assert scan.offset == i
            assert f"{scan!s}" == f"in line 0 column {i}"
            assert f"{scan!r}" == f"in line 0 column {i}:\n\t\"let:\"\n\t{' ' * (i + 1)}^"
            assert scan.line == 'let:'

        elif i == 4:
            assert e == '\n'
            # Because a \n is line feed (lineno + 1), and supposes there was \r or carriage return before (offset = -1)
            print(f"{scan!r}")
            print(f"in line 0 column 3:\n\t\"let:\"\n\t{' ' * 4}^")
            assert scan.lineno == 0
            assert scan.offset == 3
            assert f"{scan!s}" == "in line 0 column 3"
            assert f"{scan!r}" == f"in line 0 column 3:\n\t\"let:\"\n\t{' ' * 4}^"
            assert scan.line == 'let:'

        elif i < 17:
            print(f"char {i}: reading '{e}', expecting '{s[i-1]}'")
            assert e == s[i - 1]
            assert scan.lineno == 1
            assert scan.offset == i - 5
            assert f"{scan!s}" == f"in line 1 column {i - 5}"
            assert f"{scan!r}" == f"in line 1 column {i - 5}:\n\t\"  a := 1 + 2\"\n\t{' ' * (i - 4)}^"
            assert scan.line == '  a := 1 + 2'

        # elif i == 17:
        else:
            assert e == '\n'
            assert scan.lineno == 1
            assert scan.offset == i - 6
            assert f"{scan!s}" == f"in line 1 column {i - 6}"
            assert f"{scan!r}" == f"in line 1 column {i - 6}:\n\t\"  a := 1 + 2\"\n\t{' ' * (i - 5)}^"
            assert scan.line == '  a := 1 + 2'

        # else:
        #     assert False  # Potential infinite looooooooooooooop

    # begin = max(scan.data.rfind('\n', 0, scan.index - 1), 0)
    # end = scan.data.find('\n', scan.index)
    # print(f"INDEX: {scan.index}")
    # print(f"BEGIN: {begin}")
    # print(f"END  : {end}")
    # print(f"LINE : {scan.data[begin: end] if end >= 0 else scan.data[begin:]}")

    with pytest.raises(StopIteration):
        next(scan)

    assert scan.lineno == 2
    assert scan.offset == -1
    assert f"{scan!s}" == f"in line 2 column -1"
    assert f"{scan!r}" == f"in line 2 column -1:\n\t\"\"\n\t^"
    assert scan.line == ''


def test_special_space():
    """
    To validate the scanner ignores "\r".
    """
    s = "let\r:\n"
    scan = Scanner(s)

    for i, e in enumerate(scan):

        if i < 3:
            assert e == s[i]
            assert scan.lineno == 0
            assert scan.offset == i
            assert f"{scan!s}" == f"in line 0 column {i}"
            assert f"{scan!r}" == f"in line 0 column {i}:\n\t\"let:\"\n\t{' ' * (i + 1)}^"
            assert scan.line == 'let:'

        elif i == 3:
            assert e == s[i + 1]
            assert scan.lineno == 0
            assert scan.offset == i
            assert f"{scan!s}" == f"in line 0 column {i}"
            assert f"{scan!r}" == f"in line 0 column {i}:\n\t\"let:\"\n\t{' ' * (i + 1)}^"
            assert scan.line == 'let:'


def test_tabulation():
    """
    To validate the scanner considers "\t" as a single character, but double space.
    """
    s = "let\t:\n"
    scan = Scanner(s)

    for i, e in enumerate(scan):

        if i < 3:
            assert e == s[i]
            assert scan.lineno == 0
            assert scan.offset == i
            assert f"{scan!s}" == f"in line 0 column {i}"
            assert f"{scan!r}" == f"in line 0 column {i}:\n\t\"let  :\"\n\t{' ' * (i + 1)}^"
            assert scan.line == 'let  :'

        elif i == 3:
            assert e == " "
            assert scan.lineno == 0
            assert scan.offset == 3
            assert f"{scan!s}" == f"in line 0 column {3}"
            assert f"{scan!r}" == f"in line 0 column {3}:\n\t\"let  :\"\n\t{' ' * 4}^"
            assert scan.line == 'let  :'

        elif i == 4:
            assert e == " "
            assert scan.lineno == 0
            assert scan.offset == 3
            assert f"{scan!s}" == f"in line 0 column {3}"
            assert f"{scan!r}" == f"in line 0 column {3}:\n\t\"let  :\"\n\t{' ' * 4}^"
            assert scan.line == 'let  :'
