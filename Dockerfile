FROM ghcr.io/astral-sh/uv:python3.12-alpine AS base

WORKDIR /app

COPY . .
RUN uv pip install --system -r requirements.txt

EXPOSE 8000

#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
CMD uvicorn voxpop_project.asgi:application --host 0.0.0.0 --port 8000 --workers 3 --lifespan off --app-dir /app/
