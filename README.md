# korean-name-generator

Standalone Korean name generator library and CLI

The package has no runtime dependencies and supports deterministic output through a random seed.

## Install for development

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e .
```

## CLI

```bash
korean-name-generator --count 5 --gender any --seed 7
python -m korean_name_generator --count 3 --format json
python -m korean_name_generator --count 10 --format csv --order korean
python -m korean_name_generator --count 3 --gender neutral --config ./config.yaml
```

Formats:

- `plain`: one human-readable name per line.
- `json`: structured list with romanized and Hangul fields.
- `csv`: machine-readable rows on stdout.

## Python API

```python
from korean_name_generator import KoreanNameGenerator, generate_names

generator = KoreanNameGenerator.from_config("config.yaml", random_seed=7)
print(generator.generate(gender="female").hangul)

names = generate_names(5, gender="male", random_seed=42)
```

## Configuration

The packaged defaults live in `src/korean_name_generator/config.yaml`. Runtime
resolution is:

1. explicit `--config` / `config_path`
2. `$KOREAN_NAME_GENERATOR_CONFIG`
3. local `./config.yaml`
4. packaged defaults

Config files use the same shape as the packaged file:

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

The generator filters out repeated given-name syllables such as `지지`.

## Verification

```bash
python -m unittest discover -s tests
python -m compileall -q src tests
python -m korean_name_generator --count 2 --seed 1 --format json
```
