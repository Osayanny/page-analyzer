PORT ?= 8000

install:
	uv sync

lint:
	uv run ruff check page_analyzer

dev:
	uv run flask --app page_analyzer:app --debug run

start:
	uv run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

build:
	./build.sh