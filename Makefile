help:
	@grep '^[^#[:space:]].*:' Makefile | awk -F ":" '{print $$1}'

clean:
	@find . -name "*.pyc" -delete

deps:
	@pip install -r requirements.txt
	@pip install -r requirements_test.txt

setup: deps

violations:
	@echo "Verificando PEP8 compliance do código"
	@-pep8 jsonschema --ignore=E501,E126,E127

test: clean
	@nosetests
