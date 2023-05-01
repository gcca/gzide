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


from typing import Any, Dict, Final, List

from django import forms
from django.db import models
from django.http import HttpRequest, HttpResponse
from django.views.generic.edit import FormView

__all__ = ("CompleteView", "StepView")


class SequenceView(FormView[forms.ModelForm[models.Model]]):
    sequence_key: Final[str] = "sequence"

    def _Data(self, form: forms.ModelForm[models.Model]) -> Dict[str, Any]:
        return forms.model_to_dict(form.instance)

    def setup(
        self, request: HttpRequest, *args: List[Any], **kwargs: Dict[str, Any]
    ) -> None:
        super().setup(request, *args, **kwargs)
        request.session.setdefault(self.sequence_key, {})

    def get_initial(self) -> Dict[str, Any]:
        return self.request.session.get(self.sequence_key, {})


class StepView(SequenceView):
    def form_valid(self, form: forms.ModelForm[models.Model]) -> HttpResponse:
        data = self._Data(form)
        step = self.request.session[self.sequence_key]
        if form._meta.fields is None:
            raise ValueError("No fields on step view")
        step.update({field: data[field] for field in form._meta.fields})
        self.request.session[self.sequence_key] = step
        return super().form_valid(form)


class CompleteView(SequenceView):
    def form_valid(self, form: forms.ModelForm[models.Model]) -> HttpResponse:
        lastep = self.request.session[self.sequence_key]
        for field in form.instance._meta.fields:
            if field.name not in lastep:
                continue
            field.save_form_data(form.instance, lastep[field.name])
        return super().form_valid(form)
