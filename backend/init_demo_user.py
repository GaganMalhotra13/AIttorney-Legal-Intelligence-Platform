#!/usr/bin/env python3
"""
Quick script to create the demo user in MongoDB
Run this once to set up test@testing.com account
"""
import asyncio
import bcrypt
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

async def create_demo_user():
    client = AsyncIOMotorClient(os.getenv("MONGO_URL", "mongodb://localhost:27017"))
    db = client[os.getenv("MONGO_DB", "aittorney")]
    users_col = db["users"]
    
    email = "test123@testing.com"
    password = "test123"
    name = "Test User"
    
    # Check if user already exists
    existing = await users_col.find_one({"email": email})
    if existing:
        print(f"✅ User {email} already exists")
        return
    
    # Hash password
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    
    # Create user
    result = await users_col.insert_one({
        "email": email,
        "name": name,
        "password": hashed,
        "phone": None,
        "location": None,
        "plan": "free",
        "created_at": datetime.utcnow(),
        "last_login": None,
        "login_count": 0,
    })
    
    print(f"✅ Created demo user: {email}")
    print(f"   ID: {result.inserted_id}")
    print(f"   Password: {password}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(create_demo_user())
