import uvicorn

if __name__ == "__main__":
    # Dev Mode
    uvicorn.run("app.api:app", host="0.0.0.0", port=8000, reload=True)
    # Prod Mode - Will be much faster, but no hot reloading. remove SSL params if not needed. 
    # uvicorn.run("app.api:app", host="0.0.0.0", port=8000, ssl_keyfile='SSL_FILE.key', ssl_certfile='SSL_FILE.pem')