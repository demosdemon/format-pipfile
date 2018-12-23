# -*- coding: utf-8 -*-
from __future__ import absolute_import

import attr


@attr.s(str=True, frozen=True, slots=True)
class InvalidOperationException(Exception):
    operation = attr.ib(type=str)


class StackEmptyError(Exception):
    pass
