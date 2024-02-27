import uvicorn

# Starting the ASGI server at runtime if this script is executed directly and not imported
if __name__ ==  "__main__":
  uvicorn.run("app.app:app", reload = True)
