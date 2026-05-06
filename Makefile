.PHONY: setup digest bot

setup:
	uv sync

digest:
	uv run python src/run_once.py

bot:
	uv run python src/main.py
