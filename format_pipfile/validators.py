# -*- coding: utf-8 -*-
"""
``attrs`` validators
"""

from __future__ import absolute_import

from typing import Any, Callable

import attr

Predicate = Callable[[Any], bool]


@attr.s(slots=True, frozen=True)
class PredicateValidator(object):
    predicate = attr.ib(validator=attr.validators.instance_of(Callable), type=Predicate)

    def __call__(self, inst, attribute, value):
        if self.predicate(value):
            return
        raise TypeError(
            "'{name}' failed the predicate test (got {value!r}".format(
                name=attribute.name, value=value
            ),
            attribute,
            self,
            value,
        )


def is_(predicate):
    return PredicateValidator(predicate)
