from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="Task Service")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "oc"}


# Метрики для Prometheus
Instrumentator().instrument(app).expose(app)
