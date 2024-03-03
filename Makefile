.PHONY: install
setup:
	@poetry lock --no-update
	@poetry install --with coverage --with docs
	@poetry run pre-commit install

.PHONY: lint
lint:
	@poetry run ruff check .

.PHONY: format
format:
	@poetry run ruff format .

.PHONY: type-check
type-check:
	@poetry run mypy .

.PHONY: test
test:
	@poetry run pytest -v tests

.PHONY: coverage
coverage:
	@poetry run coverage run -m pytest
	@poetry run coverage html

.PHONY: docs
docs:
	@poetry run sphinx-build ./docs ./docs/_build

.PHONY: clean
clean:
	@find . -name '__pycache__' -exec rm -rf {} +
	@rm -rf dist/ .coverage docs/_build/ htmlcov/ .mypy_cache/ .pytest_cache/ .ruff_cache/
