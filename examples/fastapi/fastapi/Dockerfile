FROM python:3.13-slim

WORKDIR /src/

RUN --mount=type=bind,source=requirements.txt,target=/tmp/requirements.txt \
    pip install --requirement /tmp/requirements.txt

COPY . /src/

CMD ["fastapi", "dev", "main.py", "--host", "0.0.0.0"]
