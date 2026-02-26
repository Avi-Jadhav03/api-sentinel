from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.models.model import API
from app.schemas.schema import APICreate, APIResponse

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