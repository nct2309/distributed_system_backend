start:
	poetry run uvicorn app.main:app --reload

generate-migration: m
	poetry run alembic revision --autogenerate -m "$(m)"
#make generate-migration m="your migration message"
migrate:
	poetry run alembic upgrade head

rollback:
	poetry run alembic downgrade -1