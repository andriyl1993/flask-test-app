from dataclasses import asdict, is_dataclass


def _exclude_none_values(value):
    if isinstance(value, dict):
        return {
            item_key: _exclude_none_values(item_value)
            for item_key, item_value in value.items()
            if item_value is not None
        }

    if isinstance(value, list):
        return [
            _exclude_none_values(item_value)
            for item_value in value
            if item_value is not None
        ]

    if isinstance(value, tuple):
        return tuple(
            _exclude_none_values(item_value)
            for item_value in value
            if item_value is not None
        )

    return value


def dataclass_to_dict(instance, exclude_none: bool = False) -> dict:
    if not is_dataclass(instance):
        raise TypeError("dataclass_to_dict expects a dataclass instance")

    data = asdict(instance)
    if not exclude_none:
        return data

    return _exclude_none_values(data)
