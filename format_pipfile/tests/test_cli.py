# -*- coding: utf-8 -*-
from format_pipfile.cli import main


def test_cli_help(cli_runner):
    result = cli_runner.invoke(main, ["--help"], prog_name="format-pipfile")

    assert result.exit_code == 0
    assert "Usage: format-pipfile [OPTIONS]" in result.output
    assert "Update the requirements.txt file and reformat the Pipfile." in result.output
    assert "-r, --requirements-file FILE" in result.output
    assert "--skip-requirements-file" in result.output
    assert "-p, --pipfile FILE" in result.output
    assert "--skip-pipfile" in result.output
    assert "--help" in result.output
