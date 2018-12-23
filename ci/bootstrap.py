#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

import os

import jinja2
import matrix
import path


def load_matrix(base_path):
    environments = {}
    items = list(matrix.from_file(base_path / "setup.cfg").items())
    items.insert(0, ("check", {"coverage_flag": "False"}))
    for alias, conf in items:
        environments[alias] = conf.copy()
        pyenv = conf.pop("python_version", "py37")
        windows = not pyenv.startswith("pypy")
        python = pyenv if pyenv.startswith("pypy") else "{0[2]}.{0[3]}".format(pyenv)
        cover = conf.pop("coverage_flag", "true").lower()
        deps = conf.pop("dependencies", "").split()
        env_vars = {k.upper(): v for k, v in list(conf.items())}
        environments[alias].update(
            windows=windows,
            python=python,
            cover=cover == "true",
            deps=deps,
            env_vars=env_vars,
            pyenv=pyenv,
        )

    return environments


def main():
    base_path = path.Path(__file__).dirname().dirname()
    print(("Project path: {}".format(base_path)))

    template_path = base_path / "ci" / "templates"
    jinja = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_path),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=False,
        extensions=("jinja2.ext.do",),
    )

    environments = load_matrix(base_path)
    for name in template_path.listdir():
        name = os.path.split(name)[1]
        root = os.path.splitext(name)[0]
        tpl = jinja.get_template(name)
        contents = tpl.render(environments=environments).strip()
        with open(base_path / root, "w") as fp:
            fp.write(contents + "\n")

        print("Wrote {}".format(root))

    print("DONE.")


if __name__ == "__main__":
    main()
