all: lint test

lint:
	@echo "Running mypy..."
	mypy --explicit-package-bases .

test:
	@echo "Running tests with pytest..."
	pytest tests/

.PHONY: lint test
