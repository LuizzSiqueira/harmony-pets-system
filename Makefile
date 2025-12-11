PYTHON=python
PIP=$(PYTHON) -m pip

.PHONY: install test coverage clean

install:
	$(PIP) install --upgrade pip
	@if [ -f requirements-dev.txt ]; then \
		$(PIP) install -r requirements-dev.txt; \
	else \
		echo "requirements-dev.txt não encontrado."; exit 1; \
	fi

test:
	cd harmony_pets && $(PYTHON) manage.py test core.tests

coverage:
	./scripts/run_tests_coverage.sh

clean:
	rm -rf .pytest_cache .coverage htmlcov coverage.xml
