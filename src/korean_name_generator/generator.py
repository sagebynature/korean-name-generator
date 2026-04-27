from __future__ import annotations

import random
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path

from .data import (
    FAMILY_NAMES,
    FEMALE_SECOND_SYLLABLES,
    FIRST_SYLLABLES,
    GENDER_NEUTRAL_SECOND_SYLLABLES,
    MALE_SECOND_SYLLABLES,
    load_name_config,
)
from .models import Gender, GenderSelection, KoreanName, NamePair

_GENDERS: tuple[Gender, Gender, Gender] = ("female", "male", "neutral")


@dataclass(slots=True)
class KoreanNameGenerator:
    """Generate Korean names from configurable family and syllable pools."""

    random_seed: int | None = None
    family_names: Sequence[NamePair] = FAMILY_NAMES
    first_syllables: Sequence[NamePair] = FIRST_SYLLABLES
    male_second_syllables: Sequence[NamePair] = MALE_SECOND_SYLLABLES
    female_second_syllables: Sequence[NamePair] = FEMALE_SECOND_SYLLABLES
    gender_neutral_second_syllables: Sequence[NamePair] = (
        GENDER_NEUTRAL_SECOND_SYLLABLES
    )
    _rng: random.Random = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._validate_pools()
        self._rng = random.Random(self.random_seed)

    @classmethod
    def from_config(
        cls,
        path: str | Path | None = None,
        *,
        random_seed: int | None = None,
    ) -> KoreanNameGenerator:
        """Create a generator from packaged, local, env, or explicit YAML config."""

        config = load_name_config(path)
        return cls(
            random_seed=random_seed,
            family_names=config.family_names,
            first_syllables=config.first_syllables,
            male_second_syllables=config.male_second_syllables,
            female_second_syllables=config.female_second_syllables,
            gender_neutral_second_syllables=config.gender_neutral_second_syllables,
        )

    def generate(self, gender: GenderSelection = "any") -> KoreanName:
        """Generate one name."""

        resolved_gender = self._resolve_gender(gender)
        family_en, family_ko = self._rng.choice(tuple(self.family_names))
        first_en, first_ko = self._rng.choice(tuple(self.first_syllables))
        second_en, second_ko = self._sample_second_syllable(
            resolved_gender,
            first_ko=first_ko,
        )
        return KoreanName(
            family_name_en=family_en,
            family_name_ko=family_ko,
            given_name_en=f"{first_en}{second_en}",
            given_name_ko=f"{first_ko}{second_ko}",
            gender=resolved_gender,
        )

    def generate_many(
        self, count: int, gender: GenderSelection = "any"
    ) -> list[KoreanName]:
        """Generate `count` names using the generator's current RNG state."""

        if count < 1:
            raise ValueError("count must be at least 1")
        return [self.generate(gender=gender) for _ in range(count)]

    def _resolve_gender(self, gender: GenderSelection) -> Gender:
        if gender == "any":
            return self._rng.choice(_GENDERS)
        if gender in _GENDERS:
            return gender
        raise ValueError("gender must be 'any', 'female', 'male', or 'neutral'")

    def _sample_second_syllable(
        self,
        gender: Gender,
        *,
        first_ko: str,
    ) -> NamePair:
        pool = self._second_syllable_pool(gender)
        candidates = tuple(pair for pair in pool if pair[1] != first_ko)
        if not candidates:
            raise ValueError(
                "second-syllable pool must contain a value that differs from "
                f"the selected first syllable {first_ko!r}"
            )
        return self._rng.choice(candidates)

    def _second_syllable_pool(self, gender: Gender) -> Sequence[NamePair]:
        if gender == "male":
            return self.male_second_syllables
        if gender == "female":
            return self.female_second_syllables
        return self.gender_neutral_second_syllables

    def _validate_pools(self) -> None:
        pools = {
            "family_names": self.family_names,
            "first_syllables": self.first_syllables,
            "male_second_syllables": self.male_second_syllables,
            "female_second_syllables": self.female_second_syllables,
            "gender_neutral_second_syllables": self.gender_neutral_second_syllables,
        }
        for name, pool in pools.items():
            if not pool:
                raise ValueError(f"{name} must be non-empty")
            for index, pair in enumerate(pool):
                if len(pair) != 2 or not pair[0] or not pair[1]:
                    raise ValueError(
                        f"{name}[{index}] must contain non-empty en/ko values"
                    )


def generate_name(
    gender: GenderSelection = "any",
    *,
    random_seed: int | None = None,
    config_path: str | Path | None = None,
) -> KoreanName:
    """Generate one name with a fresh generator."""

    generator = KoreanNameGenerator.from_config(config_path, random_seed=random_seed)
    return generator.generate(gender=gender)


def generate_names(
    count: int,
    gender: GenderSelection = "any",
    *,
    random_seed: int | None = None,
    config_path: str | Path | None = None,
) -> list[KoreanName]:
    """Generate multiple names with a fresh generator."""

    generator = KoreanNameGenerator.from_config(config_path, random_seed=random_seed)
    return generator.generate_many(count, gender=gender)
