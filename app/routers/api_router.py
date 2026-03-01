from fastapi import APIRouter, Depends,HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.models.api_model import API
from app.schemas.schema import APICreate, APIResponse
import httpx,time

router = APIRouter(prefix="/apis", tags=["APIs"])

@router.post('/',response_model = APIResponse)
async def create_api(api:APICreate ,db:AsyncSession = Depends(get_db)):
    new_api = API(
        name = api.name,
        url = str(api.url)
    )

    db.add(new_api)
    await db.commit()
    await db.refresh(new_api)

    return new_api

@router.get('/',response_model = list[APIResponse])
async def get_apis(db:AsyncSession = Depends(get_db)):
    result = await db.execute(select(API))
    apis = result.scalars().all()
    return apis

@router.get('/{id}',response_model = APIResponse)
async def get_api_by_id(id:int ,db:AsyncSession = Depends(get_db)):
    result = await db.execute(select(API).where(API.id == id))
    api = result.scalars().first()
    if api is None:
        raise HTTPException(status_code=404, detail="API not found")
    
    return api

from app.models.health_log_model import HealthLog


@router.post("/{id}/check")
async def check_health_by_id(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(API).where(API.id == id))
    api = result.scalar_one_or_none()

    if api is None:
        raise HTTPException(status_code=404, detail="API not found")

    try:
        start = time.perf_counter()

        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(api.url)

        end = time.perf_counter()
        response_time = end - start

        log = HealthLog(
            api_id=api.id,
            status_code=response.status_code,
            response_time=response_time,
            is_healthy=response.status_code == 200
        )

    except httpx.RequestError as e:
        log = HealthLog(
            api_id=api.id,
            status_code=None,
            response_time=None,
            is_healthy=False
        )

    db.add(log)
    await db.commit()

    return {
        "status_code": log.status_code,
        "response_time": log.response_time,
        "is_healthy": log.is_healthy
    }

from app.models.health_log_model import HealthLog
from app.schemas.schema import HealthLogResponse
from sqlalchemy import select, desc


@router.get("/{id}/logs", response_model=list[HealthLogResponse])
async def get_api_logs(id: int, db: AsyncSession = Depends(get_db)):

    # 1️⃣ Check if API exists
    result = await db.execute(select(API).where(API.id == id))
    api = result.scalar_one_or_none()

    if api is None:
        raise HTTPException(status_code=404, detail="API not found")

    # 2️⃣ Fetch logs sorted by newest first
    logs_result = await db.execute(
        select(HealthLog)
        .where(HealthLog.api_id == id)
        .order_by(desc(HealthLog.checked_at))
    )

    logs = logs_result.scalars().all()

    return logs