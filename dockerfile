FROM python:3.9.18-slim

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get install -y git && apt-get install libgomp1 && apt-get install -y libsndfile1
RUN pip install --no-cache-dir -r requirements.txt 

COPY . .

EXPOSE 8000
RUN chmod +x ./wait-for-it.sh
COPY ./wait-for-it.sh .



