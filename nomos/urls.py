# Copyright © 2023, Cristhian Alberto Gonzales Castillo. All Rights Reserved.
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

from typing import Optional, Tuple, Type

from django.db.models import Model
from django.urls import URLPattern, path

from .views.generic import models as views_models

__all__ = ["model_patterns"]


def model_patterns(
    model: Type[Model],
    namespaceprefix: str,
    bases: Optional[Tuple[Type, ...]] = None,
) -> Tuple[Tuple[URLPattern, ...], str]:
    sname = views_models.SN.sub("-", model._meta.object_name).lower()
    namespaceprefix = f"{namespaceprefix}:{sname}"
    patterns = views_models.Patterns(
        f"{namespaceprefix}:main",
        f"{namespaceprefix}:list",
        f"{namespaceprefix}:detail",
        f"{namespaceprefix}:create",
        f"{namespaceprefix}:update",
    )
    views = views_models.modelviews_factory(model, patterns, bases)
    return (
        (
            path("", views.mainview.as_view(), name="main"),
            path("list/", views.listview.as_view(), name="list"),
            path("create/", views.createview.as_view(), name="create"),
            path(
                f"<int:{views.pk_url_kwarg}>/detail/",
                views.detailview.as_view(),
                name="detail",
            ),
            path(
                f"<int:{views.pk_url_kwarg}>/update/",
                views.updateview.as_view(),
                name="update",
            ),
        ),
        sname,
    )
