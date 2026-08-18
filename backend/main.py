from fastapi import FastAPI

app = FastAPI(
    title="CareerLens API",
    description="AI-powered resume and job match intelligence platform",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {"status": "ok"}