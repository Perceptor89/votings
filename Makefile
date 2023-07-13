test_votings:
	API_project/manage.py test votings

lint:
	flake8 API_project/votings

coverage:
	coverage run API_project/manage.py test votings
	coverage xml

run:
	API_project/manage.py runserver