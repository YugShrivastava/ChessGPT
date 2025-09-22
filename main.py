from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from analyze import get_analysis

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:6000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FENModel(BaseModel):
    fen_before: str
    fen_after: str

@app.post("/analyze")
async def analysis(data: FENModel, request: Request):
    try:
        get_analysis(data.fen_before, data.fen_after)
        return {"status": "success", "fen": data.fen}
    except Exception as e:
        return {"status": "error", "message": f"An error occurred while processing the request. Says {e}"}