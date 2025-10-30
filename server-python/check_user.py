import sys
import os

# Add the server-python directory to sys.path
sys.path.insert(0, os.path.abspath('.'))

from database import SessionLocal, User

def check_user_data(email: str):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            print(f"User found for email: {email}")
            print(f"  Username: {user.username}")
            print(f"  Hashed Password: {user.hashed_password}")
            print(f"  Is Verified: {user.is_verified}")
            print(f"  OTP Code: {user.otp_code}")
            print(f"  OTP Expires At: {user.otp_expires_at}")
        else:
            print(f"No user found for email: {email}")
    finally:
        db.close()

if __name__ == "__main__":
    target_email = "cbu11849@laoia.com"
    check_user_data(target_email)
