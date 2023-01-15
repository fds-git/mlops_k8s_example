# Проект по развертыванию сервиса с моделью машинного обучения в K8S

Для запуска сервера (на компе или в контейнере вручную):
uvicorn src.server:app --host 0.0.0.0 --port 80 --reload
где
src.server - server.py
app - FasAPI application name in server.py
в боевом режиме надо задавать значение ключа --workers

1) Локально запустить обучение (полученная модель в дальнейшем будет зашита в образ)
python3 src/train.py -d data -m models

2) Собираем образ обучениия модели (для тестирования окружения)
docker build -t model_fit -f docker/fit/Dockerfile .

3) Собираем образ инференса модели 
docker build -t fastapi_inference -f docker/deploy/Dockerfile .

4) Запускаем контейнер обучения для тестирования
docker run --name model_fit -d -it --rm model_fit
docker exec -it model_fit bash
python3 src/train.py -d data -m models

5) Запускаем контейнер инференса для тестирования
docker run --name fastapi_inference -d -it --rm -p 80:80 fastapi_inference

или в режиме разработки

docker run --name fastapi_inference -d -it --rm -p 80:80 -v /home/dima/work/MLOps/kubernetes_example/:/workdir/ fastapi_inference

6) Зайти в контейнер можно командой

docker exec -it fastapi_inference bash

7) Протестировать работу клиента в связке с сервером (на локальном компе и в контейнере вручную, необходим запуск сервера)

python3 src/client.py -host 127.0.0.1 -port 80

8) Запустить автотесты как в директоририи проекта на локальном компе, так и в контейнере (WORKDIR). Результат должен быть одинаковый.

pytest

9) В контейнере запустить переобучение командой

python3 src/train.py -d data -m models

10)  Для отправки образа в Docker Hub:
- docker login -u dmitry030309
- ввести пароль или токен
- создать репозиторий на Docker Hub
- docker tag fastapi_inference:latest dmitry030309/fastapi_inference:latest
- docker push dmitry030309/fastapi_inference:latest