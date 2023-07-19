[![Python CI](https://github.com/Perceptor89/votings/actions/workflows/pyci.yml/badge.svg)](https://github.com/Perceptor89/votings/actions/workflows/pyci.yml)

# VOTINGS
#### Web API for managing simple votings

## Example of website:
[Votings app](http://185.250.205.16:8000) ('admin' for login and password)

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
| media/<file_path> | to get photo of character or report xlsx (you need to be an admin) |
| votings/\<int:pk>/characters/\<int:pk_2>/add_vote/ | adding vote to 'pk' voting and 'pk_2' character |


## Local installation:
You need to clone repository first:
```bash
git clone https://github.com/Perceptor89/votings.git
```

Rename "env_template" to "env" and fill it in.

[Install Docker Engine](https://docs.docker.com/engine/install/ubuntu/)

[Docker-compose](https://docs.docker.com/compose/install/standalone/) helps a lot.

You can run app by docker-compose:

```bash
docker-compose build
docker-compose up -d
```


By default it starts at http://127.0.0.1:8000/

The following tools and technologies were used in the project:

| Tool                                                                     | Description                                                                                                           |
|--------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------|
| [Django](https://www.djangoproject.com/)                                 | "The web framework for perfectionists with deadlines."                                                   |
| [Django REST](https://www.django-rest-framework.org)                                 | "Django REST framework is a powerful and flexible toolkit for building Web APIs."                                                   |
| [Git](https://git-scm.com)                                               | Git is a free and open source distributed version control system designed to handle everything from small to very large projects with speed and efficiency.                                                                       |
| [Celery](https://docs.celeryq.dev/en/stable/index.html)                  | Celery is a simple, flexible, and reliable distributed system to process vast amounts of messages, while providing operations with the tools required to maintain such a system.                                                   |
| [Redis](https://redis.io)                                                | The open source, in-memory data store used by millions of developers as a database, cache, streaming engine, and message broker. |


## Questions and suggestions:
<andreyfominykh@gmail.com>