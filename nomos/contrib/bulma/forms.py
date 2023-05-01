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

from django import forms as djforms

from . import mixins

__all__ = ("Form", "CharField", "ModelChoiceField", "TextInput", "Select")


class Form(mixins.BulmaRenderableMixin, djforms.Form):
    """Bulma form support."""


class TextInput(mixins.WidgetMixin, djforms.TextInput):
    template_str = (
        '<input class="input" type="{{ widget.type }}"'
        ' name="{{ widget.name }}"'
        "{% if widget.value != None %}"
        " value=\"{{ widget.value|stringformat:'s' }}\""
        "{% endif %}"
        '{% include "django/forms/widgets/attrs.html" %}>'
    )


class Select(mixins.WidgetMixin, djforms.Select):
    template_str = (
        '<div class="select is-fullwidth">'
        '<select name="{{ widget.name }}"'
        '{% include "django/forms/widgets/attrs.html" %}>'
        "{% for group_name, group_choices, group_index in widget.optgroups %}"
        "{% if group_name %}"
        '<optgroup label="{{ group_name }}">'
        "{% endif %}"
        "{% for option in group_choices %}"
        "{% include option.template_name with widget=option %}"
        "{% endfor %}"
        "{% if group_name %}"
        "</optgroup>"
        "{% endif %}"
        "{% endfor %}"
        "</select>"
        "</div>"
    )


class CharField(djforms.CharField):
    widget = TextInput


class ModelChoiceField(djforms.ModelChoiceField):
    widget = Select
