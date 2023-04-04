
# Kwenta-Fastapi

Rest API built with Python Fastapi to interact with the Kwenta Platform.


## Deployment

To deploy the API locally

```bash
  python main.py
```
If you want it to run in the background of a linux host you can create a systemctl service or just run the following. *You will have to kill the python service to exit.*
```bash
  nohup python main.py &
```
Open http://localhost:8000/docs in your browser to get started!
## Features

- RestAPI connection to Kwenta Platform
- List Account Details
- Get token prices
- Generate Trade TX Data
- Lightweight (Can run on potato hardware)


## API Reference
When running the FastAPI navigate to "localhost:8000/docs" this will pull up all docs for the API.
