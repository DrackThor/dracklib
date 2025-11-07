import pytest

from dracklib.utils import dget


def test_dget_simple_key():
    data = {"key": "value"}
    result = dget(data, "key")
    assert result == "value"


def test_dget_nested_key():
    data = {"level1": {"level2": {"level3": "nested_value"}}}
    result = dget(data, "level1.level2.level3")
    assert result == "nested_value"


def test_dget_key_not_found_with_default():
    data = {"key": "value"}
    result = dget(data, "nonexistent", default="default_value")
    assert result == "default_value"


def test_dget_key_not_found_no_default():
    data = {"key": "value"}
    with pytest.raises(KeyError, match="Key 'nonexistent' not found in dictionary"):
        dget(data, "nonexistent")


def test_dget_invalid_delimiter():
    data = {"level1": {"level2": "value"}}
    with pytest.raises(ValueError, match="Delimiter must be a non-empty string"):
        dget(data, "level1/level2", delimiter="")


def test_dget_custom_delimiter():
    data = {"level1": {"level2": {"level3": "nested_value"}}}
    result = dget(data, "level1|level2|level3", delimiter="|")
    assert result == "nested_value"
