FROM python:3.13-slim

WORKDIR /src/

COPY requirements.txt /src/
RUN pip install -r requirements.txt

COPY . /src/

CMD ["fastapi", "dev", "main.py", "--host", "0.0.0.0"]
