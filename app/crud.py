from typing import Sequence, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import models
import schemas


async def get_sites(db: AsyncSession, active_only: bool = False) -> Sequence[models.Site]:
    query = select(models.Site)
    if active_only:
        query = query.where(models.Site.is_active)
    result = await db.execute(query)
    return result.scalars().all()


async def get_site(db: AsyncSession, site_id: int) -> Optional[models.Site]:
    query = select(models.Site).where(models.Site.id == site_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def create_site(db: AsyncSession, site: schemas.SiteCreate) -> models.Site:
    db_site = models.Site(url=str(site.url), name=site.name, is_active=site.is_active)
    db.add(db_site)
    await db.commit()
    await db.refresh(db_site)
    return db_site


async def delete_site(db: AsyncSession, site_id: int) -> bool:
    query = select(models.Site).where(models.Site.id == site_id)
    result = await db.execute(query)
    db_site = result.scalar_one_or_none()
    if db_site:
        await db.delete(db_site)
        await db.commit()
        return True
    return False


async def get_site_logs(db: AsyncSession, site_id: int, limit: int = 100) -> Sequence[models.PingLog]:
    query = (
        select(models.PingLog)
        .where(models.PingLog.site_id == site_id)
        .order_by(models.PingLog.checked_at.desc())
        .limit(limit)
    )
    result = await db.execute(query)
    return result.scalars().all()


async def create_ping_log(
    db: AsyncSession,
    site_id: int,
    status_code: Optional[int],
    response_time_ms: Optional[int],
    is_up: bool,
    error_message: Optional[str],
) -> models.PingLog:
    db_log = models.PingLog(
        site_id=site_id,
        status_code=status_code,
        response_time_ms=response_time_ms,
        is_up=is_up,
        error_message=error_message,
    )
    db.add(db_log)
    await db.commit()
    await db.refresh(db_log)
    return db_log
