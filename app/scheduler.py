import asyncio
import time
from typing import Optional
import httpx
from .database import SessionLocal
from .crud import get_sites, create_ping_log

async def ping_site(client: httpx.AsyncClient, site_id: int, url: str) -> None:
    start_time = time.perf_counter()
    status_code: Optional[int] = None
    response_time_ms: Optional[int] = None
    is_up = False
    error_message: Optional[str] = None

    try:
        response = await client.get(url, timeout=5.0, follow_redirects=True)
        status_code = response.status_code
        response_time_ms = int((time.perf_counter() - start_time) * 1000)
        is_up = 200 <= status_code < 400
        if not is_up:
            error_message = f"HTTP status error: {status_code}"
    except httpx.HTTPError as e:
        response_time_ms = int((time.perf_counter() - start_time) * 1000)
        error_message = str(e)
    except Exception as e:
        response_time_ms = int((time.perf_counter() - start_time) * 1000)
        error_message = f"Unexpected error: {type(e).__name__}"

    async with SessionLocal() as db:
        try:
            await create_ping_log(
                db=db,
                site_id=site_id,
                status_code=status_code,
                response_time_ms=response_time_ms,
                is_up=is_up,
                error_message=error_message
            )
        except Exception:
            pass

async def pinger_loop(interval: int) -> None:
    while True:
        try:
            async with SessionLocal() as db:
                sites = await get_sites(db, active_only=True)
            
            if sites:
                async with httpx.AsyncClient() as client:
                    tasks = [ping_site(client, site.id, site.url) for site in sites]
                    await asyncio.gather(*tasks, return_exceptions=True)
        except Exception:
            pass
        
        await asyncio.sleep(interval)
