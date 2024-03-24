.PHONY: install
setup:
	@poetry install --with dev,docs

.PHONY: lint
lint:
	@poetry run ruff check

.PHONY: format
format:
	@poetry run ruff format

.PHONY: type-check
type-check:
	@poetry run mypy .

.PHONY: test
test:
	@poetry run pytest -v tests/

.PHONY: test-runslow
test-runslow:
	@poetry run pytest -v --runslow tests/

.PHONY: coverage
coverage:
	@poetry run coverage run -m pytest -v --runslow tests/
	@poetry run coverage html

.PHONY: docs
docs:
	@poetry run sphinx-build ./docs ./docs/_build

.PHONY: clean
clean:
	@find . -name '__pycache__' -exec rm -rf {} +
	@rm -rf dist/ .coverage docs/_build/ htmlcov/ .mypy_cache/ .pytest_cache/ .ruff_cache/
