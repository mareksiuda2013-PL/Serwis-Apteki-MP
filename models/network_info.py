from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class NetworkInfo:

    local_ip: str = ""
    gateway: str = ""
    internet: bool = False