run:
	uv run -m src.main
push:
	git add .
	@if [ -z "$(msg)" ]; then \
		read -p "Enter commit message: " user_msg; \
		git commit -m "$$user_msg"; \
	else \
		git commit -m "$(msg)"; \
	fi
	git push
lint:
	black . -l 120
	ruff check --fix
deps:
	sed -i 's/>/~/g' pyproject.toml
install:
	uv sync
	sudo apt update -y
	sudo apt install -y libusb-1.0-0
octotree:
	uv run -m src.octotree_open3d
space:
	uv run -m src.space_op3d
