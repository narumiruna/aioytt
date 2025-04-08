lint:
	uv run ruff check .

type:
	uv run mypy --install-types --non-interactive src

test:
	uv run pytest -v -s --cov=src tests

publish:
	uv build -f wheel
	uv publish

.PHONY: lint test publish
