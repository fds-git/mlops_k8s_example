# Install base Python image
FROM python:3.8-slim-buster

# Set working directory to previously added app directory
WORKDIR /app/

COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd --user-group --shell /bin/false user
RUN chown -R user models  
USER user

# Так модель будет обучена на этапе сборки образа и зашита в него
#RUN python3 src/train.py -d data -m models

# Так при создании контейнера будет запущено обучение, после которого контейнер остановится
#CMD ["python3", "src/train.py", "-d", "data", "-m", "models"]

# Так дадим пользователю возможность самостоятельно заходить в контейнер и запускать обучение
ENTRYPOINT ["bash"]