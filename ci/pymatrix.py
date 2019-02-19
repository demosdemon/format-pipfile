#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import pprint

import click
import path
import yaml

ROOT = path.Path(__file__).dirname().dirname()
DEFAULT_MATRIX = ROOT / "matrix.yml"


@click.command()
@click.option(
    "-m",
    "--matrix-file",
    default=DEFAULT_MATRIX.relpath(),
    help="The matrix yaml file.",
)
def main(matrix_file):
    with open(matrix_file) as fp:
        text = fp.read()

    data = yaml.compose(text)
    pprint.pprint(data)


if __name__ == "__main__":
    main()
