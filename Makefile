include ./.env

SHELL := /bin/bash
PYTHON := python

help: ## Show this help
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# =================================================================================================
# FastAPI
# =================================================================================================

.PHONY: run-local
run-local: ## Run Django server local
	cd ./app && uvicorn main:app --reload
