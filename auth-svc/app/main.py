from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from app.routers import auth_router

app = FastAPI(title="Auth Service")
app.include_router(auth_router)


@app.get("/healthz")
def healthz() -> dict[str, str]:
    """Проверка состояния сервиса"""
    return {"status": "oc"}


# Метрики для Prometheus
Instrumentator().instrument(app).expose(app)
