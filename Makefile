test_votings:
	python manage.py test votings

lint:
	flake8 votings

coverage:
	coverage run manage.py test votings
	coverage xml

run:
	python manage.py runserver

migrate:
	python manage.py makemigrations
	python manage.py migrate

docker-desktop:
	systemctl --user start docker-desktop

up:
	docker-compose up -d

down:	
	docker-compose down

celery:
	python -m celery -A API_project worker -l info