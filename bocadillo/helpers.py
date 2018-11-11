"""Miscellaneous helper functions."""


def remove_nones(dict_: dict) -> dict:
    return {k: v for k, v in dict_.items() if v is not None}
