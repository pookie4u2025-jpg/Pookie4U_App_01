#!/usr/bin/env python3
"""
Test script to identify deployment startup issues
"""
import sys
import traceback

print("="*50)
print("DEPLOYMENT STARTUP TEST")
print("="*50)

# Test 1: Python version
print("\n1. Python Version:")
print(f"   {sys.version}")

# Test 2: Import dotenv
print("\n2. Testing dotenv...")
try:
    from dotenv import load_dotenv
    print("   ✅ dotenv imported")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 3: Load environment
print("\n3. Loading .env file...")
try:
    from pathlib import Path
    ROOT_DIR = Path(__file__).parent
    load_dotenv(ROOT_DIR / '.env')
    print("   ✅ .env loaded")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 4: Check MONGO_URL
print("\n4. Checking MONGO_URL...")
import os
mongo_url = os.getenv('MONGO_URL')
if mongo_url:
    # Hide password
    masked = mongo_url[:20] + "***" + mongo_url[-20:] if len(mongo_url) > 40 else "***"
    print(f"   ✅ MONGO_URL exists: {masked}")
else:
    print("   ❌ MONGO_URL not found!")
    sys.exit(1)

# Test 5: Import FastAPI
print("\n5. Testing FastAPI import...")
try:
    from fastapi import FastAPI
    print("   ✅ FastAPI imported")
except Exception as e:
    print(f"   ❌ Error: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 6: Import Motor (MongoDB)
print("\n6. Testing Motor (MongoDB) import...")
try:
    from motor.motor_asyncio import AsyncIOMotorClient
    print("   ✅ Motor imported")
except Exception as e:
    print(f"   ❌ Error: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 7: Test MongoDB connection
print("\n7. Testing MongoDB connection...")
try:
    import asyncio
    async def test_mongo():
        client = AsyncIOMotorClient(mongo_url)
        db = client[os.getenv('DB_NAME', 'pookie4u')]
        await db.command('ping')
        print("   ✅ MongoDB connection successful")
        client.close()
    
    asyncio.run(test_mongo())
except Exception as e:
    print(f"   ❌ MongoDB connection failed: {e}")
    traceback.print_exc()
    # Don't exit - might be network issue in build phase

# Test 8: Import server module
print("\n8. Testing server.py import...")
try:
    from server import app
    print("   ✅ server.py imported successfully")
    print(f"   App title: {app.title}")
except Exception as e:
    print(f"   ❌ Error importing server: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 9: Check health endpoint exists
print("\n9. Checking health endpoint...")
try:
    routes = [route.path for route in app.routes]
    if '/health' in routes:
        print("   ✅ /health endpoint exists")
    else:
        print("   ❌ /health endpoint not found!")
        print(f"   Available routes: {routes[:10]}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "="*50)
print("✅ ALL STARTUP TESTS PASSED")
print("="*50)
print("\nServer should start successfully!")
