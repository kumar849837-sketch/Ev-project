import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional

# Initialize FastAPI App
app = FastAPI(
    title="EV Analytics Profile API",
    description="Backend API to manage user profiles for the EV Dashboard.",
    version="1.0.0"
)

# Shared mocked database file
USERS_FILE = os.path.join(os.path.dirname(__file__), 'users.json')

# Pydantic Model for API Input/Output
class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    company: Optional[str] = None
    job_title: Optional[str] = None

class UserProfile(BaseModel):
    username: str
    profile: ProfileUpdate

# Helper functions
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

# --- Endpoints ---

@app.get("/")
def read_root():
    return {"message": "Welcome to the EV Analytics Profile API!"}

@app.get("/profile/{username}", response_model=UserProfile)
def get_profile(username: str):
    """
    Retrieve user profile information given a username.
    """
    users = load_users()
    if username not in users:
        raise HTTPException(status_code=404, detail="User not found")
        
    user_data = users[username]
    # Extract profile fields, set to None if they don't exist yet
    profile_data = {
        "full_name": user_data.get("full_name"),
        "email": user_data.get("email"),
        "company": user_data.get("company"),
        "job_title": user_data.get("job_title")
    }
    
    return {"username": username, "profile": profile_data}

@app.put("/profile/{username}", response_model=UserProfile)
def update_profile(username: str, profile: ProfileUpdate):
    """
    Update user profile information.
    """
    users = load_users()
    if username not in users:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Update only the fields that were provided
    user_data = users[username]
    if profile.full_name is not None:
        user_data["full_name"] = profile.full_name
    if profile.email is not None:
        user_data["email"] = profile.email
    if profile.company is not None:
        user_data["company"] = profile.company
    if profile.job_title is not None:
        user_data["job_title"] = profile.job_title
        
    users[username] = user_data
    save_users(users)
    
    return {"username": username, "profile": profile.dict()}
