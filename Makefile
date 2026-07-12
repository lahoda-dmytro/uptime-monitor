.PHONY: up down build logs backup restore clean

up:
	docker compose -f compose/docker-compose.yml up -d

down:
	docker compose -f compose/docker-compose.yml down

build:
	docker compose -f compose/docker-compose.yml build

logs:
	docker compose -f compose/docker-compose.yml logs -f

backup:
	bash scripts/backup.sh

restore:
	bash scripts/restore.sh

clean:
	bash scripts/cleanup.sh
