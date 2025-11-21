from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, Request
from fastapi.exceptions import RequestValidationError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
from motor.motor_asyncio import AsyncIOMotorClient
import os
import secrets
import re
import time
import json
from collections import defaultdict
import httpx
from dotenv import load_dotenv
import random
import string
import asyncio
import logging
from pathlib import Path
import uuid

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Import AI task service
from ai_task_service import generate_daily_tasks_for_mode, generate_weekly_tasks_for_mode

# Import AI personalization service (NEW: AI Messages, Gifts, Date Planning)
from ai_personalization_service import (
    generate_ai_message,
    get_ai_gift_recommendations,
    plan_ai_date
)

# Import Enhanced Calendar Service
from enhanced_calendar_service import enhanced_calendar_service

# Import Subscription Service
from subscription_service import subscription_service, SubscriptionInfo

# Import Push Notification Service
from push_notification_service import push_notification_service

# Import Email Service
from email_service import email_service

# Import Gamification Service
from gamification_service import init_gamification_service, LEVEL_THRESHOLDS, STORE_ITEMS

# Import Relationship Tasks Database
from relationship_tasks_database import get_tasks_for_relationship_mode

# Rate limiting storage
rate_limit_storage = defaultdict(list)
failed_attempts = defaultdict(list)

# Security configuration
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production-min-32-chars-long')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30

# OAuth configuration - Removed Google OAuth (using Emergent OAuth instead)
# Apple OAuth configuration (for future implementation)


# SMS configuration (Twilio or similar)
SMS_PROVIDER_API_KEY = os.environ.get("SMS_PROVIDER_API_KEY", "")
SMS_PROVIDER_BASE_URL = os.environ.get("SMS_PROVIDER_BASE_URL", "")

# Database configuration
mongo_url = os.environ['MONGO_URL']
db_name = os.environ.get('DB_NAME', 'pookie4u')

# Initialize MongoDB client with connection settings for production
# serverSelectionTimeoutMS: How long to wait for server selection
# connectTimeoutMS: How long to wait for a connection to be established
# maxPoolSize: Maximum number of connections in the pool
client = AsyncIOMotorClient(
    mongo_url,
    serverSelectionTimeoutMS=10000,  # 10 seconds
    connectTimeoutMS=10000,  # 10 seconds  
    maxPoolSize=50,
    minPoolSize=10
)
db = client[db_name]

# Initialize FastAPI app
app = FastAPI(title="Pookie4u Authentication API", version="1.0.0")
api_router = APIRouter(prefix="/api")

# Startup event to ensure database indexes
@app.on_event("startup")
async def startup_db_indexes():
    """Create database indexes on startup for data integrity"""
    try:
        # PHASE 3: Create unique index on Emergent OAuth ID to prevent duplicate accounts
        await db.users.create_index(
            "oauth_providers.emergent.emergent_id",
            unique=True,
            sparse=True,  # Allow users without Emergent OAuth
            name="emergent_id_unique"
        )
        print("✅ Database indexes created successfully")
        
        # Initialize gamification service
        global gamification_service
        gamification_service = init_gamification_service(db)
        print("✅ Gamification service initialized")
        
    except Exception as e:
        print(f"⚠️  Startup warning: {e}")

# Health check endpoint (for deployment monitoring)
@app.get("/health", response_model=None)
async def health_check():
    """
    Health check endpoint for deployment systems
    Returns 200 even if database is temporarily unavailable during startup
    """
    db_status = "unknown"
    try:
        # Check if database is accessible with a short timeout
        await asyncio.wait_for(
            db.users.find_one({}, {"_id": 1}),
            timeout=2.0  # 2 second timeout for health check
        )
        db_status = "connected"
    except asyncio.TimeoutError:
        db_status = "timeout"
        print("⚠️ Health check: Database connection timeout")
    except Exception as e:
        db_status = "error"
        print(f"⚠️ Health check: Database error: {e}")
    
    # Always return 200 for app health, include DB status in response
    return JSONResponse(
        content={
            "status": "healthy",
            "service": "pookie4u-api",
            "database": db_status,
            "timestamp": datetime.utcnow().isoformat()
        },
        status_code=200,
        media_type="application/json"
    )
    
@app.get("/health/ready", response_model=None)
async def readiness_check():
    """
    Readiness check - only returns 200 when database is fully connected
    Use this for Kubernetes readiness probes
    """
    try:
        # Check if database is accessible
        await db.users.find_one({}, {"_id": 1})
        return JSONResponse(
            content={
                "status": "ready",
                "service": "pookie4u-api",
                "database": "connected",
                "timestamp": datetime.utcnow().isoformat()
            },
            status_code=200,
            media_type="application/json"
        )
    except Exception as e:
        return JSONResponse(
            content={
                "status": "not_ready",
                "service": "pookie4u-api",
                "database": "disconnected",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            },
            status_code=503,
            media_type="application/json"
        )

@api_router.get("/health", response_model=None)
async def api_health_check():
    """Health check endpoint at /api/health for Emergent deployment"""
    try:
        # Check if database is accessible
        await db.users.find_one({}, {"_id": 1})
        return JSONResponse(
            content={
                "status": "healthy",
                "service": "pookie4u-api",
                "database": "connected",
                "timestamp": datetime.utcnow().isoformat()
            },
            status_code=200,
            media_type="application/json"
        )
    except Exception as e:
        return JSONResponse(
            content={
                "status": "unhealthy",
                "service": "pookie4u-api",
                "database": "disconnected",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            },
            status_code=503,
            media_type="application/json"
        )

# Add custom exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Convert complex Pydantic validation errors to simple string messages"""
    error_messages = []
    for error in exc.errors():
        field_name = " -> ".join([str(loc) for loc in error["loc"] if loc != "body"])
        field_name = field_name or "field"
        
        if error["type"] == "missing":
            error_messages.append(f"{field_name.title()} is required")
        elif error["type"] == "value_error":
            error_messages.append(f"{field_name.title()}: {error.get('msg', 'Invalid value')}")
        elif error["type"] == "type_error":
            error_messages.append(f"{field_name.title()} must be valid format")
        else:
            # Generic fallback for other error types
            error_messages.append(f"{field_name.title()}: {error.get('msg', 'Invalid input')}")
    
    # Join all error messages with semicolon, limit to first 3 to avoid overwhelming
    simple_error = "; ".join(error_messages[:3])
    return JSONResponse(
        status_code=422,
        content={"detail": simple_error}
    )

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security utilities
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def generate_otp() -> str:
    """Generate a 6-digit OTP"""
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])

def generate_device_id() -> str:
    """Generate a secure device identifier"""
    return secrets.token_urlsafe(32)

def generate_referral_code() -> str:
    """Generate a unique referral code in format POO-XXXXXX"""
    characters = string.ascii_uppercase + string.digits
    code = ''.join(random.choices(characters, k=6))
    return f"POO-{code}"

# Rate limiting functions
def check_rate_limit(key: str, max_attempts: int, window_minutes: int) -> bool:
    """Check if rate limit is exceeded"""
    now = time.time()
    window_start = now - (window_minutes * 60)
    
    # Clean old entries
    rate_limit_storage[key] = [
        timestamp for timestamp in rate_limit_storage[key] 
        if timestamp > window_start
    ]
    
    if len(rate_limit_storage[key]) >= max_attempts:
        return False
    
    rate_limit_storage[key].append(now)
    return True

# Authentication models will be defined in the MODELS section below

# Security middleware
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if user_id is None or token_type != "access":
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await db.users.find_one({"_id": user_id})
    if user is None:
        raise credentials_exception
    
    return user

# SMS utility functions
async def send_sms(phone: str, message: str) -> bool:
    """Send SMS via provider (implement with Twilio/MessageBird)"""
    # For development, just log the OTP
    print(f"SMS to {phone}: {message}")
    
    # In production, implement actual SMS sending:
    # try:
    #     async with httpx.AsyncClient() as client:
    #         response = await client.post(
    #             f"{SMS_PROVIDER_BASE_URL}/send",
    #             json={
    #                 "to": phone,
    #                 "message": message,
    #             },
    #             headers={"Authorization": f"Bearer {SMS_PROVIDER_API_KEY}"}
    #         )
    #         return response.status_code == 200
    # except Exception as e:
    #     print(f"SMS send error: {e}")
    #     return False
    
    return True  # Simulate success for development

# OAuth utility functions
async def verify_apple_token(id_token: str) -> Optional[Dict[str, Any]]:
    """Verify Apple ID token and extract user info"""
    # Apple token verification is more complex and requires fetching Apple's public keys
    # For now, return a mock implementation
    # In production, implement proper Apple JWT verification
    try:
        # Decode without verification for development
        import base64
        import json
        
        # Split the JWT and decode the payload
        parts = id_token.split('.')
        if len(parts) != 3:
            return None
            
        payload = parts[1]
        # Add padding if needed
        payload += '=' * (4 - len(payload) % 4)
        decoded = base64.urlsafe_b64decode(payload)
        user_info = json.loads(decoded)
        
        return {
            "id": user_info.get("sub"),
            "email": user_info.get("email"),
            "name": user_info.get("name"),  # May be None after first login
            "email_verified": user_info.get("email_verified", False)
        }
    except Exception as e:
        print(f"Apple token verification error: {e}")
    
    return None

# ============================================================================
# MODELS
# ============================================================================

# Legacy authentication models (kept for backward compatibility)
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    id: str
    email: str
    name: str
    created_at: datetime
    profile_completed: bool = False

# Enhanced authentication models
class PhoneNumber(BaseModel):
    country_code: str = Field(..., pattern=r'^\+\d{1,4}$')
    number: str = Field(..., pattern=r'^\d{7,15}$')
    
    @property
    def full_number(self) -> str:
        return f"{self.country_code}{self.number}"

class SendOTPRequest(BaseModel):
    phone: PhoneNumber
    device_id: Optional[str] = None

class VerifyOTPRequest(BaseModel):
    phone: PhoneNumber
    otp: str = Field(..., pattern=r'^\d{6}$')
    device_id: Optional[str] = None
    name: Optional[str] = None

class OAuthCallbackRequest(BaseModel):
    provider: str = Field(..., pattern=r'^(google|apple)$')
    id_token: str
    access_token: Optional[str] = None
    device_id: Optional[str] = None

class LinkAccountRequest(BaseModel):
    provider: str = Field(..., pattern=r'^(phone|google|apple)$')
    credential: Dict[str, Any]

class UnlinkAccountRequest(BaseModel):
    provider: str = Field(..., pattern=r'^(phone|google|apple)$')

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = ACCESS_TOKEN_EXPIRE_MINUTES * 60
    user: Dict[str, Any]

# Emergent OAuth Models
class EmergentSessionData(BaseModel):
    id: str
    email: str
    name: str
    picture: Optional[str] = None
    session_token: str

class UserSession(BaseModel):
    user_id: str
    session_token: str
    expires_at: datetime
    created_at: datetime

class EnhancedUserProfile(BaseModel):
    id: str
    phone: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None
    picture: Optional[str] = None
    linked_providers: List[str] = []
    created_at: datetime
    last_login: Optional[datetime] = None
    verified: bool = False

# Application models
class Winner(BaseModel):
    id: str
    user_name: str
    prize_amount: Optional[int] = None
    prize_type: str  # "weekly_cash", "monthly_trip"
    week_number: Optional[int] = None
    month: Optional[str] = None
    tasks_completed: int
    awarded_date: datetime
    description: str

class ProfileImageUpdate(BaseModel):
    profile_image: str  # base64 encoded image

class PartnerProfile(BaseModel):
    name: str = ""
    birthday: Optional[str] = None  # Accept DD/MM/YYYY format
    anniversary: Optional[str] = None  # Accept DD/MM/YYYY format  
    favorite_color: str = ""
    favorite_food: str = ""
    favorite_flower: str = ""
    favorite_brand: str = ""
    dress_size: str = ""
    ring_size: str = ""
    perfume_preference: str = ""
    top_size: str = ""
    jeans_size: str = ""
    notes: str = ""
    additional_notes: str = ""

class RelationshipMode(BaseModel):
    mode: Literal["SAME_HOME", "DAILY_IRL", "LONG_DISTANCE"]

class TaskComplete(BaseModel):
    task_id: str

class TaskCompleteResponse(BaseModel):
    success: bool
    message: str
    points_earned: int
    total_points: int

class TaskGenerationMetadata(BaseModel):
    generated_at: datetime
    ai_model: str
    prompt_hash: str
    version: str

class AITask(BaseModel):
    id: str
    title: str
    description: str
    category: str  # Communication, ThoughtfulGesture, MicroActivity, PhysicalActivity
    points: int
    estimated_time_minutes: int
    difficulty: str  # very_easy, easy
    tips: str
    is_physical: bool  # True for weekly physical tasks
    relationship_mode: str
    task_type: str  # daily, weekly
    generation_metadata: TaskGenerationMetadata
    completed: bool = False
    completed_at: Optional[datetime] = None

class TaskGenerationRequest(BaseModel):
    relationship_mode: str
    task_type: str  # daily, weekly
    count: Optional[int] = None
    use_profile_data: bool = False

class ReminderSettings(BaseModel):
    enabled: bool = True
    days_before: int = 10  # Start reminders X days before event
    times_per_day: int = 2  # How many times per day
    reminder_times: List[str] = Field(default_factory=lambda: ["10:00", "17:00"])  # 24-hour format
    
class CustomEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    date: datetime
    recurring: bool = False
    user_id: str = ""  # Will be set by backend
    description: Optional[str] = ""
    category: str = "custom"
    importance: str = "medium"
    reminder_settings: ReminderSettings = Field(default_factory=ReminderSettings)
    
class EventUpdateRequest(BaseModel):
    name: Optional[str] = None
    date: Optional[datetime] = None
    description: Optional[str] = None
    importance: Optional[str] = None
    reminder_settings: Optional[ReminderSettings] = None

class UserProfile(BaseModel):
    id: str
    email: str
    name: str
    phone: Optional[str] = None  # Mobile/phone number
    relationship_mode: str = "SAME_HOME"
    partner_profile: PartnerProfile = Field(default_factory=PartnerProfile)
    total_points: int = 0
    current_level: int = 1
    current_streak: int = 0
    longest_streak: int = 0
    tasks_completed: int = 0
    badges: List[str] = Field(default_factory=list)
    profile_completed: bool = False
    # Gamification System (NEW)
    points_spent: int = 0  # Track points used in store
    available_points: int = 0  # total_points - points_spent
    love_language: Optional[str] = None  # Unlocked at Level 5
    last_task_completion_date: Optional[datetime] = None  # For streak tracking
    bailout_used_this_month: bool = False  # For Bailout Streak Save
    last_bailout_date: Optional[datetime] = None  # Track when bailout was used
    daily_tasks_completed_today: int = 0  # Track progress toward all 3 tasks
    last_daily_task_reset: Optional[datetime] = None  # Track daily reset
    profile_image: Optional[str] = None  # base64 encoded image
    created_at: datetime
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    # Subscription fields
    subscription_type: str = "none"  # none, trial, monthly, half_yearly
    subscription_status: str = "inactive"  # inactive, active, expired, cancelled
    subscription_start_date: Optional[datetime] = None
    subscription_end_date: Optional[datetime] = None
    trial_started: bool = False
    # Push notification fields
    push_token: Optional[str] = None
    push_token_updated_at: Optional[datetime] = None
    notification_preferences: Dict[str, bool] = Field(default_factory=dict)

# ============================================================================
# AUTHENTICATION HELPERS
# ============================================================================

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Emergent OAuth Session Management Functions
async def get_user_from_session_token(session_token: str):
    """Get user from Emergent OAuth session token"""
    from datetime import timezone
    
    print(f"🔍 Looking for session token: {session_token[:20]}...")
    
    # Find session in database
    session = await db.user_sessions.find_one({"session_token": session_token})
    if not session:
        print(f"❌ Session not found in database")
        return None
    
    print(f"✅ Session found, user_id: {session['user_id']}")
    
    # Check if session is expired
    expires_at = session["expires_at"]
    now = datetime.now(timezone.utc)
    
    # Make sure both datetimes are timezone-aware for comparison
    if expires_at.tzinfo is None:
        # If expires_at is naive, assume it's UTC
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    if expires_at < now:
        print(f"❌ Session expired")
        # Delete expired session
        await db.user_sessions.delete_one({"session_token": session_token})
        return None
    
    print(f"✅ Session valid, fetching user...")
    # Get user from database
    user = await db.users.find_one({"_id": session["user_id"]})
    if user:
        print(f"✅ User found: {user.get('email')}")
    else:
        print(f"❌ User not found for user_id: {session['user_id']}")
    return user

async def get_current_user_flexible(request: Request):
    """
    Get current user from either:
    1. Session token (cookie or header) - Emergent OAuth
    2. JWT Bearer token - Email/Password or Google OAuth
    """
    from datetime import timezone
    
    print(f"🔐 get_current_user_flexible called")
    print(f"📋 Headers: {dict(request.headers)}")
    print(f"🍪 Cookies: {request.cookies}")
    
    # Try session_token from cookie first
    session_token = request.cookies.get("session_token")
    print(f"🍪 Session token from cookie: {session_token[:20] if session_token else 'None'}...")
    
    # If not in cookie, try Authorization header as fallback
    if not session_token:
        auth_header = request.headers.get("authorization", "")
        print(f"🔑 Authorization header: {auth_header[:50] if auth_header else 'None'}...")
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            # Check if it's a session_token (not JWT format)
            if not token.startswith("eyJ"):  # JWT tokens start with "eyJ"
                session_token = token
                print(f"✅ Found session token in Authorization header")
    
    # If we have a session_token, validate it
    if session_token:
        print(f"🔍 Validating session token...")
        user = await get_user_from_session_token(session_token)
        if user:
            print(f"✅ Session token validated successfully")
            return user
        print(f"⚠️ Session token invalid, trying JWT...")
        # If session token is invalid/expired, continue to try JWT
    
    # Fall back to JWT authentication
    auth_header = request.headers.get("authorization", "")
    if not auth_header.startswith("Bearer "):
        print(f"❌ No valid Bearer token found")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    token = auth_header.split(" ")[1]
    
    # If we already tried this token as a session token, it's definitely invalid
    if token == session_token:
        print(f"❌ Token already tried as session token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    print(f"🔑 Trying JWT validation...")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            print(f"❌ JWT payload missing 'sub'")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
    except JWTError as e:
        print(f"❌ JWT decode error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    user = await db.users.find_one({"_id": user_id})
    if user is None:
        print(f"❌ User not found for user_id: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    print(f"✅ JWT validated successfully")
    return user

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
):
    """
    Get current user with support for both JWT and session tokens.
    This is a wrapper around get_current_user_flexible for backward compatibility.
    """
    # Get request from FastAPI context
    from fastapi import Request
    from contextvars import ContextVar
    from starlette.middleware.base import BaseHTTPMiddleware
    import inspect
    
    # Try to get request from call stack
    frame = inspect.currentframe()
    request = None
    try:
        while frame:
            frame = frame.f_back
            if frame and "request" in frame.f_locals:
                potential_request = frame.f_locals["request"]
                if hasattr(potential_request, "headers") and hasattr(potential_request, "cookies"):
                    request = potential_request
                    break
    finally:
        del frame
    
    if request is None:
        # Fallback to JWT-only authentication
        if not credentials or not credentials.credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        
        token = credentials.credentials
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials"
                )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        
        user = await db.users.find_one({"_id": user_id})
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        return user
    
    return await get_current_user_flexible(request)

# ============================================================================
# TASK DATA
# ============================================================================

DAILY_TASKS = {
    "SAME_HOME": [
        {"id": "home_1", "title": "Leave a sweet note on their pillow", "category": "Romantic Acts", "points": 5},
        {"id": "home_2", "title": "Cook their favorite breakfast", "category": "Food & Outings", "points": 5},
        {"id": "home_3", "title": "Give them a 5-minute shoulder massage", "category": "Home Gestures", "points": 5},
        {"id": "home_4", "title": "Watch a movie together cuddled up", "category": "Experiences", "points": 5},
        {"id": "home_5", "title": "Do the dishes without being asked", "category": "Home Gestures", "points": 5},
        {"id": "home_6", "title": "Dance together in the living room", "category": "Experiences", "points": 5},
        {"id": "home_7", "title": "Surprise them with their favorite snack", "category": "Gifts", "points": 5},
        {"id": "home_8", "title": "Give them a warm hug from behind", "category": "Romantic Acts", "points": 5},
        {"id": "home_9", "title": "Make them coffee/tea just how they like it", "category": "Home Gestures", "points": 5},
        {"id": "home_10", "title": "Tell them three things you love about them", "category": "Romantic Acts", "points": 5}
    ],
    "DAILY_IRL": [
        {"id": "irl_1", "title": "Bring them their favorite coffee during lunch", "category": "Food & Outings", "points": 5},
        {"id": "irl_2", "title": "Send a sweet text during their busy day", "category": "Romantic Acts", "points": 5},
        {"id": "irl_3", "title": "Plan a surprise lunch date", "category": "Food & Outings", "points": 5},
        {"id": "irl_4", "title": "Walk them to their car/bus stop", "category": "Experiences", "points": 5},
        {"id": "irl_5", "title": "Give them a small flower or card", "category": "Gifts", "points": 5},
        {"id": "irl_6", "title": "Hold their hand during your walk", "category": "Romantic Acts", "points": 5},
        {"id": "irl_7", "title": "Take a cute selfie together", "category": "Experiences", "points": 5},
        {"id": "irl_8", "title": "Compliment them in front of friends", "category": "Romantic Acts", "points": 5},
        {"id": "irl_9", "title": "Share your favorite snack with them", "category": "Food & Outings", "points": 5},
        {"id": "irl_10", "title": "Give them a surprise hug when you meet", "category": "Romantic Acts", "points": 5}
    ],
    "LONG_DISTANCE": [
        {"id": "ld_1", "title": "Send them a good morning voice message", "category": "Romantic Acts", "points": 5},
        {"id": "ld_2", "title": "Watch a movie together online", "category": "Experiences", "points": 5},
        {"id": "ld_3", "title": "Send them a photo of your day", "category": "Experiences", "points": 5},
        {"id": "ld_4", "title": "Order food delivery to their place", "category": "Food & Outings", "points": 5},
        {"id": "ld_5", "title": "Send them a handwritten letter photo", "category": "Romantic Acts", "points": 5},
        {"id": "ld_6", "title": "Have a video call dinner date", "category": "Food & Outings", "points": 5},
        {"id": "ld_7", "title": "Send them a surprise online gift", "category": "Gifts", "points": 5},
        {"id": "ld_8", "title": "Play an online game together", "category": "Experiences", "points": 5},
        {"id": "ld_9", "title": "Send them a playlist of songs that remind you of them", "category": "Romantic Acts", "points": 5},
        {"id": "ld_10", "title": "Plan your next meeting together", "category": "Experiences", "points": 5}
    ]
}

WEEKLY_TASKS = {
    "SAME_HOME": [
        {"id": "w_home_1", "title": "Plan and execute a surprise date night at home", "category": "Experiences", "points": 25},
        {"id": "w_home_2", "title": "Cook an elaborate meal together", "category": "Food & Outings", "points": 25},
        {"id": "w_home_3", "title": "Create a photo album of your memories", "category": "Romantic Acts", "points": 25},
        {"id": "w_home_4", "title": "Give each other spa treatments at home", "category": "Experiences", "points": 25}
    ],
    "DAILY_IRL": [
        {"id": "w_irl_1", "title": "Plan a weekend getaway or day trip", "category": "Experiences", "points": 25},
        {"id": "w_irl_2", "title": "Try a new restaurant together", "category": "Food & Outings", "points": 25},
        {"id": "w_irl_3", "title": "Attend a local event or concert together", "category": "Experiences", "points": 25},
        {"id": "w_irl_4", "title": "Take a couples photoshoot", "category": "Experiences", "points": 25}
    ],
    "LONG_DISTANCE": [
        {"id": "w_ld_1", "title": "Send them a surprise care package", "category": "Gifts", "points": 25},
        {"id": "w_ld_2", "title": "Have a 3-hour video call date with activities", "category": "Experiences", "points": 25},
        {"id": "w_ld_3", "title": "Write and send them a heartfelt letter", "category": "Romantic Acts", "points": 25},
        {"id": "w_ld_4", "title": "Plan your next visit in detail together", "category": "Experiences", "points": 25}
    ]
}

GIFT_IDEAS = [
    # Original Romantic Gifts
    {
        "id": "1", 
        "name": "Personalized Photo Frame", 
        "category": "Romantic", 
        "price_range": "Under ₹500", 
        "link": "https://amzn.to/romantic-photo-frame", 
        "description": "Beautiful personalized frame for your special memories together",
        "image": "https://m.media-amazon.com/images/I/71KH+VqP6QL._AC_UL320_.jpg"
    },
    {
        "id": "2", 
        "name": "Couple's Coffee Mug Set", 
        "category": "Home", 
        "price_range": "Under ₹500", 
        "link": "https://amzn.to/couple-mugs-set", 
        "description": "Matching mugs with romantic quotes for your morning coffee together",
        "image": "https://m.media-amazon.com/images/I/61Xl0t8dXDL._AC_UL320_.jpg"
    },
    {
        "id": "3", 
        "name": "Romantic Scented Candles Set", 
        "category": "Romantic", 
        "price_range": "Under ₹1000", 
        "link": "https://amzn.to/scented-candles-romantic", 
        "description": "Set the perfect romantic mood with beautiful aromatic candles",
        "image": "https://m.media-amazon.com/images/I/71h8Mz+UhTL._AC_UL320_.jpg"
    },
    {
        "id": "4", 
        "name": "Customized Name Necklace", 
        "category": "Jewelry", 
        "price_range": "₹500-₹1500", 
        "link": "https://amzn.to/personalized-necklace", 
        "description": "Elegant personalized necklace with her name to make her feel special",
        "image": "https://m.media-amazon.com/images/I/61kZnB4nzrL._AC_UL320_.jpg"
    },
    {
        "id": "5", 
        "name": "Romantic Rose Bear with LED Lights", 
        "category": "Romantic", 
        "price_range": "₹500-₹1000", 
        "link": "https://amzn.to/rose-teddy-bear", 
        "description": "Adorable rose teddy bear with LED lights - a forever gift that never wilts",
        "image": "https://m.media-amazon.com/images/I/71tQfUQh8OL._AC_UL320_.jpg"
    },
    {
        "id": "6", 
        "name": "Gourmet Chocolate Gift Box", 
        "category": "Chocolates", 
        "price_range": "Under ₹1000", 
        "link": "https://amzn.to/premium-chocolates", 
        "description": "Premium assorted chocolates beautifully packaged for your sweet moments",
        "image": "https://m.media-amazon.com/images/I/81Cm7HlS6yL._AC_UL320_.jpg"
    },
    
    # Chocolates & Sweets
    {
        "id": "7",
        "name": "Cadbury Diwali Chocolate Potli 283g",
        "category": "Chocolates",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/Cadbury-Diwali-Chocolate-Potli-283g/dp/B07VWGZL7N",
        "description": "Beautiful Diwali chocolate potli gift pack",
        "image": "https://images.pexels.com/photos/21581347/pexels-photo-21581347.jpeg?auto=compress&cs=tinysrgb&w=400"
    },
    {
        "id": "8",
        "name": "Ferrero Rocher 16 Pieces",
        "category": "Chocolates",
        "price_range": "Under ₹1000",
        "link": "https://www.amazon.in/Ferrero-78205-Rocher-16-Pieces/dp/B00BYQEIL6",
        "description": "Premium Ferrero Rocher chocolate gift box",
        "image": "https://images.unsplash.com/photo-1644766532391-e5fc3ed1bbb0?w=400&q=80"
    },
    {
        "id": "9",
        "name": "Ferrero Rocher Pack 24 Pieces",
        "category": "Chocolates",
        "price_range": "₹1000-₹1500",
        "link": "https://www.amazon.in/Ferrero-Rocher-Pack-24-Pieces/dp/B07G9GDQJD",
        "description": "Luxurious 24-piece Ferrero Rocher collection",
        "image": "https://images.pexels.com/photos/7407224/pexels-photo-7407224.jpeg?auto=compress&cs=tinysrgb&w=400"
    },
    {
        "id": "10",
        "name": "Omay Foods Superman Dry Fruits Pack",
        "category": "Chocolates",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/Omay-Foods-Fathers-SUPERMAN-Fruits/dp/B07SG8THWH",
        "description": "Healthy dry fruits gift pack for special occasions",
        "image": "https://m.media-amazon.com/images/I/71rBp9Y+fJL._AC_UL320_.jpg"
    },
    {
        "id": "11",
        "name": "Ferrero Rocher Premium Collection",
        "category": "Chocolates",
        "price_range": "₹1500-₹2000",
        "link": "https://www.amazon.in/SFU-Com-Ferrero-Rocher-Pieces/dp/B07G9N5WHW",
        "description": "Elegant Ferrero Rocher premium gift collection",
        "image": "https://m.media-amazon.com/images/I/61hHOjJO3TL._AC_UL320_.jpg"
    },
    {
        "id": "12",
        "name": "Cadbury Celebrations Rich Dry Fruit Chocolate",
        "category": "Chocolates",
        "price_range": "Under ₹1000",
        "link": "https://www.amazon.in/Cadbury-Celebrations-Rich-Fruit-Chocolate/dp/B07HR1YB9Y",
        "description": "Premium Cadbury chocolate collection with dry fruits",
        "image": "https://m.media-amazon.com/images/I/81vqZWqgGxL._AC_UL320_.jpg"
    },
    {
        "id": "13",
        "name": "Cadbury Dairy Milk Silk Special Pack",
        "category": "Chocolates",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/Cadbury-Dairy-Milk-Silk-Special/dp/B07MQL2CHW",
        "description": "Smooth and creamy Dairy Milk Silk chocolate gift",
        "image": "https://m.media-amazon.com/images/I/71bVl3QKZOL._AC_UL320_.jpg"
    },
    {
        "id": "14",
        "name": "Ferrero Rocher Moments Pralines",
        "category": "Chocolates",
        "price_range": "Under ₹1000",
        "link": "https://www.amazon.in/Ferrero-Rocher-Moments-pralines-92-8gm/dp/B0C8NM93L8",
        "description": "Assorted Ferrero moments praline collection",
        "image": "https://m.media-amazon.com/images/I/71nQqD6YRZL._AC_UL320_.jpg"
    },
    {
        "id": "15",
        "name": "Pureheart Cherokee Bournville Designer Chocolate",
        "category": "Chocolates",
        "price_range": "Under ₹1000",
        "link": "https://www.amazon.in/PUREHEART-Cherokee-Bournville-Chocolate-Designer/dp/B0DSC6S99F",
        "description": "Elegant designer chocolate gift box",
        "image": "https://m.media-amazon.com/images/I/71wZNQxWqpL._AC_UL320_.jpg"
    },
    {
        "id": "16",
        "name": "HyperFoods Diwali Gift Hamper",
        "category": "Chocolates",
        "price_range": "₹1000-₹1500",
        "link": "https://www.amazon.in/HyperFoods%C2%AE-Diwali-Friends-Corporate-Employees/dp/B0DVLT4HSW",
        "description": "Premium Diwali gift hamper for loved ones",
        "image": "https://m.media-amazon.com/images/I/81sXnQRLIxL._AC_UL320_.jpg"
    },
    {
        "id": "17",
        "name": "Diwali Celebration Pataka Hamper",
        "category": "Chocolates",
        "price_range": "₹1500-₹2000",
        "link": "https://www.amazon.in/Diwali-Celebration-Pataka-Hamper-Healthy/dp/B0DFWR1HHZ",
        "description": "Festive Diwali celebration gift hamper",
        "image": "https://m.media-amazon.com/images/I/81q0zXPSo7L._AC_UL320_.jpg"
    },
    
    # Footwear
    {
        "id": "18",
        "name": "FASHIMO Women's Ankle Boot",
        "category": "Footwear",
        "price_range": "₹1000-₹1500",
        "link": "https://www.amazon.in/FASHIMO-Womens-Girls-Boot-PN1-Black-9/dp/B08T741S4M",
        "description": "Stylish women's ankle boots for all occasions",
        "image": "https://m.media-amazon.com/images/I/71rXNP8ue7L._AC_UL320_.jpg"
    },
    {
        "id": "19",
        "name": "Doctor Extra Soft Orthopedic Slippers",
        "category": "Footwear",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/DOCTOR-EXTRA-SOFT-Orthopedic-D-18-Black/dp/B074CZZQ8V",
        "description": "Comfortable orthopedic slippers for daily wear",
        "image": "https://m.media-amazon.com/images/I/61KfV+vCgAL._AC_UL320_.jpg"
    },
    {
        "id": "20",
        "name": "Adidas Factor Running Shoes",
        "category": "Footwear",
        "price_range": "₹2000-₹3000",
        "link": "https://www.amazon.in/Adidas-Factor-Running-DOVGRY-FTWWHT/dp/B08TM7PD6X",
        "description": "Premium Adidas running shoes for fitness enthusiasts",
        "image": "https://m.media-amazon.com/images/I/61xD+sOCFnL._AC_UL320_.jpg"
    },
    {
        "id": "21",
        "name": "ZOVIM Women's Casual Heels White",
        "category": "Footwear",
        "price_range": "₹500-₹1000",
        "link": "https://www.amazon.in/ZOVIM-Women-Casual-Heels-White/dp/B07YDW2FY9",
        "description": "Elegant white casual heels for women",
        "image": "https://m.media-amazon.com/images/I/61QwfV1HVWL._AC_UL320_.jpg"
    },
    {
        "id": "22",
        "name": "KRAFTER Synthetic Leather Casual Sneakers",
        "category": "Footwear",
        "price_range": "₹1000-₹1500",
        "link": "https://www.amazon.in/KRAFTER-Synthetic-Leather-Casual-Womens/dp/B08GSRPZPT",
        "description": "Comfortable synthetic leather casual sneakers",
        "image": "https://m.media-amazon.com/images/I/71YqsC2KBML._AC_UL320_.jpg"
    },
    {
        "id": "23",
        "name": "ELISE Women's Green Sneakers",
        "category": "Footwear",
        "price_range": "₹500-₹1000",
        "link": "https://www.amazon.in/ELISE-Womens-Green-Sneakers-4-EVAR-WT19-69/dp/B07XGV1W54",
        "description": "Trendy green sneakers for casual outings",
        "image": "https://m.media-amazon.com/images/I/71jZQyWDx9L._AC_UL320_.jpg"
    },
    {
        "id": "24",
        "name": "VAGON Women's Suede Leather Sandals",
        "category": "Footwear",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/VAGON-Womens-Suede-Leather-Sandals/dp/B075K8JYXY",
        "description": "Comfortable suede leather sandals for women",
        "image": "https://m.media-amazon.com/images/I/71WqrJqvB9L._AC_UL320_.jpg"
    },
    
    # Watches & Jewelry
    {
        "id": "25",
        "name": "Fastrack Limitless FS1+ Smartwatch",
        "category": "Watches",
        "price_range": "₹2000-₹3000",
        "link": "https://www.amazon.in/Fastrack-Limitless-Watchfaces-Calculator-Smartwatch/dp/B0CJJYT2Y9",
        "description": "Feature-rich smartwatch with multiple watch faces",
        "image": "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=400&q=80"
    },
    {
        "id": "26",
        "name": "Young Forever Designer Vintage Necklace",
        "category": "Jewelry",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/Young-Forever-Designer-Necklace-Vintage/dp/B06XCWW575",
        "description": "Beautiful vintage designer necklace",
        "image": "https://images.unsplash.com/photo-1643300866907-032b3baeeb1f?w=400&q=80"
    },
    {
        "id": "27",
        "name": "Titan Smartwatch with IP68",
        "category": "Watches",
        "price_range": "₹3000-₹5000",
        "link": "https://www.amazon.in/Titan-Smartwatch-Resolution-Functional-WatchfacesIP68/dp/B0CLR9LP6T",
        "description": "Premium Titan smartwatch with water resistance",
        "image": "https://images.unsplash.com/photo-1660844817855-3ecc7ef21f12?w=400&q=80"
    },
    {
        "id": "28",
        "name": "Fastrack Reflex Play+ Smartwatch",
        "category": "Watches",
        "price_range": "₹2000-₹3000",
        "link": "https://www.amazon.in/Fastrack-Smartwatch-Functional-Resolution-SingleSync/dp/B0CGTW2QL5",
        "description": "Advanced Fastrack smartwatch with fitness tracking",
        "image": "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=400&q=80"
    },
    {
        "id": "29",
        "name": "NIBOSI Rose Gold Stainless Steel Watch",
        "category": "Watches",
        "price_range": "₹1000-₹2000",
        "link": "https://www.amazon.in/NIBOSI-Stainless-Watches-Waterproof-Color-Rose/dp/B0D147BDLB",
        "description": "Elegant rose gold waterproof watch for women",
        "image": "https://images.unsplash.com/photo-1660844817855-3ecc7ef21f12?w=400&q=80"
    },
    {
        "id": "30",
        "name": "Casio Vintage Digital Grey Watch",
        "category": "Watches",
        "price_range": "₹1000-₹1500",
        "link": "https://www.amazon.in/Casio-Vintage-Digital-Grey-Watch-A158WA-1Q/dp/B000GAYQJ0",
        "description": "Classic Casio vintage digital watch",
        "image": "https://m.media-amazon.com/images/I/71kQOlztDtL._AC_UL320_.jpg"
    },
    {
        "id": "31",
        "name": "NIBOSI Diamond Stylish Watch",
        "category": "Watches",
        "price_range": "₹1000-₹2000",
        "link": "https://www.amazon.in/NIBOSI-Watches-Analogue-Stylish-Diamond/dp/B09WMWG32M",
        "description": "Stylish diamond-studded watch for special occasions",
        "image": "https://m.media-amazon.com/images/I/71bqJ+5LSEL._AC_UL320_.jpg"
    },
    {
        "id": "32",
        "name": "Titan Moments Analog Women's Watch",
        "category": "Watches",
        "price_range": "₹2000-₹3000",
        "link": "https://www.amazon.in/Titan-Moments-Analog-Womens-Watch-2606WM09/dp/B08LKVL1V9",
        "description": "Elegant Titan analog watch for women",
        "image": "https://m.media-amazon.com/images/I/71dJZGWo1nL._AC_UL320_.jpg"
    },
    
    # Soft Toys & Plushies
    {
        "id": "33",
        "name": "HUG n FEEL Teddy Bear 3 Feet",
        "category": "Soft Toys",
        "price_range": "₹1000-₹1500",
        "link": "https://www.amazon.in/HUG-FEEL-SOFT-TOYS-Birthday/dp/B08X3PCGKS",
        "description": "Large 3 feet teddy bear perfect for gifting",
        "image": "https://images.unsplash.com/photo-1602734846297-9299fc2d4703?w=400&q=80"
    },
    {
        "id": "34",
        "name": "Mirada Adorable Teddy Bear",
        "category": "Soft Toys",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/Mirada-Adorable-Toddlers-Stuffed-Birthday/dp/B0DPC27TCF",
        "description": "Cute and cuddly teddy bear for all ages",
        "image": "https://images.unsplash.com/photo-1562040506-a9b32cb51b94?w=400&q=80"
    },
    {
        "id": "35",
        "name": "Storescent Stuffed Plushie",
        "category": "Soft Toys",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/Storescent-Stuffed-Plushies-Birthday-Valentine/dp/B0CKXQNXTG",
        "description": "Adorable stuffed plushie for Valentine's Day",
        "image": "https://images.unsplash.com/photo-1556012018-50c5c0da73bf?w=400&q=80"
    },
    {
        "id": "36",
        "name": "Storio Reversible Octopus Plushie",
        "category": "Soft Toys",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/Storio-Octopus-Plushie-Reversible-Plush/dp/B0D6Z1YPTZ",
        "description": "Fun reversible octopus mood plushie",
        "image": "https://m.media-amazon.com/images/I/71xK9QDTFML._AC_UL320_.jpg"
    },
    {
        "id": "37",
        "name": "Frantic Teddy Bear - 2 Feet",
        "category": "Soft Toys",
        "price_range": "₹500-₹1000",
        "link": "https://www.amazon.in/Frantic-Non-Toxic-Birhtday-Anniversary-Valantine/dp/B0924QCJJX",
        "description": "Soft and huggable 2 feet teddy bear",
        "image": "https://m.media-amazon.com/images/I/71bULQo0uCL._AC_UL320_.jpg"
    },
    {
        "id": "38",
        "name": "Frantic Teddy Bear - Brown",
        "category": "Soft Toys",
        "price_range": "₹500-₹1000",
        "link": "https://www.amazon.in/Frantic-Non-Toxic-Birhtday-Anniversary-Valantine/dp/B08P7WL5VW",
        "description": "Classic brown teddy bear for special occasions",
        "image": "https://m.media-amazon.com/images/I/71qkd5KKNRL._AC_UL320_.jpg"
    },
    {
        "id": "39",
        "name": "Shining Diva Butterfly Necklace",
        "category": "Jewelry",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/Shining-Diva-Fashion-Butterfly-15911np/dp/B0D3DCP7JQ",
        "description": "Elegant butterfly design necklace",
        "image": "https://m.media-amazon.com/images/I/71H9ZEKqF7L._AC_UL320_.jpg"
    },
    {
        "id": "40",
        "name": "Niku Reversible Strawberry Plushie",
        "category": "Soft Toys",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/Niku-Reversible-Stuffed-plushies-Strawberry/dp/B0CPVNTZ4K",
        "description": "Cute reversible strawberry plushie toy",
        "image": "https://m.media-amazon.com/images/I/71wMQ9xXQyL._AC_UL320_.jpg"
    },
    {
        "id": "41",
        "name": "Babique Rabbit Stuffed Plush",
        "category": "Soft Toys",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/Babique-Rabbit-Stuffed-Plush-Birthday/dp/B08LTGCVQT",
        "description": "Soft rabbit plush toy perfect for gifting",
        "image": "https://m.media-amazon.com/images/I/71dqj+iX+jL._AC_UL320_.jpg"
    },
    {
        "id": "42",
        "name": "Gege Bear Color Changing Bear",
        "category": "Soft Toys",
        "price_range": "₹500-₹1000",
        "link": "https://www.amazon.in/Gege-Bear-Natural-Chemical-Free-Changing/dp/B0F7HMB65W",
        "description": "Unique color-changing teddy bear",
        "image": "https://m.media-amazon.com/images/I/71WQzMXxVBL._AC_UL320_.jpg"
    },
    {
        "id": "43",
        "name": "Pikipo Baby Rattle Toy",
        "category": "Soft Toys",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/Pikipo-Rattle-Squeeze-Handle-Squeaky/dp/B0BZYWTKLB",
        "description": "Cute rattle toy for babies and toddlers",
        "image": "https://m.media-amazon.com/images/I/71pQxN8MZXL._AC_UL320_.jpg"
    },
    {
        "id": "44",
        "name": "VRB Artificial Crochet Bouquet",
        "category": "Romantic",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/VRB-Dec-Artificial-Crochet-Bouquet/dp/B0DVQ75LVP",
        "description": "Beautiful handmade crochet flower bouquet",
        "image": "https://m.media-amazon.com/images/I/81yQlM5CHIL._AC_UL320_.jpg"
    },
    {
        "id": "45",
        "name": "Desidiya Crystal Night Lamp",
        "category": "Home",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/Desidiya-Crystal-Night-Woodern-Decorations/dp/B0D2P9JK11",
        "description": "Elegant crystal night lamp for home decor",
        "image": "https://m.media-amazon.com/images/I/71kXQDyDt3L._AC_UL320_.jpg"
    },
    {
        "id": "46",
        "name": "AUDBOT Strawberry Plushie",
        "category": "Soft Toys",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/AUDBOT-Strawberry-Plushie-Animal-Stuffed/dp/B0DG5P5NQC",
        "description": "Adorable strawberry stuffed animal plushie",
        "image": "https://m.media-amazon.com/images/I/71qxK5HNKXL._AC_UL320_.jpg"
    },
    {
        "id": "47",
        "name": "Niwlix Color Changing LED Light",
        "category": "Home",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/Niwlix-Bedroom-Changing-Valentines-Birthday/dp/B0FCRSCT7K",
        "description": "Beautiful color-changing LED decor light",
        "image": "https://m.media-amazon.com/images/I/71dMQNx8XNL._AC_UL320_.jpg"
    },
    {
        "id": "48",
        "name": "Storio Plush Lying Stuffed Animal",
        "category": "Soft Toys",
        "price_range": "₹500-₹1000",
        "link": "https://www.amazon.in/Storio-Plush-Lying-Stuffed-Animal/dp/B0FJ624J48",
        "description": "Large lying position stuffed animal toy",
        "image": "https://m.media-amazon.com/images/I/71MQJ9xL8nL._AC_UL320_.jpg"
    },
    {
        "id": "49",
        "name": "Amazon Brand Penguin Soft Toy",
        "category": "Soft Toys",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/Amazon-Brand-Penguin-Super-Soft-Birthday/dp/B0C46HFZX6",
        "description": "Super soft penguin plush toy",
        "image": "https://m.media-amazon.com/images/I/61YQJ8MX9FL._AC_UL320_.jpg"
    },
    {
        "id": "50",
        "name": "Fluffybliss Reversible Octopus Plushie",
        "category": "Soft Toys",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/Fluffybliss-Reversible-Octopus-Stuffed-Plushie/dp/B0C8NSP666",
        "description": "Fun reversible mood octopus plushie",
        "image": "https://m.media-amazon.com/images/I/71WQ8Y9QXDL._AC_UL320_.jpg"
    },
    {
        "id": "51",
        "name": "AVS Shiba Inu Huggable Pillow",
        "category": "Soft Toys",
        "price_range": "₹500-₹1000",
        "link": "https://www.amazon.in/AVS-Shiba-Huggable-Valentines-Decorative/dp/B08RX76XGH",
        "description": "Cute Shiba Inu dog huggable pillow",
        "image": "https://m.media-amazon.com/images/I/71PQY8xZ5OL._AC_UL320_.jpg"
    },
    {
        "id": "52",
        "name": "SCOOBA Giraffe Soft Toy",
        "category": "Soft Toys",
        "price_range": "₹500-₹1000",
        "link": "https://www.amazon.in/SCOOBA-Kids-Favourite-Giraffe-Height/dp/B085TBV2Y7",
        "description": "Tall giraffe plush toy for kids",
        "image": "https://m.media-amazon.com/images/I/61QZ8KQ9xFL._AC_UL320_.jpg"
    },
    {
        "id": "53",
        "name": "Mirada Penguin Soft Toy Turquoise",
        "category": "Soft Toys",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/Mirada-Penguin-Soft-Toy-Turquoise/dp/B0F249MRNW",
        "description": "Cute turquoise penguin plush toy",
        "image": "https://m.media-amazon.com/images/I/71qKQ9YxZ5L._AC_UL320_.jpg"
    },
    {
        "id": "54",
        "name": "Babique Cute Brown Bear",
        "category": "Soft Toys",
        "price_range": "₹500-₹1000",
        "link": "https://www.amazon.in/Babique-Cute-Brown-Animal-Birthday/dp/B06XH26KJ4",
        "description": "Classic brown bear stuffed animal",
        "image": "https://m.media-amazon.com/images/I/71wQd5MPXYL._AC_UL320_.jpg"
    },
    {
        "id": "55",
        "name": "Fun4you Elephant Soft Toy",
        "category": "Soft Toys",
        "price_range": "₹500-₹1000",
        "link": "https://www.amazon.in/Fun4you-Elephant-Soft-Toy-Kids/dp/B0FHPMVWLW",
        "description": "Adorable elephant plush toy for kids",
        "image": "https://m.media-amazon.com/images/I/71MQ89xXKYL._AC_UL320_.jpg"
    },
    {
        "id": "56",
        "name": "Babique Tremp Plush Animal",
        "category": "Soft Toys",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/Babique-Tremp-Plush-Animal-Decor/dp/B0BFNNS31H",
        "description": "Unique plush animal home decor",
        "image": "https://m.media-amazon.com/images/I/71yQM9xXqWL._AC_UL320_.jpg"
    },
    {
        "id": "57",
        "name": "YBN Cute Panda with Bamboo",
        "category": "Soft Toys",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/YBN-Cute-Panda-Plush-Bamboo/dp/B0DJ7VPN1Y",
        "description": "Cute panda plush with bamboo accessory",
        "image": "https://m.media-amazon.com/images/I/71QxK5HWQXL._AC_UL320_.jpg"
    },
    {
        "id": "58",
        "name": "Babique Plush Rabbit Toy",
        "category": "Soft Toys",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/Babique-Richy-Toys-Plush-Rabbit/dp/B01FC8RSAE",
        "description": "Soft and cuddly rabbit plush toy",
        "image": "https://m.media-amazon.com/images/I/71WQM8xYXDL._AC_UL320_.jpg"
    },
    {
        "id": "59",
        "name": "LOVEY DOVEY Huggable Teddy",
        "category": "Soft Toys",
        "price_range": "₹500-₹1000",
        "link": "https://www.amazon.in/LOVEY-DOVEY-Huggable-Birthday-Valentines/dp/B0F7RK17QW",
        "description": "Extra huggable teddy bear for Valentine's",
        "image": "https://m.media-amazon.com/images/I/71qKQ9XWYZL._AC_UL320_.jpg"
    },
    {
        "id": "60",
        "name": "Nyrwana Coffee Mug Gift Set",
        "category": "Home",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/Nyrwana-Delivering-Coffee-Mug-Birthday/dp/B09XDWKZQJ",
        "description": "Beautiful coffee mug gift set for birthdays",
        "image": "https://m.media-amazon.com/images/I/71MQ8YWXQZL._AC_UL320_.jpg"
    },
    {
        "id": "61",
        "name": "Storio Baby Toys Play Kit",
        "category": "Soft Toys",
        "price_range": "₹500-₹1000",
        "link": "https://www.amazon.in/Storio-Baby-Toys-Play-Kit/dp/B09CTQ7P15",
        "description": "Complete baby toys play kit set",
        "image": "https://m.media-amazon.com/images/I/71qWQ8xYXKL._AC_UL320_.jpg"
    },
    {
        "id": "62",
        "name": "Webby Plush Stuffed Animal",
        "category": "Soft Toys",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/Webby-Plush-Stuffed-Animal-Adorable/dp/B0B42TFR9D",
        "description": "Adorable plush stuffed animal toy",
        "image": "https://m.media-amazon.com/images/I/71YQ8xWKQXL._AC_UL320_.jpg"
    },
    {
        "id": "63",
        "name": "ANAB GI Kawaii Mochi Squishy",
        "category": "Soft Toys",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/ANAB-GI-Kawaii-Mochi-Squishy/dp/B0CZT7F8B9",
        "description": "Cute kawaii mochi squishy toys set",
        "image": "https://m.media-amazon.com/images/I/71WQ9xXKQYL._AC_UL320_.jpg"
    },
    {
        "id": "64",
        "name": "Birthday Combo - Scrunchies & Earrings",
        "category": "Jewelry",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/Birthday-Combo-Scrunchies-Earring-Bookmark/dp/B0BRYBRGJS",
        "description": "Beautiful birthday combo gift set",
        "image": "https://m.media-amazon.com/images/I/71MQ8WXKYXL._AC_UL320_.jpg"
    },
    {
        "id": "65",
        "name": "One94Store Panda Rechargeable Lamp",
        "category": "Home",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/One94Store-Panda-Rechargeable-Lamp-Cute/dp/B0CQGH5DFF",
        "description": "Cute panda-shaped rechargeable LED lamp",
        "image": "https://m.media-amazon.com/images/I/71WQ9xYKXQL._AC_UL320_.jpg"
    },
    {
        "id": "66",
        "name": "SCOOBA Avocado Cushion",
        "category": "Soft Toys",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/SCOOBA-Super-Avocado-Cushion-Stuffed/dp/B08L9PFC6B",
        "description": "Super soft avocado cushion plushie",
        "image": "https://m.media-amazon.com/images/I/71QM8xYWKXL._AC_UL320_.jpg"
    },
    {
        "id": "67",
        "name": "Pikipo Bunny Rattle Round Handle",
        "category": "Soft Toys",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/Pikipo-Bunny-Rattle-Round-Handle/dp/B0BZZ79KN2",
        "description": "Cute bunny rattle toy for babies",
        "image": "https://m.media-amazon.com/images/I/71WQ8xYKQXL._AC_UL320_.jpg"
    },
    {
        "id": "68",
        "name": "MeeTo Clamshell Nightlight",
        "category": "Home",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/MeeTo-Nightlight-Clamshell-Decoration-Christmas/dp/B0C58JN1FW",
        "description": "Beautiful clamshell LED nightlight decoration",
        "image": "https://m.media-amazon.com/images/I/71MQ9xXKYWL._AC_UL320_.jpg"
    },
    {
        "id": "69",
        "name": "Mirada Pokemon Squirtle Soft Toy",
        "category": "Soft Toys",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/Mirada-Pokemon-Blue-Squirtle-Soft/dp/B0DPX5BD7X",
        "description": "Adorable Pokemon Squirtle plush toy",
        "image": "https://m.media-amazon.com/images/I/71WQ8xYKQXL._AC_UL320_.jpg"
    },
    {
        "id": "70",
        "name": "Allen Solly Women's Sling Bag",
        "category": "Fashion",
        "price_range": "₹1000-₹2000",
        "link": "https://www.amazon.in/Allen-Solly-Womens-Solid-Sling/dp/B0D3TLT5ZS",
        "description": "Stylish Allen Solly sling bag for women",
        "image": "https://m.media-amazon.com/images/I/71QM8xYWKXL._AC_UL320_.jpg"
    },
    {
        "id": "71",
        "name": "SCOOBA Baby Penguin Soft Toy",
        "category": "Soft Toys",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/SCOOBA-Baby-Penguin-Soft-Toy/dp/B09TKYGSBJ",
        "description": "Cute baby penguin plush toy",
        "image": "https://m.media-amazon.com/images/I/71WQ9xYKXQL._AC_UL320_.jpg"
    },
    
    # Health & Wellness
    {
        "id": "72",
        "name": "JennaTM Sleeping Eye Mask",
        "category": "Health & Wellness",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/JennaTM-Sleeping-Insomnia-Meditation-Circles/dp/B083JJPF5N",
        "description": "Comfortable sleeping eye mask for better rest",
        "image": "https://m.media-amazon.com/images/I/71MQ8xYWKXL._AC_UL320_.jpg"
    },
    {
        "id": "73",
        "name": "HEALTH FIT Orthopedic Pillow",
        "category": "Health & Wellness",
        "price_range": "₹500-₹1000",
        "link": "https://www.amazon.in/HEALTH-FIT-Healthfit-Comfortable-Orthopedic/dp/B08BFYD4D9",
        "description": "Comfortable orthopedic pillow for neck support",
        "image": "https://m.media-amazon.com/images/I/71WQ8xYKQXL._AC_UL320_.jpg"
    },
    {
        "id": "74",
        "name": "JennaTM Grey Sleeping Mask",
        "category": "Health & Wellness",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/JennaTM-Sleeping-Insomnia-Meditation-Circles/dp/B08F3KFRZL",
        "description": "Premium grey sleeping mask for meditation",
        "image": "https://m.media-amazon.com/images/I/71QM9xXKYWL._AC_UL320_.jpg"
    },
    {
        "id": "75",
        "name": "JennaTM Pink Sleeping Mask",
        "category": "Health & Wellness",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/JennaTM-Sleeping-Insomnia-Meditation-Circles/dp/B083JJLXRG",
        "description": "Soft pink sleeping mask for insomnia relief",
        "image": "https://m.media-amazon.com/images/I/71WQ8xYKQXL._AC_UL320_.jpg"
    },
    {
        "id": "76",
        "name": "JSB Foot Massager with Vibration",
        "category": "Health & Wellness",
        "price_range": "₹2000-₹3000",
        "link": "https://www.amazon.in/JSB-HF04-Improving-Circulation-Vibration/dp/B07JJ93QTM",
        "description": "Electric foot massager for improved circulation",
        "image": "https://m.media-amazon.com/images/I/71MQ8xYWKXL._AC_UL320_.jpg"
    },
    {
        "id": "77",
        "name": "JennaTM Blue Sleeping Mask",
        "category": "Health & Wellness",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/JennaTM-Sleeping-Insomnia-Meditation-Circles/dp/B083JHZQFC",
        "description": "Calming blue sleeping mask for better sleep",
        "image": "https://m.media-amazon.com/images/I/71WQ9xYKXQL._AC_UL320_.jpg"
    },
    {
        "id": "78",
        "name": "Pyrite Crystal Bracelet",
        "category": "Health & Wellness",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/Pyrite-Crystal-Bracelet-Women-Men/dp/B0B5NF98JM",
        "description": "Natural pyrite crystal healing bracelet",
        "image": "https://m.media-amazon.com/images/I/71QM8xYWKXL._AC_UL320_.jpg"
    },
    {
        "id": "79",
        "name": "Aqualens Daily Contact Lenses",
        "category": "Health & Wellness",
        "price_range": "₹1000-₹1500",
        "link": "https://www.amazon.in/Aqualens-Daily-Disposable-Contact-Lenses/dp/B07ZFFSW67",
        "description": "Comfortable daily disposable contact lenses",
        "image": "https://m.media-amazon.com/images/I/71WQ8xYKQXL._AC_UL320_.jpg"
    },
    
    # Beauty Products
    {
        "id": "80",
        "name": "Colorbar Vegan Nail Lacquer",
        "category": "Beauty",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/Colorbar-Vegan-Nail-Lacquer-Talk/dp/B0B4K9BSN3",
        "description": "Premium vegan nail polish by Colorbar",
        "image": "https://images.unsplash.com/photo-1581839680158-103b461d8886?w=400&q=80"
    },
    {
        "id": "81",
        "name": "Colorbar Velvet Matte Lipstick",
        "category": "Beauty",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/Colorbar-Velvet-Matte-Lipstick-Surprise/dp/B074F216GZ",
        "description": "Long-lasting velvet matte lipstick",
        "image": "https://images.unsplash.com/photo-1580680509481-599991254d13?w=400&q=80"
    },
    {
        "id": "82",
        "name": "Faces Splash Nail Enamel",
        "category": "Beauty",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/Faces-Splash-Enamel-Floral-Dream/dp/B0853LTFMF",
        "description": "Vibrant nail enamel with floral design",
        "image": "https://images.unsplash.com/photo-1581839680158-103b461d8886?w=400&q=80"
    },
    {
        "id": "83",
        "name": "SUGAR Smudge Me Not Liquid Lipstick",
        "category": "Beauty",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/Sugar-Cosmetics-Smudge-Liquid-Lipstick/dp/B01N5QV746",
        "description": "Waterproof liquid lipstick by SUGAR",
        "image": "https://images.unsplash.com/photo-1580680509481-599991254d13?w=400&q=80"
    },
    {
        "id": "84",
        "name": "MyGlamm Liquid Matte Lipstick",
        "category": "Beauty",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/MyGlamm-Liquid-Matte-Lipstick-Swinger/dp/B0859Q2KXF",
        "description": "High-pigment liquid matte lipstick",
        "image": "https://images.unsplash.com/photo-1580680509481-599991254d13?w=400&q=80"
    },
    {
        "id": "85",
        "name": "Bella Vita Organic Perfume Set",
        "category": "Beauty",
        "price_range": "₹500-₹1000",
        "link": "https://www.amazon.in/Bella-Vita-Organic-Perfumes-Fragrance/dp/B09232XNTX",
        "description": "Organic perfume fragrance gift set",
        "image": "https://images.unsplash.com/photo-1523293182086-7651a899d37f?w=400&q=80"
    },
    {
        "id": "86",
        "name": "Maybelline Fit Me Concealer",
        "category": "Beauty",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/Maybelline-York-Concealer-Medium-6-8ml/dp/B0046VGJJA",
        "description": "Perfect coverage fit me concealer",
        "image": "https://m.media-amazon.com/images/I/71QM8xYWKXL._AC_UL320_.jpg"
    },
    {
        "id": "87",
        "name": "Miss Rose Waterproof Lipstick",
        "category": "Beauty",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/Miss-Rose-WaterProof-Moisturizing-LipStick/dp/B08HYRQ3LR",
        "description": "Waterproof moisturizing lipstick set",
        "image": "https://m.media-amazon.com/images/I/71WQ8xYKQXL._AC_UL320_.jpg"
    },
    {
        "id": "88",
        "name": "SUGAR Nothing Else Longwear Lipstick",
        "category": "Beauty",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/SUGAR-Cosmetics-Nothing-Longwear-Lipstick/dp/B07VX9M2NP",
        "description": "Ultra-longwear matte lipstick",
        "image": "https://m.media-amazon.com/images/I/71MQ8xYWKXL._AC_UL320_.jpg"
    },
    {
        "id": "89",
        "name": "REVLON Colorstay Eyeliner",
        "category": "Beauty",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/REVLON-Conditioning-Ingredients-Waterproof-Long-Lasting/dp/B07ZZ7DVKY",
        "description": "Long-lasting waterproof eyeliner",
        "image": "https://m.media-amazon.com/images/I/71WQ9xYKXQL._AC_UL320_.jpg"
    },
    {
        "id": "90",
        "name": "SUGAR POP Nail Lacquer",
        "category": "Beauty",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/SUGAR-POP-Nail-Lacquer-Chip-resistant/dp/B09WZY9DCV",
        "description": "Chip-resistant nail lacquer polish",
        "image": "https://m.media-amazon.com/images/I/71QM8xYWKXL._AC_UL320_.jpg"
    },
    {
        "id": "91",
        "name": "Maybelline Superstay Matte Ink",
        "category": "Beauty",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/Maybelline-Superstay-Matte-Brooklyn-Blush/dp/B09CLD61KG",
        "description": "Up to 16-hour stay matte liquid lipstick",
        "image": "https://m.media-amazon.com/images/I/71WQ8xYKQXL._AC_UL320_.jpg"
    },
    {
        "id": "92",
        "name": "Lakme Cushion Matte Lipstick",
        "category": "Beauty",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/Lakm%C3%A9-Cushion-Matte-Lipstick-Toast/dp/B08HSRP7QC",
        "description": "Smooth cushion matte finish lipstick",
        "image": "https://m.media-amazon.com/images/I/71MQ8xYWKXL._AC_UL320_.jpg"
    },
    {
        "id": "93",
        "name": "Lakme Primer Lip Gloss",
        "category": "Beauty",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/Lakme-Primer-Gloss-Colour-Business/dp/B07QFF4N7Y",
        "description": "High-shine primer lip gloss",
        "image": "https://m.media-amazon.com/images/I/71WQ9xYKXQL._AC_UL320_.jpg"
    },
    {
        "id": "94",
        "name": "Lakme Enrich Matte Lipstick",
        "category": "Beauty",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/Lakme-Enrich-Matte-Lipstick-Shade/dp/B071V63ZY2",
        "description": "Enriched matte lipstick with vitamins",
        "image": "https://m.media-amazon.com/images/I/71QM8xYWKXL._AC_UL320_.jpg"
    },
    {
        "id": "95",
        "name": "LAKME Absolute Stylist Lipstick",
        "category": "Beauty",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/LAKM%C3%89-Absolute-Stylist-Color-Royalty/dp/B08S51JDR2",
        "description": "Premium stylist color lipstick",
        "image": "https://m.media-amazon.com/images/I/71WQ8xYKQXL._AC_UL320_.jpg"
    },
    {
        "id": "96",
        "name": "Powerplay Liquid Lipstick",
        "category": "Beauty",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/Powerplay-Lipstick-Lightweight-Smudgeproof-Hydrates/dp/B08N84X9TJ",
        "description": "Lightweight smudgeproof liquid lipstick",
        "image": "https://m.media-amazon.com/images/I/71MQ8xYWKXL._AC_UL320_.jpg"
    },
    {
        "id": "97",
        "name": "OPI Nail Lacquer Barcelona",
        "category": "Beauty",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/P-I-Nail-Lacquer-Barefoot-Barcelona/dp/B00421X35C",
        "description": "Professional-grade OPI nail polish",
        "image": "https://m.media-amazon.com/images/I/71WQ9xYKXQL._AC_UL320_.jpg"
    },
    {
        "id": "98",
        "name": "Long-Lasting Transferproof Lipstick",
        "category": "Beauty",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/Long-Lasting-Lipstick-Lightweight-Transferproof-Smudgeproof/dp/B0828VX6NQ",
        "description": "Ultra-long lasting matte lipstick",
        "image": "https://m.media-amazon.com/images/I/71QM8xYWKXL._AC_UL320_.jpg"
    },
    {
        "id": "99",
        "name": "Faces Canada Ultime Matte Crayon",
        "category": "Beauty",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/Facescanada-Ultime-Matte-Crayon-Coffee/dp/B07J25JRHG",
        "description": "Easy-to-apply matte lip crayon",
        "image": "https://m.media-amazon.com/images/I/71WQ8xYKQXL._AC_UL320_.jpg"
    },
    
    # Additional Amazon Products
    {
        "id": "100",
        "name": "Plum BodyLovin Vanilla Vibes Body Mist 100ml",
        "category": "Beauty",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/dp/B0BH92CHFW",
        "description": "Refreshing vanilla scented body mist",
        "image": "https://images.unsplash.com/photo-1541643600914-78b084683601?w=400&q=80"
    },
    {
        "id": "101",
        "name": "Beauche Kojic Beauty Soap Bar 90g",
        "category": "Beauty",
        "price_range": "Under ₹500",
        "link": "https://www.amazon.in/dp/B00J59NFD6",
        "description": "Skin brightening kojic acid soap bar",
        "image": "https://images.unsplash.com/photo-1585155770998-c1a296e352f4?w=400&q=80"
    },
    {
        "id": "102",
        "name": "Women's Fashion Handbag",
        "category": "Fashion",
        "price_range": "₹1000-₹1500",
        "link": "https://www.amazon.in/dp/B0BMLRHC6T",
        "description": "Stylish handbag perfect for daily use",
        "image": "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=400&q=80"
    },
    {
        "id": "103",
        "name": "Premium Home Decor Set",
        "category": "Home",
        "price_range": "₹1000-₹2000",
        "link": "https://www.amazon.in/dp/B0C6FBL956",
        "description": "Elegant home decoration items",
        "image": "https://images.unsplash.com/photo-1513519245088-0e12902e35ca?w=400&q=80"
    },
    {
        "id": "104",
        "name": "Designer Ethnic Wear",
        "category": "Fashion",
        "price_range": "₹1500-₹2000",
        "link": "https://www.amazon.in/dp/B0D311G6W3",
        "description": "Beautiful ethnic clothing for special occasions",
        "image": "https://images.unsplash.com/photo-1610652492500-ded49ceeb4d8?w=400&q=80"
    },
    {
        "id": "105",
        "name": "Romantic Gift Hamper",
        "category": "Romantic",
        "price_range": "₹2000-₹3000",
        "link": "https://www.amazon.in/dp/B0CRBGQ33H",
        "description": "Curated gift hamper for your special someone",
        "image": "https://images.unsplash.com/photo-1549465220-1a8b9238cd48?w=400&q=80"
    },
    {
        "id": "106",
        "name": "Wireless Earbuds",
        "category": "Watches",
        "price_range": "₹1000-₹1500",
        "link": "https://www.amazon.in/dp/B0CQ4JT6NT",
        "description": "High-quality wireless bluetooth earbuds",
        "image": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=400&q=80"
    },
    {
        "id": "107",
        "name": "Skincare Gift Set",
        "category": "Beauty",
        "price_range": "₹500-₹1000",
        "link": "https://www.amazon.in/dp/B0BG8W7PJ7",
        "description": "Complete skincare routine gift set",
        "image": "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=400&q=80"
    },
    {
        "id": "108",
        "name": "Makeup Cosmetics Kit",
        "category": "Beauty",
        "price_range": "₹1000-₹1500",
        "link": "https://www.amazon.in/dp/B0BG8X8XTC",
        "description": "Professional makeup kit with essentials",
        "image": "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?w=400&q=80"
    },
    {
        "id": "109",
        "name": "Cozy Throw Blanket",
        "category": "Home",
        "price_range": "Under ₹1000",
        "link": "https://www.amazon.in/dp/B0CXJG8JPV",
        "description": "Soft and comfortable blanket for home",
        "image": "https://images.unsplash.com/photo-1631633762612-e3e9efc0c474?w=400&q=80"
    },
    {
        "id": "110",
        "name": "Aromatherapy Essential Oils Set",
        "category": "Health & Wellness",
        "price_range": "₹500-₹1000",
        "link": "https://www.amazon.in/dp/B0F7HF1DR7",
        "description": "Natural essential oils for relaxation and wellness",
        "image": "https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?w=400&q=80"
    },
    {
        "id": "111",
        "name": "Fashion Jewelry Set",
        "category": "Jewelry",
        "price_range": "Under ₹1000",
        "link": "https://www.amazon.in/dp/B09S3SRKMT",
        "description": "Trendy jewelry set for everyday wear",
        "image": "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=400&q=80"
    },
    {
        "id": "112",
        "name": "LED String Lights",
        "category": "Home",
        "price_range": "₹1000-₹1500",
        "link": "https://www.amazon.in/dp/B0D813X5DL",
        "description": "Decorative LED lights for room ambiance",
        "image": "https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?w=400&q=80"
    },
    {
        "id": "113",
        "name": "Personalized Photo Album",
        "category": "Romantic",
        "price_range": "₹1000-₹2000",
        "link": "https://www.amazon.in/dp/B09QD29JRP",
        "description": "Custom photo album for cherished memories",
        "image": "https://images.unsplash.com/photo-1542435503-956c469947f6?w=400&q=80"
    }
]

ROMANTIC_MESSAGES = {
    "good_morning": [
        "Good morning, beautiful! Can't wait to see your smile today ☀️",
        "Rise and shine, my love! Today is going to be amazing because you're in it",
        "Morning sunshine! Just thinking about you makes my day brighter",
        "Good morning to the most wonderful person in my world 💕",
        "Wake up, sleepyhead! The world needs your amazing energy today"
    ],
    "good_night": [
        "Sweet dreams, my love. Can't wait to see you tomorrow 🌙",
        "Good night, beautiful. You're the last thing on my mind tonight",
        "Sleep tight, darling. Dream of all our adventures together",
        "Good night to my favorite person. Love you to the moon and back",
        "Rest well, my heart. Tomorrow brings another day with you"
    ],
    "love_confession": [
        "I love you more than words can express. You complete me 💖",
        "Every day with you feels like a fairytale. I love you so much",
        "You're not just my partner, you're my best friend and soulmate",
        "I fall in love with you more every single day",
        "My heart beats for you and only you. I love you endlessly"
    ],
    "apology": [
        "I'm sorry, my love. Your happiness means everything to me",
        "I was wrong, and I'm sorry. Can we talk and make things right?",
        "Sorry for being stubborn. You mean the world to me",
        "I never want to hurt you. Please forgive me, sweetheart",
        "I'm sorry, babe. Let me make it up to you"
    ],
    "funny_hinglish": [
        "Tum mere dil ki rani ho, aur main tumhara deewana 👑",
        "Meri jaan, tum kitni cute ho! Main toh flat ho gaya",
        "Baby, tum toh meri life ka sabse best part ho!",
        "Yaar, tumhare bina main kuch bhi nahi hu. Tu meri zindagi hai!",
        "Sweetheart, tu meri happiness ka secret formula hai 🧪"
    ]
}

# Custom event suggestions for personal events
CUSTOM_EVENT_SUGGESTIONS = [
    {
        "category": "Family Events",
        "suggestions": [
            "Her mother's birthday",
            "Her father's birthday", 
            "Her siblings' birthdays",
            "Family anniversary dates",
            "Her grandparents' special days"
        ]
    },
    {
        "category": "Friends & Social",
        "suggestions": [
            "Best friend's birthday",
            "Best friend's wedding anniversary",
            "College friends' reunions",
            "Childhood friend's special days",
            "Work friends' celebrations"
        ]
    },
    {
        "category": "Professional Milestones", 
        "suggestions": [
            "Her work anniversary",
            "Graduation day anniversary",
            "First job anniversary",
            "Promotion celebration days",
            "Professional achievement dates"
        ]
    },
    {
        "category": "Memorial Events",
        "suggestions": [
            "Remembrance day for loved ones",
            "Pet memorial days",
            "Anniversary of special memories",
            "Tribute to important people",
            "Family memorial dates"
        ]
    },
    {
        "category": "Personal Achievements",
        "suggestions": [
            "Fitness milestone dates",
            "Learning achievement days",
            "Hobby accomplishment anniversaries", 
            "Personal goal completion dates",
            "Self-improvement milestones"
        ]
    }
]

# ============================================================================
# API ROUTES
# ============================================================================

@api_router.post("/auth/register", response_model=Token)
async def register(user: UserCreate):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user_id = str(uuid.uuid4())
    hashed_password = get_password_hash(user.password)
    
    user_doc = {
        "_id": user_id,
        "email": user.email,
        "name": user.name,
        "password": hashed_password,
        "relationship_mode": "SAME_HOME",
        "partner_profile": {},
        "total_points": 0,
        "current_level": 1,
        "current_streak": 0,
        "longest_streak": 0,
        "tasks_completed": 0,
        "badges": [],
        "profile_completed": False,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "daily_tasks": [],
        "weekly_task": None,
        "completed_tasks": [],
        "last_task_date": None,
        "custom_events": []
    }
    
    await db.users.insert_one(user_doc)
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_id}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@api_router.post("/auth/login", response_model=Token)
async def login(user: UserLogin):
    # Find user by email
    db_user = await db.users.find_one({"email": user.email})
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Check if user was created via OAuth (no password field)
    if "password" not in db_user or db_user["password"] is None:
        raise HTTPException(
            status_code=400, 
            detail="You don't have a password set yet. Please:\n1. Login with 'Continue with Google'\n2. Go to Profile → Settings → Set Password\n3. Then you can login with email/password!"
        )
    
    # Verify password
    if not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create access token with string user_id
    user_id = str(db_user["_id"])
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_id}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@api_router.post("/auth/send-otp")
async def send_otp(request: dict):
    mobile = request.get("mobile")
    if not mobile:
        raise HTTPException(status_code=400, detail="Mobile number is required")
    
    # Generate 6-digit OTP
    import random
    otp = str(random.randint(100000, 999999))
    
    # Store OTP in database with expiration (5 minutes)
    otp_expiry = datetime.utcnow() + timedelta(minutes=5)
    
    await db.otp_verification.update_one(
        {"mobile": mobile},
        {"$set": {
            "otp": otp,
            "expires_at": otp_expiry,
            "created_at": datetime.utcnow()
        }},
        upsert=True
    )
    
    # In production, send SMS via provider like Twilio, MSG91, etc.
    # For development, we'll just log it
    print(f"OTP for {mobile}: {otp}")
    
    return {"message": "OTP sent successfully", "mobile": mobile}

@api_router.post("/auth/verify-otp")
async def verify_otp(request: dict):
    mobile = request.get("mobile")
    otp = request.get("otp")
    name = request.get("name")  # For registration
    
    if not mobile or not otp:
        raise HTTPException(status_code=400, detail="Mobile and OTP are required")
    
    # Verify OTP
    otp_record = await db.otp_verification.find_one({"mobile": mobile})
    
    if not otp_record:
        raise HTTPException(status_code=404, detail="No OTP found for this mobile number")
    
    if datetime.utcnow() > otp_record["expires_at"]:
        await db.otp_verification.delete_one({"mobile": mobile})
        raise HTTPException(status_code=400, detail="OTP expired")
    
    if otp_record["otp"] != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    # OTP verified, delete it
    await db.otp_verification.delete_one({"mobile": mobile})
    
    # Check if user exists
    existing_user = await db.users.find_one({"mobile": mobile})
    
    if existing_user:
        # Login existing user
        access_token = create_access_token(data={"sub": str(existing_user["_id"])})
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(existing_user["_id"]),
                "name": existing_user["name"],
                "mobile": existing_user["mobile"],
                "relationship_mode": existing_user.get("relationship_mode", "SAME_HOME")
            }
        }
    else:
        # Register new user
        if not name:
            raise HTTPException(status_code=400, detail="Name is required for registration")
        
        user_dict = {
            "mobile": mobile,
            "name": name,
            "relationship_mode": "SAME_HOME",
            "partner_profile": {},
            "total_points": 0,
            "current_level": 1,
            "current_streak": 0,
            "longest_streak": 0,
            "tasks_completed": 0,
            "badges": [],
            "profile_completed": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await db.users.insert_one(user_dict)
        user_dict["_id"] = result.inserted_id
        
        access_token = create_access_token(data={"sub": str(result.inserted_id)})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(result.inserted_id),
                "name": name,
                "mobile": mobile,
                "relationship_mode": "SAME_HOME"
            }
        }

# OAuth endpoints
@api_router.post("/auth/oauth/apple", response_model=dict)
async def apple_oauth_callback(request: OAuthCallbackRequest):
    """Handle Apple OAuth callback (placeholder for future implementation)"""
    # Apple OAuth implementation would go here
    # For now, return a placeholder response
    raise HTTPException(status_code=501, detail="Apple OAuth not yet implemented")

# ============================================================================
# EMERGENT OAUTH ENDPOINTS
# ============================================================================

@api_router.get("/auth/emergent/session-data")
async def get_emergent_session_data(request: Request):
    """
    Process session_id from Emergent OAuth and exchange it for user data
    Frontend calls this with X-Session-ID header after OAuth redirect
    """
    from datetime import timezone
    
    # Get session_id from header
    session_id = request.headers.get("X-Session-ID") or request.headers.get("x-session-id")
    
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID is required")
    
    # Call Emergent's session data endpoint
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
                headers={"X-Session-ID": session_id}
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Invalid session ID")
            
            session_data = response.json()
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Session validation timeout")
    except Exception as e:
        print(f"Emergent OAuth error: {e}")
        raise HTTPException(status_code=500, detail="OAuth authentication failed")
    
    # Extract user data
    user_id_from_emergent = session_data.get("id")
    email = session_data.get("email")
    name = session_data.get("name", "User")
    picture = session_data.get("picture")
    emergent_session_token = session_data.get("session_token")
    
    if not email or not emergent_session_token:
        raise HTTPException(status_code=400, detail="Invalid session data")
    
    # PHASE 3: Duplicate Account Prevention
    # Check if user exists with this Google/Emergent ID (prevents duplicate accounts)
    existing_user_by_oauth = await db.users.find_one({
        "oauth_providers.emergent.emergent_id": user_id_from_emergent
    })
    
    if existing_user_by_oauth:
        # User already registered with this Google account
        # Return existing user instead of creating duplicate
        existing_user = existing_user_by_oauth
    else:
        # Check if user exists with this email (for linking accounts)
        existing_user = await db.users.find_one({"email": email})
    
    if existing_user:
        # User exists - link Emergent OAuth if not already linked
        user_id = str(existing_user["_id"])
        
        if "oauth_providers" not in existing_user:
            existing_user["oauth_providers"] = {}
        
        # Update Emergent OAuth provider data and profile picture
        update_data = {
            "oauth_providers.emergent": {
                "emergent_id": user_id_from_emergent,
                "linked_at": datetime.now(timezone.utc)
            },
            "updated_at": datetime.now(timezone.utc)
        }
        
        # Always update picture if available from Google
        if picture:
            update_data["picture"] = picture
            update_data["profile_image"] = picture  # Also store as profile_image
        
        # Update name if not set or different
        if name and (not existing_user.get("name") or existing_user.get("name") == "User"):
            update_data["name"] = name
        
        await db.users.update_one(
            {"_id": existing_user["_id"]},
            {"$set": update_data}
        )
    else:
        # Create new user with Emergent OAuth
        user_id = str(uuid.uuid4())
        user_doc = {
            "_id": user_id,
            "email": email,
            "name": name,
            "picture": picture,
            "profile_image": picture,  # Store as both for consistency
            "oauth_providers": {
                "emergent": {
                    "emergent_id": user_id_from_emergent,
                    "linked_at": datetime.now(timezone.utc)
                }
            },
            "relationship_mode": "SAME_HOME",
            "partner_profile": {},
            "total_points": 0,
            "current_level": 1,
            "current_streak": 0,
            "longest_streak": 0,
            "tasks_completed": 0,
            "badges": [],
            "profile_completed": False,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "daily_tasks": [],
            "weekly_task": None,
            "completed_tasks": [],
            "last_task_date": None,
            "custom_events": []
        }
        
        await db.users.insert_one(user_doc)
    
    # Store session in database (7 days expiry)
    session_expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    
    session_doc = {
        "user_id": user_id,
        "session_token": emergent_session_token,
        "expires_at": session_expires_at,
        "created_at": datetime.now(timezone.utc)
    }
    
    # Upsert session (replace existing if any)
    await db.user_sessions.update_one(
        {"session_token": emergent_session_token},
        {"$set": session_doc},
        upsert=True
    )
    
    # Return user data with session token
    user = await db.users.find_one({"_id": user_id})
    
    # Get profile image - prioritize saved profile_image over OAuth picture
    profile_pic = user.get("profile_image") or user.get("picture") or picture
    
    # Get partner profile with defaults
    partner_data = user.get("partner_profile", {})
    if not partner_data:
        partner_data = {}
    
    return {
        "success": True,
        "session_token": emergent_session_token,
        "user": {
            "id": user_id,
            "email": email,
            "name": user.get("name", name),
            "phone": user.get("phone"),  # Include phone/mobile number
            "picture": profile_pic,  # Return the saved profile image
            "profile_image": profile_pic,  # Also as profile_image for consistency
            "relationship_mode": user.get("relationship_mode", "SAME_HOME"),
            "partner_profile": partner_data,  # Include partner profile!
            "profile_completed": user.get("profile_completed", False),
            "total_points": user.get("total_points", 0),
            "current_level": user.get("current_level", 1),
            "current_streak": user.get("current_streak", 0),
            "longest_streak": user.get("longest_streak", 0),
            "tasks_completed": user.get("tasks_completed", 0),
            "badges": user.get("badges", []),
            "created_at": user.get("created_at", datetime.now(timezone.utc)).isoformat(),
            "updated_at": user.get("updated_at", datetime.now(timezone.utc)).isoformat()
        }
    }

@api_router.get("/auth/me")
async def get_current_user_data(request: Request):
    """
    Get current authenticated user data
    Supports both session_token (Emergent OAuth) and JWT Bearer token
    """
    user = await get_current_user_flexible(request)
    
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return {
        "id": str(user["_id"]),
        "email": user.get("email"),
        "name": user.get("name", "User"),
        "picture": user.get("picture"),
        "relationship_mode": user.get("relationship_mode", "SAME_HOME"),
        "profile_completed": user.get("profile_completed", False),
        "total_points": user.get("total_points", 0),
        "current_level": user.get("current_level", 1),
        "current_streak": user.get("current_streak", 0),
        "longest_streak": user.get("longest_streak", 0),
        "tasks_completed": user.get("tasks_completed", 0)
    }

@api_router.post("/auth/logout")
async def logout(request: Request):
    """
    Logout user by deleting session from database
    Works with both session_token and JWT tokens
    """
    from datetime import timezone
    
    # Try to get session_token
    session_token = request.cookies.get("session_token")
    
    if not session_token:
        # Try Authorization header
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            if not token.startswith("eyJ"):  # Not a JWT
                session_token = token
    
    if session_token:
        # Delete session from database
        await db.user_sessions.delete_one({"session_token": session_token})
    
    return {"success": True, "message": "Logged out successfully"}

@api_router.delete("/user/account")
async def delete_user_account(request: Request):
    """
    Permanently delete user account and all associated data
    This action is irreversible
    """
    from datetime import timezone
    
    # Get current user
    current_user = await get_current_user_flexible(request)
    
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    user_id = str(current_user["_id"])
    
    try:
        # 1. Delete user's sessions
        await db.user_sessions.delete_many({"user_id": user_id})
        
        # 2. Delete user's tasks
        await db.tasks.delete_many({"user_id": user_id})
        
        # 3. Delete user's custom events
        # Custom events are stored in user document, so will be deleted with user
        
        # 4. Delete user's subscription data (if any)
        # Subscriptions are stored in user document
        
        # 5. Delete user's push notification tokens
        # Stored in user document
        
        # 6. Delete user's feedback
        await db.feedback.delete_many({"user_id": user_id})
        
        # 7. Delete user's referral data (both as referrer and referee)
        await db.referrals.delete_many({"$or": [
            {"referrer_id": user_id},
            {"referee_id": user_id}
        ]})
        
        # 8. Finally, delete the user account
        result = await db.users.delete_one({"_id": user_id})
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Log deletion for audit purposes
        print(f"✅ User account deleted: {user_id} at {datetime.now(timezone.utc)}")
        
        return {
            "success": True,
            "message": "Your account has been permanently deleted. All your data has been removed from our servers."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error deleting user account {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete account. Please try again or contact support."
        )

@api_router.post("/auth/link-account")
async def link_account(request: LinkAccountRequest, current_user: dict = Depends(get_current_user)):
    """Link an additional authentication method to existing account"""
    try:
        provider = request.provider
        credential = request.credential
        
        if provider == "google":
            # Verify Google token
            user_info = await verify_google_token(credential.get("id_token", ""))
            if not user_info:
                raise HTTPException(status_code=400, detail="Invalid Google token")
            
            google_id = user_info.get("sub")
            google_email = user_info.get("email")
            
            # Check if this Google account is already linked to another user
            existing_google_user = await db.users.find_one({
                "oauth_providers.google.google_id": google_id,
                "_id": {"$ne": current_user["_id"]}
            })
            
            if existing_google_user:
                raise HTTPException(status_code=400, detail="This Google account is already linked to another user")
            
            # Link Google account
            await db.users.update_one(
                {"_id": current_user["_id"]},
                {"$set": {
                    "oauth_providers.google": {
                        "google_id": google_id,
                        "email": google_email,
                        "linked_at": datetime.utcnow()
                    },
                    "updated_at": datetime.utcnow()
                }}
            )
            
            return {"message": f"Google account successfully linked", "provider": provider}
            
        elif provider == "phone":
            # Handle phone linking (would require OTP verification)
            phone = credential.get("phone")
            otp = credential.get("otp")
            
            if not phone or not otp:
                raise HTTPException(status_code=400, detail="Phone number and OTP required")
            
            # Verify OTP (similar to existing OTP verification logic)
            # ... OTP verification code would go here ...
            
            return {"message": "Phone number successfully linked", "provider": provider}
            
        else:
            raise HTTPException(status_code=400, detail="Unsupported provider")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Account linking error: {e}")
        raise HTTPException(status_code=500, detail="Account linking failed")

@api_router.post("/auth/unlink-account")
async def unlink_account(request: UnlinkAccountRequest, current_user: dict = Depends(get_current_user)):
    """Unlink an authentication method from account"""
    try:
        provider = request.provider
        
        # Ensure user has at least one authentication method remaining
        oauth_providers = current_user.get("oauth_providers", {})
        has_password = "password" in current_user
        has_mobile = "mobile" in current_user
        
        auth_methods_count = len(oauth_providers) + (1 if has_password else 0) + (1 if has_mobile else 0)
        
        if auth_methods_count <= 1:
            raise HTTPException(status_code=400, detail="Cannot unlink the only authentication method")
        
        if provider in ["google", "apple"]:
            if provider not in oauth_providers:
                raise HTTPException(status_code=400, detail=f"{provider.title()} account is not linked")
            
            # Remove OAuth provider
            await db.users.update_one(
                {"_id": current_user["_id"]},
                {"$unset": {f"oauth_providers.{provider}": ""}, "$set": {"updated_at": datetime.utcnow()}}
            )
            
            return {"message": f"{provider.title()} account successfully unlinked", "provider": provider}
            
        elif provider == "phone":
            if not has_mobile:
                raise HTTPException(status_code=400, detail="Phone number is not linked")
            
            await db.users.update_one(
                {"_id": current_user["_id"]},
                {"$unset": {"mobile": ""}, "$set": {"updated_at": datetime.utcnow()}}
            )
            
            return {"message": "Phone number successfully unlinked", "provider": provider}
            
        else:
            raise HTTPException(status_code=400, detail="Unsupported provider")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Account unlinking error: {e}")
        raise HTTPException(status_code=500, detail="Account unlinking failed")

@api_router.post("/auth/refresh", response_model=dict)
async def refresh_token(request: RefreshTokenRequest):
    """Refresh access token using refresh token"""
    try:
        # Verify refresh token
        payload = jwt.decode(request.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        token_type = payload.get("type")
        
        if token_type != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        # Get user from database
        user = await db.users.find_one({"_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Create new access token
        access_token = create_access_token(data={"sub": user_id})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    except Exception as e:
        print(f"Token refresh error: {e}")
        raise HTTPException(status_code=500, detail="Token refresh failed")

@api_router.get("/user/profile", response_model=UserProfile)
async def get_profile(current_user: dict = Depends(get_current_user)):
    # Convert partner profile data to handle datetime fields
    partner_data = current_user.get("partner_profile", {})
    
    # Ensure all partner profile fields exist with defaults
    partner_defaults = {
        "name": "",
        "birthday": None,
        "anniversary": None,
        "favorite_color": "",
        "favorite_food": "",
        "favorite_flower": "",
        "favorite_brand": "",
        "dress_size": "",
        "ring_size": "",
        "perfume_preference": "",
        "top_size": "",
        "jeans_size": "",
        "notes": "",
        "additional_notes": ""
    }
    
    # Merge with defaults to ensure all fields exist
    partner_data = {**partner_defaults, **partner_data}
    
    # Convert datetime fields to string format (DD/MM/YYYY)
    if "birthday" in partner_data and partner_data["birthday"] is not None:
        if hasattr(partner_data["birthday"], 'strftime'):
            partner_data["birthday"] = partner_data["birthday"].strftime("%d/%m/%Y")
    
    if "anniversary" in partner_data and partner_data["anniversary"] is not None:
        if hasattr(partner_data["anniversary"], 'strftime'):
            partner_data["anniversary"] = partner_data["anniversary"].strftime("%d/%m/%Y")

    # Get profile image - check both fields for backwards compatibility
    profile_image = current_user.get("profile_image") or current_user.get("picture")
    
    return UserProfile(
        id=current_user["_id"],
        email=current_user["email"],
        name=current_user["name"],
        relationship_mode=current_user.get("relationship_mode", "SAME_HOME"),
        partner_profile=PartnerProfile(**partner_data),
        total_points=current_user.get("total_points", 0),
        current_level=current_user.get("current_level", 1),
        current_streak=current_user.get("current_streak", 0),
        longest_streak=current_user.get("longest_streak", 0),
        tasks_completed=current_user.get("tasks_completed", 0),
        badges=current_user.get("badges", []),
        profile_completed=current_user.get("profile_completed", False),
        profile_image=profile_image,
        created_at=current_user["created_at"],
        updated_at=current_user.get("updated_at", datetime.utcnow()),
        # Subscription fields
        subscription_type=current_user.get("subscription_type", "none"),
        subscription_status=current_user.get("subscription_status", "inactive"),
        subscription_start_date=current_user.get("subscription_start_date"),
        subscription_end_date=current_user.get("subscription_end_date"),
        trial_started=current_user.get("trial_started", False)
    )

@api_router.put("/user/profile")
async def update_user_profile(profile_update: dict, current_user: dict = Depends(get_current_user)):
    # Validate allowed fields
    allowed_fields = {"name", "email", "phone"}  # Using "phone" to match schema
    update_data = {k: v for k, v in profile_update.items() if k in allowed_fields}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No valid fields to update")
    
    # Add updated timestamp
    update_data["updated_at"] = datetime.utcnow()
    
    # Update in database
    result = await db.users.update_one(
        {"_id": current_user["_id"]},
        {"$set": update_data}
    )
    
    if result.modified_count > 0:
        print(f"✅ User profile updated: {update_data.keys()}")
    
    return {"message": "Profile updated successfully", "updated_fields": list(update_data.keys())}

@api_router.post("/user/add-password")
async def add_password(password_data: dict, current_user: dict = Depends(get_current_user)):
    """
    Allow OAuth users to add a password so they can login with email/password too
    """
    password = password_data.get("password")
    
    if not password or len(password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    
    # Hash the password
    hashed_password = hash_password(password)
    
    # Update user with password
    await db.users.update_one(
        {"_id": current_user["_id"]},
        {"$set": {
            "password": hashed_password,
            "updated_at": datetime.utcnow()
        }}
    )
    
    return {"message": "Password added successfully! You can now login with email/password."}

@api_router.post("/auth/forgot-password")
async def forgot_password(email_data: dict):
    """
    Send password reset email with code
    """
    email = email_data.get("email")
    
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    
    # Find user by email
    user = await db.users.find_one({"email": email})
    
    if not user:
        # Don't reveal if user exists for security
        return {"message": "If an account exists with this email, a password reset code has been sent."}
    
    # Check if user has a password (not OAuth-only)
    if "password" not in user or user["password"] is None:
        return {"message": "This account was created with Google Sign-In. Please use 'Continue with Google' to login, or set a password in settings after logging in."}
    
    # Generate 6-digit reset code
    reset_code = ''.join(random.choices(string.digits, k=6))
    
    # Store reset code with expiration (1 hour)
    reset_expires = datetime.utcnow() + timedelta(hours=1)
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {
            "reset_code": reset_code,
            "reset_code_expires": reset_expires
        }}
    )
    
    # Create reset link (for mobile app deep linking or web)
    app_url = os.getenv("APP_URL", "https://pookie-connect-1.preview.emergentagent.com")
    reset_link = f"{app_url}/reset-password?code={reset_code}&email={email}"
    
    # Send email
    email_sent = email_service.send_password_reset_email(email, reset_code, reset_link)
    
    if email_sent:
        return {"message": "Password reset code has been sent to your email. Please check your inbox."}
    else:
        return {"message": "If an account exists with this email, a password reset code has been sent."}

@api_router.post("/auth/reset-password")
async def reset_password(reset_data: dict):
    """
    Reset password using reset code
    """
    email = reset_data.get("email")
    reset_code = reset_data.get("code")
    new_password = reset_data.get("password")
    
    if not email or not reset_code or not new_password:
        raise HTTPException(status_code=400, detail="Email, code, and new password are required")
    
    if len(new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    
    # Find user with matching email and reset code
    user = await db.users.find_one({
        "email": email,
        "reset_code": reset_code
    })
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset code")
    
    # Check if code is expired
    if "reset_code_expires" not in user or user["reset_code_expires"] < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Reset code has expired. Please request a new one.")
    
    # Hash new password
    hashed_password = hash_password(new_password)
    
    # Update password and clear reset code
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {
            "password": hashed_password,
            "updated_at": datetime.utcnow()
        },
        "$unset": {
            "reset_code": "",
            "reset_code_expires": ""
        }}
    )
    
    return {"message": "Password has been reset successfully! You can now login with your new password."}

@api_router.put("/user/partner-profile")
async def update_partner_profile(partner: PartnerProfile, current_user: dict = Depends(get_current_user)):
    # Update partner profile
    await db.users.update_one(
        {"_id": current_user["_id"]},
        {"$set": {
            "partner_profile": partner.dict(),
            "profile_completed": True,
            "updated_at": datetime.utcnow()
        }}
    )
    
    # Create automatic events for birthday and anniversary if provided
    if partner.birthday or partner.anniversary:
        # First, remove any existing auto-generated events for this user
        await db.users.update_one(
            {"_id": current_user["_id"]},
            {"$pull": {"custom_events": {"auto_generated": True}}}
        )
        
        auto_events = []
        current_year = datetime.now().year
        
        # Create birthday event if provided
        if partner.birthday:
            try:
                # Parse DD/MM/YYYY format
                birthday_parts = partner.birthday.split('/')
                if len(birthday_parts) == 3:
                    day, month, year = birthday_parts
                    # Create event for current year and next year
                    for event_year in [current_year, current_year + 1]:
                        birthday_event = {
                            "id": f"partner_birthday_{event_year}",
                            "name": f"{partner.name}'s Birthday",
                            "date": f"{event_year}-{month.zfill(2)}-{day.zfill(2)}",
                            "category": "personal",
                            "description": f"Your beloved {partner.name}'s special day",
                            "auto_generated": True,
                            "tips": ["Plan a surprise party", "Book her favorite restaurant", "Organize a weekend getaway"],
                            "gift_suggestions": ["Jewelry", "Surprise party", "Weekend trip", "Her wishlist items"]
                        }
                        auto_events.append(birthday_event)
            except Exception as e:
                print(f"Error parsing birthday: {e}")
        
        # Create anniversary event if provided  
        if partner.anniversary:
            try:
                # Parse DD/MM/YYYY format
                anniversary_parts = partner.anniversary.split('/')
                if len(anniversary_parts) == 3:
                    day, month, year = anniversary_parts
                    # Create event for current year and next year
                    for event_year in [current_year, current_year + 1]:
                        anniversary_event = {
                            "id": f"anniversary_{event_year}",
                            "name": "Our Anniversary",
                            "date": f"{event_year}-{month.zfill(2)}-{day.zfill(2)}",
                            "category": "personal", 
                            "description": "Celebrating your love story",
                            "auto_generated": True,
                            "tips": ["Recreate your first date", "Plan a romantic getaway", "Exchange meaningful gifts"],
                            "gift_suggestions": ["Couple rings", "Photo album", "Romantic trip", "Anniversary dinner"]
                        }
                        auto_events.append(anniversary_event)
            except Exception as e:
                print(f"Error parsing anniversary: {e}")
        
        # Add auto-generated events to user's custom events
        if auto_events:
            await db.users.update_one(
                {"_id": current_user["_id"]},
                {"$push": {"custom_events": {"$each": auto_events}}}
            )
    
    return {"message": "Partner profile updated successfully", "auto_events_created": len(auto_events) if 'auto_events' in locals() else 0}
@api_router.post("/user/complete-onboarding")
async def complete_onboarding(
    current_user: dict = Depends(get_current_user)
):
    """
    Mark user's onboarding as complete
    Sets profile_completed = true
    """
    try:
        result = await db.users.update_one(
            {"_id": current_user["_id"]},
            {"$set": {
                "profile_completed": True,
                "updated_at": datetime.utcnow()
            }}
        )

        if result.modified_count > 0:
            print(f"✅ User {current_user['_id']} completed onboarding")
            return {
                "success": True,
                "message": "Onboarding completed successfully",
                "profile_completed": True
            }
        else:
            # Already completed or no change
            return {
                "success": True,
                "message": "Profile already completed",
                "profile_completed": True
            }

    except Exception as e:
        print(f"❌ Error completing onboarding: {e}")
        raise HTTPException(status_code=500, detail="Failed to complete onboarding")

@api_router.put("/user/relationship-mode")
async def update_relationship_mode(mode: RelationshipMode, current_user: dict = Depends(get_current_user)):
    """Update relationship mode and regenerate AI tasks for the new mode"""
    new_mode = mode.mode
    current_mode = current_user.get("relationship_mode", "SAME_HOME")
    
    # Update relationship mode
    await db.users.update_one(
        {"_id": current_user["_id"]},
        {"$set": {
            "relationship_mode": new_mode,
            "updated_at": datetime.utcnow()
        }}
    )
    
    # If mode changed, regenerate AI tasks for the new mode
    regenerated_tasks = {"daily": False, "weekly": False}
    if new_mode != current_mode:
        try:
            # Get profile data for personalization (with consent check)
            user_profile = current_user if current_user.get("ai_consent", False) else None
            partner_profile = current_user.get("partner_profile") if current_user.get("ai_consent", False) else None
            
            # Regenerate daily tasks for new mode
            try:
                new_daily_tasks = await generate_daily_tasks_for_mode(
                    relationship_mode=new_mode,
                    count=3,
                    user_profile=user_profile,
                    partner_profile=partner_profile
                )
                
                # Add metadata
                for task in new_daily_tasks:
                    task["relationship_mode"] = new_mode
                    task["task_type"] = "daily"
                    task["completed"] = False
                    task["completed_at"] = None
                
                regenerated_tasks["daily"] = True
                
            except Exception as e:
                print(f"Daily task regeneration failed: {e}")
                # Use fallback static tasks
                available_tasks = DAILY_TASKS.get(new_mode, DAILY_TASKS["SAME_HOME"])
                new_daily_tasks = random.sample(available_tasks, 3)
                for task in new_daily_tasks:
                    task["completed"] = False
                    task["completed_at"] = None
                    task["relationship_mode"] = new_mode
                    task["task_type"] = "daily"
            
            # Regenerate weekly tasks for new mode
            try:
                new_weekly_tasks = await generate_weekly_tasks_for_mode(
                    relationship_mode=new_mode,
                    count=1,
                    user_profile=user_profile,
                    partner_profile=partner_profile
                )
                
                # Add metadata
                for task in new_weekly_tasks:
                    task["relationship_mode"] = new_mode
                    task["task_type"] = "weekly"
                    task["completed"] = False
                    task["completed_at"] = None
                
                regenerated_tasks["weekly"] = True
                
            except Exception as e:
                print(f"Weekly task regeneration failed: {e}")
                # Use fallback static tasks
                available_tasks = WEEKLY_TASKS.get(new_mode, WEEKLY_TASKS["SAME_HOME"])
                new_weekly_tasks = random.sample(available_tasks, min(5, len(available_tasks)))
                for task in new_weekly_tasks:
                    task["completed"] = False
                    task["completed_at"] = None
                    task["relationship_mode"] = new_mode
                    task["task_type"] = "weekly"
            
            # Update tasks in database (preserving custom tasks and history)
            await db.users.update_one(
                {"_id": current_user["_id"]},
                {"$set": {
                    "ai_daily_tasks": new_daily_tasks,
                    "ai_weekly_tasks": new_weekly_tasks,
                    "last_task_date": datetime.utcnow(),
                    "last_weekly_task_date": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }}
            )
            
            return {
                "message": "Relationship mode updated and tasks regenerated successfully",
                "previous_mode": current_mode,
                "new_mode": new_mode,
                "tasks_regenerated": regenerated_tasks,
                "new_daily_tasks_count": len(new_daily_tasks),
                "new_weekly_tasks_count": len(new_weekly_tasks)
            }
            
        except Exception as e:
            print(f"Task regeneration failed during mode change: {e}")
            return {
                "message": "Relationship mode updated successfully (task regeneration will happen on next request)",
                "previous_mode": current_mode,
                "new_mode": new_mode,
                "tasks_regenerated": {"daily": False, "weekly": False},
                "regeneration_deferred": True
            }
    
    return {
        "message": "Relationship mode updated successfully (no change detected)",
        "mode": new_mode,
        "tasks_regenerated": {"daily": False, "weekly": False}
    }

@api_router.put("/user/profile-image")
async def update_profile_image(image_data: ProfileImageUpdate, current_user: dict = Depends(get_current_user)):
    await db.users.update_one(
        {"_id": current_user["_id"]},
        {"$set": {
            "profile_image": image_data.profile_image,
            "updated_at": datetime.utcnow()
        }}
    )
    return {"message": "Profile image updated successfully"}

@api_router.get("/winners")
async def get_winners():
    """Get previous winners list - Weekly cash prizes only"""
    # Sample winners data - in production this would come from database
    # Monthly trip winners removed until customer base grows
    sample_winners = [
        {
            "id": "1",
            "user_name": "Priya & Arjun",
            "prize_amount": 500,
            "prize_type": "weekly_cash",
            "week_number": 47,
            "month": None,
            "tasks_completed": 21,
            "awarded_date": "2024-11-20T00:00:00",
            "description": "Completed all daily tasks for Week 47"
        },
        {
            "id": "2", 
            "user_name": "Sneha & Rohit",
            "prize_amount": 750,
            "prize_type": "weekly_cash",
            "week_number": 46,
            "month": None,
            "tasks_completed": 21,
            "awarded_date": "2024-11-13T00:00:00",
            "description": "Perfect week with all tasks completed"
        },
        {
            "id": "3",
            "user_name": "Anjali & Karthik",
            "prize_amount": 1000,
            "prize_type": "weekly_cash",
            "week_number": 45,
            "month": None,
            "tasks_completed": 21,
            "awarded_date": "2024-11-06T00:00:00",
            "description": "Maximum weekly prize for exceptional performance"
        },
        {
            "id": "4",
            "user_name": "Riya & Aditya",
            "prize_amount": 800,
            "prize_type": "weekly_cash",
            "week_number": 44,
            "month": None,
            "tasks_completed": 21,
            "awarded_date": "2024-10-30T00:00:00",
            "description": "Perfect attendance and task completion"
        },
        {
            "id": "5",
            "user_name": "Ishita & Rohan",
            "prize_amount": 600,
            "prize_type": "weekly_cash",
            "week_number": 43,
            "month": None,
            "tasks_completed": 21,
            "awarded_date": "2024-10-23T00:00:00",
            "description": "Completed all daily tasks for Week 43"
        }
    ]
    
    return {"winners": sample_winners}


@api_router.get("/leaderboard")
async def get_leaderboard(
    timeframe: str = "all_time",
    limit: int = 20
):
    """
    Get top users by points - Leaderboard
    
    Query params:
    - timeframe: 'weekly' or 'all_time' (default: all_time)
    - limit: number of users to return (default: 20, max: 50)
    """
    try:
        # Validate limit
        if limit > 50:
            limit = 50
        
        # Build query based on timeframe
        if timeframe == "weekly":
            # Get users who earned points in last 7 days
            week_ago = datetime.utcnow() - timedelta(days=7)
            query = {
                "points": {"$gt": 0},
                "updated_at": {"$gte": week_ago.isoformat()}
            }
        else:
            # All time leaderboard
            query = {"points": {"$gt": 0}}
        
        # Get top users sorted by points
        top_users = await db.users.find(
            query,
            {
                "_id": 1,
                "name": 1,
                "email": 1,
                "points": 1,
                "profile_image": 1,
                "city": 1,
                "partner_profile.name": 1,
                "tasks_completed": 1,
                "current_streak": 1,
                "created_at": 1
            }
        ).sort("points", -1).limit(limit).to_list(length=limit)
        
        # Format leaderboard data
        leaderboard = []
        for idx, user in enumerate(top_users, start=1):
            partner_name = user.get("partner_profile", {}).get("name", "")
            
            # Create display name (user & partner)
            if partner_name:
                display_name = f"{user.get('name', 'Anonymous')} & {partner_name}"
            else:
                display_name = user.get('name', 'Anonymous')
            
            leaderboard.append({
                "rank": idx,
                "user_id": str(user["_id"]),
                "display_name": display_name,
                "points": user.get("points", 0),
                "profile_image": user.get("profile_image"),
                "city": user.get("city", "Unknown"),
                "tasks_completed": user.get("tasks_completed", 0),
                "current_streak": user.get("current_streak", 0),
                "member_since": user.get("created_at", "")
            })
        
        return {
            "success": True,
            "timeframe": timeframe,
            "total_users": len(leaderboard),
            "leaderboard": leaderboard,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching leaderboard: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch leaderboard: {str(e)}")


# AI-Powered Task Generation Endpoints

@api_router.get("/tasks/daily")
async def get_daily_tasks(
    request: Request,
    regenerate: bool = False,
    current_user: dict = Depends(get_current_user)
):
    """Get daily AI-generated tasks for current user's relationship mode"""
    today = datetime.utcnow().date()
    last_task_date = current_user.get("last_task_date")
    mode = current_user.get("relationship_mode", "SAME_HOME")
    
    # Check if we need to generate new tasks
    need_new_tasks = (
        regenerate or
        not last_task_date or 
        last_task_date.date() != today or
        not current_user.get("ai_daily_tasks")
    )
    
    if need_new_tasks:
        try:
            # Get profile data for personalization (with consent check)
            user_profile = current_user if current_user.get("ai_consent", False) else None
            partner_profile = current_user.get("partner_profile") if current_user.get("ai_consent", False) else None
            
            # Generate AI tasks
            ai_tasks = await generate_daily_tasks_for_mode(
                relationship_mode=mode,
                count=3,
                user_profile=user_profile,
                partner_profile=partner_profile
            )
            
            # Add relationship mode and type metadata
            for task in ai_tasks:
                task["relationship_mode"] = mode
                task["task_type"] = "daily"
                task["completed"] = False
                task["completed_at"] = None
            
            # Store AI tasks separately from custom tasks
            await db.users.update_one(
                {"_id": current_user["_id"]},
                {"$set": {
                    "ai_daily_tasks": ai_tasks,
                    "last_task_date": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }}
            )
            
            return {
                "tasks": ai_tasks,
                "generated_for_mode": mode,
                "generation_date": datetime.utcnow()
            }
            
        except Exception as e:
            print(f"AI task generation failed: {e}")
            # Fallback to relationship-specific static tasks (NEW DATABASE)
            available_tasks = get_tasks_for_relationship_mode(mode, "daily")
            
            if not available_tasks:
                print(f"⚠️  No tasks found for mode {mode}, using SAME_HOME as fallback")
                available_tasks = get_tasks_for_relationship_mode("SAME_HOME", "daily")
            
            # Select 3 random tasks
            daily_tasks = random.sample(available_tasks, min(3, len(available_tasks)))
            
            for task in daily_tasks:
                task["completed"] = False
                task["completed_at"] = None
                task["relationship_mode"] = mode
                task["task_type"] = "daily"
            
            await db.users.update_one(
                {"_id": current_user["_id"]},
                {"$set": {
                    "ai_daily_tasks": daily_tasks,
                    "last_task_date": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }}
            )
            
            print(f"✅ Using relationship-specific tasks from new database for mode: {mode}")
            
            return {
                "tasks": daily_tasks,
                "generated_for_mode": mode,
                "fallback": True,
                "source": "relationship_database"
            }
    
    # Return existing tasks with mode information
    existing_tasks = current_user.get("ai_daily_tasks", [])
    return {
        "tasks": existing_tasks,
        "generated_for_mode": mode
    }

@api_router.get("/tasks/weekly")
async def get_weekly_tasks(
    request: Request,
    regenerate: bool = False,
    current_user: dict = Depends(get_current_user)
):
    """Get weekly AI-generated tasks for current user's relationship mode"""
    today = datetime.utcnow()
    last_weekly_date = current_user.get("last_weekly_task_date")
    mode = current_user.get("relationship_mode", "SAME_HOME")
    
    # Get refresh tracking data
    weekly_refresh_count = current_user.get("weekly_refresh_count", 0)
    last_refresh_reset = current_user.get("last_weekly_refresh_reset")
    
    # Reset refresh count every Sunday (start of new week)
    if not last_refresh_reset or (today - last_refresh_reset).days >= 7:
        weekly_refresh_count = 0
        last_refresh_reset = today
        await db.users.update_one(
            {"_id": current_user["_id"]},
            {"$set": {
                "weekly_refresh_count": 0,
                "last_weekly_refresh_reset": today
            }}
        )
    
    # Check if manual refresh is requested but limit exceeded
    if regenerate and weekly_refresh_count >= 2:
        return {
            "error": "refresh_limit_exceeded",
            "message": "You've used both weekly refreshes. Try again next week!",
            "remaining_refreshes": 0,
            "tasks": current_user.get("ai_weekly_tasks", []),
            "generated_for_mode": mode
        }
    
    # Check if we need new weekly tasks (regenerate weekly on Sundays or after 7 days)
    need_new_tasks = (
        regenerate or
        not last_weekly_date or 
        (today - last_weekly_date).days >= 7 or
        not current_user.get("ai_weekly_tasks")
    )
    
    if need_new_tasks:
        try:
            # Get profile data for personalization (with consent check)
            user_profile = current_user if current_user.get("ai_consent", False) else None
            partner_profile = current_user.get("partner_profile") if current_user.get("ai_consent", False) else None
            
            # Generate AI tasks
            ai_tasks = await generate_weekly_tasks_for_mode(
                relationship_mode=mode,
                count=1,
                user_profile=user_profile,
                partner_profile=partner_profile
            )
            
            # Add relationship mode and type metadata
            for task in ai_tasks:
                task["relationship_mode"] = mode
                task["task_type"] = "weekly"
                task["completed"] = False
                task["completed_at"] = None
            
            # Increment refresh count if manually regenerated
            update_data = {
                "ai_weekly_tasks": ai_tasks,
                "last_weekly_task_date": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            if regenerate:
                update_data["weekly_refresh_count"] = weekly_refresh_count + 1
            
            # Store AI tasks
            await db.users.update_one(
                {"_id": current_user["_id"]},
                {"$set": update_data}
            )
            
            # Calculate remaining refreshes
            remaining_refreshes = 2 - (weekly_refresh_count + (1 if regenerate else 0))
            
            return {
                "tasks": ai_tasks,
                "generated_for_mode": mode,
                "generation_date": datetime.utcnow(),
                "remaining_refreshes": remaining_refreshes
            }
            
        except Exception as e:
            print(f"AI weekly task generation failed: {e}")
            # Fallback to relationship-specific static tasks (NEW DATABASE)
            available_tasks = get_tasks_for_relationship_mode(mode, "weekly")
            
            if not available_tasks:
                print(f"⚠️  No weekly tasks found for mode {mode}, using SAME_HOME as fallback")
                available_tasks = get_tasks_for_relationship_mode("SAME_HOME", "weekly")
            
            # Select 1 random weekly task (as per spec)
            weekly_tasks = random.sample(available_tasks, min(1, len(available_tasks)))
            
            for task in weekly_tasks:
                task["completed"] = False
                task["completed_at"] = None
                task["relationship_mode"] = mode
                task["task_type"] = "weekly"
            
            await db.users.update_one(
                {"_id": current_user["_id"]},
                {"$set": {
                    "ai_weekly_tasks": weekly_tasks,
                    "last_weekly_task_date": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }}
            )
            
            print(f"✅ Using relationship-specific weekly task from new database for mode: {mode}")
            
            return {
                "tasks": weekly_tasks,
                "generated_for_mode": mode,
                "fallback": True,
                "source": "relationship_database"
            }
    
    # Return existing tasks
    existing_tasks = current_user.get("ai_weekly_tasks", [])
    remaining_refreshes = 2 - weekly_refresh_count
    return {
        "tasks": existing_tasks,
        "generated_for_mode": mode,
        "remaining_refreshes": remaining_refreshes
    }

@api_router.post("/tasks/complete")
async def complete_task(task_data: TaskComplete, current_user: dict = Depends(get_current_user)):
    """Complete a task (both AI-generated and custom tasks)"""
    task_id = task_data.task_id
    user_id = current_user["_id"]
    
    points_earned = 0
    task_found = False
    task_category = ""
    task_type = ""
    
    # Initialize task arrays
    ai_daily_tasks = current_user.get("ai_daily_tasks", [])
    ai_weekly_tasks = current_user.get("ai_weekly_tasks", [])
    daily_tasks = current_user.get("daily_tasks", [])
    weekly_task = current_user.get("weekly_task")
    custom_tasks = current_user.get("custom_tasks", [])
    
    # Check AI daily tasks
    for task in ai_daily_tasks:
        if task["id"] == task_id and not task.get("completed", False):
            task["completed"] = True
            task["completed_at"] = datetime.utcnow()
            points_earned = task.get("points", 5)
            task_category = task.get("category", "")
            task_type = "daily"
            task_found = True
            break
    
    # Check AI weekly tasks
    if not task_found:
        for task in ai_weekly_tasks:
            if task["id"] == task_id and not task.get("completed", False):
                task["completed"] = True
                task["completed_at"] = datetime.utcnow()
                points_earned = task.get("points", 25)
                task_category = task.get("category", "")
                task_type = "weekly"
                task_found = True
                break
    
    # Check legacy daily tasks (fallback)
    if not task_found:
        for task in daily_tasks:
            if task["id"] == task_id and not task.get("completed", False):
                task["completed"] = True
                task["completed_at"] = datetime.utcnow()
                points_earned = task.get("points", 5)
                task_category = task.get("category", "")
                task_type = "daily"
                task_found = True
                break
    
    # Check legacy weekly task (fallback)
    if not task_found:
        if weekly_task and weekly_task["id"] == task_id and not weekly_task.get("completed", False):
            weekly_task["completed"] = True
            weekly_task["completed_at"] = datetime.utcnow()
            points_earned = weekly_task.get("points", 25)
            task_category = weekly_task.get("category", "")
            task_type = "weekly"
            task_found = True
    
    # Check custom tasks (user-created, preserved during mode changes)
    if not task_found:
        for task in custom_tasks:
            if task["id"] == task_id and not task.get("completed", False):
                task["completed"] = True
                task["completed_at"] = datetime.utcnow()
                points_earned = task.get("points", 5)
                task_category = "Custom"
                task_type = "custom"
                task_found = True
                break
    
    if not task_found:
        raise HTTPException(status_code=404, detail="Task not found or already completed")
    
    # GAMIFICATION SYSTEM: Award points and update stats
    print(f"🎮 GAMIFICATION: Awarding points for {task_type} task")
    
    # Check if task is a special event (birthday/anniversary)
    is_special_event = task_category in ["Birthday", "Anniversary", "Special Event"]
    
    # Check if completed within 1 hour (bonus points)
    # TODO: Implement reminder tracking to check completion time
    completed_within_hour = False
    
    # Award points through gamification service
    try:
        gamification_result = await gamification_service.award_points_for_task(
            user_id=user_id,
            task_type=task_type,
            is_special_event=is_special_event,
            completed_within_hour=completed_within_hour
        )
        
        print(f"✅ Points awarded: {gamification_result['points_earned']}")
        print(f"🔥 Streak: {gamification_result['new_streak']}")
        print(f"⬆️  Level: {gamification_result['new_level']}")
        if gamification_result['level_up']:
            print(f"🎉 LEVEL UP! New level: {gamification_result['new_level']} - {gamification_result['new_level_info']['name']}")
        
    except Exception as e:
        print(f"❌ Gamification error: {e}")
        # Fallback to old system if gamification fails
        gamification_result = {
            "points_earned": points_earned,
            "total_points": current_user.get("total_points", 0) + points_earned,
            "available_points": current_user.get("total_points", 0) + points_earned,
            "level_up": False,
            "new_level": current_user.get("current_level", 1),
            "new_level_info": None,
            "streak_update": False,
            "new_streak": current_user.get("current_streak", 0),
            "weekly_draw_eligible": False,
            "monthly_draw_eligible": False
        }
    
    # Update task arrays in database
    update_data = {
        "ai_daily_tasks": ai_daily_tasks,
        "ai_weekly_tasks": ai_weekly_tasks,
        "daily_tasks": daily_tasks,
        "custom_tasks": custom_tasks,
        "updated_at": datetime.utcnow()
    }
    
    # Update weekly task if it was modified
    if weekly_task is not None:
        update_data["weekly_task"] = weekly_task
    
    await db.users.update_one(
        {"_id": user_id},
        {"$set": update_data}
    )
    
    # Return comprehensive response
    return {
        "message": "Task completed successfully!",
        "points_earned": gamification_result["points_earned"],
        "total_points": gamification_result["total_points"],
        "available_points": gamification_result["available_points"],
        "new_level": gamification_result["new_level"],
        "level_up": gamification_result["level_up"],
        "level_up_info": gamification_result["new_level_info"],
        "current_streak": gamification_result["new_streak"],
        "streak_updated": gamification_result["streak_update"],
        "tasks_completed": current_user.get("tasks_completed", 0) + 1,
        "weekly_draw_eligible": gamification_result["weekly_draw_eligible"],
        "monthly_draw_eligible": gamification_result["monthly_draw_eligible"],
        "task_category": task_category,
        "task_type": task_type
    }

@api_router.post("/tasks/generate")
async def generate_tasks_manually(
    request: TaskGenerationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Manually generate AI tasks for testing and immediate refresh"""
    try:
        # Get profile data for personalization (with consent check)
        user_profile = current_user if request.use_profile_data and current_user.get("ai_consent", False) else None
        partner_profile = current_user.get("partner_profile") if request.use_profile_data and current_user.get("ai_consent", False) else None
        
        # Set default counts
        count = request.count or (3 if request.task_type == "daily" else 1)
        
        if request.task_type == "daily":
            ai_tasks = await generate_daily_tasks_for_mode(
                relationship_mode=request.relationship_mode,
                count=count,
                user_profile=user_profile,
                partner_profile=partner_profile
            )
        elif request.task_type == "weekly":
            ai_tasks = await generate_weekly_tasks_for_mode(
                relationship_mode=request.relationship_mode,
                count=count,
                user_profile=user_profile,
                partner_profile=partner_profile
            )
        else:
            raise HTTPException(status_code=400, detail="task_type must be 'daily' or 'weekly'")
        
        # Add metadata
        for task in ai_tasks:
            task["relationship_mode"] = request.relationship_mode
            task["task_type"] = request.task_type
            task["completed"] = False
            task["completed_at"] = None
        
        return {
            "tasks": ai_tasks,
            "relationship_mode": request.relationship_mode,
            "task_type": request.task_type,
            "count": len(ai_tasks),
            "used_profile_data": bool(user_profile and partner_profile),
            "generation_timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Task generation failed: {str(e)}")

# Alias endpoint for regenerating tasks (same as generate)
@api_router.post("/tasks/regenerate")
async def regenerate_tasks(
    request: TaskGenerationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Regenerate tasks - alias for generate_tasks_manually"""
    return await generate_tasks_manually(request, current_user)

@api_router.get("/gifts")
async def get_gift_ideas():
    return {"gifts": GIFT_IDEAS}

@api_router.get("/gifts/search")
async def search_gifts(
    query: Optional[str] = None,
    budget: Optional[str] = None,
    category: Optional[str] = None
):
    """Search and filter gifts by occasion, budget, category, or product name"""
    
    # Occasion to category mapping
    occasion_mapping = {
        "birthday": ["Chocolates", "Watches", "Jewelry", "Soft Toys", "Fashion", "Home", "Beauty"],
        "anniversary": ["Romantic", "Jewelry", "Watches", "Chocolates", "Beauty"],
        "valentine": ["Romantic", "Chocolates", "Jewelry", "Soft Toys", "Beauty"],
        "valentines": ["Romantic", "Chocolates", "Jewelry", "Soft Toys", "Beauty"],
        "wedding": ["Jewelry", "Watches", "Romantic", "Home"],
        "christmas": ["Chocolates", "Soft Toys", "Home", "Jewelry"],
        "diwali": ["Chocolates", "Jewelry", "Home", "Watches"],
        "graduation": ["Watches", "Fashion", "Home", "Jewelry"],
        "romantic": ["Romantic", "Chocolates", "Jewelry"],
        "love": ["Romantic", "Chocolates", "Jewelry", "Soft Toys"]
    }
    
    # Budget mapping
    budget_ranges = {
        "under_500": ["Under ₹500"],
        "under_1000": ["Under ₹500", "Under ₹1000", "₹500-₹1000"],
        "under_2000": ["Under ₹500", "Under ₹1000", "₹500-₹1000", "₹1000-₹1500", "₹1000-₹2000"],
        "luxury": ["₹2000-₹3000", "₹3000-₹5000", "₹1500-₹2000"]
    }
    
    filtered_gifts = GIFT_IDEAS.copy()
    filters_applied = {
        "occasion": None,
        "budget": None,
        "category": None,
        "search_term": None
    }
    
    # Apply filters
    if query:
        query_lower = query.lower().strip()
        filters_applied["search_term"] = query
        
        # Check if query matches an occasion
        matched_occasion = None
        for occasion, categories in occasion_mapping.items():
            if occasion in query_lower:
                matched_occasion = occasion
                filters_applied["occasion"] = occasion
                # Filter by occasion categories
                filtered_gifts = [g for g in filtered_gifts if g["category"] in categories]
                break
        
        # Check if query contains budget keywords
        if "under 500" in query_lower or "500" in query_lower and "1000" not in query_lower:
            budget = "under_500"
            filters_applied["budget"] = "under_500"
        elif "under 1000" in query_lower or "1000" in query_lower:
            budget = "under_1000"
            filters_applied["budget"] = "under_1000"
        elif "under 2000" in query_lower or "2000" in query_lower:
            budget = "under_2000"
            filters_applied["budget"] = "under_2000"
        elif "luxury" in query_lower or "expensive" in query_lower or "premium" in query_lower:
            budget = "luxury"
            filters_applied["budget"] = "luxury"
        
        # If not an occasion, search in name and description
        if not matched_occasion:
            filtered_gifts = [
                g for g in filtered_gifts 
                if query_lower in g["name"].lower() 
                or query_lower in g["description"].lower()
                or query_lower in g["category"].lower()
            ]
    
    # Apply budget filter
    if budget:
        budget_filter = budget_ranges.get(budget, [])
        if budget_filter:
            filters_applied["budget"] = budget
            filtered_gifts = [g for g in filtered_gifts if g["price_range"] in budget_filter]
    
    # Apply category filter
    if category and category != "All":
        filters_applied["category"] = category
        filtered_gifts = [g for g in filtered_gifts if g["category"] == category]
    
    # Generate suggestions based on results
    suggestions = []
    if len(filtered_gifts) == 0:
        suggestions = [
            "chocolates under 1000",
            "anniversary gifts",
            "romantic jewelry",
            "birthday watches"
        ]
    elif len(filtered_gifts) < 5:
        # Suggest related searches
        categories_in_results = list(set([g["category"] for g in filtered_gifts]))
        suggestions = [f"{cat.lower()} gifts" for cat in categories_in_results[:3]]
    
    return {
        "success": True,
        "total_results": len(filtered_gifts),
        "filters_applied": filters_applied,
        "gifts": filtered_gifts,
        "suggestions": suggestions
    }

@api_router.get("/messages/{category}")
async def get_messages(category: str):
    if category not in ROMANTIC_MESSAGES:
        raise HTTPException(status_code=404, detail="Message category not found")
    return {"messages": ROMANTIC_MESSAGES[category]}

@api_router.get("/messages/daily/{relationship_mode}")
async def get_daily_messages(relationship_mode: str):
    """Get 3 daily messages for specific relationship mode with monthly rotation"""
    try:
        # Import and initialize task generator
        from ai_task_service import AITaskGenerator
        
        # Validate relationship mode
        valid_modes = ["DAILY_IRL", "LONG_DISTANCE", "SAME_HOME"]
        if relationship_mode not in valid_modes:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid relationship mode. Must be one of: {valid_modes}"
            )
        
        # Get task generator instance
        task_generator = AITaskGenerator()
        
        # Get daily messages (3 messages per category, total 15 messages)
        messages = task_generator.get_daily_messages(relationship_mode, messages_per_category=3)
        
        if not messages:
            raise HTTPException(
                status_code=404, 
                detail=f"No messages available for relationship mode: {relationship_mode}"
            )
        
        return {
            "messages": messages,
            "relationship_mode": relationship_mode,
            "total_count": len(messages),
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise  # Re-raise HTTPException as-is
    except Exception as e:
        print(f"Error getting daily messages: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate daily messages")

# =======================
# NEW: AI PERSONALIZATION ENDPOINTS
# =======================

@api_router.post("/ai/generate-message")
async def generate_personalized_message(
    category: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate AI-powered personalized message
    Cost: ~₹0.02 per call (GPT-3.5 Turbo)
    Rate limit: 10 per day for free users
    """
    try:
        # Get user and partner info
        user_name = current_user.get('name', 'You')
        partner_name = current_user.get('partner_profile', {}).get('name', 'Your partner')
        relationship_mode = current_user.get('relationship_mode', 'DAILY_IRL')
        
        # Generate AI message
        message = await generate_ai_message(
            category=category,
            user_name=user_name,
            partner_name=partner_name,
            relationship_mode=relationship_mode
        )
        
        return {
            "success": True,
            "message": message,
            "category": category,
            "ai_generated": True,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"Error generating AI message: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate personalized message")


@api_router.get("/ai/smart-gifts")
async def get_smart_gift_recommendations(
    occasion: str = "general",
    budget: str = "Under ₹1000",
    current_user: dict = Depends(get_current_user)
):
    """
    Get AI-enhanced gift recommendations based on partner profile
    Cost: ~₹0.03 per call (GPT-3.5 Turbo)
    """
    try:
        # Get partner profile
        partner_profile = current_user.get('partner_profile', {})
        
        if not partner_profile:
            # Return regular gifts if no partner profile
            return {
                "success": True,
                "gifts": GIFT_IDEAS,
                "ai_enhanced": False,
                "message": "Add partner profile for personalized recommendations"
            }
        
        # Get AI-enhanced gift recommendations
        smart_gifts = await get_ai_gift_recommendations(
            partner_profile=partner_profile,
            occasion=occasion,
            budget=budget,
            available_gifts=GIFT_IDEAS
        )
        
        return {
            "success": True,
            "gifts": smart_gifts,
            "ai_enhanced": True,
            "occasion": occasion,
            "budget": budget,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"Error generating smart gifts: {e}")
        # Fallback to regular gifts
        return {
            "success": True,
            "gifts": GIFT_IDEAS,
            "ai_enhanced": False,
            "error": "AI recommendations unavailable"
        }


@api_router.post("/ai/plan-date")
async def create_ai_date_plan(
    budget: str = "Under ₹1000",
    preferences: Optional[str] = None,
    location: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate AI-powered date plan
    Cost: ~₹0.05 per call (GPT-3.5 Turbo)
    Rate limit: 3 per month for free users, unlimited for premium
    """
    try:
        relationship_mode = current_user.get('relationship_mode', 'DAILY_IRL')
        
        # Generate AI date plan
        date_plan = await plan_ai_date(
            relationship_mode=relationship_mode,
            budget=budget,
            preferences=preferences,
            location=location
        )
        
        return {
            "success": True,
            "date_plan": date_plan,
            "relationship_mode": relationship_mode,
            "ai_generated": True,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"Error generating date plan: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate date plan")

# =======================
# PUSH NOTIFICATION ENDPOINTS
# =======================

class RegisterPushTokenRequest(BaseModel):
    push_token: str
    device_info: Optional[Dict[str, Any]] = None

@api_router.post("/notifications/register")
async def register_push_token(
    request: RegisterPushTokenRequest,
    current_user: dict = Depends(get_current_user)
):
    """Register or update user's push notification token"""
    try:
        # Update user's push token
        result = await db.users.update_one(
            {"_id": current_user["_id"]},
            {
                "$set": {
                    "push_token": request.push_token,
                    "push_token_updated_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
            }
        )
        
        logger.info(f"Push token registered for user {current_user['_id']}: {result.modified_count} documents updated")
        
        return {
            "success": True,
            "message": "Push token registered successfully",
            "modified_count": result.modified_count
        }
        
    except Exception as e:
        logger.error(f"Error registering push token: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to register push token")


@api_router.post("/notifications/test")
async def send_test_notification(current_user: dict = Depends(get_current_user)):
    """Send a test push notification to current user"""
    try:
        push_token = current_user.get("push_token")
        
        if not push_token:
            raise HTTPException(
                status_code=400,
                detail="No push token registered. Please enable notifications in app."
            )
        
        # Send test notification
        success = push_notification_service.send_push_notification(
            push_token=push_token,
            title="🎉 Test Notification",
            body="Push notifications are working! You'll receive reminders for events and tasks.",
            data={"type": "test"}
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to send notification")
        
        return {
            "success": True,
            "message": "Test notification sent successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error sending test notification: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/notifications/preferences")
async def get_notification_preferences(current_user: dict = Depends(get_current_user)):
    """Get user's notification preferences"""
    preferences = current_user.get("notification_preferences", {})
    
    # Default all to True if not set
    default_prefs = {
        "streak_ending": True,
        "daily_love_message": True,
        "new_tasks": True,
        "daily_task_reminder": True,
        "weekly_task_reminder": True,
        "gift_ideas": True,
        "upcoming_events_10_days": True,
        "upcoming_events_7_days": True,
        "upcoming_events_3_days": True,
        "upcoming_events_1_day": True,
        "weekly_winner": True,
        "monthly_winner": True,
        "app_update": True,
    }
    
    return {
        "success": True,
        "preferences": {**default_prefs, **preferences}
    }


@api_router.put("/notifications/preferences")
async def update_notification_preferences(
    preferences: Dict[str, bool],
    current_user: dict = Depends(get_current_user)
):
    """Update user's notification preferences"""
    try:
        await db.users.update_one(
            {"_id": current_user["_id"]},
            {
                "$set": {
                    "notification_preferences": preferences,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return {
            "success": True,
            "message": "Notification preferences updated",
            "preferences": preferences
        }
        
    except Exception as e:
        print(f"Error updating preferences: {e}")
        raise HTTPException(status_code=500, detail="Failed to update preferences")

@api_router.get("/events")
async def get_events(
    request: Request,
    limit: Optional[int] = None,
    offset: Optional[int] = 0,
    current_user: dict = Depends(get_current_user)
):
    """Get comprehensive merged calendar with Indian + International events, auto-generated personal events, and enhanced features"""
    try:
        # Use enhanced calendar service to get all events
        calendar_data = enhanced_calendar_service.get_merged_calendar_events(current_user)
        
        # Apply pagination if requested
        if limit is not None:
            total_events = calendar_data["events"]
            paginated_events = total_events[offset:offset + limit]
            calendar_data["events"] = paginated_events
            calendar_data["pagination"] = {
                "limit": limit,
                "offset": offset,
                "total": len(total_events),
                "has_more": offset + limit < len(total_events)
            }
        
        return calendar_data
    except Exception as e:
        print(f"Error generating enhanced calendar: {e}")
        # Fallback to basic response if enhanced service fails
        return {
            "events": [],
            "total_count": 0,
            "categories": [],
            "upcoming_count": 0,
            "this_month_count": 0,
            "error": "Unable to load calendar data",
            "generated_at": datetime.utcnow().isoformat()
        }

@api_router.get("/events/{event_id}/details")
async def get_event_details(event_id: str, current_user: dict = Depends(get_current_user)):
    """Get detailed information for a specific event including tips, tasks, and reminders"""
    try:
        # Get all events first
        calendar_data = enhanced_calendar_service.get_merged_calendar_events(current_user)
        
        # Find specific event details
        event_details = enhanced_calendar_service.get_event_details(event_id, calendar_data["events"])
        
        if not event_details:
            raise HTTPException(status_code=404, detail="Event not found")
        
        return {
            "event": event_details,
            "success": True
        }
        
    except Exception as e:
        print(f"Error getting event details: {e}")
        raise HTTPException(status_code=500, detail="Unable to fetch event details")

@api_router.post("/events/custom")
async def create_custom_event(event_data: CustomEvent, current_user: dict = Depends(get_current_user)):
    """Create a custom user event with default reminders (max 20 per user)"""
    # Check if user already has 20 custom events
    user_id = str(current_user["_id"])
    existing_custom_events = len(current_user.get("custom_events", []))
    
    if existing_custom_events >= 20:
        raise HTTPException(status_code=400, detail="Maximum 20 custom events allowed per user")
    
    # Add user_id and enhanced metadata to event
    event_data.user_id = user_id
    event_dict = event_data.dict()
    event_dict["created_at"] = datetime.utcnow()
    event_dict["id"] = f"custom_{datetime.utcnow().timestamp()}"
    event_dict["category"] = "custom"
    event_dict["type"] = "custom"
    
    # Add enhanced metadata and backend-calculated fields
    event_dict["importance"] = event_dict.get("importance", "medium")
    
    # Calculate reminder date based on reminder settings
    reminder_days = event_dict["reminder_settings"]["days_before"]
    event_dict["reminder_days"] = reminder_days
    event_date = event_dict["date"]
    if isinstance(event_date, str):
        event_date = datetime.strptime(event_date, "%Y-%m-%d")
    reminder_date = event_date - timedelta(days=reminder_days)
    event_dict["reminder_date"] = reminder_date.strftime("%Y-%m-%d")
    event_dict["date"] = event_date.strftime("%Y-%m-%d")
    
    # Add default tips and tasks for custom events
    event_dict["tips"] = [
        "Plan ahead for this special occasion",
        "Set reminders for preparations needed",
        "Consider what would make this day meaningful",
        "Prepare any gifts or surprises in advance"
    ]
    
    event_dict["tasks"] = [
        {"task": "Plan activities for the day", "category": "planning", "points": 10},
        {"task": "Prepare any gifts or surprises", "category": "preparation", "points": 15},
        {"task": "Set up celebrations or arrangements", "category": "setup", "points": 10}
    ]
    
    # Add to user's custom events
    await db.users.update_one(
        {"_id": current_user["_id"]},
        {"$push": {"custom_events": event_dict}}
    )
    
    return {
        "message": "Custom event created successfully with reminders and tasks", 
        "event": event_dict
    }

@api_router.patch("/events/custom/{event_id}")
async def update_custom_event(
    event_id: str,
    update_data: EventUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update a custom event (only owner can edit)"""
    user_id = str(current_user["_id"])
    
    # Check if event exists and belongs to user
    user_events = current_user.get("custom_events", [])
    event_index = None
    for i, event in enumerate(user_events):
        if event.get("id") == event_id:
            event_index = i
            break
    
    if event_index is None:
        raise HTTPException(status_code=404, detail="Event not found or access denied")
    
    # Build update dictionary
    update_dict = {}
    if update_data.name is not None:
        update_dict[f"custom_events.{event_index}.name"] = update_data.name
    if update_data.date is not None:
        update_dict[f"custom_events.{event_index}.date"] = update_data.date.strftime("%Y-%m-%d")
        # Recalculate reminder date if date changed
        if update_data.reminder_settings:
            reminder_days = update_data.reminder_settings.days_before
        else:
            reminder_days = user_events[event_index].get("reminder_settings", {}).get("days_before", 10)
        reminder_date = update_data.date - timedelta(days=reminder_days)
        update_dict[f"custom_events.{event_index}.reminder_date"] = reminder_date.strftime("%Y-%m-%d")
        update_dict[f"custom_events.{event_index}.reminder_days"] = reminder_days
    if update_data.description is not None:
        update_dict[f"custom_events.{event_index}.description"] = update_data.description
    if update_data.importance is not None:
        update_dict[f"custom_events.{event_index}.importance"] = update_data.importance
    if update_data.reminder_settings is not None:
        update_dict[f"custom_events.{event_index}.reminder_settings"] = update_data.reminder_settings.dict()
        # Recalculate reminder date if reminder settings changed
        event_date = update_data.date or datetime.strptime(user_events[event_index]["date"], "%Y-%m-%d")
        reminder_days = update_data.reminder_settings.days_before
        reminder_date = event_date - timedelta(days=reminder_days)
        update_dict[f"custom_events.{event_index}.reminder_date"] = reminder_date.strftime("%Y-%m-%d")
        update_dict[f"custom_events.{event_index}.reminder_days"] = reminder_days
    
    if not update_dict:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    # Update the event
    result = await db.users.update_one(
        {"_id": current_user["_id"]},
        {"$set": update_dict}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Event not found or no changes made")
    
    # Return updated event
    updated_user = await db.users.find_one({"_id": current_user["_id"]})
    updated_event = updated_user["custom_events"][event_index]
    
    return {"message": "Event updated successfully", "event": updated_event}

@api_router.delete("/events/custom/{event_id}")
async def delete_custom_event(event_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a custom event or personal event (birthday/anniversary)"""
    user_id = str(current_user["_id"])
    
    # Check if it's a custom event first
    user_events = current_user.get("custom_events", [])
    event_exists = any(event.get("id") == event_id for event in user_events)
    
    if event_exists:
        # Delete custom event
        result = await db.users.update_one(
            {"_id": current_user["_id"]},
            {"$pull": {"custom_events": {"id": event_id}}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Event not found")
        
        return {"message": "Custom event deleted successfully", "deleted_event_id": event_id}
    
    # Check if it's a personal event (birthday or anniversary)
    partner_profile = current_user.get("partner_profile", {})
    
    # Handle birthday deletion
    if event_id.startswith("partner_birthday_"):
        if not partner_profile.get("birthday"):
            raise HTTPException(status_code=404, detail="Birthday event not found")
        
        # Clear the birthday from partner profile
        result = await db.users.update_one(
            {"_id": current_user["_id"]},
            {"$unset": {"partner_profile.birthday": ""}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Failed to delete birthday event")
        
        return {"message": "Birthday event deleted successfully", "deleted_event_id": event_id}
    
    # Handle anniversary deletion
    if event_id.startswith("anniversary_"):
        if not partner_profile.get("anniversary"):
            raise HTTPException(status_code=404, detail="Anniversary event not found")
        
        # Clear the anniversary from partner profile
        result = await db.users.update_one(
            {"_id": current_user["_id"]},
            {"$unset": {"partner_profile.anniversary": ""}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Failed to delete anniversary event")
        
        return {"message": "Anniversary event deleted successfully", "deleted_event_id": event_id}
    
    # Event not found in any category
    raise HTTPException(status_code=404, detail="Event not found or access denied")

@api_router.put("/events/{event_id}/reminder")
async def update_event_reminder(
    event_id: str, 
    reminder_days: int,
    current_user: dict = Depends(get_current_user)
):
    """Update reminder days for a specific event"""
    try:
        # Update reminder for custom events
        result = await db.users.update_one(
            {"_id": current_user["_id"], "custom_events.id": event_id},
            {"$set": {
                "custom_events.$.reminder_days": reminder_days,
                "custom_events.$.updated_at": datetime.utcnow()
            }}
        )
        
        if result.modified_count > 0:
            return {"message": f"Reminder updated to {reminder_days} days before event"}
        else:
            raise HTTPException(status_code=404, detail="Event not found or not customizable")
            
    except Exception as e:
        print(f"Error updating reminder: {e}")
        raise HTTPException(status_code=500, detail="Unable to update reminder")

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =======================
# GIFTS ENDPOINTS
# =======================

@app.get("/api/gifts", tags=["Gifts"])
async def get_gifts():
    """Get curated romantic gift ideas with Amazon affiliate links - All gifts have unique images"""
    return {
        "success": True,
        "gifts": GIFT_IDEAS,
        "total": len(GIFT_IDEAS)
    }

# =======================
# SUBSCRIPTION ENDPOINTS
# =======================

class CreateSubscriptionRequest(BaseModel):
    plan_type: str = Field(..., description="Plan type: 'monthly' or 'sixmonth'")

class VerifyPaymentRequest(BaseModel):
    payment_id: str
    subscription_id: str
    signature: str

class StartSubscriptionRequest(BaseModel):
    subscription_type: str = Field(..., description="trial, monthly, or half_yearly")

# =======================
# SUBSCRIPTION ENDPOINTS (MOCKUP - No Payment)
# =======================

@app.get("/api/subscription/status", tags=["Subscriptions"])
async def get_subscription_status(current_user: dict = Depends(get_current_user)):
    """Get user's subscription status with auto-renewal info"""
    try:
        # Check for auto-renewal first
        renewal_update = subscription_service.auto_renew_subscription(current_user)
        if renewal_update:
            await db.users.update_one(
                {"_id": current_user["_id"]},
                {"$set": renewal_update}
            )
            # Refresh user data after renewal
            current_user = await db.users.find_one({"_id": current_user["_id"]})
            logger.info(f"Auto-renewed subscription for user {current_user['_id']}")
        
        # Check and expire if needed (only if not renewed)
        if not renewal_update:
            expiry_update = subscription_service.check_and_expire_subscriptions(current_user)
            if expiry_update:
                await db.users.update_one(
                    {"_id": current_user["_id"]},
                    {"$set": expiry_update}
                )
                # Refresh user data
                current_user = await db.users.find_one({"_id": current_user["_id"]})
        
        # Get subscription info
        subscription_info = subscription_service.get_subscription_info(current_user)
        
        # Get renewal info
        auto_renewal_enabled = current_user.get("auto_renewal_enabled", True)
        renewal_date = None
        renewal_date_display = None
        
        if subscription_info.subscription_end_date and subscription_info.is_active:
            renewal_date = subscription_info.subscription_end_date.isoformat()
            renewal_date_display = subscription_service.get_renewal_date_display(subscription_info.subscription_end_date)
        
        # Prize eligibility check: free trial users cannot win prizes
        is_eligible_for_prizes = (
            subscription_info.is_active and 
            subscription_info.subscription_type != "free_trial"
        )
        
        return {
            "success": True,
            "subscription": {
                "type": subscription_info.subscription_type,
                "status": subscription_info.subscription_status,
                "is_active": subscription_info.is_active,
                "days_remaining": subscription_info.days_remaining,
                "can_start_trial": subscription_info.can_start_trial,
                "trial_already_used": not subscription_info.can_start_trial,  # Explicit flag
                "start_date": subscription_info.subscription_start_date.isoformat() if subscription_info.subscription_start_date else None,
                "end_date": subscription_info.subscription_end_date.isoformat() if subscription_info.subscription_end_date else None,
                "renewal_date": renewal_date,
                "renewal_date_display": renewal_date_display,
                "auto_renewal_enabled": auto_renewal_enabled,
                "renewal_count": current_user.get("renewal_count", 0),
                "display_text": subscription_service.get_display_text(subscription_info),
                "is_eligible_for_prizes": is_eligible_for_prizes  # NEW: Prize eligibility
            }
        }
    except Exception as e:
        print(f"Error getting subscription status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/subscription/start-trial", tags=["Subscriptions"])
async def start_free_trial(current_user: dict = Depends(get_current_user)):
    """Start 14-day free trial"""
    try:
        # Check if user can start trial
        subscription_info = subscription_service.get_subscription_info(current_user)
        
        if not subscription_info.can_start_trial:
            raise HTTPException(status_code=400, detail="Free trial already used")
        
        if subscription_info.is_active:
            raise HTTPException(status_code=400, detail="You already have an active subscription")
        
        # Start trial
        trial_data = subscription_service.start_trial(current_user["_id"])
        
        # Update user
        await db.users.update_one(
            {"_id": current_user["_id"]},
            {"$set": trial_data}
        )
        
        return {
            "success": True,
            "message": "Free trial started successfully!",
            "subscription": {
                "type": "trial",
                "status": "active",
                "days_remaining": 14,
                "end_date": trial_data["subscription_end_date"].isoformat()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error starting trial: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/subscription/start-mockup", tags=["Subscriptions"])
async def start_mockup_subscription(
    request: StartSubscriptionRequest,
    current_user: dict = Depends(get_current_user)
):
    """Start subscription (MOCKUP - no payment required)"""
    try:
        subscription_type = request.subscription_type
        
        if subscription_type == "trial":
            # Use the trial endpoint
            return await start_free_trial(current_user)
        
        elif subscription_type in ["monthly", "half_yearly"]:
            # Create mockup paid subscription (no payment)
            subscription_data = subscription_service.create_subscription(
                subscription_type,
                f"mock_sub_{current_user['_id']}",
                f"mock_cust_{current_user['_id']}"
            )
            
            # Update user
            await db.users.update_one(
                {"_id": current_user["_id"]},
                {"$set": subscription_data}
            )
            
            days = 30 if subscription_type == "monthly" else 180
            price = "₹79" if subscription_type == "monthly" else "₹450"
            
            return {
                "success": True,
                "message": f"Subscription activated successfully! (MOCKUP - {price})",
                "subscription": {
                    "type": subscription_type,
                    "status": "active",
                    "days_remaining": days,
                    "end_date": subscription_data["subscription_end_date"].isoformat(),
                    "mockup": True
                }
            }
        else:
            raise HTTPException(status_code=400, detail="Invalid subscription type")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error starting subscription: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Razorpay endpoint removed - Prepare for new payment gateway integration


# Razorpay endpoint removed - Prepare for new payment gateway integration



# Razorpay endpoint removed - Prepare for new payment gateway integration

# Razorpay endpoint removed - Prepare for new payment gateway integration

# Razorpay endpoint removed - Using /api/subscription/status instead

# Razorpay endpoint removed - Prepare for new payment gateway integration

# ==================== FEEDBACK SYSTEM ====================

class FeedbackSubmission(BaseModel):
    type: Literal["bug", "feature", "general"]
    message: str = Field(..., min_length=10, max_length=1000)
    email: Optional[str] = None
    images: Optional[List[str]] = Field(default=[], max_items=3)

@api_router.post("/feedback")
async def submit_feedback(
    feedback: FeedbackSubmission,
    current_user: dict = Depends(get_current_user)
):
    """Submit user feedback, bug reports, or feature requests"""
    try:
        # Create feedback document
        feedback_doc = {
            "user_id": str(current_user["_id"]),
            "user_email": current_user["email"],
            "user_name": current_user.get("name", "Anonymous"),
            "type": feedback.type,
            "message": feedback.message,
            "contact_email": feedback.email or current_user["email"],
            "images": feedback.images or [],
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Save to database
        result = await db.feedback.insert_one(feedback_doc)
        
        return {
            "success": True,
            "message": "Thanks for helping make Pookie4U better ❤️",
            "feedback_id": str(result.inserted_id)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to submit feedback: {str(e)}")

@api_router.get("/feedback/my")
async def get_my_feedback(
    current_user: dict = Depends(get_current_user)
):
    """Get user's feedback history"""
    try:
        # Get user's feedback
        feedback_list = await db.feedback.find(
            {"user_id": str(current_user["_id"])}
        ).sort("created_at", -1).to_list(length=50)
        
        # Convert ObjectId to string
        for item in feedback_list:
            item["_id"] = str(item["_id"])
        
        return {
            "success": True,
            "feedback": feedback_list
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch feedback: {str(e)}")

@api_router.get("/feedback/all")
async def get_all_feedback(
    status: Optional[str] = None,
    type: Optional[str] = None,
    limit: int = 100
):
    """
    ADMIN ENDPOINT: Get all feedback submissions
    
    Query params:
    - status: pending, reviewed, resolved (optional)
    - type: bug, feature, general (optional)
    - limit: max number of results (default 100)
    
    Access this at: https://your-domain.com/api/feedback/all
    """
    try:
        # Build query filter
        query = {}
        if status:
            query["status"] = status
        if type:
            query["type"] = type
        
        # Get feedback with filters
        feedback_list = await db.feedback.find(query).sort("created_at", -1).to_list(length=limit)
        
        # Convert ObjectId to string
        for item in feedback_list:
            item["_id"] = str(item["_id"])
        
        return {
            "success": True,
            "total": len(feedback_list),
            "feedback": feedback_list
        }
        
    except Exception as e:
        logger.error(f"Error fetching all feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch feedback: {str(e)}")

# ==================== REFERRAL SYSTEM ====================

class ReferralCode(BaseModel):
    code: str = Field(..., pattern=r'^POO-[A-Z0-9]{6}$')

@api_router.get("/referral/my-code")
async def get_my_referral_code(
    current_user: dict = Depends(get_current_user)
):
    """Get or generate user's referral code"""
    try:
        # Generate referral code if doesn't exist
        if not current_user.get("referral_code"):
            while True:
                code = generate_referral_code()
                # Check if code already exists
                existing = await db.users.find_one({"referral_code": code})
                if not existing:
                    await db.users.update_one(
                        {"_id": current_user["_id"]},
                        {"$set": {"referral_code": code}}
                    )
                    break
        else:
            code = current_user["referral_code"]
        
        # Get referral stats
        referrals_count = await db.users.count_documents({"referred_by": str(current_user["_id"])})
        points_earned = referrals_count * 50
        
        return {
            "success": True,
            "code": code,
            "referrals_count": referrals_count,
            "points_earned": points_earned
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting referral code: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get referral code: {str(e)}")

@api_router.post("/referral/apply")
async def apply_referral_code(
    referral_data: ReferralCode,
    current_user: dict = Depends(get_current_user)
):
    """Apply referral code (for new users during registration)"""
    try:
        # Check if user already used a referral code
        if current_user.get("referred_by"):
            raise HTTPException(status_code=400, detail="You have already used a referral code")
        
        # Check if user is trying to use own code
        if current_user.get("referral_code") == referral_data.code:
            raise HTTPException(status_code=400, detail="Cannot use your own referral code")
        
        # Find referrer
        referrer = await db.users.find_one({"referral_code": referral_data.code})
        if not referrer:
            raise HTTPException(status_code=404, detail="Invalid referral code")
        
        # Prevent using code from same device/account (anti-fraud)
        if current_user.get("created_at"):
            user_age_hours = (datetime.utcnow() - datetime.fromisoformat(current_user["created_at"])).total_seconds() / 3600
            if user_age_hours > 24:  # Can only apply within 24 hours of registration
                raise HTTPException(status_code=400, detail="Referral code can only be applied within 24 hours of registration")
        
        # Award points to both users
        referrer_points = referrer.get("points", 0) + 50
        new_user_points = current_user.get("points", 0) + 50
        
        # Update referrer
        await db.users.update_one(
            {"_id": referrer["_id"]},
            {
                "$set": {"points": referrer_points},
                "$inc": {"referral_count": 1}
            }
        )
        
        # Update new user
        await db.users.update_one(
            {"_id": current_user["_id"]},
            {
                "$set": {
                    "referred_by": str(referrer["_id"]),
                    "referral_code_used": referral_data.code,
                    "points": new_user_points
                }
            }
        )
        
        # Log referral in history
        referral_log = {
            "referrer_id": str(referrer["_id"]),
            "referee_id": str(current_user["_id"]),
            "referral_code": referral_data.code,
            "points_awarded": 50,
            "created_at": datetime.utcnow().isoformat()
        }
        await db.referrals.insert_one(referral_log)
        
        # Send notification to referrer
        if referrer.get("push_token"):
            try:
                push_notification_service.send_referral_success_notification(
                    push_token=referrer["push_token"],
                    referee_name=current_user.get("name", "A friend"),
                    points_earned=50
                )
            except Exception as e:
                logger.error(f"Failed to send referral notification: {str(e)}")
        
        return {
            "success": True,
            "message": "Referral code applied! You both earned 50 points 🎉",
            "points_earned": 50,
            "total_points": new_user_points
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error applying referral code: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to apply referral code: {str(e)}")

@api_router.get("/referral/stats")
async def get_referral_stats(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get detailed referral statistics"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("email")
        
        if not email:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
        user = await db.users.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get referred users
        referred_users = await db.users.find(
            {"referred_by": str(user["_id"])},
            {"name": 1, "created_at": 1}
        ).to_list(length=100)
        
        return {
            "success": True,
            "total_referrals": len(referred_users),
            "total_points_earned": len(referred_users) * 50,
            "referral_code": user.get("referral_code", ""),
            "referred_users": [
                {
                    "name": u["name"],
                    "joined_at": u.get("created_at", "")
                }
                for u in referred_users
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting referral stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get referral stats: {str(e)}")

# ==================== REWARD MILESTONE SYSTEM ====================

class RewardRedemption(BaseModel):
    reward_type: Literal["upi_transfer", "gift_coupon"]
    upi_id: Optional[str] = None  # Required for UPI transfers
    amount: int = 100  # Fixed amount for now

@api_router.get("/rewards/check-milestone")
async def check_reward_milestone(
    current_user: dict = Depends(get_current_user)
):
    """Check if user has reached 1000 points milestone and auto-generate coupons"""
    try:
        current_points = current_user.get("points", 0)
        milestones_claimed = current_user.get("milestones_claimed", 0)
        
        # Calculate how many milestones user has reached
        milestones_reached = current_points // 1000
        
        # Check if there are unclaimed milestones
        unclaimed_milestones = milestones_reached - milestones_claimed
        
        # Auto-generate coupons for unclaimed milestones
        new_coupons = []
        if unclaimed_milestones > 0:
            for i in range(unclaimed_milestones):
                milestone_number = milestones_claimed + i + 1
                coupon_code = f"POOKIE-{secrets.token_hex(4).upper()}"
                
                # Create reward record
                reward_doc = {
                    "user_id": str(current_user["_id"]),
                    "user_email": current_user["email"],
                    "user_name": current_user.get("name", "User"),
                    "reward_type": "gift_coupon",
                    "coupon_code": coupon_code,
                    "milestone_number": milestone_number,
                    "points_at_redemption": current_points,
                    "status": "approved",
                    "created_at": datetime.utcnow().isoformat(),
                    "approved_at": datetime.utcnow().isoformat(),
                    "approved_by": "system_auto"
                }
                
                await db.rewards.insert_one(reward_doc)
                new_coupons.append({
                    "coupon_code": coupon_code,
                    "milestone": milestone_number
                })
            
            # Update user's milestones_claimed count
            await db.users.update_one(
                {"_id": current_user["_id"]},
                {
                    "$set": {
                        "milestones_claimed": milestones_reached,
                        "last_reward_at": datetime.utcnow().isoformat()
                    }
                }
            )
            
            # Send push notification for new coupons
            if current_user.get("push_token") and new_coupons:
                try:
                    push_notification_service.send_reward_approved_notification(
                        push_token=current_user["push_token"],
                        reward_type="gift_coupon",
                        coupon_code=new_coupons[0]["coupon_code"]
                    )
                except Exception as e:
                    logger.error(f"Failed to send reward notification: {str(e)}")
        
        # Calculate next milestone
        next_milestone = (milestones_reached + 1) * 1000
        points_to_next = next_milestone - current_points
        
        return {
            "success": True,
            "current_points": current_points,
            "milestones_reached": milestones_reached,
            "milestones_claimed": milestones_reached,  # Now always synced
            "new_coupons": new_coupons,
            "next_milestone": next_milestone,
            "points_to_next_milestone": points_to_next,
            "has_new_rewards": len(new_coupons) > 0
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking milestone: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to check milestone: {str(e)}")

@api_router.post("/rewards/redeem")
async def redeem_reward(
    redemption: RewardRedemption,
    current_user: dict = Depends(get_current_user)
):
    """Redeem reward when user reaches 1000 points"""
    try:
        current_points = current_user.get("points", 0)
        
        # Check if user has enough points
        if current_points < 1000:
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient points. You have {current_points} points, need 1000."
            )
        
        # Validate UPI ID if UPI transfer
        if redemption.reward_type == "upi_transfer":
            if not redemption.upi_id or len(redemption.upi_id) < 3:
                raise HTTPException(status_code=400, detail="Valid UPI ID is required for UPI transfer")
        
        # Calculate cycle number
        cycles_completed = current_user.get("reward_cycles_completed", 0)
        new_cycle_number = cycles_completed + 1
        
        # Calculate remaining points after redemption
        remaining_points = current_points - 1000
        
        # Generate coupon code for gift coupon option
        coupon_code = None
        if redemption.reward_type == "gift_coupon":
            coupon_code = f"POOKIE-{secrets.token_hex(4).upper()}"
        
        # Create reward record
        reward_doc = {
            "user_id": str(current_user["_id"]),
            "user_email": current_user["email"],
            "user_name": current_user.get("name", "User"),
            "reward_type": redemption.reward_type,
            "amount": redemption.amount if redemption.reward_type == "upi_transfer" else None,
            "upi_id": redemption.upi_id if redemption.reward_type == "upi_transfer" else None,
            "coupon_code": coupon_code,
            "cycle_number": new_cycle_number,
            "status": "pending" if redemption.reward_type == "upi_transfer" else "approved",
            "points_redeemed": 1000,
            "points_before": current_points,
            "points_after": remaining_points,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "approved_at": datetime.utcnow().isoformat() if redemption.reward_type == "gift_coupon" else None,
            "approved_by": "system" if redemption.reward_type == "gift_coupon" else None
        }
        
        result = await db.rewards.insert_one(reward_doc)
        
        # Update user points and cycle count
        await db.users.update_one(
            {"_id": current_user["_id"]},
            {
                "$set": {
                    "points": remaining_points,
                    "reward_cycles_completed": new_cycle_number,
                    "last_reward_at": datetime.utcnow().isoformat()
                }
            }
        )
        
        # Send notification for instant approval (gift coupon)
        if redemption.reward_type == "gift_coupon" and current_user.get("push_token"):
            try:
                push_notification_service.send_reward_approved_notification(
                    push_token=current_user["push_token"],
                    reward_type="gift_coupon",
                    coupon_code=coupon_code
                )
            except Exception as e:
                logger.error(f"Failed to send reward notification: {str(e)}")
        
        response_message = ""
        if redemption.reward_type == "upi_transfer":
            response_message = f"UPI transfer request submitted! You'll receive ₹{redemption.amount} once approved by admin."
        else:
            response_message = f"Congratulations! Your gift coupon code is: {coupon_code}"
        
        return {
            "success": True,
            "message": response_message,
            "reward_id": str(result.inserted_id),
            "reward_type": redemption.reward_type,
            "cycle_number": new_cycle_number,
            "coupon_code": coupon_code,
            "remaining_points": remaining_points,
            "status": reward_doc["status"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error redeeming reward: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to redeem reward: {str(e)}")

@api_router.get("/rewards/history")
async def get_reward_history(
    current_user: dict = Depends(get_current_user)
):
    """Get user's reward redemption history"""
    try:
        # Get all rewards for this user
        rewards = await db.rewards.find(
            {"user_id": str(current_user["_id"])}
        ).sort("created_at", -1).to_list(length=100)
        
        # Convert ObjectId to string
        for reward in rewards:
            reward["_id"] = str(reward["_id"])
        
        return {
            "success": True,
            "total_redemptions": len(rewards),
            "rewards": rewards,
            "current_points": current_user.get("points", 0),
            "cycles_completed": current_user.get("reward_cycles_completed", 0)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching reward history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch reward history: {str(e)}")

@api_router.get("/admin/rewards/pending")
async def get_pending_rewards(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Admin endpoint to get all pending reward requests"""
    try:
        # TODO: Add admin authentication check
        
        pending_rewards = await db.rewards.find(
            {"status": "pending"}
        ).sort("created_at", -1).to_list(length=100)
        
        for reward in pending_rewards:
            reward["_id"] = str(reward["_id"])
        
        return {
            "success": True,
            "pending_count": len(pending_rewards),
            "rewards": pending_rewards
        }
        
    except Exception as e:
        logger.error(f"Error fetching pending rewards: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch pending rewards: {str(e)}")

@api_router.post("/admin/rewards/{reward_id}/approve")
async def approve_reward(
    reward_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Admin endpoint to approve a reward request"""
    try:
        # TODO: Add admin authentication check
        
        from bson import ObjectId
        
        reward = await db.rewards.find_one({"_id": ObjectId(reward_id)})
        if not reward:
            raise HTTPException(status_code=404, detail="Reward not found")
        
        if reward["status"] != "pending":
            raise HTTPException(status_code=400, detail="Reward is not pending")
        
        # Update reward status
        await db.rewards.update_one(
            {"_id": ObjectId(reward_id)},
            {
                "$set": {
                    "status": "approved",
                    "approved_at": datetime.utcnow().isoformat(),
                    "approved_by": "admin",
                    "updated_at": datetime.utcnow().isoformat()
                }
            }
        )
        
        # Send notification to user
        user = await db.users.find_one({"_id": ObjectId(reward["user_id"])})
        if user and user.get("push_token"):
            try:
                push_notification_service.send_reward_approved_notification(
                    push_token=user["push_token"],
                    reward_type=reward["reward_type"],
                    amount=reward.get("amount"),
                    coupon_code=reward.get("coupon_code")
                )
            except Exception as e:
                logger.error(f"Failed to send approval notification: {str(e)}")
        
        return {
            "success": True,
            "message": "Reward approved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error approving reward: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to approve reward: {str(e)}")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

# ============================================================================
# GAMIFICATION SYSTEM API ENDPOINTS
# ============================================================================

# Global gamification service instance
gamification_service = None

@api_router.get("/gamification/stats")
async def get_gamification_stats(current_user: dict = Depends(get_current_user_flexible)):
    """
    Get user's complete gamification stats
    Returns points, level, streak, and eligibility info
    """
    user_id = current_user["_id"]
    user = await db.users.find_one({"_id": user_id})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Calculate available points
    total_points = user.get("total_points", 0)
    points_spent = user.get("points_spent", 0)
    available_points = total_points - points_spent
    
    # Get current level info
    current_level = user.get("current_level", 1)
    level_info = LEVEL_THRESHOLDS.get(current_level, LEVEL_THRESHOLDS[1])
    
    # Get next level info
    next_level = current_level + 1
    next_level_info = LEVEL_THRESHOLDS.get(next_level)
    
    # Calculate progress to next level
    if next_level_info:
        points_needed = next_level_info["points"] - total_points
        progress_percentage = ((total_points - level_info["points"]) / 
                              (next_level_info["points"] - level_info["points"])) * 100
    else:
        points_needed = 0
        progress_percentage = 100
    
    # Check prize eligibility
    current_streak = user.get("current_streak", 0)
    weekly_eligible = current_streak >= 7
    monthly_eligible = current_streak >= 30
    
    return {
        "success": True,
        "points": {
            "total": total_points,
            "available": available_points,
            "spent": points_spent
        },
        "level": {
            "current": current_level,
            "name": level_info["name"],
            "unlock": level_info["unlock"],
            "next_level": next_level if next_level_info else None,
            "next_level_name": next_level_info["name"] if next_level_info else None,
            "next_level_unlock": next_level_info["unlock"] if next_level_info else None,
            "points_to_next": points_needed,
            "progress_percentage": min(100, max(0, progress_percentage))
        },
        "streak": {
            "current": current_streak,
            "longest": user.get("longest_streak", 0),
            "daily_tasks_today": user.get("daily_tasks_completed_today", 0),
            "tasks_total": user.get("tasks_completed", 0)
        },
        "prize_eligibility": {
            "weekly_draw": weekly_eligible,
            "monthly_draw": monthly_eligible,
            "days_to_weekly": max(0, 7 - current_streak) if not weekly_eligible else 0,
            "days_to_monthly": max(0, 30 - current_streak) if not monthly_eligible else 0
        },
        "features_unlocked": {
            "love_language": current_level >= 5,
            "mood_tracker": current_level >= 5,
            "advanced_date_generator": current_level >= 10,
            "love_language_filtering": current_level >= 15,
            "anniversary_toolkit": current_level >= 20
        }
    }

@api_router.post("/store/purchase")
async def purchase_store_item(
    item_request: dict,
    current_user: dict = Depends(get_current_user_flexible)
):
    """
    Purchase an item from the in-app store
    Body: { "item_id": "doover_pass" | "advanced_message_pack" | "bailout_streak_save" }
    """
    item_id = item_request.get("item_id")
    
    if not item_id:
        raise HTTPException(status_code=400, detail="item_id is required")
    
    if item_id not in STORE_ITEMS:
        raise HTTPException(status_code=404, detail=f"Item '{item_id}' not found in store")
    
    try:
        result = await gamification_service.purchase_store_item(
            current_user["_id"],
            item_id
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error purchasing item: {e}")
        raise HTTPException(status_code=500, detail="Failed to purchase item")

@api_router.get("/store/items")
async def get_store_items(current_user: dict = Depends(get_current_user_flexible)):
    """Get all available store items with user's purchase eligibility"""
    user = await db.users.find_one({"_id": current_user["_id"]})
    
    available_points = user.get("total_points", 0) - user.get("points_spent", 0)
    bailout_used = user.get("bailout_used_this_month", False)
    
    items_with_eligibility = []
    for item_id, item_info in STORE_ITEMS.items():
        can_afford = available_points >= item_info["cost"]
        
        # Check bailout monthly limitation
        if item_id == "bailout_streak_save":
            can_purchase = can_afford and not bailout_used
            reason = "Already used this month" if bailout_used else None
        else:
            can_purchase = can_afford
            reason = None
        
        items_with_eligibility.append({
            "id": item_id,
            **item_info,
            "can_purchase": can_purchase,
            "can_afford": can_afford,
            "reason": reason
        })
    
    return {
        "success": True,
        "items": items_with_eligibility,
        "user_points": available_points
    }

@api_router.get("/gamification/leaderboard/weekly")
async def get_weekly_leaderboard(current_user: dict = Depends(get_current_user_flexible)):
    """
    Get users eligible for weekly prize draw (7+ day streak)
    """
    # Find users with 7+ day streak
    eligible_users = await db.users.find(
        {"current_streak": {"$gte": 7}},
        {"name": 1, "current_streak": 1, "total_points": 1}
    ).to_list(length=100)
    
    # Sort by streak (descending), then by points
    sorted_users = sorted(
        eligible_users,
        key=lambda x: (x.get("current_streak", 0), x.get("total_points", 0)),
        reverse=True
    )
    
    return {
        "success": True,
        "draw_type": "weekly",
        "eligible_count": len(sorted_users),
        "top_users": [
            {
                "name": user.get("name", "User"),
                "streak": user.get("current_streak", 0),
                "points": user.get("total_points", 0)
            }
            for user in sorted_users[:10]  # Top 10
        ]
    }

@api_router.get("/gamification/leaderboard/monthly")
async def get_monthly_leaderboard(current_user: dict = Depends(get_current_user_flexible)):
    """
    Get users eligible for monthly prize draw (30+ day streak)
    """
    # Find users with 30+ day streak
    eligible_users = await db.users.find(
        {"current_streak": {"$gte": 30}},
        {"name": 1, "current_streak": 1, "total_points": 1}
    ).to_list(length=100)
    
    # Sort by streak (descending), then by points
    sorted_users = sorted(
        eligible_users,
        key=lambda x: (x.get("current_streak", 0), x.get("total_points", 0)),
        reverse=True
    )
    
    return {
        "success": True,
        "draw_type": "monthly",
        "eligible_count": len(sorted_users),
        "top_users": [
            {
                "name": user.get("name", "User"),
                "streak": user.get("current_streak", 0),
                "points": user.get("total_points", 0)
            }
            for user in sorted_users[:10]  # Top 10
        ]
    }

@api_router.put("/user/love-language")
async def set_love_language(
    request: dict,
    current_user: dict = Depends(get_current_user_flexible)
):
    """
    Set user's love language (only available at Level 5+)
    Body: { "love_language": "WoA" | "AoS" | "QT" | "Gifts" | "PT" }
    """
    user = await db.users.find_one({"_id": current_user["_id"]})
    
    # Check if user is Level 5+
    if user.get("current_level", 1) < 5:
        raise HTTPException(
            status_code=403,
            detail="Love Language selection unlocks at Level 5"
        )
    
    love_language = request.get("love_language")
    valid_languages = ["WoA", "AoS", "QT", "Gifts", "PT"]
    
    if not love_language or love_language not in valid_languages:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid love language. Must be one of: {', '.join(valid_languages)}"
        )
    
    # Update love language
    await db.users.update_one(
        {"_id": current_user["_id"]},
        {"$set": {
            "love_language": love_language,
            "updated_at": datetime.utcnow()
        }}
    )
    
    return {
        "success": True,
        "message": "Love language updated successfully",
        "love_language": love_language
    }

# ============================================================================
# PHASE 4: TRIAL EXPIRY NOTIFICATIONS - CRON ENDPOINT
# ============================================================================

@api_router.post("/admin/check-trial-expiry")
async def trigger_trial_expiry_check(current_user: dict = Depends(get_current_user_flexible)):
    """
    Manually trigger trial expiry check and notifications
    Should be called daily by a cron job or external scheduler
    """
    from trial_expiry_notifier import check_and_notify_trial_expiry
    
    result = await check_and_notify_trial_expiry()
    
    return {
        "success": True,
        "message": "Trial expiry check completed",
        "result": result
    }

# Include API router with all endpoints
app.include_router(api_router)