from asyncore import loop
from urllib.request import Request
from fastapi import FastAPI, Query,File, UploadFile, status
from fastapi.responses import FileResponse
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import pandas as pd
import os
import traceback
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width',250)
import warnings
warnings.filterwarnings('ignore')
import json
import sys 
from app.utils.kwenta_v2_sdk import *


app = FastAPI(title="KWENTA API",
    version="1.0.0",
    contact={
        "name": "Kwenta Dev"
    }
)

token_list = kwenta(provider_rpc,"wallet_addr").token_list

origins = [
    "http://localhost:3000",
    "localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

def expand_list(df, list_column, new_column): 
    lens_of_lists = df[list_column].apply(len)
    origin_rows = range(df.shape[0])
    destination_rows = np.repeat(origin_rows, lens_of_lists)
    non_list_cols = (
      [idx for idx, col in enumerate(df.columns)
       if col != list_column]
    )
    expanded_df = df.iloc[destination_rows, non_list_cols].copy()
    expanded_df[new_column] = (
      [item for items in df[list_column] for item in items]
      )
    expanded_df.reset_index(inplace=True, drop=True)
    return expanded_df

#default Route
@app.get("/", tags=["root"])
async def read_root() -> dict:
    return {"message": "Welcome to the Kwenta API."}

#list all routes
@app.get("/endpoints")
def get_all_urls():
    url_list = [{"path": route.path, "name": route.name} for route in app.routes]
    return url_list

#################################################################################################################################################
#Market Data
#################################################################################################################################################
# EX: http://localhost:8000/eth/price
@app.get("/{token}/price", tags=["Market"])
async def get_token_price(token: str) -> dict:
    token = token.upper()
    if not (token in token_list):
        return {"data" : f"No Token found with symbol {token}, Please choose from one of the following: {token_list}" }
    account = kwenta(provider_rpc, "wallet")
    data = account.get_current_asset_price(token)
    return {"data" : data}

# EX: http://localhost:8000/tokenlist
@app.get("/tokenlist", tags=["Market"])
async def get_token_list() -> dict:
    account = kwenta(provider_rpc, "wallet")
    data = account.token_list
    return {"data" : {"tokens":data}}

# EX: http://localhost:8000/eth/candles/?hoursback=48&period_seconds=60
@app.get("/{token}/candles/", tags=["Market"])
async def get_candle_data(token: str,hoursback:int=24,period_seconds:int=300) -> dict:
    token = token.upper()
    if not (token in token_list):
        return {"data" : f"No Token found with symbol {token}, Please choose from one of the following: {token_list}" }
    account = kwenta(provider_rpc, "wallet")
    data = account.get_historicals(token,hoursback,period_seconds)
    return {"data" : data}

# EX: http://localhost:8000/eth/pendingorders/?wallet_address=Address 
@app.get("/{token}/pendingorders/", tags=["Market"])
async def get_pending_orders(wallet_address:str,token: str) -> dict:
    token = token.upper()
    if not (token in token_list):
        return {"data" : f"No Token found with symbol {token}, Please choose from one of the following: {token_list}" }
    if not wallet_address:
        return {"data" : f"Please specify a wallet address. Ex: http://localhost:8000/eth/?wallet_address=ADDRESS" }
    account = kwenta(provider_rpc, wallet_address)
    data = account.check_delayed_orders(token)
    return {"data" : data}

# EX: http://localhost:8000/eth/currentposition/?wallet_address=Address 
@app.get("/{token}/currentposition/", tags=["Market"])
async def get_current_position(wallet_address:str,token: str) -> dict:
    token = token.upper()
    if not (token in token_list):
        return {"data" : f"No Token found with symbol {token}, Please choose from one of the following: {token_list}" }
    if not wallet_address:
        return {"data" : f"Please specify a wallet address. Ex: http://localhost:8000/eth/?wallet_address=ADDRESS" }
    account = kwenta(provider_rpc, wallet_address)
    data = account.get_current_positions(token)
    return {"data" : data}

# EX: http://localhost:8000/eth/margin/?wallet_address=Address 
@app.get("/{token}/margin/", tags=["Market"])
async def get_accessiblemargin(wallet_address:str,token: str) -> dict:
    token = token.upper()
    if not (token in token_list):
        return {"data" : f"No Token found with symbol {token}, Please choose from one of the following: {token_list}" }
    if not wallet_address:
        return {"data" : f"Please specify a wallet address. Ex: http://localhost:8000/eth/?wallet_address=ADDRESS" }
    account = kwenta(provider_rpc, wallet_address)
    data = account.get_accessible_margin(token)
    return {"data" : data}

# EX: http://localhost:8000/eth/marketskew/
@app.get("/{token}/marketskew/", tags=["Market"])
async def get_marketskew(token: str) -> dict:
    token = token.upper()
    if not (token in token_list):
        return {"data" : f"No Token found with symbol {token}, Please choose from one of the following: {token_list}" }
    account = kwenta(provider_rpc, wallet_address)
    data = account.get_market_skew(token)
    return {"data" : data}

# EX: http://localhost:8000/eth/susdbalance/?wallet_address=Address 
@app.get("/susdbalance/", tags=["Market"])
async def get_susdbalance(wallet_address:str) -> dict:
    if not wallet_address:
        return {"data" : f"Please specify a wallet address. Ex: http://localhost:8000/eth/?wallet_address=ADDRESS" }
    account = kwenta(provider_rpc, wallet_address)
    data = account.get_susd_balance()
    return {"data" : data}

# EX: http://localhost:8000/eth/margin/?wallet_address=Address&leverage_multi=5
@app.get("/{token}/leverage/", tags=["Market"])
async def get_leverage_available(wallet_address:str,token: str,leverage_multi:float=1) -> dict:
    token = token.upper()
    if not (token in token_list):
        return {"data" : f"No Token found with symbol {token}, Please choose from one of the following: {token_list}" }
    if not wallet_address:
        return {"data" : f"Please specify a wallet address. Ex: http://localhost:8000/eth/?wallet_address=ADDRESS" }
    account = kwenta(provider_rpc, wallet_address)
    data = account.get_leveraged_amount(token,leverage_multi)
    return {"data" : data}

# EX: http://localhost:8000/eth/transfermargin/?wallet_address=Address&token_amount=500
@app.get("/{token}/transfermargin/", tags=["Account Actions"])
async def gen_margin_transfer_tx(wallet_address:str,token_amount:int,token: str) -> dict:
    token = token.upper()
    if not (token in token_list):
        return {"data" : f"No Token found with symbol {token}, Please choose from one of the following: {token_list}" }
    if not wallet_address:
        return {"data" : f"Please specify a wallet address. Ex: http://localhost:8000/eth/?wallet_address=ADDRESS" }
    account = kwenta(provider_rpc, wallet_address)
    data = account.transfer_margin(token,token_amount)
    return {"data" : data}

# EX: http://localhost:8000/eth/position/open/?wallet_address=Address&token_amount=500&leverage_multiplier=400
@app.get("/{token}/position/open", tags=["Positions"])
async def gen_open_position_tx(wallet_address:str,token: str,short:bool=Query(default=False),leverage_multiplier:float=Query(default=None),token_amount:int=Query(default=None)) -> dict:
    token = token.upper()
    if not (token in token_list):
        return {"data" : f"No Token found with symbol {token}, Please choose from one of the following: {token_list}" }
    if not wallet_address:
        return {"data" : f"Please specify a wallet address. Ex: http://localhost:8000/eth/?wallet_address=ADDRESS" }
    if leverage_multiplier and token_amount:
        return {"error" : "Enter EITHER a position amount or a leverage multiplier."}
    elif leverage_multiplier:
        account = kwenta(provider_rpc, wallet_address)
        data = account.open_position(token,short,leverage_multiplier=leverage_multiplier)
        return {"data" : data}
    elif token_amount:
        account = kwenta(provider_rpc, wallet_address)
        data = account.open_position(token,short,position_amount=token_amount)
        return {"data" : data}
    
# EX: http://localhost:8000/eth/position/close/?wallet_address=Address
@app.get("/{token}/position/close", tags=["Positions"])
async def gen_open_position_tx(wallet_address:str,token: str) -> dict:
    token = token.upper()
    if not (token in token_list):
        return {"data" : f"No Token found with symbol {token}, Please choose from one of the following: {token_list}" }
    if not wallet_address:
        return {"data" : f"Please specify a wallet address. Ex: http://localhost:8000/eth/?wallet_address=ADDRESS" }
    account = kwenta(provider_rpc, wallet_address)
    data = account.close_position(token)
    return {"data" : data}
