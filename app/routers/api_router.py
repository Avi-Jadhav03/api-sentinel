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
from app.services.health_service import check_single_api

@router.post("/{id}/check")
async def check_health_by_id(id: int):
    result = await check_single_api(id)

    if result is None:
        raise HTTPException(status_code=404, detail="API not found")

    return result


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


from app.services.health_service import get_api_stats

@router.get("/{id}/stats")
async def get_stats(id: int):
    return await get_api_stats(id)