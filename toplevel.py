import argparse
import itertools
import re
import sys
import os
import imp

import crayons
from pip.req import parse_requirements


def is_import(line):
    """Does this line use the import keyword"""
    pattern = r"[ \t]*import[ \t]+|[ \t]+import[ \t]*"
    return not line.strip().startswith("#") and bool(re.findall(pattern, line))


def clean_line(line):
    """Find the toplevel module which is imported"""
    pattern = r"(\.?\w+)?(\.?\w+)*[ ]?import[ ]?(\.?\w+)?"
    groups = re.search(pattern, line.strip()).groups()
    module = groups[0] if groups[0] is not None else groups[2]
    if "." in module:
        return None
    else:
        return module.strip()


def ignore_docstrings(lines):
    in_docstring = False
    for line in lines:
        found_marker = '"""' in line or "'''" in line
        if not in_docstring and not found_marker:
            yield line
        in_docstring = in_docstring != found_marker


def find_toplevel_imports(filename):
    with open(filename, "r") as f:
        imports = (clean_line(line) for line in ignore_docstrings(f.readlines()) if is_import(line))
    return set(filter(bool, imports))


def _get_module_path(module_name):
    paths = sys.path[:]
    if os.getcwd() in sys.path:
        paths.remove(os.getcwd())
    try:
        return imp.find_module(module_name, paths)[1]
    except ImportError:
        return ''


def is_std_lib(module_name):
    if not module_name:
        return False

    if module_name in sys.builtin_module_names:
        return True

    module_path = _get_module_path(module_name)
    if 'site-packages' in module_path:
        return False
    return 'python' in module_path


def is_in_cwd(module_name):
    return module_name in [f.split(".py")[0] for f in os.listdir(os.getcwd())]


def collect_extern_file_imports(fname):
    imports = find_toplevel_imports(fname)
    return [i for i in imports if not is_in_cwd(i) and not is_std_lib(i)]


def collect_dir_imports(dir):
    imports = {}
    for root, dirs, files in os.walk(dir, topdown=False):
        for f in [f for f in files if os.path.splitext(f)[1] == ".py"]:
            path_to_file = os.path.join(root, f)
            imports[path_to_file] = collect_extern_file_imports(path_to_file)
    return imports


def validate_imports(imports, requirements):
    valid = True
    for i in imports:
        if i not in requirements:
            msg = "{} not listed in requirements.".format(i)
            print(crayons.red(msg))
            valid = False
    return valid


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--file", default=None, help="single file")
    group.add_argument("--dir", default=None, help="directory")
    parser.add_argument("--req", default=None, help="compare to requirements")
    args = parser.parse_args()

    if args.file is not None:
        imports = set(collect_extern_file_imports(args.file))
    else:
        imports = set(itertools.chain.from_iterable(collect_dir_imports(args.dir).values()))


    if args.req is not None:
        req = [r.req.name for r in parse_requirements(args.req, session="hack")]
        all_valid = validate_imports(imports, req)
        if all_valid:
            msg = "All imports of {} are listed in {}".format(args.dir or args.file, args.req)
            print(crayons.green(msg))
            sys.exit(0)
        else:
            sys.exit(1)

if __name__ == '__main__':
    main()
