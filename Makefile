.PHONY: install-hooks lint typecheck test check

install-hooks:
	uv run pre-commit install --install-hooks --hook-type pre-commit --hook-type commit-msg

lint:
	uv run ruff check .
	uv run ruff format --check .

typecheck:
	uv run ty check src/korean_name_generator/*.py tests/*.py

test: typecheck
	uv run python -m pytest

check: lint test