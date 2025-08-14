.PHONY: dev stop logs psql

DEV?=1

dev:
	docker compose up --build

stop:
	docker compose down

logs:
	docker compose logs -f --tail=100

psql:
	PGPASSWORD=txwell psql -h localhost -U txwell -d txwell