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

from typing import Any, Dict, NamedTuple

from django.db.models import Model
from django.views.generic.base import ContextMixin


class MultipleObjectMixin(ContextMixin):
    model: Model

    paginate_by = 16
    fields = "__all__"

    def get_context_data(self, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        object_fields = (
            tuple(field.name for field in self.model._meta.fields)
            if self.fields == "__all__"
            else self.fields
        )

        object_items = tuple(
            self.Item(
                obj.pk, tuple(getattr(obj, field) for field in object_fields)
            )
            for obj in context["page_obj"]
        )

        context["object_fields"] = object_fields
        context["object_items"] = object_items

        return context

    class Item(NamedTuple):
        pk: Any
        fields: Any
