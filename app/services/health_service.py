import time
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.api_model import API
from app.models.health_log_model import HealthLog
import asyncio
from app.db.database import AsyncSessionLocal

async def check_single_api(api_id: int):
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(API).where(API.id == api_id))
        api = result.scalar_one_or_none()

        if api is None:
            return None

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

        except httpx.RequestError:
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


async def check_all_apis():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(API))
        apis = result.scalars().all()

        tasks = [                                            #List Comprehension
            check_single_api(api.id)
            for api in apis
        ]

        await asyncio.gather(*tasks)

async def background_monitor():
    while True:
        try:
            await check_all_apis()
            print("Background monitor running...")
            await asyncio.sleep(30)
        except Exception as e:
            print("Background Monitor Error :",e)
            await asyncio.sleep(30)


from sqlalchemy import func

async def get_api_stats(api_id: int):
    async with AsyncSessionLocal() as db:

        total_result = await db.execute(
            select(func.count(HealthLog.id)).where(HealthLog.api_id == api_id)
        )
        total_checks = total_result.scalar()

        healthy_result = await db.execute(
            select(func.count(HealthLog.id)).where(
                HealthLog.api_id == api_id,
                HealthLog.is_healthy == True
            )
        )
        healthy_checks = healthy_result.scalar()

        avg_result = await db.execute(
            select(func.avg(HealthLog.response_time)).where(
                HealthLog.api_id == api_id
            )
        )
        avg_response_time = avg_result.scalar()

        if total_checks == 0:
            uptime = 0
        else:
            uptime = (healthy_checks / total_checks) * 100

        return {
            "total_checks": total_checks,
            "healthy_checks": healthy_checks,
            "uptime_percentage": round(uptime, 2),
            "avg_response_time": avg_response_time
        }