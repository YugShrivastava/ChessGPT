from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from analyze import get_analysis
from dotenv import load_dotenv
from LLM.chat import chat

load_dotenv()

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
    fen: str

@app.post("/analyze")
async def analysis(data: FENModel):
    try:
        res = chat(get_analysis(data.fen))
        return {"status": "success", "message": res}
    except Exception as e:
        return {"status": "error", "message": f"An error occurred while processing the request. Says {e}"}