.PHONY: up down logs migrate bootstrap smoke smoke-win

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f --tail=200

migrate:
	docker compose exec backend alembic upgrade head

bootstrap:
	curl -s -X POST http://localhost:8000/auth/dev/bootstrap | cat

smoke:
	bash scripts/smoke.sh

smoke-win:
	powershell -ExecutionPolicy Bypass -File scripts/win/smoke.ps1
