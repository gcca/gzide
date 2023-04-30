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

from django.forms import renderers as form_renderers
from django.utils.functional import cached_property


class AppDjangoTemplates(form_renderers.DjangoTemplates):
    @cached_property
    def engine(self):
        loaders = [
            (
                "django.template.loaders.cached.Loader",
                [
                    "django.template.loaders.app_directories.Loader",
                    "django.template.loaders.filesystem.Loader",
                ],
            )
        ]
        return self.backend(
            {
                "APP_DIRS": False,
                "DIRS": [
                    Path(form_renderers.__file__).parent
                    / self.backend.app_dirname
                ],
                "NAME": "djangoforms",
                "OPTIONS": {"loaders": loaders},
            }
        )
