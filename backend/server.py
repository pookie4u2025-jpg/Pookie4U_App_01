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
import logging
from pathlib import Path
import uuid

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Import AI task service
from ai_task_service import generate_daily_tasks_for_mode, generate_weekly_tasks_for_mode

# Import Enhanced Calendar Service
from enhanced_calendar_service import enhanced_calendar_service

# Import Razorpay Service
from razorpay_service import razorpay_service

# Rate limiting storage
rate_limit_storage = defaultdict(list)
failed_attempts = defaultdict(list)

# Security configuration
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30

# OAuth configuration
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")

# SMS configuration (Twilio or similar)
SMS_PROVIDER_API_KEY = os.environ.get("SMS_PROVIDER_API_KEY", "")
SMS_PROVIDER_BASE_URL = os.environ.get("SMS_PROVIDER_BASE_URL", "")

# Database configuration
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'pookie4u')]

# Initialize FastAPI app
app = FastAPI(title="Pookie4u Authentication API", version="1.0.0")
api_router = APIRouter(prefix="/api")

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
async def verify_google_token(id_token: str) -> Optional[Dict[str, Any]]:
    """Verify Google ID token and extract user info"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}"
            )
            
            if response.status_code == 200:
                user_info = response.json()
                if user_info.get("aud") == GOOGLE_CLIENT_ID:
                    return {
                        "id": user_info.get("sub"),
                        "email": user_info.get("email"),
                        "name": user_info.get("name"),
                        "picture": user_info.get("picture"),
                        "email_verified": user_info.get("email_verified", False)
                    }
    except Exception as e:
        print(f"Google token verification error: {e}")
    
    return None

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
    notes: str = ""

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
    relationship_mode: str = "SAME_HOME"
    partner_profile: PartnerProfile = Field(default_factory=PartnerProfile)
    total_points: int = 0
    current_level: int = 1
    current_streak: int = 0
    longest_streak: int = 0
    tasks_completed: int = 0
    badges: List[str] = Field(default_factory=list)
    profile_completed: bool = False
    profile_image: Optional[str] = None  # base64 encoded image
    created_at: datetime
    updated_at: datetime = Field(default_factory=datetime.utcnow)

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

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await db.users.find_one({"_id": user_id})
    if user is None:
        raise credentials_exception
    return user

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
    {"id": "1", "name": "Personalized Photo Frame", "category": "Romantic", "price_range": "Under ₹500", "link": "https://amzn.to/46k7tSR", "description": "Beautiful personalized frame for your special memories"},
    {"id": "2", "name": "Couple's Coffee Mug Set", "category": "Home", "price_range": "Under ₹500", "link": "https://amzn.to/47mpgdb", "description": "Matching mugs for your morning coffee together"},
    {"id": "3", "name": "Romantic Scented Candles", "category": "Romantic", "price_range": "Under ₹1000", "link": "https://amzn.to/4g7fRs4", "description": "Set the perfect romantic mood"},
    {"id": "4", "name": "Jewelry Gift Set", "category": "Jewelry", "price_range": "₹1000-5000", "link": "https://amzn.to/485YoOK", "description": "Elegant jewelry to make her shine"},
    {"id": "5", "name": "Luxury Perfume", "category": "Beauty", "price_range": "₹1000-5000", "link": "https://amzn.to/4p1cpDv", "description": "A fragrance she'll love"},
    {"id": "6", "name": "Gourmet Chocolate Box", "category": "Food", "price_range": "Under ₹1000", "link": "https://amzn.to/4g58AJo", "description": "Premium chocolates for your sweet moments"}
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
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user["_id"]}, expires_delta=access_token_expires
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
@api_router.post("/auth/oauth/google", response_model=dict)
async def google_oauth_callback(request: OAuthCallbackRequest):
    """Handle Google OAuth callback"""
    try:
        # Verify Google ID token
        user_info = await verify_google_token(request.id_token)
        if not user_info:
            raise HTTPException(status_code=400, detail="Invalid Google token")
        
        email = user_info.get("email")
        name = user_info.get("name", "")
        google_id = user_info.get("sub")
        
        if not email or not google_id:
            raise HTTPException(status_code=400, detail="Missing required user information")
        
        # Check if user exists with this email
        existing_user = await db.users.find_one({"email": email})
        
        if existing_user:
            # Check if Google account is already linked
            if "oauth_providers" not in existing_user:
                existing_user["oauth_providers"] = {}
            
            # Link Google account if not already linked
            if "google" not in existing_user["oauth_providers"]:
                await db.users.update_one(
                    {"_id": existing_user["_id"]},
                    {"$set": {
                        "oauth_providers.google": {
                            "google_id": google_id,
                            "linked_at": datetime.utcnow()
                        },
                        "updated_at": datetime.utcnow()
                    }}
                )
            
            # Create access token
            access_token = create_access_token(data={"sub": str(existing_user["_id"])})
            refresh_token = create_refresh_token(data={"sub": str(existing_user["_id"])})
            
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "user": {
                    "id": str(existing_user["_id"]),
                    "email": existing_user["email"],
                    "name": existing_user["name"],
                    "relationship_mode": existing_user.get("relationship_mode", "SAME_HOME"),
                    "profile_completed": existing_user.get("profile_completed", False)
                }
            }
        else:
            # Create new user with Google OAuth
            user_id = str(uuid.uuid4())
            user_doc = {
                "_id": user_id,
                "email": email,
                "name": name,
                "oauth_providers": {
                    "google": {
                        "google_id": google_id,
                        "linked_at": datetime.utcnow()
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
            access_token = create_access_token(data={"sub": user_id})
            refresh_token = create_refresh_token(data={"sub": user_id})
            
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "user": {
                    "id": user_id,
                    "email": email,
                    "name": name,
                    "relationship_mode": "SAME_HOME",
                    "profile_completed": False
                },
                "is_new_user": True
            }
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Google OAuth error: {e}")
        raise HTTPException(status_code=500, detail="OAuth authentication failed")

@api_router.post("/auth/oauth/apple", response_model=dict)
async def apple_oauth_callback(request: OAuthCallbackRequest):
    """Handle Apple OAuth callback (placeholder for future implementation)"""
    # Apple OAuth implementation would go here
    # For now, return a placeholder response
    raise HTTPException(status_code=501, detail="Apple OAuth not yet implemented")

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
    
    # Convert datetime fields to string format (DD/MM/YYYY)
    if "birthday" in partner_data and partner_data["birthday"] is not None:
        if hasattr(partner_data["birthday"], 'strftime'):
            partner_data["birthday"] = partner_data["birthday"].strftime("%d/%m/%Y")
    
    if "anniversary" in partner_data and partner_data["anniversary"] is not None:
        if hasattr(partner_data["anniversary"], 'strftime'):
            partner_data["anniversary"] = partner_data["anniversary"].strftime("%d/%m/%Y")

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
        profile_image=current_user.get("profile_image"),
        created_at=current_user["created_at"],
        updated_at=current_user.get("updated_at", datetime.utcnow())
    )

@api_router.put("/user/profile")
async def update_user_profile(profile_update: dict, current_user: dict = Depends(get_current_user)):
    # Validate allowed fields
    allowed_fields = {"name", "email"}
    update_data = {k: v for k, v in profile_update.items() if k in allowed_fields}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No valid fields to update")
    
    # Add updated timestamp
    update_data["updated_at"] = datetime.utcnow()
    
    # Update in database
    await db.users.update_one(
        {"_id": current_user["_id"]},
        {"$set": update_data}
    )
    
    return {"message": "Profile updated successfully"}

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
    """Get previous winners list"""
    # Sample winners data - in production this would come from database
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
            "user_name": "Kavya & Vikram",
            "prize_amount": None,
            "prize_type": "monthly_trip",
            "week_number": None,
            "month": "October 2024",
            "tasks_completed": 93,
            "awarded_date": "2024-10-31T00:00:00",
            "description": "Won couple trip to Goa for completing all October tasks"
        },
        {
            "id": "4",
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
            "id": "5",
            "user_name": "Meera & Siddharth",
            "prize_amount": None,
            "prize_type": "monthly_trip",
            "week_number": None,
            "month": "September 2024",
            "tasks_completed": 90,
            "awarded_date": "2024-09-30T00:00:00",
            "description": "Couple trip to Udaipur for September achievements"
        }
    ]
    
    return {"winners": sample_winners}

# AI-Powered Task Generation Endpoints

@api_router.get("/tasks/daily")
async def get_daily_tasks(
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
            # Fallback to static tasks
            available_tasks = DAILY_TASKS.get(mode, DAILY_TASKS["SAME_HOME"])
            daily_tasks = random.sample(available_tasks, 3)
            
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
            
            return {
                "tasks": daily_tasks,
                "generated_for_mode": mode,
                "fallback": True
            }
    
    # Return existing tasks with mode information
    existing_tasks = current_user.get("ai_daily_tasks", [])
    return {
        "tasks": existing_tasks,
        "generated_for_mode": mode
    }

@api_router.get("/tasks/weekly")
async def get_weekly_tasks(
    regenerate: bool = False,
    current_user: dict = Depends(get_current_user)
):
    """Get weekly AI-generated tasks for current user's relationship mode"""
    today = datetime.utcnow()
    last_weekly_date = current_user.get("last_weekly_task_date")
    mode = current_user.get("relationship_mode", "SAME_HOME")
    
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
            
            # Store AI tasks
            await db.users.update_one(
                {"_id": current_user["_id"]},
                {"$set": {
                    "ai_weekly_tasks": ai_tasks,
                    "last_weekly_task_date": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }}
            )
            
            return {
                "tasks": ai_tasks,
                "generated_for_mode": mode,
                "generation_date": datetime.utcnow()
            }
            
        except Exception as e:
            print(f"AI weekly task generation failed: {e}")
            # Fallback to static tasks
            available_tasks = WEEKLY_TASKS.get(mode, WEEKLY_TASKS["SAME_HOME"])
            weekly_tasks = random.sample(available_tasks, min(5, len(available_tasks)))
            
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
            
            return {
                "tasks": weekly_tasks,
                "generated_for_mode": mode,
                "fallback": True
            }
    
    # Return existing tasks
    existing_tasks = current_user.get("ai_weekly_tasks", [])
    return {
        "tasks": existing_tasks,
        "generated_for_mode": mode
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
    
    # Update user stats
    new_total_points = current_user.get("total_points", 0) + points_earned
    new_level = (new_total_points // 100) + 1
    new_tasks_completed = current_user.get("tasks_completed", 0) + 1
    
    # Update streak (simplified logic)
    current_streak = current_user.get("current_streak", 0) + 1
    longest_streak = max(current_user.get("longest_streak", 0), current_streak)
    
    # Update badges (simplified)
    badges = current_user.get("badges", [])
    if new_tasks_completed >= 10 and "First 10 Tasks" not in badges:
        badges.append("First 10 Tasks")
    if current_streak >= 7 and "Week Warrior" not in badges:
        badges.append("Week Warrior")
    if new_level >= 5 and "Level 5 Master" not in badges:
        badges.append("Level 5 Master")
    
    update_data = {
        "ai_daily_tasks": ai_daily_tasks,
        "ai_weekly_tasks": ai_weekly_tasks,
        "daily_tasks": daily_tasks,
        "custom_tasks": custom_tasks,
        "total_points": new_total_points,
        "current_level": new_level,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "tasks_completed": new_tasks_completed,
        "badges": badges,
        "updated_at": datetime.utcnow()
    }
    
    # Update weekly task if it was modified
    if weekly_task is not None:
        update_data["weekly_task"] = weekly_task
    
    await db.users.update_one(
        {"_id": user_id},
        {"$set": update_data}
    )
    
    return {
        "message": "Task completed successfully!",
        "points_earned": points_earned,
        "total_points": new_total_points,
        "new_level": new_level,
        "streak": current_streak,
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

@api_router.get("/gifts")
async def get_gift_ideas():
    return {"gifts": GIFT_IDEAS}

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

@api_router.get("/events")
async def get_events(
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

# Include the router in the main app
app.include_router(api_router)

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
    """Get curated gift ideas with affiliate links"""
    gifts = [
        {
            "id": "1",
            "name": "Personalized Photo Frame",
            "category": "Romantic",
            "price_range": "Under ₹500",
            "link": "https://amzn.to/46k7tSR",
            "description": "Beautiful personalized frame for your special memories"
        },
        {
            "id": "2",
            "name": "Couple's Coffee Mug Set",
            "category": "Home",
            "price_range": "Under ₹500",
            "link": "https://amzn.to/47mpgdb",
            "description": "Matching mugs for your morning coffee together"
        },
        {
            "id": "3",
            "name": "Romantic Scented Candles",
            "category": "Romantic",
            "price_range": "Under ₹1000",
            "link": "https://amzn.to/4g7fRs4",
            "description": "Set the perfect romantic mood"
        },
        {
            "id": "4",
            "name": "Jewelry Gift Set",
            "category": "Jewelry",
            "price_range": "₹1000-5000",
            "link": "https://amzn.to/485YoOK",
            "description": "Elegant jewelry to make her shine"
        },
        {
            "id": "5",
            "name": "Luxury Perfume",
            "category": "Beauty",
            "price_range": "₹1000-5000",
            "link": "https://amzn.to/4p1cpDv",
            "description": "A fragrance she'll love"
        },
        {
            "id": "6",
            "name": "Gourmet Chocolate Box",
            "category": "Food",
            "price_range": "Under ₹1000",
            "link": "https://amzn.to/4g58AJo",
            "description": "Premium chocolates for your sweet moments"
        },
    ]
    
    return {
        "success": True,
        "gifts": gifts,
        "total": len(gifts)
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

@app.post("/api/subscriptions/create", tags=["Subscriptions"])
async def create_subscription(
    request: CreateSubscriptionRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Create a new Razorpay subscription"""
    try:
        # Get current user
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("email")
        
        if not email:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
        # Get user data
        user = await db.users.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Validate plan type
        if request.plan_type not in ['monthly', 'sixmonth']:
            raise HTTPException(status_code=400, detail="Invalid plan type. Must be 'monthly' or 'sixmonth'")
        
        # Create customer data
        customer_data = {
            'email': email,
            'name': user.get('name', ''),
            'phone': user.get('phone', '')
        }
        
        # Create subscription
        result = razorpay_service.create_subscription(request.plan_type, customer_data)
        
        if not result.get('success'):
            raise HTTPException(status_code=500, detail=result.get('error', 'Failed to create subscription'))
        
        # Save subscription info to user
        await db.users.update_one(
            {"email": email},
            {"$set": {
                "subscription": {
                    "subscription_id": result['subscription_id'],
                    "plan_type": request.plan_type,
                    "plan_id": result['plan_id'],
                    "status": result['status'],
                    "created_at": datetime.utcnow().isoformat(),
                }
            }}
        )
        
        return {
            "success": True,
            "subscription_id": result['subscription_id'],
            "short_url": result.get('short_url'),
            "plan_type": request.plan_type,
            "status": result['status'],
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating subscription: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create subscription: {str(e)}")

@app.post("/api/subscriptions/verify", tags=["Subscriptions"])
async def verify_payment(
    request: VerifyPaymentRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Verify Razorpay payment signature"""
    try:
        # Get current user
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("email")
        
        if not email:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
        # Verify signature
        is_valid = razorpay_service.verify_payment_signature(
            request.payment_id,
            request.subscription_id,
            request.signature
        )
        
        if not is_valid:
            raise HTTPException(status_code=400, detail="Invalid payment signature")
        
        # Update subscription status
        await db.users.update_one(
            {"email": email},
            {"$set": {
                "subscription.status": "active",
                "subscription.activated_at": datetime.utcnow().isoformat(),
                "subscription.payment_id": request.payment_id,
            }}
        )
        
        return {
            "success": True,
            "message": "Payment verified successfully",
            "subscription_status": "active"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying payment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to verify payment: {str(e)}")

@app.get("/api/subscriptions/status", tags=["Subscriptions"])
async def get_subscription_status(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get current subscription status"""
    try:
        # Get current user
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("email")
        
        if not email:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
        # Get user data
        user = await db.users.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        subscription_data = user.get('subscription', {})
        
        if not subscription_data or not subscription_data.get('subscription_id'):
            return {
                "has_subscription": False,
                "subscription": None
            }
        
        # Fetch latest details from Razorpay
        subscription_id = subscription_data['subscription_id']
        latest_details = razorpay_service.get_subscription_details(subscription_id)
        
        if latest_details:
            # Update local copy
            await db.users.update_one(
                {"email": email},
                {"$set": {
                    "subscription.status": latest_details['status'],
                    "subscription.updated_at": datetime.utcnow().isoformat(),
                }}
            )
        
        return {
            "has_subscription": True,
            "subscription": latest_details or subscription_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting subscription status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get subscription status: {str(e)}")

@app.post("/api/subscriptions/cancel", tags=["Subscriptions"])
async def cancel_subscription(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Cancel current subscription"""
    try:
        # Get current user
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("email")
        
        if not email:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
        # Get user data
        user = await db.users.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        subscription_data = user.get('subscription', {})
        subscription_id = subscription_data.get('subscription_id')
        
        if not subscription_id:
            raise HTTPException(status_code=404, detail="No active subscription found")
        
        # Cancel subscription
        result = razorpay_service.cancel_subscription(subscription_id, cancel_at_cycle_end=True)
        
        if not result.get('success'):
            raise HTTPException(status_code=500, detail=result.get('error', 'Failed to cancel subscription'))
        
        # Update local status
        await db.users.update_one(
            {"email": email},
            {"$set": {
                "subscription.status": result['status'],
                "subscription.cancelled_at": datetime.utcnow().isoformat(),
            }}
        )
        
        return {
            "success": True,
            "message": "Subscription cancelled successfully",
            "status": result['status']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling subscription: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to cancel subscription: {str(e)}")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()