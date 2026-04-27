from __future__ import annotations

import argparse
import csv
import json
import logging
import logging.config
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Literal, TextIO

from .generator import generate_names
from .models import KoreanName, NameOrder

OutputFormat = Literal["plain", "json", "csv"]
logger = logging.getLogger(__name__)


def _default_logging_config_path() -> Path:
    source_layout_path = Path(__file__).resolve().parents[1] / "logging.conf"
    if source_layout_path.is_file():
        return source_layout_path
    return Path(__file__).resolve().with_name("logging.conf")


def init_logging(config_path: str | Path | None = None) -> None:
    logging_config_path = (
        Path(config_path) if config_path is not None else _default_logging_config_path()
    )
    if not logging_config_path.is_file():
        return

    try:
        logging.config.fileConfig(
            str(logging_config_path),
            disable_existing_loggers=False,
        )
        logger.debug("Initialized logging from %s", logging_config_path)
    except ImportError:
        logging.basicConfig(level=logging.INFO)
        logging.getLogger(__name__).warning(
            "Unable to load logging config from %s; using basic logging.",
            logging_config_path,
        )


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
    init_logging()
    parser = build_parser()
    args = parser.parse_args(argv)
    logger.info(
        "Generating %s Korean name(s): gender=%s format=%s order=%s seed=%s config=%s",
        args.count,
        args.gender,
        args.format,
        args.order,
        "set" if args.seed is not None else "random",
        args.config or "default",
    )
    try:
        names = generate_names(
            args.count,
            gender=args.gender,
            random_seed=args.seed,
            config_path=args.config,
        )
    except ValueError as exc:
        logger.error("Unable to generate Korean names: %s", exc)
        parser.error(str(exc))
    emit_names(names, output_format=args.format, order=args.order)
    logger.info("Emitted %s Korean name(s) as %s", len(names), args.format)
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
