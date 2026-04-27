# korean-name-generator

Dependency-free Korean name generator library and CLI.

It generates Korean names with both romanized and Hangul forms, supports seeded
repeatable output, allows male/female/gender-neutral name pools, and can be
customized with a `config.yaml` file.

## Requirements

- Python 3.10+
- No runtime dependencies

## Installation

### From this repository, editable development install

Use this when you are working on the package locally:

```bash
git clone <repo-url>
cd korean-name-generator
python -m venv .venv
. .venv/bin/activate
python -m pip install -e .
```

### From this repository, normal local install

Use this when you just want the CLI and importable package from the local
checkout:

```bash
cd korean-name-generator
python -m pip install .
```

### Build and install a wheel

```bash
python -m pip wheel . --no-deps -w dist
python -m pip install dist/korean_name_generator-0.1.0-py3-none-any.whl
```

After installation, the console command is available as:

```bash
korean-name-generator --help
```

You can also run it without installing by setting `PYTHONPATH` from the repo
root:

```bash
PYTHONPATH=src python -m korean_name_generator --help
```

## CLI examples

Generate five names:

```bash
korean-name-generator --count 5
```

Generate deterministic output with a seed:

```bash
korean-name-generator --count 5 --seed 7
```

Select a given-name pool:

```bash
korean-name-generator --count 3 --gender male
korean-name-generator --count 3 --gender female
korean-name-generator --count 3 --gender neutral
```

Use Korean-order display in plain output:

```bash
korean-name-generator --count 3 --order korean
```

Emit JSON:

```bash
korean-name-generator --count 2 --seed 1 --format json
```

Example JSON shape:

```json
[
  {
    "family_name_en": "Lim",
    "family_name_ko": "임",
    "given_name_en": "Seseo",
    "given_name_ko": "세서",
    "gender": "female",
    "romanized": "Seseo Lim",
    "hangul": "임세서"
  }
]
```

Emit CSV:

```bash
korean-name-generator --count 10 --format csv > names.csv
```

Use an explicit config file:

```bash
korean-name-generator --count 3 --gender neutral --config ./config.yaml
```

## Python API examples

Generate one name:

```python
from korean_name_generator import generate_name

name = generate_name(gender="female", random_seed=7)
print(name.romanized)  # Western order, e.g. "Seseo Lim"
print(name.hangul)     # Korean order, e.g. "임세서"
```

Generate many names:

```python
from korean_name_generator import generate_names

names = generate_names(10, gender="male", random_seed=42)
for name in names:
    print(name.display())
```

Reuse a generator so the random state advances between calls:

```python
from korean_name_generator import KoreanNameGenerator

generator = KoreanNameGenerator(random_seed=7)
print(generator.generate(gender="neutral"))
print(generator.generate(gender="neutral"))
```

Load a custom config:

```python
from korean_name_generator import KoreanNameGenerator

generator = KoreanNameGenerator.from_config("config.yaml", random_seed=7)
name = generator.generate(gender="female")
print(name.as_dict())
```

## Configuration

The packaged defaults live in `src/korean_name_generator/config.yaml`.
Runtime config resolution is:

1. explicit `--config` / `config_path`
2. `$KOREAN_NAME_GENERATOR_CONFIG`
3. local `./config.yaml`
4. packaged defaults

Config files use this shape:

```yaml
name_pools:
  family_names:
    - { en: Kim, ko: 김 }
  first_syllables:
    - { en: Ji, ko: 지 }
  male_second_syllables:
    - { en: Ho, ko: 호 }
  female_second_syllables:
    - { en: Na, ko: 나 }
  gender_neutral_second_syllables:
    - { en: Sol, ko: 솔 }
```

The parser is intentionally small and dependency-free. It supports the package's
YAML shape shown above and JSON-compatible YAML. Each pool must be non-empty and
each entry must include non-empty `en` and `ko` values.

The generator filters out repeated given-name syllables such as `지지`. If a
custom second-syllable pool cannot provide a non-repeating option for the chosen
first syllable, generation raises `ValueError`.

## Output fields

`KoreanName.as_dict()` and structured CLI output include:

| Field | Meaning |
| --- | --- |
| `family_name_en` | Romanized family name |
| `family_name_ko` | Hangul family name |
| `given_name_en` | Romanized two-syllable given name |
| `given_name_ko` | Hangul two-syllable given name |
| `gender` | Selected pool: `female`, `male`, or `neutral` |
| `romanized` | Western-order display name |
| `hangul` | Korean-order Hangul display name |

## Development and verification

```bash
PYTHONPATH=src python -m unittest discover -s tests
python -m compileall -q src tests
PYTHONPATH=src python -m korean_name_generator --count 2 --seed 1 --format json
python -m pip wheel . --no-deps -w dist
```

Or use the Makefile shortcuts:

```bash
make test
make compile
make smoke
make check
```

## Release automation

Merges to `main` run the GitHub Actions workflow in
`.github/workflows/publish.yml`. The workflow runs linting, formatting checks,
type checking, tests, builds the source distribution and wheel, then publishes to
PyPI when the `pyproject.toml` version does not already exist on PyPI.

Publishing uses PyPI Trusted Publishing, so no long-lived PyPI API token is
required. Configure the PyPI project trusted publisher with:

- owner: `sagebynature`
- repository: `korean-name-generator`
- workflow: `publish.yml`
- environment: `pypi`

Bump `[project].version` before merging when a new PyPI release should be
created.
