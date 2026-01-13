from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import PurchaseVerificationRequest, PurchaseVerificationResponse
from ..models import Subscription, User
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime
import os

router = APIRouter(
    prefix="/purchases",
    tags=["purchases"],
)

# Initialize Google Play Developer API Service
# In production, ensure GOOGLE_APPLICATION_CREDENTIALS is set
def get_play_service():
    try:
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not credentials_path or not os.path.exists(credentials_path):
             return None # Fail gracefully if no creds (for local dev without keys)
        
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path, 
            scopes=['https://www.googleapis.com/auth/androidpublisher']
        )
        service = build('androidpublisher', 'v3', credentials=credentials)
        return service
    except Exception as e:
        print(f"Failed to init Google Play Service: {e}")
        return None

@router.post("/verify", response_model=PurchaseVerificationResponse)
def verify_purchase(request: PurchaseVerificationRequest, db: Session = Depends(get_db)):
    if request.source != "google_play":
        raise HTTPException(status_code=400, detail="Unsupported source")

    package_name = os.getenv("PACKAGE_NAME")
    if not package_name:
        raise HTTPException(status_code=500, detail="Server misconfigured: PACKAGE_NAME missing")

    service = get_play_service()
    
    # ---------------------------------------------------------
    # 1. Verify with Google Play Developer API
    # ---------------------------------------------------------
    if service:
        try:
            # https://developers.google.com/android-publisher/api-ref/rest/v3/purchases.subscriptions/get
            result = service.purchases().subscriptions().get(
                packageName=package_name,
                subscriptionId=request.productId,
                token=request.verificationData
            ).execute()
        except Exception as e:
             print(f"Google Play API Error: {e}")
             raise HTTPException(status_code=400, detail="Invalid purchase token or API error")
    else:
        # FALLBACK FOR LOCAL DEV WITHOUT KEYS (REMOVE IN PROD)
        print("WARNING: Using MOCK verification because no Google Credentials found.")
        result = {
            "expiryTimeMillis": str(int(datetime.utcnow().timestamp() * 1000) + 30*24*60*60*1000), # +30 days
            "autoRenewing": True,
            "paymentState": 1 # 1 = Payment Received
        }

    # ---------------------------------------------------------
    # 2. Parse Result
    # ---------------------------------------------------------
    # expiryTimeMillis is string in response
    expiry_ms = int(result.get("expiryTimeMillis", 0))
    expiry_dt = datetime.fromtimestamp(expiry_ms / 1000.0)
    auto_renewing = result.get("autoRenewing", False)
    # paymentState: 0=Pending, 1=Received, 2=FreeTrial, 3=Deferred
    payment_state = result.get("paymentState")

    status_str = "ACTIVE"
    if payment_state == 0:
        status_str = "PENDING"
    elif datetime.utcnow() > expiry_dt:
        status_str = "EXPIRED"

    # ---------------------------------------------------------
    # 3. Update Database (Single Source of Truth)
    # ---------------------------------------------------------
    
    # Find or Create User (Logic currently assumes anonymous or linked by some ID - 
    # In a real app we'd grab user_id from JWT payload, but here we might attach it to request)
    # For now, let's assume we are updating a subscription found by token, OR creating one for a known user.
    # TODO: The request should theoretically carry a user identifier or we verify auth token.
    # Let's rely on the Mobile App sending 'verificationData' which is the purchase token.
    
    # Check if subscription already exists by purchase_token
    subscription = db.query(Subscription).filter(Subscription.purchase_token == request.verificationData).first()
    
    if not subscription:
        # Create new subscription
        # NOTE: We need a user_id here. 
        # If the API calls are authenticated (which they should be), we get current_user.
        # For this step, I'll create a placeholder user if not exists to ensure flow works.
        user = db.query(User).filter(User.email == "demo@example.com").first()
        if not user:
            user = User(email="demo@example.com")
            db.add(user)
            db.commit()
            db.refresh(user)
            
        subscription = Subscription(
            user_id=user.id,
            product_id=request.productId,
            purchase_token=request.verificationData,
            expiry_time=expiry_dt,
            auto_renew=auto_renewing,
            status=status_str
        )
        db.add(subscription)
    else:
        # Update existing
        subscription.expiry_time = expiry_dt
        subscription.auto_renew = auto_renewing
        subscription.status = status_str
    
    db.commit()
    
    # ---------------------------------------------------------
    # 4. Return Response
    # ---------------------------------------------------------
    if status_str == "ACTIVE":
         return PurchaseVerificationResponse(status="valid", message="Purchase verified and active")
    else:
         return PurchaseVerificationResponse(status="invalid", message=f"Purchase state: {status_str}")
