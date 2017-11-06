import os
import subprocess

import pytest

from pip_validate import *

is_import_test_lines = [
    ("from .a import b", True),
    ("from a import b", True),
    ("import a as b", True),
    ("import a.b", True),
    ("is_import(a)", False),
    ("def is_import(line):", False),
    ('"All imports of {} are listed in {}".format(args.dir or args.file, args.req)', False)
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


def test_ignore_docstrings_and_comments():
    text = ["abc", 'e"""', "'''docstring1", "docstring2", '"""', "#comment", "def"]
    text_wo_doc = ["abc", 'e', "def"]
    assert text_wo_doc == list(ignore_docstrings_and_comments(text))


def test_is_relative_import():
    assert is_relative_import(".version")
    assert not is_relative_import("version")

def test_in_path():
    assert in_path("pip_validate", ".")


def test_is_std_lib():
    assert is_std_lib("sys")
    assert is_std_lib("os")
    assert not is_std_lib("apps")
    assert not is_std_lib("")


def is_connected():
    import socket
    try:
        host = socket.gethostbyname("www.google.com")
        socket.create_connection((host, 80), 2)
        return True
    except:
        pass
    return False


@pytest.mark.skipif(not is_connected(), reason="Need an internet connection")
def test_match_to_alias():
    imports = ["dateutil"]
    requirements = ["python-dateutil"]
    aliases = match_to_alias(imports, requirements)
    for i, r in zip(imports, requirements):
        assert aliases[i] == r

@pytest.mark.skipif(not is_connected(), reason="Need an internet connection")
def test_validate_imports_alias():
    assert validate_imports(["dateutil"], ["python-dateutil"])
    assert not validate_imports(["dateutil"], ["___"])


def test_validate_imports():
    assert validate_imports(["a", "b", "c"], ["a", "b", "c"])

# self-test
@pytest.mark.skipif(not is_connected(), reason="Need an internet connection")
def test_collect_extern_file_imports():
    assert set(collect_extern_file_imports("pip_validate.py")) == set(["pip", "crayons"])


@pytest.mark.skipif(not is_connected(), reason="Need an internet connection")
def test_collect_dir_imports():
    imports = collect_dir_imports(os.path.dirname(__file__))
    for k, v in imports.items():
        if "setup.py" in k:
            assert v == ["setuptools"]
        elif "test_" in k:
            assert v == ["pytest"]
        else:
            assert set(v) == set(["pip", "crayons"])


def test_end_to_end_file():
    assert subprocess.call("pip-validate --file pip_validate.py --req requirements.txt", shell=True) == 0


@pytest.mark.skipif(not is_connected(), reason="Need an internet connection")
def test_end_to_end_dir():
    # dev requirements are missing and this file imports pytest
    assert subprocess.call("python pip_validate.py --dir . --req requirements.txt", shell=True) == 1
