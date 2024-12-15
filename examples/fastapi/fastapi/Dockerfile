FROM python:3.13-slim

WORKDIR /src/

# TODO:
# RUN --mount=type=bind,source=requirements.txt,target=/tmp/requirements.txt \
#     pip install --requirement /tmp/requirements.txt

COPY requirements.txt /src/
RUN pip install -r requirements.txt

COPY . /src/

CMD ["fastapi", "dev", "main.py", "--host", "0.0.0.0"]
