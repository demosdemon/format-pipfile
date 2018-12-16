# -*- coding: utf-8 -*-
from __future__ import absolute_import

import pytest
import requests
from format_pipfile import cli
from tomlkit.items import Key

from . import html


def test_cli_help(cli_runner):
    result = cli_runner.invoke(cli.main, ["--help"], prog_name="format-pipfile")

    assert result.exit_code == 0
    assert "Usage: format-pipfile [OPTIONS]" in result.output
    assert "Update the requirements.txt file and reformat the Pipfile." in result.output
    assert "-r, --requirements-file FILE" in result.output
    assert "--skip-requirements-file" in result.output
    assert "-p, --pipfile FILE" in result.output
    assert "--skip-pipfile" in result.output
    assert "--help" in result.output


def test_unwrap_key():
    k = Key("test")
    assert cli.unwrap_key(k) == "test"
    assert cli.unwrap_key("test") == "test"
    assert cli.unwrap_key(None) is None


def test_reorder_container():
    pass


@pytest.mark.parametrize(
    ("pair", "expected"),
    [
        (("name", "pypi"), (0, "name")),
        (("url", "https://pypi.org/simple"), (1, "url")),
        (("verify_ssl", True), (2, "verify_ssl")),
        (("extra_key", None), (3, "extra_key")),
        (("another_key", None), (3, "another_key")),
        ((None, None), (4, None)),
    ],
)
def test_pipfile_source_key(pair, expected):
    res = cli.pipfile_source_key(pair)
    assert res == expected


@pytest.mark.parametrize(
    ("pair", "expected"),
    [
        (("source", {}), (0, "source", "source")),
        (("SOURCE", {}), (0, "source", "SOURCE")),
        (("packages", {}), (1, "packages", "packages")),
        (("PACKAGES", {}), (1, "packages", "PACKAGES")),
        (("dev-packages", {}), (2, "dev-packages", "dev-packages")),
        (("dev_packages", {}), (2, "dev-packages", "dev_packages")),
        (("DEV-PACKAGES", {}), (2, "dev-packages", "DEV-PACKAGES")),
        (("requires", {}), (3, "requires", "requires")),
        (("REQUIRES", {}), (3, "requires", "REQUIRES")),
        (("scripts", {}), (4, "scripts", "scripts")),
        (("SCRIPTS", {}), (4, "scripts", "SCRIPTS")),
        (("another_key", {}), (5, "another-key", "another_key")),
        (("ANOTHER KEY", {}), (5, "another key", "ANOTHER KEY")),
        ((None, {}), (6, None, None)),
    ],
)
def test_pipfile_section_key(pair, expected):
    res = cli.pipfile_section_key(pair)
    assert res == expected


def pypi_packages():
    """Return a tuple (Package Name, Package ID) from PyPI simple index."""
    tree = None
    tries = 0
    while tree is None:
        try:
            res = requests.get("https://pypi.org/simple/")
            res.raise_for_status()
        except requests.HTTPError:
            if tries > 5:
                raise

            import time

            time.sleep(1 * tries)
            tries += 1
        else:
            tree = html.fromstring(res.content)

    for anchor in tree.xpath("/html/body/a"):
        name = anchor.text
        href = anchor.get("href")
        segments = href.split("/")
        assert len(segments) == 4
        assert segments[0] == segments[3] == ""
        assert segments[1] == "simple"
        pkgid = segments[2]

        yield (name, pkgid)


@pytest.mark.parametrize(("package_name", "package_id"), pypi_packages())
def test_pipfile_packages_key(package_name, package_id):
    result = cli.pipfile_packages_key((package_name, {}))
    assert result == (False, package_id)
    result = cli.pipfile_packages_key((None, {}))
    assert result == (True, None)
