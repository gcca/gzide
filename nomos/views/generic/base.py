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

from typing import Any, Callable, List, Optional, Type, cast

from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.forms import models as model_forms
from django.views.generic import base as base_views

__all__ = ["MixModelFormMixin"]


class MixModelFormMixin(base_views.View):
    form_mixins: List[Any] = []
    formfield_callback: Optional[
        Callable[[models.Field], model_forms.Field]
    ] = None

    form_class: Optional[Type[model_forms.ModelForm]]

    def get_form_class(self) -> Type[model_forms.ModelForm]:
        if self.form_class:
            if self.fields is not None:
                raise ImproperlyConfigured(
                    "Only specify one of 'fields' or 'form_class'."
                )

            return self.form_class
        else:
            if self.fields is None:
                raise ImproperlyConfigured(
                    "Using without the 'fields' attribute is prohibited."
                )

            model = (
                self.model
                if self.model is not None
                else self.get_queryset().model
            )

            model_form = type(
                "ModelForm", (model_forms.ModelForm, *self.form_mixins), {}
            )

            return cast(
                Type[model_forms.ModelForm],
                model_forms.modelform_factory(
                    model,
                    model_form,
                    fields=self.fields,
                    formfield_callback=self.formfield_callback,
                ),
            )
