from typing import Any


def dget(d: dict[str, Any], k: str, delimiter: str = ".", default: Any = None) -> Any:
    """
    Retrieve a value from a nested dictionary using a delimiter-separated key.
    If the key does not exist in the dictionary, the method either returns
    a default value (if provided) or raises an exception.
    The method validates the delimiter to ensure that it is a non-empty string.

    :param d: The dictionary to search in.
               Must be a dictionary type containing potential nested dictionaries.
    :type d: dict
    :param k: The delimiter-separated key used to access values in the nested dictionary.
    :type k: str
    :param delimiter: The string acting as a delimiter for separating keys.
                      Must be a non-empty string.
    :type delimiter: str
    :param default: Optional. The value to return if the key is not found in the dictionary.
                    If not provided or is None, a KeyError will be raised upon failure.
    :type default: Any
    :return: The value found in the nested dictionary corresponding to the given key.
    :rtype: Any
    :raises ValueError: If the delimiter is not a non-empty string.
    :raises KeyError: If the key does not exist in the dictionary and no default value is provided.
    """
    # Validate delimiter
    if not delimiter:
        raise ValueError("Delimiter must be a non-empty string")

    # Split the key by delimiter
    keys = k.split(delimiter)

    # Traverse the nested dictionary
    current = d
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            # Key not found
            if default is not None:
                return default
            else:
                raise KeyError(f"Key '{k}' not found in dictionary")

    return current
