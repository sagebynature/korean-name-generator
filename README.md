# korname-generator

Dependency-free Korean name generator library and CLI.

It generates Korean names with both romanized and Hangul forms, supports seeded
repeatable output, allows male/female/gender-neutral name pools, and can be
customized with a `config.yaml` file.

## Requirements

- Python 3.10+
- [`uv`](https://docs.astral.sh/uv/) for the install, run, build, and test commands below
- No runtime dependencies

## Installation

### From PyPI as a uv-managed CLI tool

```bash
uv tool install korname-generator
```

The PyPI distribution is `korname-generator`; the installed console command is
`korean-name-generator`.

After installation, run:

```bash
korean-name-generator --help
```

For a one-off run without installing the tool first, use `uvx`:

```bash
uvx --from korname-generator korean-name-generator --help
```

### From this repository for local development

Use this when you are working on the package locally:

```bash
git clone <repo-url>
cd korean-name-generator
uv sync --dev
uv run korean-name-generator --help
```

### From this repository as a local uv-managed CLI tool

Use this when you want to install the CLI from the local checkout into uv's tool
space:

```bash
cd korean-name-generator
uv tool install .
korean-name-generator --help
```

### Build and install a wheel with uv

```bash
uv build
uv tool install dist/korname_generator-0.1.0-py3-none-any.whl
```

You can also run the package module directly from the local checkout:

```bash
uv run python -m korean_name_generator --help
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
uv run python -m pytest
uv run python -m compileall -q src tests
uv run python -m korean_name_generator --count 2 --seed 1 --format json
uv build
```

Or use the Makefile shortcuts:

```bash
make lint
make test
make check
```

## Release automation

Merges to `main` or `dev` run the GitHub Actions workflow in
`.github/workflows/release.yml`. The workflow first runs `make check` (Ruff
linting, Ruff format checks, Ty type checking, and pytest). If semantic-release
creates a release, the publish job builds the source distribution and wheel with
`uv build`, then publishes the `korname-generator` distribution to PyPI.

Publishing uses PyPI Trusted Publishing, so no long-lived PyPI API token is
required. The PyPI project trusted publisher is configured with:

- owner: `sagebynature`
- repository: `korean-name-generator`
- workflow: `release.yml`
- environment: `pypi`

Semantic-release owns `[project].version` in `pyproject.toml`; use Conventional
Commits on `main` for stable releases and on `dev` for `rc` prereleases.
