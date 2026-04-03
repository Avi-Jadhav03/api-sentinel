from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.db.database import get_db
from app.models.api_model import API
from app.models.health_log_model import HealthLog
from app.schemas.schema import APICreate, APIResponse, HealthLogResponse
from app.services.health_service import check_single_api, get_api_stats, load_test_api
from app.services.ai_service import ai_query

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


@router.post("/{id}/check")
async def check_health_by_id(id: int):
    result = await check_single_api(id)

    if result is None:
        raise HTTPException(status_code=404, detail="API not found")

    return result


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


@router.get("/{id}/stats")
async def get_stats(id: int):
    return await get_api_stats(id)


@router.post("/{id}/load-test")
async def load_test(id: int, n: int = 20):
    result = await load_test_api(id, n)

    if result is None:
        raise HTTPException(status_code=404, detail="API not found")

    return result


@router.post("/ai/query")
async def ask_ai(question: str = Query(...)):
    return await ai_query(question)