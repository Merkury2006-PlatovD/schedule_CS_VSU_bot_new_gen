FROM python:3.12-alpine
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install -r requirements.txt
WORKDIR /app
COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.main_controller:app", "--host", "0.0.0.0"]