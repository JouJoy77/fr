### Установка и запуск

- Загрузить на локаль репозиторий с gitlab/github с помощью git clone
- Создать файл .env с переменными окружения
- Выполнить команду docker-compose up --build -d

Другой способ (не через Docker)

- Загрузить на локаль репозиторий с gitlab/github с помощью git clone
- Создать и активировать виртуальную среду командами python -m venv .venv , затем .venv/Scripts/Activate.ps1
- Если не открыта папка с проектом, то перейти в нее. Скорее всего будет достаточно cd ./fr
- Выполнить pip install -r requirements.txt
- Запуск через python manage.py runserver

### Администрирование

- Django Admin: http://localhost:8000/admin/
- Celery (через Flower): http://localhost:5555/

### API Сервиса (Описание)

- http://localhost:8000/api/schema/
- http://localhost:8000/api/schema/redoc/
- http://localhost:8000/api/schema/swagger-ui/

### API Сервиса (Использование)

- http://localhost:8000/api/<path>

### Использованные технологии

Python, Django, DRF, Redis, Celery, SQLite, Git, Docker

### Задание

Задача
Необходимо разработать сервис управления рассылками API администрирования и получения статистики.

### Выполненные дополнительные задания

- 3 задание
- 5 задание
- 8 задание
- 11 задание
- 12 задание
