# -*- coding: utf-8 -*-
from __future__ import absolute_import

import pytest
from format_pipfile import cli
from tomlkit.items import Key


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
