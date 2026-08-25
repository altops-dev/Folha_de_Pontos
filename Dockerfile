FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py sheets_handler.py ./
COPY templates ./templates
COPY static ./static

ENV FLASK_DEBUG=false
ENV PORT=5000

EXPOSE 5000

CMD ["python", "app.py"]
