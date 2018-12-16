# -*- coding: utf-8 -*-
"""Root module for the ``tests`` package."""

from __future__ import absolute_import

import requests
from lxml import html

__all__ = ["pypi_packages"]


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
