from __future__ import annotations

import json
import logging
import os
from collections.abc import Mapping
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path
from typing import Any, cast

from .models import NamePair

CONFIG_ENV_VAR = "KOREAN_NAME_GENERATOR_CONFIG"
logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class NameConfig:
    family_names: tuple[NamePair, ...]
    first_syllables: tuple[NamePair, ...]
    male_second_syllables: tuple[NamePair, ...]
    female_second_syllables: tuple[NamePair, ...]
    gender_neutral_second_syllables: tuple[NamePair, ...]


DEFAULT_CONFIG_PATH = Path(str(files("korean_name_generator").joinpath("config.yaml")))


def load_name_config(path: str | os.PathLike[str] | None = None) -> NameConfig:
    """Load name pools from a YAML config file.

    Resolution order is explicit `path`, `$KOREAN_NAME_GENERATOR_CONFIG`, local
    `./config.yaml`, then the packaged default config. The parser is intentionally
    small and dependency-free; it supports the package's list-of-inline-maps YAML
    shape and JSON-compatible YAML.
    """

    source = _resolve_config_path(path)
    logger.debug("Loading Korean name config from %s", source)
    payload = _load_mapping(source)
    pools = payload.get("name_pools", payload)
    if not isinstance(pools, dict):
        raise ValueError("config must contain a mapping or name_pools mapping")

    config = NameConfig(
        family_names=_required_name_pairs(pools, "family_names"),
        first_syllables=_required_name_pairs(pools, "first_syllables"),
        male_second_syllables=_required_name_pairs(pools, "male_second_syllables"),
        female_second_syllables=_required_name_pairs(pools, "female_second_syllables"),
        gender_neutral_second_syllables=_required_name_pairs(
            pools, "gender_neutral_second_syllables"
        ),
    )
    logger.info(
        "Loaded Korean name config from %s: "
        "family=%s first=%s male=%s female=%s neutral=%s",
        source,
        len(config.family_names),
        len(config.first_syllables),
        len(config.male_second_syllables),
        len(config.female_second_syllables),
        len(config.gender_neutral_second_syllables),
    )
    return config


def _resolve_config_path(path: str | os.PathLike[str] | None) -> Path:
    if path is not None:
        return Path(path)
    env_path = os.environ.get(CONFIG_ENV_VAR)
    if env_path:
        return Path(env_path)
    local_path = Path.cwd() / "config.yaml"
    if local_path.exists():
        return local_path
    return Path(str(DEFAULT_CONFIG_PATH))


def _load_mapping(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"unable to read config {path}: {exc}") from exc

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        parsed = _parse_inline_map_yaml(text)

    if not isinstance(parsed, dict):
        raise ValueError(f"config {path} must contain a mapping")
    return parsed


def _parse_inline_map_yaml(text: str) -> dict[str, Any]:
    root: dict[str, Any] = {}
    current_key: str | None = None
    in_name_pools = False

    for raw_line in text.splitlines():
        line = _strip_comment(raw_line).rstrip()
        if not line.strip():
            continue

        stripped = line.strip()
        indent = len(line) - len(line.lstrip(" "))

        if indent == 0 and stripped == "name_pools:":
            root.setdefault("name_pools", {})
            in_name_pools = True
            current_key = None
            continue

        if stripped.endswith(":") and not stripped.startswith("-"):
            key = stripped[:-1].strip()
            target = root["name_pools"] if in_name_pools and indent > 0 else root
            if indent == 0:
                in_name_pools = False
            target[key] = []
            current_key = key
            continue

        if stripped.startswith("- "):
            if current_key is None:
                raise ValueError("config list item found before a key")
            target = root["name_pools"] if in_name_pools else root
            target.setdefault(current_key, []).append(_parse_inline_pair(stripped[2:]))
            continue

        raise ValueError(f"unsupported config line: {raw_line!r}")

    return root


def _strip_comment(line: str) -> str:
    quote: str | None = None
    for index, char in enumerate(line):
        if char in {'"', "'"}:
            quote = None if quote == char else char
        if char == "#" and quote is None:
            return line[:index]
    return line


def _parse_inline_pair(item: str) -> dict[str, str]:
    item = item.strip()
    if item.startswith("{") and item.endswith("}"):
        item = item[1:-1]

    values: dict[str, str] = {}
    for part in item.split(","):
        key, separator, value = part.partition(":")
        if not separator:
            raise ValueError(f"config pair must use key: value syntax: {item!r}")
        values[key.strip()] = value.strip().strip("\"'")
    return values


def _required_name_pairs(payload: dict[str, Any], key: str) -> tuple[NamePair, ...]:
    raw_pairs = payload.get(key)
    if not isinstance(raw_pairs, list) or not raw_pairs:
        raise ValueError(f"{key} must be a non-empty list")

    pairs: list[NamePair] = []
    for index, raw_pair in enumerate(raw_pairs):
        if not isinstance(raw_pair, Mapping):
            raise ValueError(f"{key}[{index}] must be a mapping")
        typed_pair = cast("Mapping[str, object]", raw_pair)
        en = typed_pair.get("en")
        ko = typed_pair.get("ko")
        if not isinstance(en, str) or not en:
            raise ValueError(f"{key}[{index}].en must be a non-empty string")
        if not isinstance(ko, str) or not ko:
            raise ValueError(f"{key}[{index}].ko must be a non-empty string")
        pairs.append((en, ko))
    return tuple(pairs)


_DEFAULT_CONFIG = load_name_config(DEFAULT_CONFIG_PATH)

FAMILY_NAMES = _DEFAULT_CONFIG.family_names
FIRST_SYLLABLES = _DEFAULT_CONFIG.first_syllables
MALE_SECOND_SYLLABLES = _DEFAULT_CONFIG.male_second_syllables
FEMALE_SECOND_SYLLABLES = _DEFAULT_CONFIG.female_second_syllables
GENDER_NEUTRAL_SECOND_SYLLABLES = _DEFAULT_CONFIG.gender_neutral_second_syllables
