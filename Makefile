help:
	@grep '^[^#[:space:]].*:' Makefile | awk -F ":" '{print $$1}'

clean:
	@find . -name "*.pyc" -delete

deps:
	@pip install -r requirements_test.txt

setup: deps

test: clean deps
	@nosetests -s -v
	@flake8 .
