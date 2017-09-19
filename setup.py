import io
import os
import sys
from shutil import rmtree

from setuptools import setup, Command

NAME = "pip-validate"
DESCRIPTION = "Validate toplevel imports against requirements.txt"
URL = "https://github.com/ohjeah/toplevel"
EMAIL = "info@markusqua.de"
AUTHOR = "Markus Quade"
VERSION = "0.2.1"

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "requirements.txt"), "r") as f:
    REQUIRED = f.readlines()


class PublishCommand(Command):
    """Support setup.py publish."""

    description = "Build and publish the package."
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print("\033[1m{0}\033[0m".format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status("Removing previous builds ...")
            rmtree(os.path.join(here, "dist"))
        except FileNotFoundError:
            pass

        self.status("Building Source and Wheel (universal) distribution...")
        os.system("{0} setup.py sdist bdist_wheel --universal".format(sys.executable))

        self.status("Uploading the package to PyPi via Twine...")
        os.system("twine upload dist/*")

        sys.exit()


setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=__doc__,
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    py_modules=["pip_validate"],
    install_requires=REQUIRED,
    license="MIT",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
    cmdclass={
        "publish": PublishCommand,
    },
    entry_points={
            "console_scripts": [
                "pip-validate = pip_validate:main"
            ]
        },
)
