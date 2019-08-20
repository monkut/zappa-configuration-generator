.PHONY: flake8 pylint mypy test coverage check

#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

#################################################################################
# COMMANDS                                                                      #
#################################################################################


## Run flake8 and pydocstyle
flake8:
	pipenv run flake8 --max-line-length 150 --max-complexity 15 --ignore F403,F405,E252 gappa/
	pipenv run pydocstyle --ignore D100,D102,D104,D105,D106,D107,D200,D203,D204,D205,D212,D213,D301,D400,D403,D415 gappa/

## run pylint
pylint:
	pipenv run pylint --rcfile .pylintrc gappa/

mypy:
	export MYPYPATH=./stubs/ mypy
	pipenv run mypy gappa/ --disallow-untyped-defs --ignore-missing-imports --allow-untyped-globals --allow-redefinition

## Run tests (without coverage)
test:
	mkdir test-reports || true
	pipenv run pytest -v --junitxml=test-reports/junit.xml

## Run tests (with coverage)
coverage:
	pipenv run pytest --cov gappa/ --cov-report term-missing

## Define checks to run on PR
check: flake8 pylint mypy



#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help

# Inspired by <http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html>
# sed script explained:
# /^##/:
# 	* save line in hold space
# 	* purge line
# 	* Loop:
# 		* append newline + line to hold space
# 		* go to next line
# 		* if line starts with doc comment, strip comment character off and loop
# 	* remove target prerequisites
# 	* append hold space (+ newline) to line
# 	* replace newline plus comments by `---`
# 	* print line
# Separate expressions are necessary because labels cannot be delimited by
# semicolon; see <http://stackoverflow.com/a/11799865/1968>
.PHONY: help
help:
	@echo "$$(tput bold)Available commands:$$(tput sgr0)"
	@echo
	@sed -n -e "/^## / { \
		h; \
		s/.*//; \
		:doc" \
		-e "H; \
		n; \
		s/^## //; \
		t doc" \
		-e "s/:.*//; \
		G; \
		s/\\n## /---/; \
		s/\\n/ /g; \
		p; \
	}" ${MAKEFILE_LIST} \
	| LC_ALL='C' sort --ignore-case \
	| awk -F '---' \
		-v ncol=$$(tput cols) \
		-v indent=19 \
		-v col_on="$$(tput setaf 6)" \
		-v col_off="$$(tput sgr0)" \
	'{ \
		printf "%s%*s%s ", col_on, -indent, $$1, col_off; \
		n = split($$2, words, " "); \
		line_length = ncol - indent; \
		for (i = 1; i <= n; i++) { \
			line_length -= length(words[i]) + 1; \
			if (line_length <= 0) { \
				line_length = ncol - indent - length(words[i]) - 1; \
				printf "\n%*s ", -indent, " "; \
			} \
			printf "%s ", words[i]; \
		} \
		printf "\n"; \
	}' \
	| more $(shell test $(shell uname) = Darwin && echo '--no-init --raw-control-chars')
