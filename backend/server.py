from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
import os
import logging
import uuid
from pathlib import Path
import socketio
from fuzzywuzzy import fuzz
import asyncio

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here-change-in-production')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Security
security = HTTPBearer()

# Create Socket.IO server
sio = socketio.AsyncServer(
    cors_allowed_origins="*",
    async_mode='asgi'
)

# Create FastAPI app
app = FastAPI(title="Testnet API", version="1.0.0")

# Create API router
api_router = APIRouter(prefix="/api")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================================
# MODELS
# ================================

class UserRole(str):
    SEEKER = "seeker"
    MENTOR = "mentor"
    ADMIN = "admin"

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    name: str
    role: str = UserRole.SEEKER
    is_verified: bool = False
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str
    role: str = UserRole.SEEKER

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Profile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    bio: str = ""
    skills: List[str] = []
    experience_years: int = 0
    hourly_rate: float = 0.0
    available: bool = True
    avatar_url: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ProfileCreate(BaseModel):
    bio: str = ""
    skills: List[str] = []
    experience_years: int = 0
    hourly_rate: float = 0.0
    available: bool = True
    avatar_url: str = ""

class Conversation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    members: List[str]  # user IDs
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str
    sender_id: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class MessageCreate(BaseModel):
    conversation_id: str
    content: str

class Schedule(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    mentor_id: str
    seeker_id: str
    start_time: datetime
    end_time: datetime
    status: str = "scheduled"  # scheduled, completed, cancelled
    title: str = ""
    description: str = ""
    meeting_link: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ScheduleCreate(BaseModel):
    mentor_id: str
    start_time: datetime
    end_time: datetime
    title: str = ""
    description: str = ""

class ScheduleUpdate(BaseModel):
    status: str
    title: Optional[str] = None
    description: Optional[str] = None
    meeting_link: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# ================================
# AUTHENTICATION
# ================================

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
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = await db.users.find_one({"email": token_data.username})
    if user is None:
        raise credentials_exception
    return User(**user)

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# ================================
# API ROUTES
# ================================

@api_router.post("/auth/register", response_model=Token)
async def register(user: UserCreate):
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Create user
    hashed_password = get_password_hash(user.password)
    user_dict = user.dict()
    del user_dict["password"]
    user_dict["hashed_password"] = hashed_password
    user_dict["id"] = str(uuid.uuid4())
    user_dict["is_verified"] = False
    user_dict["is_active"] = True
    user_dict["created_at"] = datetime.utcnow()
    user_dict["updated_at"] = datetime.utcnow()
    
    await db.users.insert_one(user_dict)
    user_obj = User(**{k: v for k, v in user_dict.items() if k != "hashed_password"})
    
    # Create empty profile
    profile_obj = Profile(user_id=user_obj.id)
    await db.profiles.insert_one(profile_obj.dict())
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@api_router.post("/auth/login", response_model=Token)
async def login(user: UserLogin):
    # Authenticate user
    db_user = await db.users.find_one({"email": user.email})
    if not db_user or not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@api_router.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@api_router.get("/users/me/profile", response_model=Profile)
async def read_user_profile(current_user: User = Depends(get_current_active_user)):
    profile = await db.profiles.find_one({"user_id": current_user.id})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return Profile(**profile)

@api_router.put("/users/me/profile", response_model=Profile)
async def update_user_profile(
    profile_data: ProfileCreate,
    current_user: User = Depends(get_current_active_user)
):
    profile_dict = profile_data.dict()
    profile_dict["updated_at"] = datetime.utcnow()
    
    result = await db.profiles.update_one(
        {"user_id": current_user.id},
        {"$set": profile_dict}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    updated_profile = await db.profiles.find_one({"user_id": current_user.id})
    return Profile(**updated_profile)

@api_router.get("/search/mentors")
async def search_mentors(
    q: str,
    current_user: User = Depends(get_current_active_user)
):
    # Get all mentors with profiles
    mentors = await db.users.find({"role": UserRole.MENTOR, "is_verified": True}).to_list(100)
    mentor_results = []
    
    for mentor in mentors:
        profile = await db.profiles.find_one({"user_id": mentor["id"]})
        if profile and profile.get("available"):
            # Calculate fuzzy score
            search_text = f"{mentor['name']} {profile.get('bio', '')} {' '.join(profile.get('skills', []))}"
            score = fuzz.partial_ratio(q.lower(), search_text.lower())
            
            mentor_results.append({
                "user": User(**mentor),
                "profile": Profile(**profile),
                "score": score
            })
    
    # Sort by score (descending)
    mentor_results.sort(key=lambda x: x["score"], reverse=True)
    
    return mentor_results[:10]  # Return top 10 results

@api_router.get("/conversations", response_model=List[Conversation])
async def get_conversations(current_user: User = Depends(get_current_active_user)):
    conversations = await db.conversations.find(
        {"members": current_user.id}
    ).to_list(100)
    return [Conversation(**conv) for conv in conversations]

@api_router.post("/conversations", response_model=Conversation)
async def create_conversation(
    mentor_id: str,
    current_user: User = Depends(get_current_active_user)
):
    # Check if conversation already exists
    existing_conv = await db.conversations.find_one({
        "members": {"$all": [current_user.id, mentor_id]}
    })
    
    if existing_conv:
        return Conversation(**existing_conv)
    
    # Create new conversation
    conversation = Conversation(members=[current_user.id, mentor_id])
    await db.conversations.insert_one(conversation.dict())
    
    return conversation

@api_router.get("/conversations/{conversation_id}/messages", response_model=List[Message])
async def get_messages(
    conversation_id: str,
    current_user: User = Depends(get_current_active_user)
):
    # Verify user is part of conversation
    conversation = await db.conversations.find_one({"id": conversation_id})
    if not conversation or current_user.id not in conversation["members"]:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = await db.messages.find(
        {"conversation_id": conversation_id}
    ).sort("created_at", 1).to_list(100)
    
    return [Message(**msg) for msg in messages]

@api_router.post("/messages", response_model=Message)
async def create_message(
    message_data: MessageCreate,
    current_user: User = Depends(get_current_active_user)
):
    # Verify user is part of conversation
    conversation = await db.conversations.find_one({"id": message_data.conversation_id})
    if not conversation or current_user.id not in conversation["members"]:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Create message
    message = Message(
        conversation_id=message_data.conversation_id,
        sender_id=current_user.id,
        content=message_data.content
    )
    await db.messages.insert_one(message.dict())
    
    # Emit to socket
    await sio.emit("new_message", message.dict(), room=message_data.conversation_id)
    
    return message

# ================================
# SCHEDULING ROUTES
# ================================

@api_router.post("/schedules", response_model=Schedule)
async def create_schedule(
    schedule_data: ScheduleCreate,
    current_user: User = Depends(get_current_active_user)
):
    # Verify mentor exists
    mentor = await db.users.find_one({"id": schedule_data.mentor_id, "role": UserRole.MENTOR})
    if not mentor:
        raise HTTPException(status_code=404, detail="Mentor not found")
    
    # Check for conflicts
    existing_schedule = await db.schedules.find_one({
        "mentor_id": schedule_data.mentor_id,
        "start_time": {"$lte": schedule_data.end_time},
        "end_time": {"$gte": schedule_data.start_time},
        "status": {"$in": ["scheduled", "confirmed"]}
    })
    
    if existing_schedule:
        raise HTTPException(status_code=400, detail="Time slot already booked")
    
    # Create schedule
    schedule = Schedule(
        mentor_id=schedule_data.mentor_id,
        seeker_id=current_user.id,
        start_time=schedule_data.start_time,
        end_time=schedule_data.end_time,
        title=schedule_data.title,
        description=schedule_data.description
    )
    
    await db.schedules.insert_one(schedule.dict())
    return schedule

@api_router.get("/schedules", response_model=List[Schedule])
async def get_schedules(current_user: User = Depends(get_current_active_user)):
    # Get schedules based on user role
    if current_user.role == UserRole.MENTOR:
        schedules = await db.schedules.find({"mentor_id": current_user.id}).to_list(100)
    else:
        schedules = await db.schedules.find({"seeker_id": current_user.id}).to_list(100)
    
    return [Schedule(**schedule) for schedule in schedules]

@api_router.get("/schedules/{schedule_id}", response_model=Schedule)
async def get_schedule(
    schedule_id: str,
    current_user: User = Depends(get_current_active_user)
):
    schedule = await db.schedules.find_one({"id": schedule_id})
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    # Check if user has access to this schedule
    if schedule["mentor_id"] != current_user.id and schedule["seeker_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return Schedule(**schedule)

@api_router.put("/schedules/{schedule_id}", response_model=Schedule)
async def update_schedule(
    schedule_id: str,
    schedule_data: ScheduleUpdate,
    current_user: User = Depends(get_current_active_user)
):
    schedule = await db.schedules.find_one({"id": schedule_id})
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    # Check if user has access to update this schedule
    if schedule["mentor_id"] != current_user.id and schedule["seeker_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update schedule
    update_data = schedule_data.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    
    result = await db.schedules.update_one(
        {"id": schedule_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    updated_schedule = await db.schedules.find_one({"id": schedule_id})
    return Schedule(**updated_schedule)

@api_router.delete("/schedules/{schedule_id}")
async def delete_schedule(
    schedule_id: str,
    current_user: User = Depends(get_current_active_user)
):
    schedule = await db.schedules.find_one({"id": schedule_id})
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    # Check if user has access to delete this schedule
    if schedule["mentor_id"] != current_user.id and schedule["seeker_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    result = await db.schedules.delete_one({"id": schedule_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    return {"message": "Schedule deleted successfully"}

# Admin routes
@api_router.get("/admin/mentors")
async def get_pending_mentors(current_user: User = Depends(get_current_active_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    mentors = await db.users.find({"role": UserRole.MENTOR}).to_list(100)
    mentor_results = []
    
    for mentor in mentors:
        profile = await db.profiles.find_one({"user_id": mentor["id"]})
        mentor_results.append({
            "user": User(**mentor),
            "profile": Profile(**profile) if profile else None
        })
    
    return mentor_results

@api_router.put("/admin/mentors/{mentor_id}/verify")
async def verify_mentor(
    mentor_id: str,
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    result = await db.users.update_one(
        {"id": mentor_id, "role": UserRole.MENTOR},
        {"$set": {"is_verified": True, "updated_at": datetime.utcnow()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Mentor not found")
    
    return {"message": "Mentor verified successfully"}

@api_router.delete("/admin/mentors/{mentor_id}")
async def delete_mentor(
    mentor_id: str,
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Delete user and profile
    await db.users.delete_one({"id": mentor_id})
    await db.profiles.delete_one({"user_id": mentor_id})
    
    return {"message": "Mentor deleted successfully"}

# Seed data endpoint (admin only)
@api_router.post("/admin/seed-data")
async def seed_dummy_data(current_user: User = Depends(get_current_active_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Import and run seed data
    from pathlib import Path
    import importlib.util
    
    seed_file = Path(__file__).parent / "seed_data.py"
    spec = importlib.util.spec_from_file_location("seed_data", seed_file)
    seed_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(seed_module)
    
    await seed_module.create_dummy_mentors()
    
    return {"message": "Dummy data seeded successfully"}

# ================================
# SOCKET.IO EVENTS
# ================================

@sio.event
async def connect(sid, environ, auth):
    print(f"Client {sid} connected")

@sio.event
async def disconnect(sid):
    print(f"Client {sid} disconnected")

@sio.event
async def join_room(sid, data):
    room = data.get("room")
    await sio.enter_room(sid, room)
    print(f"Client {sid} joined room {room}")

@sio.event
async def leave_room(sid, data):
    room = data.get("room")
    await sio.leave_room(sid, room)
    print(f"Client {sid} left room {room}")

@sio.event
async def send_message(sid, data):
    room = data.get("room")
    message = data.get("message")
    await sio.emit("receive_message", message, room=room)

# Include router
app.include_router(api_router)

# Create Socket.IO ASGI app
socket_app = socketio.ASGIApp(sio, app)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

# For uvicorn to run socket.io
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(socket_app, host="0.0.0.0", port=8001)