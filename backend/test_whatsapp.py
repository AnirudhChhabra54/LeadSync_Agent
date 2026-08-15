import asyncio
import os
import sys
import httpx
from dotenv import load_dotenv

env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.env"))
load_dotenv(env_path)

from app.config import get_settings
from app.services.whatsapp import send_whatsapp_template, send_new_contact_notification

async def main():
    settings = get_settings()

    print("==================================================")
    print("📲 LEADSYNC WHATSAPP CLOUD API TESTER")
    print("==================================================")
    print(f"Phone Number ID : {settings.WHATSAPP_PHONE_NUMBER_ID}")
    print(f"Manager Number  : {settings.WHATSAPP_MANAGER_NUMBER}")
    print(f"Template Name   : {settings.WHATSAPP_TEMPLATE_NAME or '(Not set, default freeform text / fallback)'}")
    print(f"Template Lang   : {settings.WHATSAPP_TEMPLATE_LANG}")
    print(f"Access Token    : {settings.WHATSAPP_ACCESS_TOKEN[:15]}...{settings.WHATSAPP_ACCESS_TOKEN[-6:] if settings.WHATSAPP_ACCESS_TOKEN else 'MISSING'}")
    print("==================================================\n")

    if not settings.WHATSAPP_ACCESS_TOKEN or not settings.WHATSAPP_PHONE_NUMBER_ID:
        print("❌ Error: WHATSAPP_ACCESS_TOKEN or WHATSAPP_PHONE_NUMBER_ID is missing in .env")
        return

    # Check recipient number
    if not settings.WHATSAPP_MANAGER_NUMBER:
        print("❌ Error: WHATSAPP_MANAGER_NUMBER is missing in .env")
        return

    to_number = settings.WHATSAPP_MANAGER_NUMBER

    # Test 1: Send Approved Template (if provided via sys.argv or env)
    template_to_test = sys.argv[1] if len(sys.argv) > 1 else (settings.WHATSAPP_TEMPLATE_NAME or "hello_world")
    print(f"🚀 Sending Template '{template_to_test}' to {to_number}...")

    # If testing hello_world (no params), otherwise pass dynamic contact sample params
    params = None if template_to_test == "hello_world" else ["David Vance", "Apex Systems", "+1-415-555-0199"]
    
    success = await send_whatsapp_template(
        to_number=to_number,
        template_name=template_to_test,
        language_code=settings.WHATSAPP_TEMPLATE_LANG,
        body_parameters=params,
    )

    if success:
        print(f"\n🎉 SUCCESS! WhatsApp message delivered to {to_number}.")
    else:
        print("\n❌ Failed to send template message. Check token expiration or parameter count in Meta Dashboard.")

if __name__ == "__main__":
    asyncio.run(main())
