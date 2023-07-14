# Продуктовый помощник Foodgram - дипломный проект студента 52 когорты Яндекс.Практикум 2022-2023 гг. Заводова А. В.

Адрес сервера: 158.160.0.113, foodgramcool123.ddns.net
Суперюзер (админ): логин - admin@mail.com; пароль - admin

После запуска проекта, он будет доступен по адресу http://127.0.0.1
Как запустить и посмотреть в действии описано ниже.


## Описание проекта Foodgram
«Продуктовый помощник»: Приложение позволяет пользователям публиковать рецепты, подписываться на публикации других авторов и добавлять рецепты в избранное.
Сервис "Список покупок" позволяет создать список продуктов, которые необходимо приобрести для приготовления выбранного блюда в соответствии с рецептом.

## Запуск с использованием CI/CD и Docker

```bash
# В Settings - Secrets and variables создаем переменный с вашими данными
# Это необходимо для работы с CI/CD, DockerHub, GitHub
ALLOWED_HOSTS
DB_ENGINE
DB_HOST
DB_PORT
HOST
MY_LOGIN
MY_PASS
PASSPHRASE
POSTGRES_DB
POSTGRES_PASSWORD
POSTGRES_USER
SECRET_KEY
SSH_KEY
USER
```

Все действия мы будем выполнять в Docker, docker-compose как на локальной машине так и на сервере ВМ Yandex.Cloud.
Предварительно установим на ВМ в облаке необходимые компоненты для работы:

```bash
# username - ваш логин, ip - ip ВМ под управлением Linux Дистрибутива с пакетной базой deb.
ssh username@ip
```

```bash
sudo apt update && sudo apt upgrade -y && sudo apt install curl -y
```

```bash
sudo curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh && sudo rm get-docker.sh
```

```bash
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```

```bash
sudo chmod +x /usr/local/bin/docker-compose
```

```bash
sudo systemctl start docker.service && sudo systemctl enable docker.service
```

Всё, что нам нужно, установлено, далее, создаем папку /infra в домашней директории /home/username/:

```bash
cd ~
```

```bash
mkdir infra
```

Предварительно из папки /backend и /frontend загрузим актуальные данные на DockerHub (на вашем ПК):

Выполняйте команды из корневого каталога проекта.
```bash
docker login -u sleekvortex
```

```bash
cd backend
```

```bash
docker build -t sleekvortex/foodgram_backend:latest .
```

```bash
docker push sleekvortex/foodgram_backend:latest
```

```bash
cd ../frontend
```

```bash
docker build -t sleekvortex/foodgram_frontend:latest .
```

```bash
docker push sleekvortex/foodgram_frontend:latest
```

Перенести файлы docker-compose.yml и default.conf на сервер, из папки infra в текущем репозитории (на вашем ПК).

Выполняйте команды из корневого каталога проекта.
```bash
cd infra
```

```bash
scp docker-compose.yml username@server_ip:/home/username/
```

```bash
scp default.conf username@server_ip:/home/username/
```

Так же, создаем файл .env в директории infra на ВМ:

```bash
touch .env
```

Заполнить в настройках репозитория секреты .env

Пример заполненного файла:

```python
DB_ENGINE='django.db.backends.postgresql'
POSTGRES_DB='foodgram' # Пример имени для БД.
POSTGRES_USER='foodgram' # Пример пользователя БД.
POSTGRES_PASSWORD='foodgram' # Задаем пароль для БД.
DB_HOST='db' # Пример хоста для БД.
DB_PORT='5432' # Пример порта для БД.
SECRET_KEY='secret'  # Пример секретного ключа.
ALLOWED_HOSTS='127.0.0.1, backend' # Вставляем свой IP сервера и домен.
DEBUG = False # Или же True, в случае дебага.
```

На этом настройка закончена, далее в папке infra выполняем команду:

```bash
sudo docker-compose up -d --build
```

Проект запустится на ВМ и будет доступен по указанному вами домену либо IP. 
Завершение настройки на ВМ:

В папке infra выполните команду, что бы собрать контейнеры:

Остановить Контейнеры: 

```bash
sudo docker-compose stop
```

Удалить вместе с volumes:

```bash
# Все данные удалятся!
sudo docker-compose down -v
``` 

Для доступа к контейнеру foodgram_backend и сборки финальной части выполняем следующие команды:

```bash
sudo docker-compose exec foodgram_backend python manage.py makemigrations
```

```bash
sudo docker-compose exec foodgram_backend python manage.py migrate --noinput
```

```bash
sudo docker-compose exec foodgram_backend python manage.py createsuperuser
```

```bash
sudo docker-compose exec foodgram_backend python manage.py collectstatic --no-input
```

Дополнительно можно наполнить DB ингредиентами и тэгами:

```bash
sudo docker-compose exec foodgram_backend python manage.py load_tags
```

```bash
sudo docker-compose exec foodgram_backend python manage.py load_csv
```
Также в проекте предусмотрена команда, которая наполняет БД ингредиентами и тегами одновременно:
```bash
sudo docker-compose exec foodgram_backend python manage.py load_data
```
Если вы получили зеленое сообщение, значит всё прошло успешно!

На этом всё, продуктовый помощник запущен, можно наполнять его рецептами и делится с друзьями!

### Запуск проекта в Docker на localhost

Для Linux ставим Docker как описано выше, для Windows устанавливаем актуальный Docker Desktop.

В папке infra выполняем команду, что бы собрать контейнеры:

```bash
sudo docker-compose up -d --build
```

Остановить контейнеры можно следующей командой: 

```bash
sudo docker-compose stop
```

Удалить вместе с volumes:

Внимание! Будьте осторожны, следующая команда удаляет все volumes, а значит все данные будут утеряны!
```bash
sudo docker-compose down -v
``` 
Если вы не хотите удалять volumes, то выполните ту же команду, но без флага -v
```bash
sudo docker-compose down
``` 

Чтобы получить доступ к контейнерам нужно выполнить следующие команды:

```bash
# Создаем миграции
sudo docker-compose exec foodgram_backend python manage.py makemigrations
```

```bash
# Применяем миграции
sudo docker-compose exec foodgram_backend python manage.py migrate --noinput
```

```bash
# Создаем суперюзера (админа)
sudo docker-compose exec foodgram_backend python manage.py createsuperuser
```

```bash
# Собираем статику проекта
sudo docker-compose exec foodgram_backend python manage.py collectstatic --no-input
```
Также, если у вас есть Докер клиент для компьютера, вы можете через терминал контейнера, отвечающего за бекенд, напрямую писать команды для контейнера. P.S. Всё, что выше, но без sudo.

Дополнительно можно наполнить БД ингредиентами и тегами:

```bash
sudo docker-compose exec foodgram_backend python manage.py load_tags
```

```bash
sudo docker-compose exec foodgram_backend python manage.py load_ingrs
```
Или воспользуйтесь следующей командой, которая объединяет функционал предыдущих двух:
```bash
sudo docker-compose exec foodgram_backend python manage.py load_data
```
### Документация к API доступна после запуска

```url
http://localhost/api/docs/redoc.html
```


Автор: [Заводов Андрей](https://github.com/sleekvortex)
