all: lint test

lint:
	@echo "Running mypy..."
	mypy .

test:
	@echo "Running tests with pytest..."
	pytest tests/

.PHONY: lint test
