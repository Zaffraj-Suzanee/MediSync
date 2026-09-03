FROM python:3.12-slim

WORKDIR /app

COPY backend/requirements.txt .

RUN python -m pip install --no-cache-dir -r requirements.txt

COPY backend/app.py .

COPY templates ./templates

COPY static ./static

EXPOSE 5000

CMD ["python", "app.py"]