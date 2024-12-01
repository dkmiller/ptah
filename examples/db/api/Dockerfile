FROM python:3.13-slim

RUN apt-get update && apt-get install -y build-essential libmariadb-dev pkg-config

WORKDIR /src/

COPY requirements.txt /src/
RUN pip install -r requirements.txt

COPY . /src/

CMD ["fastapi", "dev", "main.py", "--host", "0.0.0.0"]
