from fastapi import FastAPI


app = FastAPI(title="TX Well Lookup API", version="0.1.0")


@app.get("/health")
def health() -> dict:
    return {"ok": True}


