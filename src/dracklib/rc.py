from dataclasses import dataclass
from typing import Any


@dataclass
class RC:
    ok: bool
    rc: int
    msg: str
    obj: Any
