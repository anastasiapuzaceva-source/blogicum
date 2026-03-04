# Блогикум — социальная сеть на Django

**Блогикум** — проект социальной сети с публикациями, авторизацией пользователей и системой комментариев.

## Возможности проекта

* регистрация и авторизация пользователей;
* создание, редактирование и удаление публикаций;
* просмотр ленты постов;
* добавление комментариев;
* административная панель для управления контентом;
* разделение проекта на Django-приложения.

## Использованные технологии

* Python
* Django
* HTML
* CSS
* Bootstrap
* Django Templates

## Запуск проекта локально

1. Клонировать репозиторий:

```
git clone git@github.com:anastasiapuzaceva-source/blogicum.git
```

2. Перейти в папку проекта:

```
cd blogicum
```

3. Создать и активировать виртуальное окружение:

```
python -m venv venv
source venv/bin/activate  # Linux / macOS
venv\\Scripts\\activate     # Windows
```

4. Установить зависимости:

```
pip install -r requirements.txt
```

5. Применить миграции:

```
python manage.py migrate
```

6. Запустить сервер:

```
python manage.py runserver
```

Проект будет доступен по адресу:

```
http://127.0.0.1:8000/
```

## Автор

GitHub: [Anastasiia Puzacheva](https://github.com/anastasiapuzaceva-source)
