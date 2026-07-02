import asyncio
from app.services.mongodb import ping_mongo
from app.config import get_settings

async def main():
    print(get_settings().MONGODB_URI)
    print(await ping_mongo())

asyncio.run(main())
