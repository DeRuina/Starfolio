from fastapi import FastAPI, Request, HTTPException, Cookie
from dotenv import load_dotenv
from fastapi.responses import RedirectResponse
import os
import binascii
import httpx


load_dotenv()  # Load environment variables from .env file for configuration


app = FastAPI() # FastAPI instance for building the web application


# Redirect the user to /login
@app.get("/", tags=["ROOT"])
async def root(request: Request) -> RedirectResponse:
  return RedirectResponse(request.url_for("github_login"))

# Redirect the user to GitHub's authorization page
@app.get("/login", tags=["LOGIN"])
async def github_login(request: Request) -> RedirectResponse:
  client_id = os.getenv("GITHUB_CLIENT_ID")
  state = binascii.hexlify(os.urandom(16)).decode() # To prevent CSRF attacks
  response = RedirectResponse(f"https://github.com/login/oauth/authorize?client_id={client_id}&state={state}")
  response.set_cookie(key="state", value=state, secure=True)
  return response

# Exchange the authorization code for an access token
@app.get("/authorize", tags=["AUTHORIZE"])
async def authorize(request: Request, state: str = Cookie(None)):
  if state is None:
    raise HTTPException(status_code=400, detail="State cookie not found")

  state_returned = request.query_params.get("state")
  if state_returned != state:
    raise HTTPException(status_code=400, detail="Invalid state parameter")

  code = request.query_params.get("code")
  if not code:
    raise HTTPException(status_code=400, detail="No code received")
  
  client_id = os.getenv("GITHUB_CLIENT_ID")
  client_secret = os.getenv("GITHUB_CLIENT_SECRET")
  params = {
    "client_id": client_id,
    "client_secret": client_secret,
    "code": code
  }
  headers = {"Accept": "application/json"}

  async with httpx.AsyncClient() as client:
    response = await client.post(url="https://github.com/login/oauth/access_token", params=params, headers=headers)
    if response.status_code == 200:
      token_data = response.json()
      access_token = token_data.get("access_token")
      if not access_token:
        raise HTTPException(status_code=400, detail="Failed to obtain access token")
    else:
      raise HTTPException(status_code=response.status_code, detail="Failed to make request to GitHub OAuth")
    
  
  