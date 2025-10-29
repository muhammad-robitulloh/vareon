import logging
from datetime import datetime, timedelta
import os
import sys
import argparse
import time

from fastapi import FastAPI, Depends, HTTPException, status, Request, Response, WebSocket, WebSocketDisconnect
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

# Add the script's directory to sys.path for relative imports if run directly
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# Now relative imports should work if main.py is run directly
from auth import get_password_hash, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user, generate_otp, send_verification_email
from database import Base, engine, SessionLocal, setup_default_user, get_user_from_db, create_user_in_db, get_db, User as DBUser, get_user_by_username_or_email # Alias User from database to DBUser
from schemas import Token, User, UserCreate, UserBase
import llm_service # Import the new LLM service

# --- Logging Setup ---
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Vareon Backend",
    description="Backend server for Vareon, with authentication and AI/ML integration.",
    version="0.1.0"
)

# --- CORS Middleware ---
# Adjust allow_origins as needed for your frontend deployment
origins = [
    "http://localhost",
    "http://localhost:3000", # React development server
    "http://127.0.0.1:3000",
    "http://localhost:8000", # Frontend served by Node.js server
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Custom Logging Middleware ---
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request details
    logger.info(f"[API Request] Method: {request.method}, URL: {request.url}, Headers: {request.headers.get('user-agent')}")
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    # Log response details
    logger.info(f"[API Response] Method: {request.method}, URL: {request.url}, Status: {response.status_code}, Time: {process_time:.4f}s")
    
    return response

# --- Application Startup Event ---
@app.on_event("startup")
async def startup_event():
    logger.info("Application startup event triggered.")
    # Create database tables
    Base.metadata.create_all(bind=engine)
    # Setup a default user for testing purposes
    db = SessionLocal()
    try:
        setup_default_user(db, get_password_hash)
    finally:
        db.close()

# --- API Routes ---
@app.get("/health")
async def health_check():
    logger.info("Health check endpoint accessed.")
    return {"status": "ok"}

@app.post("/api/register", response_model=User)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_from_db(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    db_email = db.query(DBUser).filter(DBUser.email == user.email).first()
    if db_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    otp_code = generate_otp()
    otp_expires_at = datetime.utcnow() + timedelta(minutes=15) # OTP valid for 15 minutes

    new_user = create_user_in_db(db, user.username, hashed_password, user.email, otp_code, otp_expires_at)
    
    try:
        send_verification_email(new_user.email, otp_code)
    except HTTPException as e:
        # If email sending fails, we might want to delete the user or mark for retry
        logger.error(f"Failed to send verification email for user {new_user.username}: {e.detail}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User registered, but failed to send verification email.")

    return new_user

class VerifyEmailRequest(BaseModel):
    email: str
    otp_code: str

@app.post("/api/verify-email")
async def verify_email(request: VerifyEmailRequest, db: Session = Depends(get_db)):
    user = db.query(DBUser).filter(DBUser.email == request.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    if user.is_verified:
        return {"message": "Email already verified.", "status": "success"}

    if not user.otp_code or user.otp_code != request.otp_code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP.")

    if user.otp_expires_at < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP expired.")

    user.is_verified = True
    user.otp_code = None
    user.otp_expires_at = None
    db.commit()
    db.refresh(user)

    return {"message": "Email verified successfully!", "status": "success"}

@app.post("/api/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_username_or_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please check your email for a verification code."
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"username": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/dashboard", response_model=User)
async def read_dashboard(current_user: User = Depends(get_current_user)):
    return current_user

class SystemStatusModule(BaseModel):
    status: str
    uptime: str
    activeChats: int = 0
    messagesProcessed: int = 0
    avgResponseTime: str = "0s"
    activeAgents: int = 0
    jobsCompleted: int = 0
    devicesConnected: int = 0
    activeWorkflows: int = 0
    datasetsManaged: int = 0
    searchQueriesProcessed: int = 0
    modelsActive: int = 0
    routingRules: int = 0
    requestsRouted: int = 0

class SystemStatus(BaseModel):
    arcana: SystemStatusModule
    myntrix: SystemStatusModule
    neosyntis: SystemStatusModule
    cognisys: SystemStatusModule

@app.get("/api/system/status", response_model=SystemStatus)
async def get_system_status():
    # In a real application, this would fetch actual system metrics
    # For now, return mock data similar to the frontend's mockApi.ts
    return {
        "arcana": {
            "status": "online",
            "uptime": "99.9%",
            "activeChats": 12,
            "messagesProcessed": 1543,
            "avgResponseTime": "1.2s",
        },
        "myntrix": {
            "status": "online",
            "uptime": "98.7%",
            "activeAgents": 8,
            "jobsCompleted": 234,
            "devicesConnected": 3,
        },
        "neosyntis": {
            "status": "online",
            "uptime": "99.5%",
            "activeWorkflows": 5,
            "datasetsManaged": 18,
            "searchQueriesProcessed": 892,
        },
        "cognisys": {
            "status": "online",
            "uptime": "100%",
            "modelsActive": 12,
            "routingRules": 24,
            "requestsRouted": 3421,
        },
    }


# --- Chat Interface API ---
class ChatRequest(BaseModel):
    message: str

@app.post("/api/chat")
async def chat_with_llm(request: ChatRequest, current_user: User = Depends(get_current_user)):
    user_id = current_user.username # Use username as user_id for conversation history
    llm_response = await llm_service.get_openrouter_completion(user_id, request.message)
    return {"response": llm_response}

@app.post("/api/chat/demo")
async def chat_with_llm_demo(request: ChatRequest):
    user_id = "demo_user" # Hardcoded user_id for demo purposes
    llm_response = await llm_service.get_openrouter_completion(user_id, request.message)
    return {"response": llm_response}

@app.post("/api/chat/clear")
async def clear_chat_history(current_user: User = Depends(get_current_user)):
    user_id = current_user.username
    llm_service.clear_conversation_history(user_id)
    return {"message": "Chat history cleared."}

# --- WebSocket Endpoint for Interactive Shell ---
@app.websocket("/ws/shell/{chat_id}")
async def websocket_shell(websocket: WebSocket, chat_id: int):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # For now, just echo back the message or log it
            logger.info(f"[WebSocket] Received from client {chat_id}: {data}")
            await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        logger.info(f"[WebSocket] Client {chat_id} disconnected.")
    except Exception as e:
        logger.error(f"[WebSocket] Error in websocket_shell for client {chat_id}: {e}")

# --- Static Files and Frontend Serving ---
# Determine the path to the frontend build directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir) # This is /data/data/com.termux/files/home/VE/Vareon
frontend_build_dir = os.path.join(project_root, 'dist', 'public') # Corrected path for build output

# Mount the static files directory (e.g., assets, favicon, etc.)
# We are mounting the entire build directory, as assets seem to be directly under it.
app.mount("/assets", StaticFiles(directory=os.path.join(frontend_build_dir, "assets")), name="assets")
app.mount("/favicon.ico", StaticFiles(directory=frontend_build_dir), name="favicon") # For favicon directly in root
app.mount("/logo192.png", StaticFiles(directory=frontend_build_dir), name="logo192") # For logo directly in root
app.mount("/logo512.png", StaticFiles(directory=frontend_build_dir), name="logo512") # For logo directly in root
app.mount("/manifest.json", StaticFiles(directory=frontend_build_dir), name="manifest") # For manifest directly in root


@app.get("/{rest_of_path:path}")
async def serve_react_app(request: Request, rest_of_path: str):
    """
    Serves the React application.
    This endpoint catches all GET requests that were not handled by other routes.
    It serves the 'index.html' file, which is the entry point for the React app.
    The React router will then handle the specific path on the client-side.
    """
    index_path = os.path.join(frontend_build_dir, 'index.html')
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        logger.error(f"Frontend entry point not found: {index_path}")
        raise HTTPException(status_code=404, detail="Frontend not found. Please build the frontend first.")

# --- To run this app directly for development ---
if __name__ == "__main__":
    import uvicorn

    # Parse arguments if run directly
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8001)
    args, unknown = parser.parse_known_args() # Use parse_known_args to ignore args not defined here

    uvicorn.run(app, host=args.host, port=args.port)