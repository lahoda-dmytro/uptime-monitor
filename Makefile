.PHONY: up down build logs backup restore clean restart ps

service ?=

up:
	docker compose -f compose/docker-compose.yml up -d

down:
	docker compose -f compose/docker-compose.yml down

restart:
	docker compose -f compose/docker-compose.yml restart $(service)

ps:
	docker compose -f compose/docker-compose.yml ps

build:
	docker compose -f compose/docker-compose.yml build

logs:
	docker compose -f compose/docker-compose.yml logs -f $(service)

backup:
	bash scripts/backup.sh

restore:
	bash scripts/restore.sh

clean:
	bash scripts/cleanup.sh
