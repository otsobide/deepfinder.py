<h1 align="center">🔍 Deepfinder</h1>

<div align="center">

[![GitHub](https://img.shields.io/github/license/otsobide/deepfinder.py)](https://github.com/otsobide/deepfinder.py/blob/main/LICENSE)
[![Pypi](https://img.shields.io/pypi/v/deepfinder)](https://pypi.org/project/deepfinder/)
[![Downloads](https://pepy.tech/badge/deepfinder)](https://pepy.tech/project/deepfinder)
[![GA](https://github.com/otsobide/deepfinder.py/workflows/Tests/badge.svg)](https://github.com/otsobide/deepfinder.py/actions/workflows/tests.yml)

</div>

## What is Deepfinder?

Deepfinder reads values out of nested data using a dot path. Instead of a ladder of
`if` statements and `.get()` calls, you write the shape of what you want:

```python
>>> from deepfinder import deep_find
>>> user = {'name': 'ash', 'links': {'pokehub': '@ash'}}
>>> deep_find(user, 'links.pokehub')
'@ash'

```

It has no dependencies, ships type hints, and supports Python 3.9+.

Every example in this file is executed as part of the test suite, so nothing here
can drift away from what the code actually does.

### Key features

- **Dot paths** into dictionaries, sequences and objects: `'user.profile.name'`
- **Indexing**, including from the end: `'users.0.name'`, `'users.-1.name'`
- **Fan-out** over sequences: `'users.*.name'`
- **Null handling**: `'users.?.email'` for the first hit, `'users.*?.email'` for all of them
- **Never raises** on a lookup: a miss yields `default`
- **Container subclasses** that carry the method with them

## Installation

```bash
pip install deepfinder
```

## Path syntax

| Segment | Meaning | Example |
| --- | --- | --- |
| `name` | Dictionary key, mapping key, or object attribute | `'user.name'` |
| `0`, `-1` | Sequence index, negative counts from the end | `'users.0.name'` |
| `*` | Every item, one result per item | `'users.*.name'` |
| `?` | The first item that resolves to a non-`None` value | `'users.?.email'` |
| `*?` | Every item that resolves to a non-`None` value (`?*` also works) | `'users.*?.email'` |

The separator is configurable with `path_token`, which is also how you reach keys
that contain a dot:

```python
>>> deep_find({'a.b': {'c': 1}}, 'a.b/c', path_token='/')
1

```

## Quick start

### Dictionaries and lists

```python
>>> trainer = {
...     'name': 'ash',
...     'pokemons': [
...         {'name': 'pikachu', 'type': 'electric'},
...         {'name': 'charmander', 'type': 'fire'},
...     ],
... }
>>> deep_find(trainer, 'pokemons.0.name')
'pikachu'
>>> deep_find(trainer, 'pokemons.-1.name')
'charmander'
>>> deep_find(trainer, 'pokemons.*.name')
['pikachu', 'charmander']

```

### Missing values

A lookup never raises. When it does not resolve, you get `default`:

```python
>>> deep_find(trainer, 'pokemons.99.name') is None
True
>>> deep_find(trainer, 'pokemons.99.name', default='unknown')
'unknown'

```

### First hit, and all the hits

```python
>>> squad = {
...     'pokemons': [
...         {'name': 'pikachu'},
...         {'name': 'charmander', 'ball': 'superball'},
...         {'name': 'lucario', 'ball': 'ultraball'},
...     ],
... }
>>> deep_find(squad, 'pokemons.?.ball')
'superball'
>>> deep_find(squad, 'pokemons.*?.ball')
['superball', 'ultraball']

```

`*` keeps one slot per item, so it tells you *which* items missed:

```python
>>> deep_find(squad, 'pokemons.*.ball')
[None, 'superball', 'ultraball']

```

### Objects

Instance attributes, `__slots__`, class attributes and properties all resolve:

```python
>>> class Address:
...     def __init__(self, city):
...         self.city = city
>>> class Trainer:
...     region = 'Kanto'
...     def __init__(self, name, address):
...         self.name = name
...         self.address = address
...     @property
...     def display_name(self):
...         return self.name.title()
>>> ash = Trainer('ash', Address('Pallet Town'))
>>> deep_find(ash, 'address.city')
'Pallet Town'
>>> deep_find(ash, 'display_name')
'Ash'
>>> deep_find(ash, 'region')
'Kanto'

```

Methods are not values, so a segment that collides with a method name misses rather
than handing back a bound method:

```python
>>> deep_find(ash, 'display_name.upper', default='not found')
'not found'

```

Named tuples resolve both ways:

```python
>>> from collections import namedtuple
>>> Point = namedtuple('Point', ['x', 'y'])
>>> deep_find({'p': Point(1, 2)}, 'p.y')
2
>>> deep_find({'p': Point(1, 2)}, 'p.0')
1

```

### Mappings

Anything that is a `Mapping` resolves by key, not just `dict`:

```python
>>> from collections import ChainMap
>>> deep_find(ChainMap({'a': 1}, {'b': 2}), 'b')
2

```

### Containers that carry the method

```python
>>> from deepfinder.entity import DeepFinderDict, DeepFinderList
>>> DeepFinderDict(squad).deep_find('pokemons.?.ball')
'superball'
>>> DeepFinderList([squad]).deep_find('0.pokemons.*?.ball')
['superball', 'ultraball']

```

Both accept the same `path_token` and `default` arguments as `deep_find`.

## Behaviour worth knowing

These are the sharp edges, all of them covered by tests.

| Situation | Result | Why |
| --- | --- | --- |
| The stored value is `None` | `default` | A resolved `None` is indistinguishable from a miss |
| `*` or `*?` with `default` set | `[...]`, never `default` | A list is never `None`, so substitution cannot fire |
| Falsy values (`0`, `''`, `False`, `[]`) | returned as-is | Substitution keys off `None`, not truthiness |
| A key containing the separator | miss | Use a different `path_token` |
| Strings | not indexable | So a path never walks into single characters |
| `bytes` / `bytearray` | indexed as integers | They are ordinary non-string iterables |
| Methods | never resolve | So `'count'` or `'items'` yields `default`, not a truthy bound method |
| Callables held as instance state | resolve | They are data the object is carrying |
| Generators and iterators | advanced only as far as the index needs | The fan-out operators still read all of it |
| Large sequences such as `range` | indexed in place, never copied | `deep_find(range(10 ** 10), '3')` is instant |
| Sets and frozen sets | indexable, order not guaranteed | Materialised in iteration order |

### Paths and untrusted input

`deep_find` walks data, not the interpreter. Dunder segments never resolve, and
attributes are never read off modules, functions, frames, tracebacks, coroutines or
code objects, and methods do not resolve. A path therefore cannot pivot from your
data into module globals or frame locals:

```python
>>> deep_find(ash, '__class__')  is None
True
>>> deep_find(ash, 'display_name.__globals__') is None
True

```

That said, `deep_find` will happily return any value your own object graph exposes.
If paths come from users, keep deciding for yourself which roots you hand it.

### Argument validation

Misuse of the API is loud, unlike a lookup that simply misses:

```python
>>> deep_find({'a': 1}, 1)
Traceback (most recent call last):
    ...
TypeError: path must be a str, got int
>>> deep_find({'a': 1}, 'a', path_token='')
Traceback (most recent call last):
    ...
ValueError: path_token must not be empty

```

## Deprecated: `nativify()`

`deepfinder.entity.nativify()` rebinds `builtins.list` and `builtins.dict` so that
containers built through those *constructors* gain a `deep_find` method. It is
deprecated as of 1.6.0: it mutates the interpreter for every library in the process,
and it never affected list and dict **literals**, which are built by bytecode that
does not consult `builtins`. Use `DeepFinderList` / `DeepFinderDict`, or just call
`deep_find`.

## Development

```bash
git clone https://github.com/otsobide/deepfinder.py
cd deepfinder.py
make install    # installs the package plus the dev extras
make check      # lint, format check, type check, tests with coverage
```

Individual targets:

```bash
make lint       # ruff check
make format     # ruff format
make typecheck  # mypy --strict
make test       # unittest
make coverage   # unittest under coverage, fails under 100%
make build      # sdist + wheel, validated with twine
```

To run one test module or a single test:

```bash
python -m unittest tests.unit.deep_find_in_lists_test
python -m unittest tests.unit.deep_find_in_lists_test.TestFindInLists.test_all_values_of_list
```

## Contributing

Contributions are welcome. Please keep the suite green and the coverage at 100%,
and add a test that fails before your fix and passes after it.

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/otsobide/deepfinder.py/blob/main/LICENSE) file for details.
