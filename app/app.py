from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

@app.get("/", tags=["ROOT"])
async def root() ->dict:
  return {"name": "Dean"}