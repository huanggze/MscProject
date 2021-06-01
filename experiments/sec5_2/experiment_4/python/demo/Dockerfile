FROM python:3.9.5-alpine3.13
# FROM python:3.6-slim
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /app
COPY . .
RUN python get-pip.py
RUN python -m pip install Django

EXPOSE 8080
CMD [ "python", "/app/manage.py", "runserver", "0.0.0.0:8080" ]