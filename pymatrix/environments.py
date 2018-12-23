# -*- coding: utf-8 -*-
from __future__ import absolute_import

from typing import Dict, List, Mapping, Optional, Union

import attr
from attr.validators import instance_of
from pymatrix.validators import all_, is_
from requirementslib.models.requirements import Requirement

Env = Dict[str, str]


def is_setenv(value):
    if isinstance(value, list):
        return all(isinstance(v, str) for v in value)
    if isinstance(value, Mapping):
        return all(isinstance(k, str) and isinstance(v, str) for k, v in value.items())
    return False


@attr.s()
class Environment(object):
    #: The NAME used in ``[testenv:NAME]``
    name = attr.ib(type=str)
    #: The parent test env to inherit settings from
    parent = attr.ib(default="default", type=str)
    #: Whether or not the environment is exposed in {[tox]envlist}
    expose = attr.ib(default=False, type=bool)
    #: Control whether or not to emit this environment
    emit = attr.ib(default=True, type=bool)
    #: Override the base python
    basepython = attr.ib(default=None, type=Optional[str])
    #: The commands to be called for testing. Only executed if ``commands_pre`` succeed.
    commands = attr.ib(factory=list, type=List[str])
    #: The commands to run before running the ``commands``.
    commands_pre = attr.ib(factory=list, type=List[str])
    #: The commands to run after running ``commands``.
    commands_post = attr.ib(factory=list, type=List[str])
    #: Override the default install command
    install_command = attr.ib(default=None, type=Optional[str])
    #: Override the list dependencies command
    list_dependencies_command = attr.ib(default=None, type=Optional[str])
    #: Override the default ignore errors option
    ignore_errors = attr.ib(default=None, type=Optional[bool])
    #: Install the latest pre-release versions
    pip_pre = attr.ib(default=False, type=bool)
    #: list of commands outside of the virtual env
    whitelist_externals = attr.ib(factory=list, type=List[str])
    #: Override the working directory
    changedir = attr.ib(default=None, type=Optional[str])
    #: list of pip dependencies
    deps = attr.ib(
        factory=list, type=List[Requirement], validator=all_(instance_of(Requirement))
    )
    #: ``sys.platform`` matching regex
    platform = attr.ib(default=None, type=Optional[str])
    #: set KEY=VALUE environment variables for all invocations
    setenv = attr.ib(factory=list, type=Union[List[str], Env], validator=is_(is_setenv))
    #: list of environment variable globs to pass through to invocations
    passenv = attr.ib(factory=list, type=List[str])
    #: always recreate environment
    recreate = attr.ib(default=None, type=Optional[bool])
    #: set to true to create virtual environments with access to global packages
    sitepackages = attr.ib(default=None, type=Optional[bool])
    #: always copy files instead of symlinking
    alwayscopy = attr.ib(default=None, type=Optional[bool])
    #: treat positional arguments passed to tox as paths and rewrite them according to
    #: ``changedir``
    args_are_paths = attr.ib(default=None, type=Optional[bool])
    #: define a temporary directory for the virtual env that will be cleared before
    #: each group of commands
    envtmpdir = attr.ib(default=None, type=Optional[str])
    #: define a directory for logging
    envlogdir = attr.ib(default=None, type=Optional[str])
    #: override the default environment dir
    envdir = attr.ib(default=None, type=Optional[str])
    #: install the package in develop mode instead of from the sdist package
    usedevelop = attr.ib(default=None, type=Optional[bool])
    #: do not install the current package
    skip_install = attr.ib(default=None, type=Optional[bool])
    #: ignore failing outcomes
    ignore_outcome = attr.ib(default=None, type=Optional[bool])
    #: A list of package extras to include
    extras = attr.ib(factory=list, type=List[str])
    #: A short description of the environment.
    description = attr.ib(default=None, type=Optional[str])

    #: whether or not to inherit the commands
    inherit_commands = attr.ib(type=bool)
    #: whether or not to inherit the commands_pre
    inherit_commands_pre = attr.ib(type=bool)
    #: whether or not to inherit the commands_post
    inherit_commands_post = attr.ib(type=bool)
    #: whether or not to inherit the whitelisted externals
    inherit_whitelist_externals = attr.ib(type=bool)
    #: whether or not to inherit the dependencies
    inherit_deps = attr.ib(type=bool)
    #: whether or not to inherit the setenv
    inherit_setenv = attr.ib(type=bool)
    #: whether or not to inherit the passenv
    inherit_passenv = attr.ib(type=bool)
    #: whether or not to inherit the extras
    inherit_extras = attr.ib(type=bool)

    @inherit_commands.default
    @inherit_commands_pre.default
    @inherit_commands_post.default
    @inherit_whitelist_externals.default
    @inherit_deps.default
    @inherit_setenv.default
    @inherit_passenv.default
    @inherit_extras.default
    def __default_inherit(self):
        if self.parent is None:
            return False
        return self.basepython is None


@attr.s()
class Entry(object):
    alias = attr.ib(type=str, validator=is_(str.isidentifier))
    environment = attr.ib(type=Environment, validator=instance_of(Environment))
