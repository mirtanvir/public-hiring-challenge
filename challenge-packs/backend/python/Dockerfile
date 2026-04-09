FROM python:3.11

WORKDIR /app

COPY python/requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY python/app.py /app/python/app.py
COPY sql /app/sql
COPY data/visible /app/data/visible

EXPOSE 8080

CMD ["python", "/app/python/app.py"]
