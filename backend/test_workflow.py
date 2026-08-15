import asyncio
import os
import io
from fastapi import UploadFile
from fastapi.datastructures import Headers
from app.routes.sessions import create_session, list_sessions, get_session_messages, delete_session
from app.routes.chat import upload_image, send_message
from app.models import ChatMessageRequest
from app.services.mongodb import ping_mongo
from app.services.whatsapp import send_new_contact_notification

async def run_full_workflow_test():
    print("==================================================")
    print("🚀 STARTING LEADSYNC WORKFLOW INTEGRATION TEST")
    print("==================================================")

    # 1. MongoDB Health
    print("\n[Step 1] Verifying MongoDB Connection...")
    mongo_ok = await ping_mongo()
    print(f"  -> MongoDB Status: {'✅ CONNECTED' if mongo_ok else '⚠️ NOT CONNECTED (check MONGODB_URI)'}")

    # 2. Session Lifecycle
    print("\n[Step 2] Creating a Test Session...")
    session_res = await create_session()
    session_id = session_res.session_id
    print(f"  -> Session Created: {session_id} (Title: {session_res.title})")

    # 3. Card Image Upload & OCR Workflow
    print("\n[Step 3] Testing Visiting Card Upload & OCR Extraction...")
    test_image_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../TestBCard.jpeg"))
    
    if os.path.exists(test_image_path):
        with open(test_image_path, "rb") as f:
            image_bytes = f.read()
        filename = "TestBCard.jpeg"
        content_type = "image/jpeg"
    else:
        image_bytes = b"sample_mock_visiting_card_bytes"
        filename = "sample_card.jpg"
        content_type = "image/jpeg"

    upload_file = UploadFile(
        file=io.BytesIO(image_bytes),
        size=len(image_bytes),
        filename=filename,
        headers=Headers({"content-type": content_type})
    )

    try:
        ocr_response = await upload_image(session_id=session_id, file=upload_file)
        print(f"  -> Upload Status: {ocr_response.status}")
        print(f"  -> Extracted Contact: {ocr_response.extracted_data}")
        if ocr_response.messages:
            for m in ocr_response.messages:
                print(f"     [{m.role}] {m.content[:100]}...")
    except Exception as e:
        print(f"  -> OCR Upload Error: {e}")
        ocr_response = None

    # 4. Human-In-The-Loop Confirmation
    print("\n[Step 4] Testing HITL Confirmation (Approve & Sync to CRM)...")
    if ocr_response and ocr_response.status.value == "awaiting_confirmation":
        confirm_req = ChatMessageRequest(
            session_id=session_id,
            action="confirm",
            edits={"name": "Verified Lead"} if not (ocr_response.extracted_data and ocr_response.extracted_data.name) else {}
        )
        try:
            confirm_res = await send_message(confirm_req)
            print(f"  -> Confirmation Result Status: {confirm_res.status}")
            for m in confirm_res.messages:
                print(f"     [{m.role}] {m.content}")
        except Exception as e:
            print(f"  -> Confirmation Error: {e}")
    else:
        print("  -> Session not in awaiting_confirmation state, sending test text message instead...")
        msg_req = ChatMessageRequest(
            session_id=session_id,
            message="Hello LeadSync! What are your capabilities?"
        )
        msg_res = await send_message(msg_req)
        print(f"  -> Message Result Status: {msg_res.status}")
        for m in msg_res.messages:
            print(f"     [{m.role}] {m.content[:120]}...")

    # 5. History Retrieval API
    print("\n[Step 5] Testing Session History Retrieval (GET /api/sessions/{session_id}/messages)...")
    history_res = await get_session_messages(session_id)
    print(f"  -> Retrieved {len(history_res.messages)} messages from session history:")
    for i, msg in enumerate(history_res.messages, 1):
        print(f"     {i}. [{msg.role}] {msg.content[:80]}...")

    # 6. WhatsApp Notification Dispatch Verification
    print("\n[Step 6] Testing WhatsApp Notification Dispatch...")
    sample_contact = {
        "name": "Alex Mercer",
        "company": "Apex Dynamics Inc",
        "designation": "VP of Engineering",
        "phone": "+14155552671",
        "email": "alex.mercer@apexdynamics.com"
    }
    wa_result = await send_new_contact_notification(sample_contact)
    print(f"  -> WhatsApp Notification Status: {'✅ SUCCESS / DISPATCHED' if wa_result else '❌ FAILED'}")

    # 7. Cleanup
    print("\n[Step 7] Cleaning up Test Session...")
    del_res = await delete_session(session_id)
    print(f"  -> Session Cleaned Up: {del_res}")

    print("\n==================================================")
    print("✨ LEADSYNC WORKFLOW INTEGRATION TEST COMPLETE")
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(run_full_workflow_test())
