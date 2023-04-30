# Copyright © 2023, Nomos-Team. All Rights Reserved.
#
# This file is part of Nomos.
#
# Nomos is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# Nomos is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with Nomos. If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations

import functools
import sys
from inspect import getfullargspec, unwrap
from typing import Callable, Generic, Tuple, TypeVar

from django.template import Library as LibraryBase
from django.template import Node
from django.template.base import NodeList, Parser, Token
from django.template.context import RequestContext
from django.template.library import parse_bits

if sys.version_info >= (3, 10):
    from typing import ParamSpec
else:
    from typing_extensions import ParamSpec

__all__ = ["Library"]

T = TypeVar("T")
P = ParamSpec("P")


class Library(LibraryBase):
    def inlinetag(self, call: Callable[P, str]):
        @functools.wraps(call)
        def compile_function(parser: Parser, token: Token):
            args, kwargs = self.__CallArguments(parser, token, call)
            return InlineNode(call, args, kwargs)

        self.tag(call.__name__, compile_function)
        return call

    def relinetag(self, call: Callable[P, str]):
        @functools.wraps(call)
        def compile_function(parser: Parser, token: Token):
            args, kwargs = self.__CallArguments(parser, token, call)
            return RelineNode(call, args, kwargs)

        self.tag(call.__name__, compile_function)
        return call

    def bigentag(self, call: Callable[P, Tuple[str, str]]):
        @functools.wraps(call)
        def compile_function(parser: Parser, token: Token):
            nodelist = parser.parse((f"end_{call.__name__}",))
            parser.delete_first_token()
            args, kwargs = self.__CallArguments(parser, token, call)
            return BigenNode(call, args, kwargs, nodelist)

        self.tag(call.__name__, compile_function)
        return call

    @staticmethod
    def __CallArguments(
        parser: Parser, token: Token, call: Callable[P, T]
    ) -> Tuple[P.args, P.kwargs]:
        argspec = getfullargspec(unwrap(call))[:-1]
        bits = token.split_contents()[1:]
        args, kwargs = parse_bits(
            parser,
            bits,
            *argspec,
            False,
            call.__name__,
        )
        return args, kwargs


class ArgspecNodeBase(Node, Generic[T]):
    def __init__(self, call: Callable[P, T], args: P.args, kwargs: P.kwargs):
        self.call = call
        self.args = args
        self.kwargs = kwargs
        super().__init__()

    def _Call(self, context: RequestContext) -> T:
        args, kwargs = self.__ResolveArguments(context)
        return self.call(*args, **kwargs)

    def __ResolveArguments(
        self, context: RequestContext
    ) -> Tuple[P.args, P.kwargs]:
        args = [arg.resolve(context) for arg in self.args]
        kwargs = {k: v.resolve(context) for k, v in self.kwargs.items()}
        return args, kwargs


class InlineNode(ArgspecNodeBase):
    def render(self, context: RequestContext):
        return self._Call(context)


class RelineNode(InlineNode):
    def render(self, context: RequestContext):
        return context.template.engine.from_string(
            super().render(context)
        ).render(context)


class BigenNode(ArgspecNodeBase):
    def __init__(
        self,
        call: Callable[P, Tuple[str, str]],
        args: P.args,
        kwargs: P.kwargs,
        nodelist: NodeList,
    ):
        super().__init__(call, args, kwargs)
        self.nodelist = nodelist

    def render(self, context: RequestContext):
        begin, end = self._Call(context)
        body = self.nodelist.render(context)
        return f"{begin}{body}{end}"
