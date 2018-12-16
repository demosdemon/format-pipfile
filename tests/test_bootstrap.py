# -*- coding: utf-8 -*-
"""
Test the ``bootstrap.py`` script in CI. Bail CI if if there are updates.
"""

from __future__ import absolute_import

import os

import path

ROOT = path.Path(__file__).dirname().dirname()


def test_bootstrap(delegator):
    with ROOT:
        status = delegator("git status --porcelain")
        assert status == "", "git tree is dirty!"
        response = delegator("python ci/bootstrap.py").splitlines()
        assert response[0].strip() == "Project path:"
        assert response[-1].strip() == "DONE."
        status = delegator("git status --porcelain").splitlines()
        dirty_files = {f[3:] for f in status}
        dirty = len(dirty_files) > 0
        for line in response[1:-1]:
            assert line.startswith("Wrote ")
            name = line.split(" ", 1)[1]
            if name in dirty_files:
                dirty_files.remove(name)
        if dirty_files:
            raise AssertionError(
                "Wrote file but did not print file name. {}".format(
                    ", ".join(dirty_files)
                )
            )
        if dirty and "CI" in os.environ:
            raise AssertionError("Wrote file in CI environment!")
