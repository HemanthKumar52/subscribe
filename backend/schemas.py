from pydantic import BaseModel

class PurchaseVerificationRequest(BaseModel):
    source: str # 'google_play' or 'app_store'
    verificationData: str # Token
    productId: str

class PurchaseVerificationResponse(BaseModel):
    status: str
    message: str | None = None
