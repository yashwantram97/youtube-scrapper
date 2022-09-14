# youtube-scrapper
Scrap Youtube data of recently uploaded videos.

# Setup Process
Please install docker and docker-compose add the config details in the below paths below continuing furthur
1) Queue/api/config.py
2) Queue/celery-queue/config.py
3) Scrapper-flask/api/config.py
4) client/src/config.js
5) client/Caddyfile

## For bringing up the queue service
1) Go inside /Queue file
1) docker-compose up -d --build

## For bringing up the Scrapper-flask service
1) Go inside /Scrapper-flask file
1) docker-compose up -d --build

## Basic architecture of youtube scrapper.
https://github.com/yashwantram97/Ineuron-Assignments/blob/main/Youtube%20scrapper%20architecture%20(1).pdf

## Basic features and tech used.
1) Flask - Rest API
2) React - UI
3) Selinium - For scraping data
4) pytube - For downloading video
5) S3 - For storing videos
6) Caddy - For reverse proxy
7) Docker and Docker compose - For containerization
8) EC2 - VM for hosting the application

## Project Demo
https://youtu.be/JGmLGclV0MY
