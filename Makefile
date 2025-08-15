.PHONY: dev.web dev.api

# Start Astro web dev server on port 4321
dev.web:
	@npm --prefix apps/web ci
	@npm --prefix apps/web run dev

# Start FastAPI dev server (if scaffolded). Creates a venv in apps/api/.venv
dev.api:
	@if [ -f apps/api/app/main.py ]; then \
		python3 -m venv apps/api/.venv; \
		apps/api/.venv/bin/pip install -r apps/api/requirements.txt; \
		apps/api/.venv/bin/uvicorn app.main:app --reload --port 8000 --app-dir apps/api; \
	else \
		echo "API not scaffolded yet. See docs/sprints/sprint2_api_and_db_shell.md"; \
	fi


