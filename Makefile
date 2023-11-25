all: lint test

lint:
#	@echo "Running mypy..."
#	@mypy --explicit-package-bases .
	@echo "Running pylint..."
	@pylint MIEMards_backend

test:
	@echo "Running tests with pytest..."
	pytest tests/

.PHONY: lint test
