# -*- coding: utf-8 -*-
"""
Generate a matrix based on a generative syntax.

    <expression>
        : <merge>
        | <for_loop>
        | <mapping>
        | <bool>
        | <?mako>
        | <scalar>
        | <matrix>

    <merge>:
        $merge: <expression>

    $secure:
        <identifier>:
            $ci:
                <identifier>: <scalar>
    $variables:
        <identifier>: <scalar>
    $matrix:
        <identifier>: <expression>
    $ci:
        $matrix:
            <identifier>: <expression>
        <identifier>: <expression>
    $environments:
        # implicit loop construct over $matrix • $ci
        [$*]: <expression>
        <identifier>: <expression>

    <expression>:
        <merge> | <for_loop> | <mapping> | <bool> | <?mako> | <scalar>
        ? = within loop construct

    <identifier>:
        `str.isidentifier` | <?mako>
        ? = within loop construct

    <merge>:
        $merge: [ <expression>, ... ]

    <for_loop>:
        $for: <identifier>
        $in: <python>
        $yield: <expression>  # push loop construct

    <mapping>:
        <identifier>: <expression>
        [$ci]:
            <identifier>: <scalar>

    <bool>:
        $if: <python>
        $then: <merge> | <mapping> | <bool> | <?template> | <?mako> | <scalar>
        [$else]: <merge> | <mapping> | <bool> | <?template> | <?mako> | <scalar>

    <mako>:
        $mako: <template_string>

"""


from __future__ import absolute_import

from itertools import repeat
from typing import Any, Tuple

from attr import attrib, attrs
from inflection import underscore


@attrs(slots=True, frozen=True)
class Node(object):
    """A node within our tree."""

    @property
    def type(self):  # type: () -> str
        return underscore(self.__class__.__name__)

    @property
    def children(self):  # type: () -> List[Node]
        return []

    def accept_visitor(self, visitor):
        def traverse(node):
            # type: (Node) -> None
            for n in node.children:  # type: Node
                if n:
                    n.accept_visitor(visitor)

        method = getattr(visitor, "visit_" + self.type, traverse)
        method(self)

    @staticmethod
    def make_node(value):  # type: (Any) -> Node
        if value is None:
            return None

        if isinstance(value, Node):
            return value


@attrs(slots=True, frozen=True)
class ScalarNode(Node):
    """
    A simple scalar value.

    The value itself may not be simple; however, it is not a ``Node``.
    """

    value = attrib(type=Any)


@attrs(slots=True, frozen=True)
class SequenceNode(Node):
    nodes = attrib(type=Tuple[Node, ...], converter=tuple)

    @property
    def children(self):
        return list(self.nodes)

    def __add__(self, other):
        other = Node.make_node(other)
        if isinstance(other, SequenceNode):
            return self.extend(other)
        else:
            return self.append(other)

    def __contains__(self, value):
        value = Node.make_node(value)
        return value in self.nodes

    def __getitem__(self, item):
        value = self.nodes[item]
        if isinstance(item, slice):
            return self.__class__(value)
        return value

    def __iter__(self):
        return iter(self.nodes)

    def __mul__(self, value):
        return self.__class__(repeat(self, value))

    def __rmul__(self, value):
        return self * value

    def __len__(self):
        return len(self.nodes)

    def __reversed__(self):
        return reversed(self.nodes)

    def append(self, value):
        nodes = self.nodes + (value,)
        return self.__class__(nodes)

    def count(self, value):
        return self.nodes.count(value)

    def extend(self, iterable):
        nodes = self.nodes + tuple(iterable)
        return self.__class__(nodes)

    def index(self, value, start=0, stop=None):
        return self.nodes.index(value, start, stop)

    def insert(self, index, value):
        if index == 0:
            nodes = (value,) + self.nodes
        else:
            nodes = self.nodes[0 : index - 1] + (value,) + self.nodes[index:]

        return self.__class__(nodes)


@attrs(slots=True, frozen=True)
class KeyValueNode(Node):
    key = attrib(type=Node, converter=Node.make_node)
    value = attrib(type=Node, converter=Node.make_node)

    @property
    def children(self):
        return [self.key, self.value]


@attrs(slots=True, frozen=True)
class MappingNode(SequenceNode):
    __mul__ = None
    __rmul__ = None

    def __contains__(self, item):
        try:
            self[item]
        except KeyError:
            return False
        else:
            return True

    def __getitem__(self, item):
        if isinstance(item, (int, slice)):
            return super(MappingNode, self).__getitem__(item)
        item = Node.make_node(item)
        for key, value in self.items():
            if key == item:
                return value

        raise KeyError(item)

    def __iter__(self):
        return iter(self.keys())

    def keys(self):
        return [kvp.key for kvp in self.nodes]

    def values(self):
        return [kvp.value for kvp in self.nodes]

    def items(self):
        return [(kvp.key, kvp.value) for kvp in self.nodes]


@attrs(slots=True, frozen=True)
class RootNode(Node):
    """
    The root node. It is implicitly also a MappingNode; however, it may not be the
    descendent of any other node.

    The RootNode consists of any the following nodes::

        $secure:
            <identifier>:
                $ci:
                    <identifier>: <scalar>
        $variables:
            <identifier>: <scalar>
        $matrix:
            <identifier>: <MatrixNode>
        $ci:
            <identifier>: <CINode>
        $environments:
            [$*]: <EnvironmentNode>
            <identifier>: <EnvironmentNode>
    """


@attrs(slots=True, frozen=True)
class MatrixNode(Node):
    """
    A Matrix node. Matrix node are combined into a matrix of job structures. The
    definition of a Matrix node consists of:

         $merge: [ <MergeNode>, ... ]

    or

        <identifier>: <scalar> |
    """
