from fastapi import FastAPI

from routes.routes import reports_router

app = FastAPI(title="EduFlex Reports API", version="1.0.0")
app.include_router(reports_router, prefix="/api/reports", tags=["Reportes"])


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}
