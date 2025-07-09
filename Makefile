.DEFAULT_GOAL := install

install:
	@mise install
	@pre-commit install
	@poetry install

check:
	@poetry run tox -e lint
	@pre-commit run --all-files

update:
	@poetry update
	@poetry lock
	@pre-commit autoupdate

test:
	# Running tests
	@poetry run tox
