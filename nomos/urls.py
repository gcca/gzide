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

from typing import List, Optional, Tuple, Type

from django.db import models
from django.urls import URLPattern, path

from .views.generic import menu as views_menu

__all__ = ["menu_patterns"]


default_menu_traits = views_menu.MenuTraits()


def menu_patterns(
    model: Type[models.Model],
    template_basedir: str,
    app_name: str,
    patterns_prefix: str,
    pk_url_type: Optional[str] = None,
    menu_traits: views_menu.MenuTraits = default_menu_traits,
) -> Tuple[List[URLPattern], str]:
    views = views_menu.menuviews_factory(
        model,
        template_basedir,
        f"{patterns_prefix}:{app_name}",
        menu_traits,
    )
    pk_url_kwarg = views.detail.pk_url_kwarg
    if pk_url_type is None:
        pk_url_type = __infer_pk_url_type(model)

    return (
        [
            path("list/", views.list.as_view(), name="list"),
            path("create/", views.create.as_view(), name="create"),
            path(
                f"<{pk_url_type}:{pk_url_kwarg}>/detail/",
                views.detail.as_view(),
                name="detail",
            ),
            path(
                f"<{pk_url_type}:{pk_url_kwarg}>/update/",
                views.update.as_view(),
                name="update",
            ),
            path(
                f"<{pk_url_type}:{pk_url_kwarg}>/delete/",
                views.delete.as_view(),
                name="delete",
            ),
        ],
        app_name,
    )


def __infer_pk_url_type(model: Type[models.Model]) -> str:
    pk = model._meta.pk
    if isinstance(pk, (models.BigIntegerField, models.ForeignKey)):
        return "int"
    if isinstance(pk, models.CharField):
        return "str"
    raise ValueError("Uninferable primary key field to type string")
