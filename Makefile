BUMP := 'patch'

help:
	@grep '^[^#[:space:]].*:' Makefile | awk -F ":" '{print $$1}'

clean:
	@find . -name "*.pyc" -delete

deps:
	@pip install -r requirements_test.txt

setup: deps

patch:
	@$(eval BUMP := 'patch')

minor:
	@$(eval BUMP := 'minor')

major:
	@$(eval BUMP := 'major')

bump:
	@bumpversion ${BUMP}

release:
	@echo 'PyPI server: '; read PYPI_SERVER; \
		python setup.py -q sdist upload -r $$PYPI_SERVER
	@git push
	@git push --tags

coverage_html:
	@coverage html --include='pluct/**'
	@echo 'Check "htmlcov/index.html" for coverage report.'

test: clean
	@nosetests -s -v --with-coverage --cover-package=pluct --cover-branches --cover-erase
	@flake8 pluct/
