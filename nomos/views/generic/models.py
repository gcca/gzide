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

import re
from pathlib import Path
from typing import (
    Any,
    Dict,
    Iterator,
    List,
    NamedTuple,
    Optional,
    Tuple,
    Type,
    TypedDict,
    Union,
    cast,
)

from django.conf import settings
from django.db.models import Model
from django.http import HttpRequest
from django.template.base import Template
from django.template.context import make_context
from django.template.engine import Engine
from django.template.exceptions import TemplateDoesNotExist
from django.template.response import TemplateResponse
from django.urls import reverse, reverse_lazy
from django.utils.functional import Promise
from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView

__all__ = ["modelviews_factory", "Patterns"]


class ModelViews(NamedTuple):
    mainview: Type[TemplateView]
    listview: Type[ListView]
    detailview: Type[DetailView]
    createview: Type[CreateView]
    updateview: Type[UpdateView]
    pk_url_kwarg: str


class Patterns:
    def __init__(
        self,
        mainname: str,
        listname: str,
        detailname: str,
        createname: str,
        updatename: str,
    ):
        self.mainname = mainname
        self.listname = listname
        self.detailname = detailname
        self.createname = createname
        self.updatename = updatename

    @property
    def mainurl(self) -> str:
        return reverse(self.mainname)

    @property
    def listurllazy(self) -> Promise:
        return reverse_lazy(self.listname)

    @property
    def listurl(self) -> str:
        return reverse(self.listname)

    @property
    def createurl(self) -> str:
        return reverse(self.createname)


def modelviews_factory(
    model: Type[Model],
    patterns: Patterns,
    bases: Optional[Tuple[Type, ...]] = None,
) -> ModelViews:
    viewname = model._meta.object_name
    sname = SN.sub("_", viewname).lower()
    pk_url_kwarg = f"{sname}_id"
    if bases is None:
        bases = ()
    return ModelViews(
        _TypeView(
            f"{viewname}View",
            (*bases, TemplateResponseModelMixin, TemplateView),
            {
                "template_name": "main.html",
                "patterns": patterns,
            },
        ),
        _TypeView(
            f"{viewname}ListView",
            (*bases, TemplateResponseModelMixin, ListView),
            {
                "template_name": "list.html",
                "model": model,
                "patterns": patterns,
            },
        ),
        _TypeView(
            f"{viewname}DetailView",
            (*bases, TemplateResponseModelMixin, DetailModelView),
            {
                "template_name": "detail.html",
                "model": model,
                "pk_url_kwarg": pk_url_kwarg,
                "patterns": patterns,
            },
        ),
        _TypeView(
            f"{viewname}CreateView",
            (*bases, TemplateResponseModelMixin, CreateView),
            {
                "template_name": "form.html",
                "model": model,
                "fields": "__all__",
                "success_url": patterns.listurllazy,
                "patterns": patterns,
            },
        ),
        _TypeView(
            f"{viewname}UpdateView",
            (*bases, TemplateResponseModelMixin, UpdateView),
            {
                "template_name": "form.html",
                "model": model,
                "fields": "__all__",
                "success_url": patterns.listurllazy,
                "pk_url_kwarg": pk_url_kwarg,
                "patterns": patterns,
            },
        ),
        pk_url_kwarg,
    )


class ModelTemplate:
    def __init__(self, template: Template):
        self.template = template

    def render(
        self,
        context: Optional[Dict[str, Any]] = None,
        request: Optional[HttpRequest] = None,
    ) -> str:
        context = make_context(context, request)
        return self.template.render(context)


class ModelTemplateResponse(TemplateResponse):
    def resolve_template(self, template: Iterator[str]) -> ModelTemplate:
        chain = []
        for name in template:
            try:
                return ModelTemplate(ModelEngine.get_template(name))
            except TemplateDoesNotExist as error:
                chain.append(error)
        raise TemplateDoesNotExist(", ".join(template), chain=chain)


ModelEngine = Engine(
    debug=settings.DEBUG, dirs=[Path(__file__).parent / "templates" / "models"]
)


class TemplateResponseModelMixin:
    template_engine = ModelEngine
    response_class = ModelTemplateResponse


class DetailModelView(DetailView):
    @property
    def fieldvalues(self) -> Iterator[Tuple[str, Union[int, float, str]]]:
        names = (field.name for field in self.object._meta.concrete_fields)
        values = self.object.__dict__
        return ((name, values[name]) for name in names)


class _AttrsDict(TypedDict, total=False):
    template_name: str
    model: Optional[Type[Model]]
    success_url: Optional[str]
    fields: Optional[Union[str, List[str]]]
    pk_url_kwarg: Optional[str]
    patterns: Patterns


def _TypeView(
    name: str, bases: Tuple[Union[Type[View], Type], ...], attrs: _AttrsDict
) -> Type[View]:
    return type(name, bases, cast(dict, attrs))


SN = re.compile(r"(?<!^)(?=[A-Z])")
