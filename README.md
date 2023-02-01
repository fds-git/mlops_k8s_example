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

    docker push dmitry030309/fastapi_inference:latest

5) Для автоматизированного CD не забыть добавить секреты в GitHub для доступа к DockerHub

### Проверка CI/CD

1) Делаем push в репозиторий

2) В GitHub Actions видим успешные workflows

3) В DockerHub видим обновленную версию контейнера

4) Не забываем, что в процессе CI/CD модель будет переобучена и будет отлична от той, что лежит в репозитории

### Разворачиваем кластер K8S в YC с названием mykuber, создаем группу узлов с названием mynodes

1) Пользуемся инструкцией для развертывания и настройки кластера https://cloud.yandex.ru/docs/managed-kubernetes/quickstart

- необходимо установить и настроить утилиту yc (https://cloud.yandex.ru/docs/cli/quickstart#install)
- необходимо установить и настроить утилиту kubectl (https://kubernetes.io/ru/docs/tasks/tools/install-kubectl/)

- CIDR кластера 192.168.0.0/23
- CIDR сервисов 192.168.8.0/23
- Маска подсети узлов 27
- Макс. кол-во узлов 8
- Макс. кол-во подов в узле 16
  
2) Обновляем конфигурационный файл (~/.kube/config)

    yc managed-kubernetes cluster get-credentials mykuber --external --force

3) Проверяем, что утилита kubectl связалась с кластером mykuber

    kubectl config view

Если узлы не будут долго создаваться (более 15 минут), возможно, превышен лимит по ресурсам.
Надо проверять, что не превышено максимальное количество подов (задается при создании кластера путем применения маски подсети)

### Запускаем сервис

Если будут ошибки, иногда помогает перезапуск командной оболочки.

1) Запускаем манифесты на кластере

    cd ~/work/MLOps_plus/mlops_k8s_homework
    kubectl apply -f k8s/deployment.yml
    kubectl apply -f k8s/service.yml

2) Проверяем что все запустилось

    kubectl get deployments
    kubectl get service

3) Зайдем в контейнер и проверим что все работает

    Проверка работоспособности внутри пода
    После этой команды запомним NAME и IP
    kubectl get pod -o wide
    kubectl exec --stdin --tty "NAME" -- /bin/bash
    python3 src/client.py -host 127.0.0.1 -port 80
    или
    python3 src/client.py -host "IP" -port 80

### Проверка работоспособности через развертывание клиента в k8s

1) Создаем образ клиента и загружаем на DockerHub

    cd ~/work/MLOps_plus/mlops_k8s_homework
    docker build -t model_client -f docker/client/Dockerfile .
    docker tag model_client:latest dmitry030309/model_client:latest
    docker push dmitry030309/model_client:latest

2) Запускаем под клиента

    kubectl apply -f k8s/pod_client.yml

3) Запоминаем IP сервиса model-service, который связан с подами сервера ("IP")

    kubectl get services

4) Заходим на POD клиента и тестируем доступность сервера

    kubectl exec -it pods/client -- bash
    python3 client.py -host "IP" -port 80

### Проверка работоспособности через проброс портов сервиса

1) Пробрасываем порт сервиса на локальный компьютер

    kubectl port-forward svc/model-service 8080:80

2) Тестируем через клиента

    cd ~/work/MLOps_plus/mlops_k8s_homework
    python3 src/client.py -host 127.0.0.1 -port 8080

### Проверка работоспособности через внешний IP

1) Запускаем сервис с внешним IP-адресом

    kubectl apply -f k8s/load-balancer.yaml

2) Находим EXTERNAL-IP для model-service-out

    kubectl get services

3) Тестируем приложение

    python3 src/client.py -host 51.250.83.48 -port 80