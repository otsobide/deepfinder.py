<h1 align="center">🔍 Deepfinder</h1>

<div align="center">

[![GitHub](https://img.shields.io/github/license/otsobide/deepfinder.py)](https://github.com/otsobide/deepfinder.py/blob/main/LICENSE)
[![Pypi](https://img.shields.io/pypi/v/deepfinder)](https://pypi.org/project/deepfinder/)
[![Downloads](https://pepy.tech/badge/deepfinder)](https://pepy.tech/project/deepfinder)
[![GA](https://github.com/otsobide/deepfinder.py/workflows/Tests/badge.svg)](https://github.com/otsobide/deepfinder.py/actions/workflows/tests.yml)

</div>

## What is Deepfinder?

Deepfinder is a Python library that makes it easy to access nested data in dictionaries, lists, and objects using simple dot notation. Instead of writing complex nested access code, you can use intuitive paths like `'users.0.name'` to get the data you need.

### Key Features

- **Simple Dot Notation**: Access nested data using paths like `'user.profile.name'`
- **List Support**: Access list items using indices like `'users.0.name'`
- **Object Support**: Access class attributes and properties using dot notation
- **Wildcard Search**: Use `*` to get all items in a list
- **Smart Null Handling**: Use `?` to find first non-null value or `*?` for all non-null values
- **Custom Classes**: Built-in support for dictionary, list, and object deep finding capabilities

### Path Syntax

Deepfinder uses a simple but powerful path syntax to navigate through your data:

- `.` - Access dictionary keys, object attributes, or properties (e.g., `'user.name'`, `'person.address.city'`)
- `0`, `1`, etc. - Access list items by index (e.g., `'users.0.name'`)
- `*` - Get all items in a list (e.g., `'users.*.name'` returns all names)
- `?` - Get first non-null value (e.g., `'users.?.email'` returns first non-null email)
- `*?` - Get all non-null values (e.g., `'users.*?.email'` returns all non-null emails)

### When to Use Deepfinder?

Deepfinder is particularly useful when:
- Working with complex nested JSON data
- Accessing deeply nested configuration files
- Processing API responses with multiple levels of nesting
- Working with data structures that mix dictionaries and lists
- Accessing nested object attributes and properties
- Working with complex class hierarchies
- You need to find specific values in complex data structures or objects

## Installation

```bash
pip install deepfinder
```

## Quick Start

### Basic Dictionary Access

```python
from deepfinder import deep_find

# Example data
user = {
    'name': 'ash',
    'links': {
        'pokehub': '@ash'
    }
}

# Get the pokehub link
result = deep_find(user, 'links.pokehub')
print(result)  # Output: '@ash'
```

### Working with Lists

```python
from deepfinder import deep_find

# Example data with a list of pokemon
user = {
    'name': 'ash',
    'pokemons': [
        {
            'name': 'pikachu',
            'type': 'electric'
        },
        {
            'name': 'charmander',
            'type': 'fire'
        }
    ]
}

# Get pikachu's name (first pokemon)
result = deep_find(user, 'pokemons.0.name')
print(result)  # Output: 'pikachu'

# Get all pokemon names
result = deep_find(user, 'pokemons.*.name')
print(result)  # Output: ['pikachu', 'charmander']
```

### Working with Objects

```python
from deepfinder import deep_find

class Address:
    def __init__(self, city, country):
        self.city = city
        self.country = country

class User:
    def __init__(self, name, address):
        self.name = name
        self.address = address

# Create nested objects
address = Address('Pallet Town', 'Kanto')
user = User('Ash', address)

# Access nested object attributes
result = deep_find(user, 'address.city')
print(result)  # Output: 'Pallet Town'
```

### Finding First Non-Null Value

Use `?` to get the first non-null value in a list:

```python
user = {
    'pokemons': [
        {'name': 'pikachu'},  # no ball
        {'name': 'charmander', 'ball': 'superball'},  # has ball
        {'name': 'lucario', 'ball': 'ultraball'}  # has ball
    ]
}

# Get the first pokemon that has a ball
result = deep_find(user, 'pokemons.?.ball')
print(result)  # Output: 'superball'
```

### Finding All Non-Null Values

Use `*?` to get all non-null values in a list:

```python
user = {
    'pokemons': [
        {'name': 'pikachu'},  # no ball
        {'name': 'charmander', 'ball': 'superball'},  # has ball
        {'name': 'lucario', 'ball': 'ultraball'}  # has ball
    ]
}

# Get all pokemon balls
result = deep_find(user, 'pokemons.*?.ball')
print(result)  # Output: ['superball', 'ultraball']
```

## Using Custom Classes

Deepfinder provides custom classes that make it even easier to work with nested data:

### DeepFinderDict

```python
from deepfinder.entity import DeepFinderDict

# Create a dictionary with built-in deep finding
user = DeepFinderDict({
    'name': 'ash',
    'pokemons': [
        {'name': 'pikachu'},
        {'name': 'charmander', 'ball': 'superball'}
    ]
})

# Use the deep_find method directly on the dictionary
result = user.deep_find('pokemons.?.ball')
print(result)  # Output: 'superball'
```

### DeepFinderList

```python
from deepfinder.entity import DeepFinderList

# Create a list with built-in deep finding
users = DeepFinderList([{
    'name': 'ash',
    'pokemons': [
        {'name': 'pikachu'},
        {'name': 'charmander', 'ball': 'superball'}
    ]
}])

# Use the deep_find method directly on the list
result = users.deep_find('0.pokemons.?.ball')
print(result)  # Output: 'superball'
```

## Contributing

Contributions are welcome! Feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
