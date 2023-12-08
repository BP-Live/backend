from fastapi import APIRouter

from routers import (
    accounts,
    gpt,
    bkk,
    ws,
)

# models
from .accounts import Account

router = APIRouter()

prefixes = {
    "/accounts": accounts.router,
    "/gpt": gpt.router,
    '/bkk': bkk.router,
    '/ws': ws.router,
}

for prefix, child in prefixes.items():
    router.include_router(child, prefix=prefix)
