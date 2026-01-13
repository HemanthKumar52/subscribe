from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Subscription
import base64
import json
from datetime import datetime

router = APIRouter(
    prefix="/rtdn",
    tags=["rtdn"],
)

@router.post("/")
async def receive_rtdn(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint for Google Cloud Pub/Sub to push notifications.
    """
    body = await request.json()
    
    # 1. Extract message from Pub/Sub format
    if not body or "message" not in body:
         raise HTTPException(status_code=400, detail="Invalid Pub/Sub message format")
         
    pubsub_message = body["message"]
    data_b64 = pubsub_message.get("data")
    
    if not data_b64:
        # Sometimes it's just a sync check
        return {"status": "ok"}
        
    # 2. Decode Data
    try:
        data_str = base64.b64decode(data_b64).decode("utf-8")
        data_json = json.loads(data_str)
    except Exception:
        raise HTTPException(status_code=400, detail="Could not decode message data")
        
    # 3. Check if it is a Subscription Notification
    # https://developer.android.com/google/play/billing/rtdn-reference
    if "subscriptionNotification" not in data_json:
        return {"status": "ignored", "reason": "Not a subscription notification"}
        
    sub_notif = data_json["subscriptionNotification"]
    notification_type = sub_notif.get("notificationType")
    purchase_token = sub_notif.get("purchaseToken")
    subscription_id = sub_notif.get("subscriptionId")
    
    print(f"Received RTDN: Type={notification_type} for Sub={subscription_id}")
    
    # 4. Handle Lifecycle Events
    # (1) SUBSCRIPTION_RECOVERED, (2) SUBSCRIPTION_RENEWED, (3) SUBSCRIPTION_CANCELED, etc.
    # Ideally, we trigger a re-verification with the Google Play API here to get the authoritative state.
    # For now, we update local state based on the signal if possible, or mark for sync.
    
    subscription = db.query(Subscription).filter(Subscription.purchase_token == purchase_token).first()
    
    if subscription:
        if notification_type == 2: # SUBSCRIPTION_RENEWED
            # We should technically Fetch fresh expiry from API, but let's assume active
            subscription.status = "ACTIVE"
            subscription.auto_renew = True
        elif notification_type == 3: # SUBSCRIPTION_CANCELED (Voluntary)
            subscription.auto_renew = False
        elif notification_type == 12: # SUBSCRIPTION_REVOKED
            subscription.status = "REVOKED"
        elif notification_type == 5: # SUBSCRIPTION_ON_HOLD
            subscription.status = "ON_HOLD"
            
        db.commit()
    
    return {"status": "processed"}
