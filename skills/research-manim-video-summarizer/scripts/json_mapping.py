from __future__ import annotations


def as_object_map(value: object) -> dict[str, object] | None:
    if not isinstance(value, dict):
        return None
    mapped: dict[str, object] = {}
    for key, item in value.items():
        if not isinstance(key, str):
            return None
        mapped[key] = item
    return mapped
