# -*- coding: utf-8 -*-
"""
AppVeyor will at least have a few Pythons around, so there's no point of implementing a
bootstrapper in PowerShell.

This is a port of
<https://github.com/pypa/python-packaging-user-guide/blob/master/source/code/install.ps1>
with various fixes and improvements that just weren't feasible to implement in
PowerShell.
"""

from __future__ import print_function

from os import environ
from os.path import exists
from shlex import shlex
from subprocess import check_call

try:
    from urllib.request import urlretrieve
except ImportError:
    from urllib import urlretrieve  # noqa


def shlex_split(string):
    lex = shlex(string, posix=True)
    lex.whitespace_split = True
    lex.commenters = ""
    return list(lex)


BASE_URL = "https://www.python.org/ftp/python/"
GET_PIP_URL = "https://bootstrap.pypa.io/get-pip.py"
GET_PIP_PATH = "C:\\get-pip.py"

VERSIONS = {
    "2.7": ("2.7.15", "msi"),
    "3.4": ("3.4.4", "msi"),
    "3.5": ("3.5.6", "exe"),
    "3.6": ("3.6.7", "exe"),
    "3.7": ("3.7.1", "exe"),
}
ARITY = {"64": "{0}/python-{0}.amd64.{1}", "32": "{0}/python-{0}.{1}"}

INSTALL_CMD = {
    # Commands are allowed to fail only if they are not the last command.
    # Eg: uninstall (/x) allowed to fail
    "msi": [
        shlex_split("msiexec.exe /L*+! install.log /qn /x {path}"),
        shlex_split("msiexec.exe /L*+! install.log /qn /x {path}"),
    ],
    "exe": [shlex_split("{path} /quiet TargetDir={home}")],
}


def download_file(url, path):
    print("Downloading: {} (into {})".format(url, path))
    progress = [0, 0]

    def report(count, size, total):
        progress[0] = count * size
        if progress[0] - progress[1] > 1000000:
            progress[1] = progress[0]
            print("Downloaded {:,}/{:,} ...".format(progress[1], total))

    dest, _ = urlretrieve(url, path, reporthook=report)
    return dest


def install_python(version, arch, home):
    print(
        "Installing Python {} for {} bit architecture to {}".format(version, arch, home)
    )
    if exists(home):
        return

    path, extension = download_python(version, arch)
    print("Installing {} to {}".format(path, home))
    success = False
    for cmd in INSTALL_CMD[extension]:
        cmd = [part.format(home=home, path=path) for part in cmd]
        print("Running: {}".format(" ".join(cmd)))
        try:
            check_call(cmd)
        except Exception as exc:
            print("Failed command '{}' with: {}".format(" ".join(cmd), exc))
            if exists("install.log"):
                with open("install.log") as fp:
                    print(fp.read())
        else:
            success = True

    if success:
        print("Installation complete!")
    else:
        print("Installation failed!")


def download_python(version, arch):
    full_version, extension = VERSIONS[version]
    url = ARITY[arch].format(full_version, extension)
    path = "installer.{}".format(extension)
    for _ in range(3):
        try:
            return download_file(url, path), extension
        except Exception as exc:
            print("Failed to download: {}".format(exc))
        print("Retrying...")


def install_pip(home):
    pip_path = home + "/Scripts/pip.exe"
    python_path = home + "/python.exe"
    if exists(pip_path):
        print("pip already installed.")
    else:
        print("Installing pip...")
        download_file(GET_PIP_URL, GET_PIP_PATH)
        print("Executing: {} {}".format(python_path, GET_PIP_PATH))
        check_call([python_path, GET_PIP_PATH])


def install_packages(home, *packages):
    cmd = [home + "/Scripts/pip.exe", "install"]
    cmd.extend(packages)
    check_call(cmd)


if __name__ == "__main__":
    install_python(
        environ["PYTHON_VERSION"], environ["PYTHON_ARCH"], environ["PYTHON_HOME"]
    )
    install_pip(environ["PYTHON_HOME"])
    install_packages(
        environ["PYTHON_HOME"],
        "setuptools>=18.0.1",
        "wheel",
        "tox",
        "virtualenv>=13.1.0",
    )
