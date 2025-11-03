.PHONY: migrate fixtures setup run

migrate:
    @echo "Running database migrations..."
    python manage.py makemigrations
    python manage.py migrate

fixtures:
    @echo "Creating test fixtures..."
    python manage.py create_fixtures

setup: migrate fixtures
    @echo ""
    @echo "Setup complete!"
    @echo ""
    @echo "To start the server:"
    @echo "  uvicorn config.asgi:application --reload --port 8000"
    @echo ""
    @echo "Then visit: http://localhost:8000/graphql"
    @echo ""

run:
    uvicorn config.asgi:application --reload --port 8000
