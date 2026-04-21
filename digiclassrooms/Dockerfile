FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install gunicorn

COPY . .

EXPOSE 8000

CMD ["gunicorn", "digiclassrooms.wsgi", "--bind", "0.0.0.0:8000"]