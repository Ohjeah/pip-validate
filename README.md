**pip-validate**
---
[![PyPI version](https://badge.fury.io/py/pip-validate.svg)](https://badge.fury.io/py/pip-validate) [![](https://travis-ci.org/Ohjeah/pip-validate.svg)](https://travis-ci.org/Ohjeah/pip-validate/) [![codecov](https://codecov.io/gh/Ohjeah/pip-validate/branch/master/graph/badge.svg)](https://codecov.io/gh/Ohjeah/pip-validate)

### Installation

`pip install pip-validate`

### Usage

`pip-validate --file pip_validate.py --reg requirements.txt`

You can either use `--file` to check a single file or `--dir` to check a module.

### How does it work

Python files are parsed for import and import from statements. (other ways to import modules, e.g. using `__import__()` are not considered).

Found _external_ imports and entries in your `requirements.txt` file will be matched. If PyPI name and module name differ, e.g. `delegator.py` and `delegator`, `pip-search` is used to resolve aliases.

Namespace modules are currently not resolved.
