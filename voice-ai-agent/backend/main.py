from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from backend.websocket import router as ws_router
from memory.persistent_memory import init_db
import os

app = FastAPI(title="Voice AI Agent - Clinical Booking")

@app.on_event("startup")
async def on_startup():
    init_db()

app.include_router(ws_router)

@app.get("/")
def read_root():
    html_path = os.path.join(os.path.dirname(__file__), "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000)
