# FastAPI Project - Backend Makefile

# Install dependencies
.PHONY: install
install:
	uv sync

# Activate virtual environment (run this with 'source' command)
# Example: source $(MAKE) activate
.PHONY: activate
activate:
	echo "source .venv/bin/activate"

# Run tests
.PHONY: test
test:
	bash ./scripts/test.sh

# Run tests with specific arguments
# Example: make test-args ARGS="-x"
.PHONY: test-args
test-args:
	poetry run pytest $(ARGS)

# Create a migration
# Example: make migration MESSAGE="Add column last_name to User model"
.PHONY: migration
migration:
	poetry run alembic revision --autogenerate -m "$(MESSAGE)"

# Apply migrations
.PHONY: migrate
migrate:
	poetry run alembic upgrade head


# Run live reload server inside container
.PHONY: server
server:
	fastapi run --reload app/main.py
