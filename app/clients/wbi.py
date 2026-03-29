from __future__ import annotations

import time
from hashlib import md5
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlparse

MIXIN_KEY_ENC_TAB: list[int] = [
    46,
    47,
    18,
    2,
    53,
    8,
    23,
    32,
    15,
    50,
    10,
    31,
    58,
    3,
    45,
    35,
    27,
    43,
    5,
    49,
    33,
    9,
    42,
    19,
    29,
    28,
    14,
    39,
    12,
    38,
    41,
    13,
    37,
    48,
    7,
    16,
    24,
    55,
    40,
    61,
    26,
    17,
    0,
    1,
    60,
    51,
    30,
    4,
    22,
    25,
    54,
    21,
    56,
    59,
    6,
    63,
    57,
    62,
    11,
    36,
    20,
    34,
    44,
    52,
]


def extract_key_from_url(url: str) -> str:
    path = urlparse(url).path
    return Path(path).stem


def gen_mixin_key(img_key: str, sub_key: str) -> str:
    raw = img_key + sub_key
    return "".join(raw[index] for index in MIXIN_KEY_ENC_TAB)[:32]


def sanitize_wbi_value(value: Any) -> str:
    text = str(value)
    return "".join(char for char in text if char not in "!'()*")


def encode_query_sorted(params: dict[str, Any]) -> str:
    sorted_items = sorted(
        (key, sanitize_wbi_value(value)) for key, value in params.items() if value is not None
    )
    return "&".join(
        f"{quote(str(key), safe='')}={quote(str(value), safe='~-._')}" for key, value in sorted_items
    )


def sign_wbi_params(
    params: dict[str, Any],
    img_key: str,
    sub_key: str,
    wts: int | None = None,
) -> dict[str, Any]:
    mixin_key = gen_mixin_key(img_key, sub_key)
    signed_params: dict[str, Any] = {key: value for key, value in params.items() if value is not None}
    signed_params["wts"] = wts or int(time.time())

    query = encode_query_sorted(signed_params)
    signed_params["w_rid"] = md5((query + mixin_key).encode("utf-8")).hexdigest()
    return signed_params
