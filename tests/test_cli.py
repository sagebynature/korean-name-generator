from __future__ import annotations

import io
import json
import tempfile
import unittest
from pathlib import Path
from contextlib import redirect_stdout

from korean_name_generator.cli import emit_names, main
from korean_name_generator.generator import generate_names


class CliTests(unittest.TestCase):
    def test_main_emits_seeded_json(self) -> None:
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main(["--count", "2", "--seed", "7", "--format", "json"])

        self.assertEqual(exit_code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertEqual(len(payload), 2)
        self.assertEqual(
            set(payload[0]),
            {
                "family_name_en",
                "family_name_ko",
                "given_name_en",
                "given_name_ko",
                "gender",
                "romanized",
                "hangul",
            },
        )

    def test_plain_output_supports_korean_order(self) -> None:
        names = generate_names(1, gender="male", random_seed=2)
        stream = io.StringIO()

        emit_names(names, output_format="plain", order="korean", stream=stream)

        self.assertIn(names[0].hangul, stream.getvalue())
        self.assertIn("[male]", stream.getvalue())

    def test_csv_output_has_header_and_rows(self) -> None:
        names = generate_names(2, random_seed=5)
        stream = io.StringIO()

        emit_names(names, output_format="csv", order="western", stream=stream)

        lines = stream.getvalue().splitlines()
        self.assertEqual(
            lines[0],
            (
                "family_name_en,family_name_ko,given_name_en,given_name_ko,"
                "gender,romanized,hangul"
            ),
        )
        self.assertEqual(len(lines), 3)

    def test_main_accepts_config_path(self) -> None:
        config_text = """
name_pools:
  family_names:
    - { en: Test, ko: 테 }
  first_syllables:
    - { en: Ji, ko: 지 }
  male_second_syllables:
    - { en: Ho, ko: 호 }
  female_second_syllables:
    - { en: Na, ko: 나 }
  gender_neutral_second_syllables:
    - { en: Sol, ko: 솔 }
"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.yaml"
            path.write_text(config_text, encoding="utf-8")
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        "--count",
                        "1",
                        "--gender",
                        "neutral",
                        "--config",
                        str(path),
                    ]
                )

        self.assertEqual(exit_code, 0)
        self.assertIn("테지솔", stdout.getvalue())

    def test_invalid_count_exits_with_error(self) -> None:
        with self.assertRaises(SystemExit) as raised:
            main(["--count", "0"])

        self.assertEqual(raised.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
