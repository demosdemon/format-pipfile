# -*- coding: utf-8 -*-

from __future__ import absolute_import

import os
import sys

import pytest

try:
    from shlex import quote
except ImportError:
    from pipes import quote  # noqa


@pytest.fixture()
def delegator():
    """Execute a command and return its value."""
    import delegator

    def run(command):
        if "|" in command:
            res = delegator.chain(command)
        else:
            res = delegator.run(command)
        if res.return_code == 127:
            raise FileNotFoundError(res.err)
        if res.return_code != 0:
            raise RuntimeError(res.err)
        if res.err:
            sys.stderr.write(res.err)
            if not res.err.endswith(os.linesep):
                sys.stderr.write(os.linesep)

        return res.out.strip()

    return run


@pytest.fixture()
def git_command(delegator, git_directory):
    """A delegator to ``git`` setting the appropriate ``--git-dir``."""

    def run(cmd, **kwargs):
        cmd = "git --git-dir={} {}".format(quote(git_directory), cmd)
        return delegator(cmd, **kwargs)

    return run


@pytest.fixture()
def git_directory(delegator):
    """The ``.git`` directory for the current project."""
    return delegator("git rev-parse --git-dir")
