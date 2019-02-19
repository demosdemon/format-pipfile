# -*- coding: utf-8 -*-
from __future__ import absolute_import

import re


def attr_name(inst, attr):
    return "{}.{}".format(type(inst).__name__, attr.name)


def validate_nonempty(inst, attr, value):
    try:
        _len = len(value)
    except TypeError:
        raise TypeError("{}: does not have a len()".format(attr_name(inst, attr)))

    if _len > 0:
        return

    raise TypeError(
        "{}: len() must be greater than 0, got {}".format(attr_name(inst, attr), _len)
    )


def validate_is_identifier(inst, attr, value):
    try:
        valid = str.isidentifier(value)
    except AttributeError:
        valid = re.match(r"^(?!\d)\w*$", value)

    if valid:
        return

    raise TypeError(
        "{}: expected a valid identifier string, got: {!r}".format(
            attr_name(inst, attr), value
        )
    )
