## Домашнее задание по развертыванию сервиса с моделью машинного обучения в K8S

### Задачи:
- Напишите на python REST API для вашей модели.
- Настройте на github actions CI/CD с тестами, сборкой docker и его публикацией в registry.
- Создайте k8s манифест для запуска вашего сервиса.
- Создайте в YC k8s кластер из 3-х узлов.
- Запустите ваш сервис в k8s и проведите тестирование через публичный API.
  
### Локальное тестирование приложения

1) Создаем рабочую директорию и клонируем репозиторий

    cd ~
    mkdir work && cd work && mkdir MLOps_plus && cd MLOps_plus && git clone https://github.com/fds-git/mlops_k8s_homework

2) Запускаем сервер

    uvicorn src.server:app --host 0.0.0.0 --port 8080 --reload
    где
    src.server - server.py
    app - FasAPI application name in server.py
    в боевом режиме можно задавать значение ключа --workers, но не рекомендуется так делать при развертывании через контейнеры (надо масштабировать контейнеры, один контейнер - один сервис)

3) Тестируем работу через клинента

    cd ~/work/MLOps_plus/mlops_k8s_homework
    python3 src/client.py -host 127.0.0.1 -port 8080

4) Проверяем работу pytest

    pytest

5) Проверяем скрипт обучения модели (после обучения новой модели pytest может быть не пройден, если новая модель будет отличаться от заложенной в проекте)

    python3 src/train.py -d data -m models

### Тестирование обучения в контейнере (для тестирования окружения)

1) Собираем образ обучениия модели

    docker build -t model_fit -f docker/fit/Dockerfile .

2) Запускаем контейнер и обучение

    docker run --name model_fit -it --rm model_fit
    python3 src/train.py -d data -m models

3) Проверяем результат

    ls -la models/

### Тестирование приложения в контейнере (все элементы будут протестированы в том же окружении, в котором будет запущен CI/CD)

1) Собираем образ инференса модели

    docker build -t fastapi_inference -f docker/deploy/Dockerfile .
    
2) Запускаем контейнер инференса для тестирования

    docker run --name fastapi_inference -it -d --rm -p 80:80 fastapi_inference

или в режиме разработки

    docker run --name fastapi_inference -it --rm -p 80:80 -v ~/work/MLOps_plus/mlops_k8s_homework/:/workdir/ fastapi_inference

3) Зайти в контейнер командой

    docker exec -it fastapi_inference bash

4) Запустить автотесты из контейнера

    pytest

5) Запустить клиента из контейнера

    python3 src/client.py -host 127.0.0.1 -port 80

6) Запустить клиента на локальном компе

    python3 src/client.py -host 127.0.0.1 -port 80

### Отправка образа в Docker Hub

1) Залогиниться (ввести пароль или токен)

    docker login -u dmitry030309

2) Создать репозиторий на Docker Hub (fastapi_inference)

3) Сделать ссылку на необходимый образ с изменением его названия

    docker tag fastapi_inference:latest dmitry030309/fastapi_inference:latest

4) Отправить образ в репозиторий

5) Для автоматизированного CD не забыть добавить секреты в GitHub для доступа к DockerHub

### Проверка CI/CD

1) Делаем коммит в репозиторий

    