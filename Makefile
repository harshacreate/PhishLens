.PHONY: setup run test evaluate docker
setup:
	python3 -m pip install -r requirements.txt
run:
	python3 -m phishlens.app
test:
	python3 -m pytest -q
evaluate:
	python3 -m phishlens.evaluate
docker:
	docker compose up --build -d
