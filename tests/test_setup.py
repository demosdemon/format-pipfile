# -*- coding: utf-8 -*-

from __future__ import absolute_import

import itertools
import operator
import textwrap

import packaging.version
import path
import pytest
from six.moves import map

PARDIR = path.Path(__file__).dirname().dirname()

try:
    _accumulate = itertools.accumulate
except AttributeError:

    def _accumulate(iterable, func=operator.add):
        it = iter(iterable)
        try:
            total = next(it)
        except StopIteration:
            return
        yield total
        for element in it:
            total = func(total, element)
            yield total


def last(iterable, default=None):
    it = iter(iterable)
    _last = next(it, default)
    while True:
        try:
            _last = next(it)
        except StopIteration:
            return _last


def accumulate(changelog):
    tags = list(map(operator.itemgetter(1), changelog))
    return last(_accumulate(tags, set.__or__))


@pytest.fixture()
def current_pbr_version(git_command):
    res = git_command("log --decorate=full --format=%h%x00%s%x00%d").splitlines()
    changelog = []
    for line in res:
        parts = line.split("\x00")
        if len(parts) != 3:
            continue

        sha, msg, refname = parts
        tags = set()

        # refname can be:
        #  <empty>
        #  HEAD, tag: refs/tags/1.4.0, refs/remotes/origin/master, \
        #    refs/heads/master
        #  refs/tags/1.3.4
        if "refs/tags/" in refname:
            refname = refname.strip()[1:-1]  # remove wrapping ()'s
            # If we start with "tag: refs/tags/1.2b1, tag: refs/tags/1.2"
            # The first split gives us "['', '1.2b1, tag:', '1.2']"
            # Which is why we do the second split below on the comma
            for tag_string in refname.split("refs/tags/")[1:]:
                # git tag does not allow : or " " in tag names, so we split
                # on ", " which is the separator between elements
                candidate = tag_string.split(", ")[0]
                tags.add(candidate)

        changelog.append((sha, tags, msg))

    tags = accumulate(changelog)
    current = max(tags, key=packaging.version.parse)
    count = itertools.count()
    for sha, tags, msg in changelog:
        step = next(count)
        if current in tags:
            break
    else:
        step = len(changelog)

    v = packaging.version.parse(current)
    if step != 0:
        major, minor, patch = v.release
        patch += 1
        # noinspection PyProtectedMember
        v._version = v._version._replace(
            dev=("post", step), release=(major, minor, patch)
        )

    return str(v)


@pytest.mark.parametrize(
    ("parameter", "expected"),
    [
        ("--name", "format-pipfile"),
        ("--author", "Brandon LeBlanc"),
        ("--author-email", "projects+format-pipfile@leblanc.codes"),
        ("--maintainer", "UNKNOWN"),
        ("--maintainer-email", "UNKNOWN"),
        ("--contact", "Brandon LeBlanc"),
        ("--contact-email", "projects+format-pipfile@leblanc.codes"),
        ("--url", "https://github.com/demosdemon/format-pipfile"),
        ("--license", "MIT"),
        (
            "--description",
            "A Python utility to format TOML Pipfiles with some very opinionated rules.",
        ),
        (
            "--long-description",
            "A Python utility to format TOML Pipfiles with some very opinionated rules.",
        ),
        ("--platforms", "UNKNOWN"),
        (
            "--classifiers",
            """
            Development Status :: 4 - Beta
            Intended Audience :: Developers
            License :: OSI Approved :: MIT License
            Natural Language :: English
            Operating System :: OS Independent
            Programming Language :: Python :: 2
            Programming Language :: Python :: 2.7
            Programming Language :: Python :: 3
            Programming Language :: Python :: 3.4
            Programming Language :: Python :: 3.5
            Programming Language :: Python :: 3.6
            Programming Language :: Python :: 3.7
            Programming Language :: Python :: Implementation :: CPython
            Programming Language :: Python :: Implementation :: PyPy
            Topic :: Software Development
            """,
        ),
        ("--provides", ""),
        ("--keywords", ""),
        ("--requires", ""),
        ("--obsoletes", ""),
    ],
)
def test_metadata(delegator, parameter, expected):
    with PARDIR:
        cmd = "python setup.py {}".format(parameter)
        res = delegator(cmd)

    if "\n" in expected:
        expected = textwrap.dedent(expected).strip()

    assert res == expected


def test_metadata_version(delegator, current_pbr_version):
    with PARDIR:
        cmd = "python setup.py --version"
        res = delegator(cmd)

    assert res == current_pbr_version

    with PARDIR:
        cmd = "python setup.py --fullname"
        res = delegator(cmd)

    assert res == "format-pipfile-{}".format(current_pbr_version)
