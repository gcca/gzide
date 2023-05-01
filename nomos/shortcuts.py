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

from typing import List, Type

from django.contrib.auth import get_permission_codename
from django.db import models

__all__ = ("PermissionNames",)


class PermissionNames:
    __slots__ = "list", "create", "detail", "update", "delete"

    def __init__(
        self,
        list: List[str],
        create: List[str],
        detail: List[str],
        update: List[str],
        delete: List[str],
    ) -> None:
        self.list = list
        self.create = create
        self.detail = detail
        self.update = update
        self.delete = delete

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}(list={self.list},"
            f" create={self.create}, detail={self.detail}),"
            f" update={self.update}, delete={self.delete})"
        )

    @classmethod
    def Make(cls, model: Type[models.Model]) -> PermissionNames:
        opts = model._meta

        add_permission = cls.__get_name(opts, "add")
        change_permission = cls.__get_name(opts, "change")
        delete_permission = cls.__get_name(opts, "delete")
        view_permission = cls.__get_name(opts, "view")

        return PermissionNames(
            list=[view_permission],
            create=[add_permission],
            detail=[view_permission],
            update=[change_permission],
            delete=[delete_permission],
        )

    @staticmethod
    def __get_name(
        opts: models.options.Options[models.Model], action: str
    ) -> str:
        return ".".join(
            (opts.app_label, get_permission_codename(action, opts))
        )
