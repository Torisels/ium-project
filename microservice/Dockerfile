FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt


WORKDIR  /app
COPY src src

WORKDIR /app/src
ENV PYTHONPATH "${PYTHONPATH}:/app/src"

EXPOSE 80
ENV MS_RUNNING_REMOTE "True"
CMD [ "uvicorn", "--host" , "0.0.0.0", "--port", "80","recommendation_service.app:app"]