from __future__ import annotations

import argparse
import csv
import json
import sys
from collections.abc import Sequence
from typing import Literal, TextIO

from .generator import generate_names
from .models import GenderSelection, KoreanName, NameOrder

OutputFormat = Literal["plain", "json", "csv"]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="korean-name-generator",
        description="Generate romanized and Hangul Korean names.",
    )
    parser.add_argument(
        "-c",
        "--count",
        type=int,
        default=1,
        help="Number of names to generate. Defaults to 1.",
    )
    parser.add_argument(
        "-g",
        "--gender",
        choices=("any", "female", "male", "neutral"),
        default="any",
        help="Given-name pool to use. Defaults to any.",
    )
    parser.add_argument(
        "-s",
        "--seed",
        type=int,
        default=None,
        help="Random seed for deterministic output.",
    )
    parser.add_argument(
        "--config",
        default=None,
        help=(
            "YAML config path. Defaults to $KOREAN_NAME_GENERATOR_CONFIG, "
            "./config.yaml, or the packaged config."
        ),
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=("plain", "json", "csv"),
        default="plain",
        help="Output format. Defaults to plain.",
    )
    parser.add_argument(
        "--order",
        choices=("western", "korean"),
        default="western",
        help="Display order for plain output. Defaults to western.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        names = generate_names(
            args.count,
            gender=args.gender,
            random_seed=args.seed,
            config_path=args.config,
        )
    except ValueError as exc:
        parser.error(str(exc))
    emit_names(names, output_format=args.format, order=args.order)
    return 0


def emit_names(
    names: Sequence[KoreanName],
    *,
    output_format: OutputFormat,
    order: NameOrder,
    stream: TextIO | None = None,
) -> None:
    stream = stream or sys.stdout
    if output_format == "plain":
        for name in names:
            print(f"{name.display(order)} [{name.gender}]", file=stream)
        return

    rows = [name.as_dict() for name in names]
    if output_format == "json":
        json.dump(rows, stream, ensure_ascii=False, indent=2)
        print(file=stream)
        return

    if output_format == "csv":
        fieldnames = [
            "family_name_en",
            "family_name_ko",
            "given_name_en",
            "given_name_ko",
            "gender",
            "romanized",
            "hangul",
        ]
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
        return

    raise ValueError("output_format must be 'plain', 'json', or 'csv'")


if __name__ == "__main__":
    raise SystemExit(main())
