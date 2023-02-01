# Install base Python image
FROM python:3.8-slim-buster

# Set working directory to previously added app directory
WORKDIR /app/

RUN pip install --upgrade pip && \
    pip install argparse==1.1 && \
    pip install requests==2.28.1

COPY ./src/client.py .

# Expose the port
EXPOSE 80

# Run uvicorn server
CMD ["bash"]