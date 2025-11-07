# dracklib

My collection of useful Python stuff.

* [Installation](#installation)
* [API Reference](#api-reference)
  * [`RC` - Return Code Dataclass](#rc---return-code-dataclass)
  * [`dget` - Dictionary Nested Value Retrieval](#dget---dictionary-nested-value-retrieval)
* [Documentation](#documentation)
* [Development](#development)
* [License](#license)
* [Author](#author)
* [Repository](#repository)

## Installation

```shell
pip install dracklib
# or with uv:
uv add dracklib
```

See [installation.md](installation.md) for more details on setting up uv and Python.

## API Reference

### `RC` - Return Code Dataclass

A simple dataclass for structured function returns containing status information.

```python
from dracklib import RC

res = RC(ok=True, rc=0, msg="Success", obj=None)
```

**Fields:**

- `ok: bool` - Whether the operation was successful
- `rc: int` - Return code (typically HTTP-style codes like 200, 404, etc.)
- `msg: str` - Human-readable message
- `obj: Any` - Optional object containing result data

**Usage Example:**

```python
from dummy import load_data
from dracklib import RC


def fetch_data() -> RC:
    try:
        data = load_data()
        return RC(ok=True, rc=200, msg="Data loaded", obj=data)
    except Exception as e:
        return RC(ok=False, rc=500, msg=str(e), obj=None)


result = fetch_data()
if result.ok:
    print(f"Success: {result.obj}")
else:
    print(f"Error {result.rc}: {result.msg}")
```

### `dget` - Dictionary Nested Value Retrieval

Retrieve values from nested dictionaries using a delimiter-separated key string.

```python
from dracklib import dget

data = {'user': {'name': 'John', 'address': {'city': 'New York', 'zip': '10001'}}}

# Get nested value
city = dget(data, 'user.address.city')  # Returns 'New York'

# Use custom delimiter
data2 = {'a/b/c': 'value'}
result = dget(data2, 'a/b/c', delimiter='/')

# With default value
missing = dget(data, 'user.phone', default='N/A')  # Returns 'N/A'
```

**Parameters:**

- `d: dict` - The dictionary to search in
- `k: str` - Delimiter-separated key path (e.g., `'user.address.city'`)
- `delimiter: str` - Key separator (default: `'.'`)
- `default: Any` - Value to return if key not found (default: `None`)

**Returns:**

- The value at the specified path, or `default` if not found

**Raises:**

- `ValueError` - If delimiter is not a non-empty string
- `KeyError` - If key path doesn't exist and no default is provided

## Documentation

- [installation.md](installation.md) - Installing uv and Python
- [development.md](development.md) - Development setup and workflows
- [publishing.md](publishing.md) - Publishing releases to PyPI

## Development

See [development.md](development.md) for detailed development instructions.

Quick start:

```shell
# install dependencies
make install

# run linting and tests
make

# run tests individually
uv run pytest
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Author

Daniel Drack (daniel@drackthor.me)

## Repository

https://github.com/DrackThor/dracklib