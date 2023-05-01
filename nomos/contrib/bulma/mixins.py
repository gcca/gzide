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

from typing import Any, Dict, cast

from django.forms.renderers import DjangoTemplates
from django.forms.utils import RenderableMixin

__all__ = ["BulmaRenderableMixin"]


class BulmaRenderableMixin(RenderableMixin):
    def as_bulma_v(self) -> str:
        return cast(str, self.render("nomos/bulma/form_v.html"))


class WidgetMixin:
    template_str = ""

    def _render(
        self,
        template_name: str,
        context: Dict[str, Any],
        renderer: DjangoTemplates,
    ) -> str:
        template = renderer.engine.from_string(self.template_str)
        return cast(str, template.render(context))
