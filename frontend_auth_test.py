#!/usr/bin/env python3
"""
Frontend Authentication Test
Test if the issue is with authentication or API calls from frontend perspective
"""

import requests
import json
from datetime import datetime

# Configuration
BACKEND_URL = "https://pookie-couple.preview.emergentagent.com/api"

class FrontendAuthTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        
    def test_authentication_flow(self):
        """Test the complete authentication flow that frontend would use"""
        print("🔐 Testing Frontend Authentication Flow")
        print("-" * 50)
        
        # Step 1: Register/Login
        try:
            # Try login first
            login_data = {
                "email": "frontend.test@pookie4u.com",
                "password": "FrontendTest123!"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                print(f"✅ Login successful")
                print(f"   Token received: {self.auth_token[:20]}...")
                return True
            elif response.status_code == 401:
                # User doesn't exist, try registration
                register_data = {
                    "email": "frontend.test@pookie4u.com",
                    "password": "FrontendTest123!",
                    "name": "Frontend Tester"
                }
                
                register_response = self.session.post(f"{BACKEND_URL}/auth/register", json=register_data)
                
                if register_response.status_code == 200:
                    data = register_response.json()
                    self.auth_token = data.get("access_token")
                    print(f"✅ Registration successful")
                    print(f"   Token received: {self.auth_token[:20]}...")
                    return True
                else:
                    print(f"❌ Registration failed: {register_response.status_code}")
                    print(f"   Response: {register_response.text}")
                    return False
            else:
                print(f"❌ Login failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def test_profile_fetch(self):
        """Test profile fetching like frontend does"""
        print("\n👤 Testing Profile Fetch")
        print("-" * 50)
        
        if not self.auth_token:
            print("❌ No auth token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = self.session.get(f"{BACKEND_URL}/user/profile", headers=headers)
            
            if response.status_code == 200:
                profile = response.json()
                print(f"✅ Profile fetch successful")
                print(f"   User: {profile.get('name')} ({profile.get('email')})")
                print(f"   Relationship mode: {profile.get('relationship_mode')}")
                return True
            else:
                print(f"❌ Profile fetch failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Profile fetch error: {str(e)}")
            return False
    
    def test_events_api_like_frontend(self):
        """Test events API exactly like frontend does"""
        print("\n📅 Testing Events API (Frontend Style)")
        print("-" * 50)
        
        if not self.auth_token:
            print("❌ No auth token available")
            return False
        
        try:
            # Simulate exact frontend request
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json",
                "User-Agent": "Expo/1.0 (React Native)"
            }
            
            print(f"Making request to: {BACKEND_URL}/events")
            print(f"Headers: {headers}")
            
            response = self.session.get(f"{BACKEND_URL}/events", headers=headers, timeout=30)
            
            print(f"Response status: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                events_count = len(data.get("events", []))
                print(f"✅ Events API successful")
                print(f"   Events returned: {events_count}")
                print(f"   Total count: {data.get('total_count')}")
                print(f"   Categories: {len(data.get('categories', []))}")
                print(f"   Upcoming count: {data.get('upcoming_count')}")
                print(f"   This month count: {data.get('this_month_count')}")
                
                # Test response structure
                required_fields = ["events", "total_count", "categories", "upcoming_count", "this_month_count"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    print(f"⚠️  Missing response fields: {missing_fields}")
                else:
                    print("✅ Response structure complete")
                
                return True
            elif response.status_code == 403:
                print(f"❌ Events API failed: Authentication required (403)")
                print(f"   This suggests token is invalid or expired")
                return False
            elif response.status_code == 401:
                print(f"❌ Events API failed: Unauthorized (401)")
                print(f"   This suggests token is missing or malformed")
                return False
            else:
                print(f"❌ Events API failed: {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                return False
                
        except requests.exceptions.ConnectTimeout:
            print("❌ Connection timeout - Network request failed")
            return False
        except requests.exceptions.ConnectionError as e:
            print(f"❌ Connection error - Network request failed: {str(e)}")
            return False
        except requests.exceptions.Timeout:
            print("❌ Request timeout - Network request failed")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")
            return False
    
    def test_token_validation(self):
        """Test if the token is valid and properly formatted"""
        print("\n🔍 Testing Token Validation")
        print("-" * 50)
        
        if not self.auth_token:
            print("❌ No auth token available")
            return False
        
        try:
            # Decode JWT token (without verification for inspection)
            import base64
            import json
            
            # Split JWT token
            parts = self.auth_token.split('.')
            if len(parts) != 3:
                print(f"❌ Invalid JWT format: {len(parts)} parts instead of 3")
                return False
            
            # Decode header
            header_padding = '=' * (4 - len(parts[0]) % 4)
            header = base64.urlsafe_b64decode(parts[0] + header_padding)
            header_data = json.loads(header)
            print(f"✅ JWT Header: {header_data}")
            
            # Decode payload
            payload_padding = '=' * (4 - len(parts[1]) % 4)
            payload = base64.urlsafe_b64decode(parts[1] + payload_padding)
            payload_data = json.loads(payload)
            print(f"✅ JWT Payload: {payload_data}")
            
            # Check expiration
            if 'exp' in payload_data:
                exp_time = datetime.fromtimestamp(payload_data['exp'])
                current_time = datetime.now()
                if exp_time > current_time:
                    print(f"✅ Token valid until: {exp_time}")
                else:
                    print(f"❌ Token expired at: {exp_time}")
                    return False
            
            return True
            
        except Exception as e:
            print(f"❌ Token validation error: {str(e)}")
            return False
    
    def run_frontend_tests(self):
        """Run all frontend-style tests"""
        print("🚀 FRONTEND AUTHENTICATION & API TESTING")
        print("Simulating exact frontend behavior")
        print("=" * 80)
        
        # Test authentication
        if not self.test_authentication_flow():
            print("\n❌ Authentication failed - cannot proceed")
            return False
        
        # Test token validation
        self.test_token_validation()
        
        # Test profile fetch
        self.test_profile_fetch()
        
        # Test events API
        events_success = self.test_events_api_like_frontend()
        
        print("\n" + "=" * 80)
        print("🎯 FRONTEND TEST SUMMARY")
        print("=" * 80)
        
        if events_success:
            print("✅ All tests passed - Events API is working correctly")
            print("   The 'Network request failed' issue is likely:")
            print("   1. Frontend authentication state management")
            print("   2. React Native/Expo network configuration")
            print("   3. Token persistence issues")
        else:
            print("❌ Events API test failed")
            print("   This indicates a backend authentication issue")
        
        return events_success

if __name__ == "__main__":
    tester = FrontendAuthTester()
    tester.run_frontend_tests()