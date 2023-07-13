[![Python CI](https://github.com/Perceptor89/votings/actions/workflows/pyci.yml/badge.svg)](https://github.com/Perceptor89/votings/actions/workflows/pyci.yml)

# VOTINGS
#### Web API for managing simple votings

## Example of website:
[Votings app](https://185.250.205.16:8000) ('admin' for login and password)

## Available end-points:
|           End-point |     Description             |
|-----------------------|-----------------------|
| admin/ | admin panel |
| votings/ | list of all votings |
| votings/active/ | votings with actual date and no leader by 'max votes' if setted |
| votings/finished/ | finished votings by date or geeting max votes for a member |
| votings/\<int:pk>/ | information about pointed voting |
| votings/winner/ | that's how you get the voting leader |
| votings/\<int:pk>/members/ | to get information about voting members |
| characters/ | list all characters |
| characters/\<int:pk>/ | details of pointed character |
| characters/\<int:pk>/get_img/ | to get character image (you need to be an admin) |
| votings/\<int:pk>/characters/\<int:pk_2>/add_vote/ | adding vote to 'pk' voting and 'pk_2' character |


## Local installation:
You need to clone repository first:
```bash
git clone https://github.com/Perceptor89/votings.git
```

Rename ".env.example" to ".env" and fill it in.

To install dependencies use new virtual environment. Then install dependencies.

```bash
pip install -r requirements.txt
```

You can run postgresql by docker-compose:

```bash
docker-compose up -d
```

Need to migrate:

```bash
./manage.py migrate
```

Start server with:

```bash
./manage.py runserver <host:port>
```

By default it starts at http://127.0.0.1:8000/

The following tools and technologies were used in the project:

| Tool                                                                     | Description                                                                                                           |
|--------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------|
| [django](https://www.djangoproject.com/)                                 | "The web framework for perfectionists with deadlines."                                                   |
| [django REST](https://www.django-rest-framework.org)                                 | "Django REST framework is a powerful and flexible toolkit for building Web APIs."                                                   |
| [git](https://git-scm.com)                                               | Git is a free and open source distributed version control system designed to handle everything from small to very large projects with speed and efficiency.                                                                       |
| [flake](https://flake8.pycqa.org/en/latest/)                             | "Tool For Style Guide Enforcement."                                                                                 |


## Questions and suggestions:
<andreyfominykh@gmail.com>