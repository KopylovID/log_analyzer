.PHONY: test # Помечаем папку test как фиктивную

test:
	uv run pytest -

ruff:
    # --exit-non-zero-on-fix выходит с отрицательным результатом
	uv run ruff check --output-format=github --exit-non-zero-on-fix .

