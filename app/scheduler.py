import asyncio
import logging
import time
from typing import Optional

import httpx

from config import settings
from database import SessionLocal
from crud import get_sites, create_ping_log, get_last_ping_log

logger = logging.getLogger(__name__)


async def send_telegram_alert(client: httpx.AsyncClient, message: str) -> None:
    token = settings.telegram_bot_token
    chat_id = settings.telegram_chat_id
    if not token or not chat_id:
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        await client.post(url, json={"chat_id": chat_id, "text": message, "parse_mode": "HTML"})
    except Exception:
        logger.exception("Failed to send Telegram alert")


async def ping_site(client: httpx.AsyncClient, site_id: int, url: str, site_name: str) -> None:
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
            previous_log = await get_last_ping_log(db, site_id)
            previous_status = previous_log.is_up if previous_log else None

            await create_ping_log(
                db=db,
                site_id=site_id,
                status_code=status_code,
                response_time_ms=response_time_ms,
                is_up=is_up,
                error_message=error_message,
            )

            if previous_status != is_up:
                if previous_status is None and is_up:
                    pass
                elif not is_up:
                    message = (
                        f"<b>Site down</b>\n"
                        f"<b>{site_name}</b> is not responding\n"
                        f"URL: {url}\n"
                        f"Error: {error_message}"
                    )
                    await send_telegram_alert(client, message)
                else:
                    message = (
                        f"<b>Site recovered</b>\n"
                        f"<b>{site_name}</b> is back online\n"
                        f"URL: {url}\n"
                        f"Response time: {response_time_ms}ms"
                    )
                    await send_telegram_alert(client, message)

        except Exception:
            logger.exception("Failed to save ping log for site_id=%s", site_id)


async def pinger_loop(interval: int) -> None:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    while True:
        try:
            async with SessionLocal() as db:
                sites = await get_sites(db, active_only=True)

            if sites:
                async with httpx.AsyncClient(headers=headers) as client:
                    tasks = [ping_site(client, site.id, site.url, site.name) for site in sites]
                    await asyncio.gather(*tasks, return_exceptions=True)
        except Exception:
            logger.exception("Unexpected error in pinger_loop")

        await asyncio.sleep(interval)
