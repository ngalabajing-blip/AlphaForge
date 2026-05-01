from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from alphaforge_api.core.security import CurrentUser, get_current_user
from alphaforge_shared.chains import all_chains, get_chain

router = APIRouter(prefix="/chains")


@router.get("", response_model=list[dict])
async def list_chains(_: CurrentUser = Depends(get_current_user)) -> list[dict]:
    return [
        {
            "id": c.id,
            "name": c.name,
            "family": c.family.value,
            "chain_id": c.chain_id,
            "native_symbol": c.native_symbol,
            "block_time_seconds": c.block_time_seconds,
            "finality_blocks": c.finality_blocks,
            "explorer": c.explorer,
            "dexes": list(c.dexes),
        }
        for c in all_chains()
    ]


@router.get("/{chain_id}")
async def get_chain_info(chain_id: str, _: CurrentUser = Depends(get_current_user)) -> dict:
    try:
        c = get_chain(chain_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="chain not found") from exc
    return {
        "id": c.id,
        "name": c.name,
        "family": c.family.value,
        "chain_id": c.chain_id,
        "native_symbol": c.native_symbol,
        "block_time_seconds": c.block_time_seconds,
        "finality_blocks": c.finality_blocks,
        "explorer": c.explorer,
        "dexes": list(c.dexes),
    }
