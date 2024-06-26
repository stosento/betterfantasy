import os
from fastapi.security import APIKeyHeader
from fastapi import Security, HTTPException
from starlette.status import HTTP_403_FORBIDDEN

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

BF_API_KEYS = os.getenv('BF_API_KEYS').split(',')

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header in BF_API_KEYS:
        return api_key_header
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
        )