![workflow](https://github.com/IgorKalchenko/foodgram-project-react/actions/workflows/main.yml/badge.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# О ПРОЕКТЕ

Cайт Foodgram, «Продуктовый помощник». На этом сервисе пользователи могут:
* публиковать рецепты,
* подписываться на публикации других пользователей,
* добавлять понравившиеся рецепты в список «Избранное»,
* скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд. 

Проект доступен по [адресу](http://51.250.110.182/)

# ТЕХНОЛОГИИ

Backend:

* Python
* Django
* Djnago REST framework
* Docker/Docker-compose
* Nginx
* Gunicorn

Frontend:

* JavaScript
* React

# ОПИСАНИЕ КОМАНД ДЛЯ ЗАПУСКА ПРИЛОЖЕНИЯ


Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/IgorKalchenko/yamdb_final.git
```

```
cd yamdb_final
```
Перейти в директорию 'infra':

```
cd infra
```

Соберать контейнеры:

```
docker-compose up -d
```

Выполнить миграции

```
docker-compose exec web python manage.py migrate
```

Создать суперпользователя:

```
docker-compose exec web python manage.py createsuperuser
```

Собрать статику:

```
docker-compose exec web python manage.py collectstatic --no-input
```

Для загрузки тестовой базы данных выполните команду и подтвердите отчистку базы данных:

```
docker-compose exec web python manage.py import_ingredients
```

```
Y
```

## Автор

[Игорь Кальченко](https://github.com/IgorKalchenko)
