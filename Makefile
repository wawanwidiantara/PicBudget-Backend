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

.PHONY: startapp
startapp:
	@if [ -z "$(app)" ]; then \
		echo "Error: app name not provided. Usage: make startapp app=<app_name>"; \
	else \
		mkdir -p picbudget/$(app); \
		python -m picbudget.manage startapp $(app) picbudget/$(app); \
	fi

.PHONY: setup
setup:
	@if [ -z "$(app)" ]; then \
		echo "Error: app name not provided. Usage: make setup app=<app_name>"; \
	else \
		echo "Creating required folders for $(app)..."; \
		for folder in models views serializers tests; do \
			mkdir -p picbudget/$(app)/$$folder; \
			touch picbudget/$(app)/$$folder/__init__.py; \
		done; \
		if [ -f picbudget/$(app)/views.py ]; then \
			mv picbudget/$(app)/views.py picbudget/$(app)/views/views.py; \
		fi; \
		if [ -f picbudget/$(app)/tests.py ]; then \
			mv picbudget/$(app)/tests.py picbudget/$(app)/tests/tests.py; \
		fi; \
		if [ -f picbudget/$(app)/models.py ]; then \
			mv picbudget/$(app)/models.py picbudget/$(app)/models/models.py; \
		fi; \
		touch picbudget/$(app)/urls.py; \
	fi

.PHONY: create-app
create-app: startapp setup