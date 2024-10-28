.PHONY: install
install:
	pip install -r requirements.txt

.PHONY: migrate
migrate:
	python -m picbudget.manage migrate

.PHONY: migrations
migrations:
	python -m picbudget.manage makemigrations

.PHONY: run-server
run-server:
	python -m picbudget.manage runserver

.PHONY: shell
shell:
	python -m picbudget.manage shell

.PHONY: superuser
superuser:
	python -m picbudget.manage createsuperuser

.PHONY: test
test:
	pytest -v -rs -n auto --show-capture=no

.PHONY: up-dependencies-only
up-dependencies-only:
	test -f .env || touch .env
	docker-compose -f docker-compose.dev.yml up --force-recreate db

.PHONY: update
update: install migrate;