@echo off
IF "%1"=="build" docker-compose build
IF "%1"=="up" docker-compose up -d
IF "%1"=="start" (
    docker-compose build
    docker-compose up -d
)
IF "%1"=="run" docker-compose exec youtube_videos python3 main.py
IF "%1"=="exec" docker-compose exec youtube_videos bash
IF "%1"=="kill" (
    docker-compose stop
    docker-compose rm -f
)
IF "%1"=="build-outside" pip install -r requirements-outside.txt
IF "%1"=="outside" (
    python3 main.py
)
