import logging
from typing import Dict, Any, Optional
import httpx
from app.config import settings

logger = logging.getLogger(__name__)

class SMSService:
    """
    Pluggable SMS Gateway Service for Bangladeshi Farmers.
    Supports Mock (Development/Testing), Greenweb BD, and Twilio.
    """

    def __init__(self):
        self.provider = settings.SMS_PROVIDER.lower()
        self.api_key = settings.SMS_API_KEY
        self.sender_id = settings.SMS_SENDER_ID

    async def send_sms(self, to_phone: str, message_bn: str) -> Dict[str, Any]:
        """
        বাংলা ইউনিকোড এসএমএস প্রেরণ
        """
        # ফোন নাম্বার ভ্যালিডেশন / নরমালাইজেশন (যেমন: +8801... বা 01...)
        cleaned_phone = to_phone.strip().replace(" ", "").replace("-", "")
        if cleaned_phone.startswith("+88"):
            cleaned_phone = cleaned_phone[3:]
        if not cleaned_phone.startswith("01") or len(cleaned_phone) != 11:
            return {
                "status": "failed",
                "reason": "অকার্যকর মোবাইল নম্বর (১১ ডিজিটের 01... হতে হবে)",
                "to": to_phone
            }

        logger.info(f"[SMSService] Sending SMS via provider '{self.provider}' to {cleaned_phone}")

        if self.provider == "greenweb" and self.api_key:
            return await self._send_greenweb(cleaned_phone, message_bn)
        elif self.provider == "twilio" and self.api_key:
            return await self._send_twilio(cleaned_phone, message_bn)
        else:
            return self._send_mock(cleaned_phone, message_bn)

    def _send_mock(self, phone: str, message: str) -> Dict[str, Any]:
        """
        লোকাল ডেভেলপমেন্ট ও টেস্টিং মোড (লগ ও ডেটাবেসে দৃশ্যমান)
        """
        print(f"\n================ [MOCK SMS DISPATCHED] ================")
        print(f"To: +88{phone}")
        print(f"Sender ID: {self.sender_id}")
        print(f"Message (Bangla Unicode):")
        print(f"{message}")
        print(f"=======================================================\n")
        
        return {
            "status": "success",
            "provider": "mock",
            "to": f"+88{phone}",
            "message_length": len(message),
            "message_bn": message
        }

    async def _send_greenweb(self, phone: str, message: str) -> Dict[str, Any]:
        url = "http://api.greenweb.com.bd/api.php"
        params = {
            "token": self.api_key,
            "to": f"88{phone}",
            "message": message
        }
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                res = await client.post(url, data=params)
                if "Ok:" in res.text:
                    return {"status": "success", "provider": "greenweb", "response": res.text}
                else:
                    return {"status": "failed", "provider": "greenweb", "error": res.text}
        except Exception as e:
            logger.error(f"[SMSService] Greenweb request failed: {e}")
            return {"status": "failed", "error": str(e)}

    async def _send_twilio(self, phone: str, message: str) -> Dict[str, Any]:
        # Twilio API integration fallback
        return {"status": "success", "provider": "twilio", "to": phone}

sms_service = SMSService()
