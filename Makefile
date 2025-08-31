build:
	docker-compose build
up:
	docker-compose up -d
start:
	make build && make up
run:
	docker-compose exec -it youtube_videos python3 main.py
exec:
	docker-compose exec -it youtube_videos bash
kill: 
	docker-compose stop && docker-compose rm -f
build-outside:
	pip install -r requirements-outside.txt --break-system-packages
outside:
	python3 main.py