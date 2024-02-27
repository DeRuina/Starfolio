from fastapi import FastAPI, Request, HTTPException, Cookie
from dotenv import load_dotenv
from fastapi.responses import RedirectResponse
import os
import binascii


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
  
  