# Standard library imports
import os
import binascii
import json

# Third-party library imports
from fastapi import FastAPI, Request, HTTPException, Cookie
from dotenv import load_dotenv
from fastapi.responses import RedirectResponse, Response
import httpx

# Local application imports
from .helpers import exchange_code_for_token, save_token_to_env, delete_token_from_env


load_dotenv()  # Load environment variables from .env file for configuration


app = FastAPI() # FastAPI instance for building the web application

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
  response.set_cookie(key="state", value=state, secure=True,  httponly=True)
  return response

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
  await save_token_to_env(access_token)
  return RedirectResponse(url=request.url_for('get_starred_repositories'))
  
# Fetch starred repositories
@app.get("/starred", tags=["Starred Repositories"])
async def get_starred_repositories() -> Response:

  access_token = os.getenv("ACCESS_TOKEN")
  await delete_token_from_env()
  
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
        
        # Found the info of serialising an object before return from here:
        # https://stackoverflow.com/questions/73972660/how-to-return-data-in-json-format-using-fastapi 
        prettify_json = json.dumps(data, indent=4)
        return Response(content=prettify_json, media_type="application/json")
      
      else:
        raise HTTPException(status_code=response.status_code, detail="Failed to make Get request")
  except (httpx.RequestError, httpx.HTTPStatusError, httpx.TimeoutException) as ex:
        raise HTTPException(status_code=500, detail=f"Failed to make request: {ex}")
  

  