from fastapi import FastAPI

app = FastAPI(title="Price Monitor API")

@app.get("/health")
def health():
    return {"status": "ok"}
