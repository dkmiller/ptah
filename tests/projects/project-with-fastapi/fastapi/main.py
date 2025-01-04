from fastapi import FastAPI, Request

app = FastAPI()


@app.get("/probe")
def probe(request: Request):
    return {"headers": request.headers}
