# Проект по развертыванию сервиса с моделью машинного обучения в K8S

Для запуска сервера (на компе или в контейнере вручную):
uvicorn server:app --host 0.0.0.0 --port 80 --reload
где
server - server.py
app - FasAPI application name in server.py
в боевом режиме надо задавать значение ключа --workers

0) Локально запустить обучение командой

python3 train.py -d ../data -m ../models

1) Собираем образ
docker build -t fastapi_inference -f Dockerfile .

2) Запускаем контейнер для локального тестирования

docker run --name fastapi_inference -d -it --rm -p 80:80 fastapi_inference

или в режиме разработки

docker run --name fastapi_inference -d -it --rm -p 80:80 -v /home/dima/work/MLOps/kubernetes_example/:/workdir/ fastapi_inference

3) Зайти в контейнер можно командой

docker exec -it fastapi_inference bash

4) Протестировать работу клиента в связке с сервером (на компе или в контейнере вручную, необходим запуск сервера)

python3 client.py -host 127.0.0.1 -port 80

5) Запустить автотесты (в директории, где есть test_*.py файлы)

pytest

6) В контейнере запустить переобучение командой

python3 train.py (значение ключей по умолчанию предполагает горизонтальное размещение исходных данных и будущей модели, так как Docker не сохраняет стректуру каталогов при команде COPY)

