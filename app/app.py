from fastapi import FastAPI, Request, HTTPException
from dotenv import load_dotenv
from fastapi.responses import RedirectResponse
import os

load_dotenv()

app = FastAPI()

@app.get("/", tags=["ROOT"])
async def root(request: Request) -> RedirectResponse:
  return RedirectResponse(request.url_for("github_login"))


@app.get("/login", tags=["LOGIN"])
async def github_login(request: Request) -> RedirectResponse:
  client_id = os.getenv("GITHUB_CLIENT_ID")
  redirect_uri = request.url_for("authorize")
  return RedirectResponse(f"https://github.com/login/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}")


@app.get("/authorize")
async def authorize(code: str):
  print(code)