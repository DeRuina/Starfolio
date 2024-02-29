from fastapi import FastAPI, Request, HTTPException, Cookie
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
from fastapi.responses import RedirectResponse, Response
import os
import binascii
import httpx
import json


load_dotenv()  # Load environment variables from .env file for configuration


app = FastAPI() # FastAPI instance for building the web application

app.add_middleware(SessionMiddleware, secret_key="your_secret_key")

# Redirect the user to /login
@app.get("/", tags=["Root"])
async def root(request: Request) -> RedirectResponse:
  return RedirectResponse(request.url_for("github_login"))

# Redirect the user to GitHub's authorization page
@app.get("/login", tags=["Login"])
async def github_login(request: Request) -> RedirectResponse:
  client_id = os.getenv("GITHUB_CLIENT_ID")
  state = binascii.hexlify(os.urandom(16)).decode() # To prevent CSRF attacks
  redirect_uri = request.url_for("authorize")
  response = RedirectResponse(f"https://github.com/login/oauth/authorize?client_id={client_id}&state={state}&redirect_uri={redirect_uri}")
  response.set_cookie(key="state", value=state, secure=True,  httponly=True, samesite='strict')
  return response

# Exchange the authorization code for an access token
async def exchange_code_for_token(code:str, client_id: str, client_secret: str) -> str:
  params = {
    "client_id": client_id,
    "client_secret": client_secret,
    "code": code
  }
  headers = {"Accept": "application/json"}
  # Found that is better to use httpx.AsyncClient() for asynchronous requests 
  # from this Medium post: https://medium.com/featurepreneur/what-is-httpx-a0071df05c4a
  try:
    async with httpx.AsyncClient() as client:
      response = await client.post(url="https://github.com/login/oauth/access_token", params=params, headers=headers)
      if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get("access_token")
        if not access_token:
          raise HTTPException(status_code=400, detail="Failed to obtain access token")
        return access_token
      else:
        raise HTTPException(status_code=response.status_code, detail="Failed to make request to GitHub OAuth")
  except (httpx.RequestError, httpx.HTTPStatusError, httpx.TimeoutException) as ex:
        raise HTTPException(status_code=500, detail=f"Failed to make request: {ex}")
    
# Perform checks and call helper functions
@app.get("/authorize", tags=["Authorize"])
async def authorize(request: Request, state: str = Cookie(None)) -> RedirectResponse:
  if state is None or not state.isalnum():
    raise HTTPException(status_code=400, detail="State cookie not found")

  state_returned = request.query_params.get("state")
  if state_returned != state:
    raise HTTPException(status_code=400, detail="Invalid state parameter")

  code = request.query_params.get("code")
  if not code or not code.isalnum():
    raise HTTPException(status_code=400, detail="No code received")
  
  client_id = os.getenv("GITHUB_CLIENT_ID")
  client_secret = os.getenv("GITHUB_CLIENT_SECRET")

  access_token = await exchange_code_for_token(code, client_id, client_secret)
  request.session["access_token"] = access_token
  return RedirectResponse(url=request.url_for('get_starred_repositories'))
  
  # Fetch starred repositories
@app.get("/starred", tags=["Starred Repositories"])
async def get_starred_repositories(request: Request) -> Response:
  access_token = request.session.get("access_token")
  try:
    async with httpx.AsyncClient() as client:
      headers = {"Accept": "application/json", "Authorization": f"Bearer {access_token}"}
      response = await client.get(url="https://api.github.com/user/starred", headers=headers)
      if response.status_code == 200:
        repos = response.json()
        public_repos = [ # list comprehension 
          {
            "name": repo["name"], 
            "description": repo["description"], 
            "URL": repo["url"], 
            **({"license": repo["license"]["name"]} if repo["license"] is not None else {}),
            "topics": repo["topics"]
          } for repo in repos if not repo["private"]
          ]
        data = [
          {"number_of_starred_repositories": len(public_repos), 
          **({"repositories_list": public_repos} if len(public_repos) != 0 else {})}
          ]
        prettify_json = json.dumps(data, indent=4)
        # Found the info of serialising an object before return from here:
        # https://stackoverflow.com/questions/73972660/how-to-return-data-in-json-format-using-fastapi 
        return Response(content=prettify_json, media_type="application/json")
      else:
        raise HTTPException(status_code=response.status_code, detail="Failed to make Get request")
  except (httpx.RequestError, httpx.HTTPStatusError, httpx.TimeoutException) as ex:
        raise HTTPException(status_code=500, detail=f"Failed to make request: {ex}")
  