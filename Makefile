.PHONY: test test-unit test-integration test-fast test-coverage clean

test:
	pytest -v

test-unit:
	pytest -v -m unit

test-api:
	pytest -v -m api

test-voice:
	pytest -v -m voice

test-integration:
	pytest -v -m integration

test-fast:
	pytest -v -m "not slow"

test-coverage:
	pytest --cov=. --cov-report=html --cov-report=term-missing
	@echo "\nCoverage report generated in htmlcov/index.html"

test-watch:
	ptw -- -v

clean:
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

report:
	coverage report
	coverage html
	@echo "\nOpening coverage report..."
	python -m webbrowser htmlcov/index.html