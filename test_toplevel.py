import subprocess

import pytest

from toplevel import *

NAME = __file__.split("/")[-1].split(".")[0].split("_")[-1]

is_import_test_lines = [
( "from .a import b", True),
( "from a import b", True),
( "import a as b", True),
( "import a.b", True),
( "is_import(a)", False),
( "def is_import(line):", False),
( "  # import a", False)
]


@pytest.mark.parametrize(["line", "result"],  is_import_test_lines)
def test_is_import(line, result):
    assert result == is_import(line)


clean_line_test_lines = ["from .a import b", "from abc import b",
                        "import a as b", "import a.b", "from a.b.c import d"]

clean_line_test_results = None, "abc", "a", "a", "a"

@pytest.mark.parametrize(["line", "result"],  zip(*[clean_line_test_lines, clean_line_test_results]))
def test_clean_line(line, result):
    assert result == clean_line(line)


def test_is_in_cwd():
    assert is_in_cwd(NAME)

def test_is_std_lib():
    assert is_std_lib("sys")
    assert is_std_lib("os")
    assert not is_std_lib("apps")


def test_ignore_docstrings():
    text = ["abc", '"""', "comment", '"""', "def"]
    text_wo_doc = ["abc", "def"]
    assert text_wo_doc == list(ignore_docstrings(text))

# self-test
def collect_extern_file_imports():
    assert collect_extern_file_imports(NAME) == ["pip"]


def test_end_to_end():
    assert subprocess.call("python toplevel.py --file toplevel.py --req requirements.txt", shell=True) == 0
