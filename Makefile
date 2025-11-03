.PHONY: clean-db migrate fixtures setup run test

clean-db: ; @echo "Removing local SQLite database..."; \
	  rm -f db.sqlite3

migrate: ; @echo "Running database migrations..."; \
	  python manage.py makemigrations users deployedapps; \
	  python manage.py migrate

fixtures: ; @echo "Creating test fixtures..."; \
	   python manage.py create_fixtures

setup: clean-db migrate fixtures ; @printf "\nSetup complete!\n\n"; \
			 printf "To start the server:\n"; \
			 printf "  python -m uvicorn config.asgi:application --reload --port 8000\n\n"; \
			 printf "Then visit: http://localhost:8000/graphql\n\n"

run: ; python -m uvicorn config.asgi:application --reload --port 8000

test: ; pytest -q
