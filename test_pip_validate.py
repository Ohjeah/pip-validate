import os
import subprocess

import pytest

from pip_validate import *

NAME = "pip_validate"

def test_is_in_cwd():
    assert is_in_cwd(NAME)


def test_is_std_lib():
    assert is_std_lib("sys")
    assert is_std_lib("os")
    assert not is_std_lib("apps")
    assert not is_std_lib("")

# self-test
def test_collect_extern_file_imports():
    assert set(collect_extern_file_imports(NAME + ".py")) == set(["pip", "crayons"])


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


def test_end_to_end_dir():
    # dev requirements are missing and this file imports pytest
    assert subprocess.call("python pip_validate.py --dir . --req requirements.txt", shell=True) == 1
