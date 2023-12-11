FROM python:3.10-slim-buster
WORKDIR /app
COPY requirements.txt /app/
RUN pip install -r requirements.txt
COPY . /app/
CMD ["scrapy", "crawl", "your_spider_name"]