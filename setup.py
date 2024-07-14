import subprocess

from setuptools import find_packages, setup

from larch import __version__

pipenv_run = subprocess.run(["pipenv", "requirements"], stdout=subprocess.PIPE)
requirements_txt = pipenv_run.stdout.decode()

setup(
    name="larch-pm",
    version=__version__,
    description="Universal CLI package manager, written in Python",
    url="https://github.com/alex-rusakevich/larch",
    packages=find_packages(),
    entry_points={"console_scripts": ["larch = larch.cli:run_cli"]},
    install_requires=requirements_txt.splitlines()[1:],
    python_requires=">=3.8",
)
