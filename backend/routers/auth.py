from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
# import firebase_admin
# from firebase_admin import auth

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

# def verify_firebase_token(authorization: str = Header(...)):
#     token = authorization.replace("Bearer ", "")
#     try:
#         decoded_token = auth.verify_id_token(token)
#         return decoded_token
#     except Exception:
#         raise HTTPException(status_code=401, detail="Invalid authentication credentials")

@router.post("/login")
def login_sync(authorization: str = Header(...), db: Session = Depends(get_db)):
    """
    Called by mobile app after Firebase Login.
    Syncs the Firebase User ID/Email to our Postgres DB.
    """
    
    # MOCK TOKEN VERIFICATION for now (Real logic in comments above)
    token = authorization.replace("Bearer ", "")
    if not token or token == "null":
         raise HTTPException(status_code=401, detail="Missing Token")
         
    # Mock decoding (In reality, we'd get uid/email from verify_id_token)
    # We'll assume the token sent IS the email for this 'no-creds' demo
    fake_email = "demo@example.com" 
    if "@" in token:
        fake_email = token
        
    user = db.query(User).filter(User.email == fake_email).first()
    if not user:
        user = User(email=fake_email)
        db.add(user)
        db.commit()
        db.refresh(user)
        
    return {
        "user_id": user.id,
        "email": user.email,
        "status": "synced"
    }
