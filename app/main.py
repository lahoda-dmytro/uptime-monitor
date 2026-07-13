import asyncio
import logging
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import engine, Base, get_db
from config import settings
from scheduler import pinger_loop
import crud
import schemas

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    pinger_task = asyncio.create_task(pinger_loop(settings.ping_interval_seconds))
    yield
    pinger_task.cancel()
    try:
        await pinger_task
    except asyncio.CancelledError:
        pass


app = FastAPI(title="Uptime Monitor API", lifespan=lifespan)


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {"status": "healthy"}


@app.post("/api/v1/sites", response_model=schemas.SiteResponse, status_code=status.HTTP_201_CREATED)
async def create_site(site: schemas.SiteCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await crud.create_site(db=db, site=site)
    except Exception:
        logger.exception("Failed to create site with url=%s", site.url)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Site URL may already exist or input is invalid",
        )


@app.get("/api/v1/sites", response_model=List[schemas.SiteResponse])
async def list_sites(db: AsyncSession = Depends(get_db)):
    return await crud.get_sites(db=db)


@app.get("/api/v1/sites/{site_id}", response_model=schemas.SiteResponse)
async def get_site(site_id: int, db: AsyncSession = Depends(get_db)):
    db_site = await crud.get_site(db=db, site_id=site_id)
    if db_site is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")
    return db_site


@app.delete("/api/v1/sites/{site_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_site(site_id: int, db: AsyncSession = Depends(get_db)):
    success = await crud.delete_site(db=db, site_id=site_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")


@app.get("/api/v1/sites/{site_id}/history", response_model=List[schemas.PingLogResponse])
async def get_site_history(site_id: int, limit: int = 100, db: AsyncSession = Depends(get_db)):
    db_site = await crud.get_site(db=db, site_id=site_id)
    if db_site is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")
    return await crud.get_site_logs(db=db, site_id=site_id, limit=limit)
