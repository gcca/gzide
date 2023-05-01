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

import functools
import string
from typing import Dict

from django import template

register = template.Library()

CHS = string.ascii_lowercase
CHSLEN = len(CHS)
COUNT = -1
KEYS: Dict[str, str] = {}


@functools.lru_cache(maxsize=1024)
def __skey(i: int) -> str:
    return __skey(i // CHSLEN - 1) + CHS[int(i) % CHSLEN] if i + 1 else ""


def skey(s: str) -> str:
    if s in KEYS:
        return KEYS[s]
    global COUNT
    COUNT += 1
    KEYS[s] = ktok = __skey(COUNT // CHSLEN - 1) + CHS[int(COUNT) % CHSLEN]
    return ktok


@register.simple_tag
@functools.cache
def nomos_sk(s: str) -> str:
    return skey(s)
