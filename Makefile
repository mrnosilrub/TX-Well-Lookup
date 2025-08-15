dev:
	docker compose up --build

stop:
	docker compose down

db.shell:
	docker exec -it txwell_db psql -U postgres -d txwell

api.shell:
	docker exec -it txwell_api /bin/sh

seed.sample:
	docker exec -it txwell_api python /app/data/scripts/seed_sdr_sample.py

.PHONY: dev.web dev.api dev stop db.shell api.shell seed.sample

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

dev:
	docker compose up --build

stop:
	docker compose down -v

db.shell:
	docker compose exec -it db psql -U postgres -d txwl

api.shell:
	docker compose exec -it api /bin/sh


# Generate and seed SDR sample into DB via API container
seed.sample:
	python3 data/scripts/generate_sdr_sample.py data/fixtures/sdr_sample.csv
	docker compose exec -T -e DATABASE_URL="postgresql://postgres:postgres@db:5432/txwl" api \
		python /app/data/scripts/seed_sdr_sample.py /app/data/fixtures/sdr_sample.csv || \
		echo "Start docker compose (make dev) to ensure DB is available, then retry."


