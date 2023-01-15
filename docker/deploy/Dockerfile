# Install base Python image
FROM python:3.8-slim-buster

# Set working directory to previously added app directory
WORKDIR /app/

COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# Install dependencies
RUN pip install -r requirements.txt

# Модель можно обучить на этапе сборки, если 
# она не была обучена ранее
#RUN python train.py

# Expose the port uvicorn is running on
EXPOSE 80

# Set environment variable
ENV MODEL=./models/serialized_model.sav

# Run uvicorn server
CMD ["uvicorn", "src.server:app", "--reload", "--host", "0.0.0.0", "--port", "80"]