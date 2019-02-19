# -*- coding: utf-8 -*-
from __future__ import absolute_import

from typing import Any, Dict, List, MutableMapping

from attr import attrib, attrs
from pymatrix.exceptions import StackEmptyError


def distinct(iterable):
    seen = set()
    for item in iterable:
        if item in seen:
            continue
        seen.add(item)
        yield item


@attrs(slots=True, frozen=True, hash=False)
class Namespace(MutableMapping):
    """A scoped object for tracking name resolution."""

    #: The namespace stack. Mappings are appended as new scoped are added.
    _stack = attrib(type=List[Dict[str, Any]], factory=list, init=False)

    def __attrs_post_init__(self):
        self.push_stack()

    def __enter__(self):
        self.push_stack()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        assert self._stack
        # should not raise
        self.pop_stack()
        if exc_type:
            self["exc_info"] = (exc_type, exc_val, exc_tb)

    def push_stack(*args, **kwargs):
        if not args:
            raise TypeError("Missing required self.")
        self, args = args[0], args[1:]
        if args and len(args) > 1:
            raise TypeError("Expected at most one argument.")
        if args and kwargs:
            raise TypeError(
                "Expected either a positional argument or keyword arguments, not both."
            )
        source = dict(args[0] if args else kwargs)
        self._stack.append(source)

    def pop_stack(self):
        try:
            return self._stack.pop()
        except IndexError:
            raise StackEmptyError

    @property
    def _levels(self):
        return self._stack[::-1]

    def __len__(self):
        return len({key for level in self._levels for key in level})

    def __iter__(self):
        return distinct(key for level in self._levels for key in level)

    def __getitem__(self, key):
        for level in self._levels:
            try:
                return level[key]
            except KeyError:
                pass
        raise KeyError(key)

    def __setitem__(self, key, value):
        try:
            self._levels[0][key] = value
        except IndexError:
            raise StackEmptyError

    def __delitem__(self, key):
        for level in self._levels:
            try:
                del level[key]
            except KeyError:
                pass
            else:
                return
        else:
            raise KeyError(key)
