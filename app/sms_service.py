"""
sms_service.py — Pluggable SMS backend for OTP delivery.

To switch provider, set in settings.py:
    SMS_PROVIDER = 'console'   # print to console (default / dev)
    SMS_PROVIDER = 'twilio'    # Twilio
    SMS_PROVIDER = 'fast2sms'  # Fast2SMS (India)
    SMS_PROVIDER = 'msg91'     # MSG91

Then add the relevant credentials to settings.py for your chosen provider.
"""

import logging
from django.conf import settings

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────
# Provider: Console (development / fallback)
# ─────────────────────────────────────────────────────────────
def _send_console(mobile: str, otp: str) -> dict:
    """Prints OTP to console instead of sending SMS. Use in development."""
    print(f"\n{'='*50}")
    print(f"[SMS CONSOLE] To: {mobile}")
    print(f"[SMS CONSOLE] OTP: {otp}")
    print(f"[SMS CONSOLE] Message: Your EduReview password reset OTP is {otp}. Valid for 5 minutes. Do not share.")
    print(f"{'='*50}\n")
    logger.info(f"[console] OTP {otp} sent to {mobile}")
    return {"success": True, "provider": "console", "message_id": "console-dev"}


# ─────────────────────────────────────────────────────────────
# Provider: Twilio
# ─────────────────────────────────────────────────────────────
def _send_twilio(mobile: str, otp: str) -> dict:
    """
    Requires in settings.py:
        TWILIO_ACCOUNT_SID = 'ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
        TWILIO_AUTH_TOKEN  = 'your_auth_token'
        TWILIO_FROM_NUMBER = '+1xxxxxxxxxx'
    """
    try:
        from twilio.rest import Client
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        msg = client.messages.create(
            body=f"Your EduReview password reset OTP is {otp}. Valid for 5 minutes. Do not share.",
            from_=settings.TWILIO_FROM_NUMBER,
            to=mobile,
        )
        logger.info(f"[twilio] SID={msg.sid} to {mobile}")
        return {"success": True, "provider": "twilio", "message_id": msg.sid}
    except Exception as exc:
        logger.error(f"[twilio] Failed: {exc}")
        return {"success": False, "provider": "twilio", "error": str(exc)}


# ─────────────────────────────────────────────────────────────
# Provider: Fast2SMS (India)
# ─────────────────────────────────────────────────────────────
def _send_fast2sms(mobile: str, otp: str) -> dict:
    """
    Requires in settings.py:
        FAST2SMS_API_KEY = 'your_api_key'
    """
    try:
        import requests
        url = "https://www.fast2sms.com/dev/bulkV2"
        payload = {
            "route":    "otp",
            "variables_values": otp,
            "flash":    0,
            "numbers":  mobile.replace("+91", "").replace(" ", ""),
        }
        headers = {
            "authorization": settings.FAST2SMS_API_KEY,
            "Content-Type": "application/json",
        }
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        data = resp.json()
        if data.get("return"):
            logger.info(f"[fast2sms] request_id={data.get('request_id')} to {mobile}")
            return {"success": True, "provider": "fast2sms", "message_id": data.get("request_id")}
        logger.error(f"[fast2sms] API error: {data}")
        return {"success": False, "provider": "fast2sms", "error": str(data)}
    except Exception as exc:
        logger.error(f"[fast2sms] Failed: {exc}")
        return {"success": False, "provider": "fast2sms", "error": str(exc)}


# ─────────────────────────────────────────────────────────────
# Provider: MSG91
# ─────────────────────────────────────────────────────────────
def _send_msg91(mobile: str, otp: str) -> dict:
    """
    Requires in settings.py:
        MSG91_AUTH_KEY    = 'your_auth_key'
        MSG91_TEMPLATE_ID = 'your_template_id'
        MSG91_SENDER_ID   = 'EDURV'
    """
    try:
        import requests
        url = "https://api.msg91.com/api/v5/otp"
        payload = {
            "template_id": settings.MSG91_TEMPLATE_ID,
            "mobile":      mobile,
            "authkey":     settings.MSG91_AUTH_KEY,
            "otp":         otp,
        }
        resp = requests.post(url, json=payload, timeout=10)
        data = resp.json()
        if data.get("type") == "success":
            logger.info(f"[msg91] to {mobile}")
            return {"success": True, "provider": "msg91", "message_id": data.get("request_id", "")}
        logger.error(f"[msg91] API error: {data}")
        return {"success": False, "provider": "msg91", "error": str(data)}
    except Exception as exc:
        logger.error(f"[msg91] Failed: {exc}")
        return {"success": False, "provider": "msg91", "error": str(exc)}


# ─────────────────────────────────────────────────────────────
# Public API — the only function you should call
# ─────────────────────────────────────────────────────────────
PROVIDERS = {
    "console":  _send_console,
    "twilio":   _send_twilio,
    "fast2sms": _send_fast2sms,
    "msg91":    _send_msg91,
}


def send_otp_sms(mobile: str, otp: str) -> dict:
    """
    Send an OTP SMS via the configured provider.

    Returns:
        {"success": True/False, "provider": str, "message_id": str, "error": str}
    """
    provider_name = getattr(settings, "SMS_PROVIDER", "console")
    handler = PROVIDERS.get(provider_name, _send_console)
    try:
        result = handler(mobile, otp)
    except Exception as exc:
        logger.error(f"[sms_service] Unhandled exception ({provider_name}): {exc}")
        result = {"success": False, "provider": provider_name, "error": str(exc)}
    return result
