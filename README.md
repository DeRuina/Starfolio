# Starfolio

## Short Description

This project is a FastAPI application that allows users to authenticate with GitHub using OAuth and fetch their starred repositories. The application provides a web interface for users to log in and view their starred repositories, as well as a command-line interface (CLI) for fetching the repositories programmatically.

## Instructions

### Prerequisites

- Python 3.6 or newer
- FastAPI
- Uvicorn (ASGI server)
- `httpx` (for making HTTP requests)
- `python-dotenv` (for loading environment variables)

### GitHub OAuth Setup

1. Go to your GitHub account's [Developer Settings](https://github.com/settings/developers).
2. Click on "New OAuth App" to create a new OAuth application.
3. Fill in the "Application name", "Homepage URL", and "Authorization callback URL" fields.
   - For "Homepage URL", use `http://127.0.0.1:8000`.
   - For "Authorization callback URL", use `http://127.0.0.1:8000/authorize`.
4. After creating the OAuth application, you will receive a `client_id` and `client_secret`.

### Environment Setup

1. Rename the `.env.example` file to `.env`.
2. Open the `.env` file and fill in the `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET` fields with the values you received from GitHub.

### Running the Application

1. Install the required dependencies by running `pip install fastapi uvicorn httpx python-dotenv`.
2. Start the application by running `python3 main.py`.
3. Open your web browser and navigate to `http://127.0.0.1:8000`.
4. Click on the "Login with GitHub" button to authenticate.
5. After successful authentication, you will be redirected to the `/starred` endpoint, where you can view your starred repositories.

### Using the Command-Line Interface (CLI)

1. After authenticating, you can use the following `curl` command to fetch your starred repositories programmatically:
```bash
curl -X GET "http://127.0.0.1:8000/starred" -H "Authorization: Bearer ${ACCESS_TOKEN}"
```

### Additional Notes

- Ensure that your `.env` file is not committed to version control systems like Git to protect your sensitive credentials.


## Author

- [@DeRuina](https://github.com/DeRuina)