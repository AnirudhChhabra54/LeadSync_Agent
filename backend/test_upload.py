import asyncio
from fastapi import UploadFile
from fastapi.datastructures import Headers
from app.routes.chat import upload_image
import io

async def test():
    file = UploadFile(
        file=io.BytesIO(b"dummy image content"),
        size=19,
        filename="test.jpeg",
        headers=Headers({"content-type": "image/jpeg"})
    )
    try:
        res = await upload_image("test_session", file)
        print("Success LangGraph Extractor! Extracted data:", res.extracted_data)
    except Exception as e:
        import traceback
        traceback.print_exc()

asyncio.run(test())
