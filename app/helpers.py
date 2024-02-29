# Standard library imports
import os

# Third-party library imports
import httpx
from dotenv import load_dotenv
from fastapi import HTTPException

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

# saving the token to the .env 
async def save_token_to_env(value: str) -> None:
    with open(".env", "a") as file1:
      file1.write(f'\nACCESS_TOKEN="{value}"')  
    load_dotenv()

# deleting the token from .env so next server restart the old token won't load
async def delete_token_from_env() -> None:
  client_id = os.getenv("GITHUB_CLIENT_ID")
  client_secret = os.getenv("GITHUB_CLIENT_SECRET")
  with open(".env", "w") as file:
    file.write(f'GITHUB_CLIENT_ID="{client_id}"\nGITHUB_CLIENT_SECRET="{client_secret}"')