import argparse
import itertools
import re
import sys
import os
import imp

import crayons
from pip.req import parse_requirements
from pip.commands import SearchCommand


def is_import(line):
    """Does this line use the import keyword"""
    pattern = r"[ \t]*import[ \t]+|[ \t]+import[ \t]+"
    for token in ["'", '"']: # do we use import in a string
        if token in line:
            return False
    return bool(re.findall(pattern, line))


def clean_line(line):
    """Find the toplevel module which is imported"""
    pattern = r"(\.?\w+)?(\.?\w+)*[ ]?import[ ]?(\.?\w+)?"
    groups = re.search(pattern, line.strip()).groups()
    module = groups[0] if groups[0] is not None else groups[2]
    if "." in module:
        return None
    else:
        return module.strip()


def ignore_docstrings_and_comments(lines):
    """Only look at the acutal code when searching for imports"""
    marker = None
    for line in lines:

        if marker is None:
            l = line.split("'''")[0].split('"""')[0].split('#')[0]
            if l:
                yield l

            if '"""' in line:
                marker = '"""'
            elif "'''" in line:
                marker = "'''"

        elif marker in line:
            marker = None


def find_toplevel_imports(filename):
    with open(filename, "r") as f:
        imports = (clean_line(line) for line in
                   ignore_docstrings_and_comments(f.readlines())
                   if is_import(line))
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
    if "site-packages" in module_path:
        return False
    return "python" in module_path or "lib" in module_path


def in_path(module_name, path="."):
    return module_name in [f.split(".py")[0] for f in os.listdir(path)] or module_name == path


def collect_extern_file_imports(fname, path="."):
    imports = find_toplevel_imports(fname)
    return [i for i in imports if not in_path(i, path) and not is_std_lib(i)]


def collect_dir_imports(path):
    imports = {}
    for root, dirs, files in os.walk(path, topdown=False):
        for f in [f for f in files if os.path.splitext(f)[1] == ".py"]:
            path_to_file = os.path.join(root, f)
            imports[path_to_file] = collect_extern_file_imports(path_to_file, path)
    return imports


def read_requirements(fname):
    return [r.req.name for r in parse_requirements(fname, session="hack")]


def find_alias_on_pypi(name):
    search = SearchCommand()
    options, query = search.parse_args([name])
    hits = search.search(query, options)
    return [hit["name"] for hit in hits]


def match_to_alias(imports, requirements):
    req = requirements[:]
    aliases = {}
    for import_ in imports:
        hits = find_alias_on_pypi(import_)
        for hit in hits:
            if hit in req:
                req.pop(req.index(hit))
                aliases[import_] = hit
                break
        else:
            aliases[import_] = None
    return aliases


def validate_imports(imports, requirements):
    valid = True
    not_in_req = [i for i in imports if i not in requirements]
    unsed_req = [r for r in requirements if r not in imports]

    if not_in_req and not unsed_req:
        valid = False

    elif not_in_req:
        aliases = match_to_alias(not_in_req, unsed_req)
        for k, v in aliases.items():
            if v is None:
                msg = "{} not listed in requirements.".format(k)
                print(crayons.red(msg))
                valid = False
    return valid


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--file", default=None, help="single file")
    group.add_argument("--dir", default=None, help="directory")
    parser.add_argument("--req", nargs='*', help="compare to requirements")
    args = parser.parse_args()

    if args.file is not None:
        imports = set(collect_extern_file_imports(args.file))
    else:
        imports = set(itertools.chain.from_iterable(
                        collect_dir_imports(args.dir).values()))

    if args.req:
        req = sum(map(read_requirements, args.req), [])
        all_valid = validate_imports(imports, req)
        if all_valid:
            msg = "All imports of {} are listed in {}".format(args.dir or args.file, args.req)
            print(crayons.green(msg))
            sys.exit(0)
        else:
            sys.exit(1)
    #else:
    #    for i in imports:
    #        print("Found:", i)


if __name__ == '__main__':
    main()
