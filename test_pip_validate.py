import os
import ast
import subprocess

import pytest

from pip_validate import *


import_test_cases = [
    ("import a", ("a",)),
    ("import a.b", ("a",)),
    ("""def f(a):
        import a as b
    """, ("a",)),
    ("""class A:
        class B:
            def __init__(self):
                import c
        def __init__(self):
            self.b = B()
    """, ("c",)),
    ("#a comment", ()),
]


@pytest.mark.parametrize(["case", "result"],  import_test_cases)
def test_ImportVisitor(case, result):
    tree = ast.parse(case)
    visitor = ImportVisitor()
    visitor.visit(tree)
    assert sorted(result) == visitor.non_relative_imports


def test_in_path():
    assert in_path("pip_validate", ".")


def test_is_std_lib():
    assert is_std_lib("sys")
    assert is_std_lib("os")
    assert not is_std_lib("apps")
    assert not is_std_lib("..apps")


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
    aliases, unsed_req = match_to_alias(imports, requirements)
    for i, r in zip(imports, requirements):
        assert aliases[i] == r
    assert unsed_req == []


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
