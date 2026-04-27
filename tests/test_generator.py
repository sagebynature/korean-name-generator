from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from korean_name_generator import (
    FEMALE_SECOND_SYLLABLES,
    FIRST_SYLLABLES,
    GENDER_NEUTRAL_SECOND_SYLLABLES,
    MALE_SECOND_SYLLABLES,
    KoreanNameGenerator,
    load_name_config,
    generate_name,
    generate_names,
)


class KoreanNameGeneratorTests(unittest.TestCase):
    def test_seeded_generation_is_deterministic(self) -> None:
        first = generate_names(5, random_seed=7)
        second = generate_names(5, random_seed=7)
        self.assertEqual(first, second)

    def test_gender_specific_second_syllable_pool(self) -> None:
        male = generate_name("male", random_seed=1)
        female = generate_name("female", random_seed=1)

        male_seconds = {syllable for _, syllable in MALE_SECOND_SYLLABLES}
        female_seconds = {syllable for _, syllable in FEMALE_SECOND_SYLLABLES}

        self.assertEqual(male.gender, "male")
        self.assertEqual(female.gender, "female")
        self.assertIn(male.given_name_ko[-1], male_seconds)
        self.assertIn(female.given_name_ko[-1], female_seconds)


    def test_neutral_generation_uses_neutral_second_syllable_pool(self) -> None:
        name = generate_name("neutral", random_seed=1)
        neutral_seconds = {syllable for _, syllable in GENDER_NEUTRAL_SECOND_SYLLABLES}

        self.assertEqual(name.gender, "neutral")
        self.assertIn(name.given_name_ko[-1], neutral_seconds)

    def test_generated_names_do_not_repeat_given_name_syllables(self) -> None:
        names = generate_names(500, random_seed=23)

        self.assertTrue(
            all(name.given_name_ko[0] != name.given_name_ko[1] for name in names)
        )

    def test_custom_config_yaml_overrides_name_pools(self) -> None:
        config_text = textwrap.dedent(
            """
            name_pools:
              family_names:
                - { en: Test, ko: 테 }
              first_syllables:
                - { en: Ji, ko: 지 }
              male_second_syllables:
                - { en: Ji, ko: 지 }
                - { en: Ho, ko: 호 }
              female_second_syllables:
                - { en: Ji, ko: 지 }
                - { en: Na, ko: 나 }
              gender_neutral_second_syllables:
                - { en: Ji, ko: 지 }
                - { en: Sol, ko: 솔 }
            """
        ).strip()
        with tempfile.TemporaryDirectory() as directory:
            config_path = Path(directory) / "config.yaml"
            config_path.write_text(config_text, encoding="utf-8")

            config = load_name_config(config_path)
            name = generate_name("male", random_seed=1, config_path=config_path)

        self.assertEqual(config.family_names, (("Test", "테"),))
        self.assertEqual(name.family_name_ko, "테")
        self.assertEqual(name.given_name_ko, "지호")

    def test_generated_name_is_two_syllable_given_name_plus_family_name(self) -> None:
        name = generate_name(random_seed=3)
        first_syllables = {syllable for _, syllable in FIRST_SYLLABLES}

        self.assertIn(name.given_name_ko[0], first_syllables)
        self.assertEqual(len(name.given_name_ko), 2)
        self.assertNotEqual(name.given_name_ko[0], name.given_name_ko[1])
        self.assertEqual(name.hangul, f"{name.family_name_ko}{name.given_name_ko}")
        self.assertEqual(name.romanized, f"{name.given_name_en} {name.family_name_en}")

    def test_generator_advances_rng_state(self) -> None:
        generator = KoreanNameGenerator(random_seed=11)
        self.assertNotEqual(generator.generate(), generator.generate())

    def test_rejects_invalid_count_and_empty_pools(self) -> None:
        with self.assertRaisesRegex(ValueError, "count must be at least 1"):
            generate_names(0)

        with self.assertRaisesRegex(ValueError, "family_names must be non-empty"):
            KoreanNameGenerator(family_names=())

    def test_display_orders(self) -> None:
        name = generate_name("female", random_seed=4)
        self.assertEqual(name.display("western"), f"{name.romanized} ({name.hangul})")
        self.assertEqual(
            name.display("korean"),
            f"{name.hangul} ({name.family_name_en} {name.given_name_en})",
        )
        with self.assertRaisesRegex(ValueError, "order must"):
            name.display("invalid")  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
