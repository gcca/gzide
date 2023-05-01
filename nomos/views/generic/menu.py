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

from pathlib import Path
from typing import (
    Any,
    Dict,
    List,
    NamedTuple,
    Optional,
    Tuple,
    Type,
    TypedDict,
    Union,
    cast,
)

from django import urls
from django.db.models import Model
from django.forms import ModelForm
from django.views.generic.base import ContextMixin, View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView

__all__ = ["menuviews_factory", "MenuViews", "ViewTraits", "MenuTraits"]


class MenuViews(NamedTuple):
    list: Type[ListView[Model]]
    create: Type[CreateView[Model, ModelForm[Model]]]
    detail: Type[DetailView[Model]]
    update: Type[UpdateView[Model, ModelForm[Model]]]
    delete: Type[DeleteView[Model, ModelForm[Model]]]


class MenuAfterPatterns(NamedTuple):
    create: str
    update: str


class ViewTraits(NamedTuple):
    bases: Tuple[Type[object], ...] = ()


class MenuTraits(NamedTuple):
    list: ViewTraits = ViewTraits()
    create: ViewTraits = ViewTraits()
    detail: ViewTraits = ViewTraits()
    update: ViewTraits = ViewTraits()
    delete: ViewTraits = ViewTraits()


def menuviews_factory(
    model: Type[Model],
    template_basedir: str,
    patterns_prefix: str,
    menu_traits: MenuTraits,
) -> MenuViews:
    after_patterns = MenuAfterPatterns(
        f"{patterns_prefix}:list",
        f"{patterns_prefix}:detail",
    )
    factory = __MenuFactory(
        template_basedir, model, after_patterns, menu_traits
    )
    return MenuViews(
        factory.MakeListView(),
        factory.MakeCreateView(),
        factory.MakeDetailView(),
        factory.MakeUpdateView(),
        factory.MakeDeleteView(),
    )


class _AttrsDict(TypedDict, total=False):
    template_name: str
    model: Optional[Type[Model]]
    success_url: Optional[str]
    success_pattern: Optional[str]
    fields: Optional[Union[str, List[str]]]
    pk_url_kwarg: Optional[str]


class MenuMixin(ContextMixin, View):
    def get_context_data(self, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        if self.request.resolver_match is None:
            raise ValueError("request.resolver_match is None")

        name = self.request.resolver_match.app_name
        context["menu"] = {
            "list_name": f"{name}:list",
            "create_name": f"{name}:create",
            "detail_name": f"{name}:detail",
            "update_name": f"{name}:update",
            "delete_name": f"{name}:delete",
        }

        return context


class __MenuFactory:
    def __init__(
        self,
        template_basedir: str,
        model: Type[Model],
        after_patterns: MenuAfterPatterns,
        menu_traits: MenuTraits,
    ):
        if model._meta.object_name is None:
            raise ValueError("Unsupported model _meta with none object_name")

        self.template_basedir = Path(template_basedir)
        self.model = model
        self.model_name = model._meta.object_name
        self.pk_url_name = f"{self.model_name.lower()}_id"
        self.after_patterns = after_patterns
        self.menu_traits = menu_traits

    def MakeListView(self) -> Type[ListView[Model]]:
        return self.__TypeView(
            self.__NameView("List"),
            (
                *self.menu_traits.list.bases,
                MenuMixin,
                ListView,
            ),
            {
                "template_name": self.__NameTemplate("list"),
                "model": self.model,
            },
        )

    def MakeCreateView(self) -> Type[CreateView[Model, ModelForm[Model]]]:
        return self.__TypeView(
            self.__NameView("Create"),
            (
                *self.menu_traits.create.bases,
                MenuMixin,
                CreateView,
            ),
            {
                "template_name": self.__NameTemplate("create"),
                "model": self.model,
                "fields": "__all__",
                "success_url": urls.reverse_lazy(self.after_patterns.create),
            },
        )

    def MakeDetailView(self) -> Type[DetailView[Model]]:
        return self.__TypeView(
            self.__NameView("Detail"),
            (
                *self.menu_traits.detail.bases,
                MenuMixin,
                DetailView,
            ),
            {
                "template_name": self.__NameTemplate("detail"),
                "model": self.model,
                "pk_url_kwarg": self.pk_url_name,
            },
        )

    def MakeUpdateView(self) -> Type[UpdateView[Model, ModelForm[Model]]]:
        return self.__TypeView(
            self.__NameView("Update"),
            (
                *self.menu_traits.update.bases,
                MenuMixin,
                _UpdateView,
            ),
            {
                "template_name": self.__NameTemplate("update"),
                "model": self.model,
                "fields": "__all__",
                "success_pattern": self.after_patterns.update,
                "pk_url_kwarg": self.pk_url_name,
            },
        )

    def MakeDeleteView(self) -> Type[DeleteView[Model, ModelForm[Model]]]:
        return self.__TypeView(
            self.__NameView("Delete"),
            (
                *self.menu_traits.delete.bases,
                MenuMixin,
                DeleteView,
            ),
            {
                "template_name": self.__NameTemplate("delete"),
                "model": self.model,
                "success_url": urls.reverse_lazy(self.after_patterns.create),
                "pk_url_kwarg": self.pk_url_name,
            },
        )

    def __NameView(self, viewname: str) -> str:
        return f"{self.model_name}{viewname}View"

    def __NameTemplate(self, basename: str) -> str:
        return str(self.template_basedir / f"{basename}.html")

    @staticmethod
    def __TypeView(
        name: str,
        bases: Tuple[Union[Type[View], Type[object]], ...],
        attrs: _AttrsDict,
    ) -> type:
        return type(name, bases, cast(Dict[str, Any], attrs))


class _UpdateView(UpdateView[Model, ModelForm[Model]]):
    success_pattern: str

    def get_success_url(self) -> str:
        return urls.reverse(
            self.success_pattern, args=[self.kwargs[self.pk_url_kwarg]]
        )
