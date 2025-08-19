build:
	docker-compose build
up:
	docker-compose up -d
start:
	make build && make up
run:
	docker-compose exec -it yotube_videos python3 main.py
exec:
	docker-compose exec -it yotube_videos bash
kill: 
	docker-compose stop && docker-compose rm -f
outside:
	python3 main.py