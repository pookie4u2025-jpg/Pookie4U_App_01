#!/usr/bin/env python3
"""
Network Connectivity Test for Events API
Specifically testing the "Network request failed" issue reported by user
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://pookie-couples-1.preview.emergentagent.com/api"
FRONTEND_URL = "https://pookie-couples-1.preview.emergentagent.com"

class NetworkTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        
    def test_basic_connectivity(self):
        """Test basic network connectivity"""
        print("🌐 Testing Basic Network Connectivity")
        print("-" * 50)
        
        try:
            # Test frontend URL
            response = self.session.get(FRONTEND_URL, timeout=10)
            print(f"✅ Frontend URL ({FRONTEND_URL}): Status {response.status_code}")
        except Exception as e:
            print(f"❌ Frontend URL failed: {str(e)}")
        
        try:
            # Test backend root
            response = self.session.get(BACKEND_URL.replace('/api', ''), timeout=10)
            print(f"✅ Backend Root: Status {response.status_code}")
        except Exception as e:
            print(f"❌ Backend Root failed: {str(e)}")
        
        try:
            # Test API endpoint without auth
            response = self.session.get(f"{BACKEND_URL}/gifts", timeout=10)
            print(f"✅ API Endpoint (/gifts): Status {response.status_code}")
        except Exception as e:
            print(f"❌ API Endpoint failed: {str(e)}")
    
    def authenticate(self):
        """Get authentication token"""
        print("\n🔐 Testing Authentication")
        print("-" * 50)
        
        try:
            # Try login first
            login_data = {
                "email": "calendar.tester@pookie4u.com",
                "password": "SecureTest123!"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data, timeout=10)
            
            if response.status_code == 200:
                self.auth_token = response.json()["access_token"]
                print("✅ Authentication successful")
                return True
            else:
                print(f"❌ Authentication failed: Status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def test_events_api_detailed(self):
        """Detailed test of events API with various scenarios"""
        print("\n📅 Testing Events API - Detailed Analysis")
        print("-" * 50)
        
        if not self.auth_token:
            print("❌ No auth token available")
            return
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # Test 1: Basic GET request
        try:
            start_time = time.time()
            response = self.session.get(f"{BACKEND_URL}/events", headers=headers, timeout=30)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                events_count = len(data.get("events", []))
                print(f"✅ GET /api/events: Status {response.status_code}")
                print(f"   Response time: {response_time:.2f}s")
                print(f"   Events returned: {events_count}")
                print(f"   Total count: {data.get('total_count', 'N/A')}")
                print(f"   Categories: {len(data.get('categories', []))}")
                
                # Test response structure
                required_fields = ["events", "total_count", "categories", "upcoming_count", "this_month_count"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    print(f"⚠️  Missing response fields: {missing_fields}")
                else:
                    print("✅ Response structure complete")
                
            else:
                print(f"❌ GET /api/events failed: Status {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                
        except requests.exceptions.ConnectTimeout:
            print("❌ Connection timeout - Network request failed")
        except requests.exceptions.ConnectionError as e:
            print(f"❌ Connection error - Network request failed: {str(e)}")
        except requests.exceptions.Timeout:
            print("❌ Request timeout - Network request failed")
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")
    
    def test_events_api_without_auth(self):
        """Test events API without authentication"""
        print("\n🔒 Testing Events API Without Authentication")
        print("-" * 50)
        
        try:
            response = self.session.get(f"{BACKEND_URL}/events", timeout=10)
            
            if response.status_code in [401, 403]:
                print(f"✅ Correctly requires authentication: Status {response.status_code}")
            else:
                print(f"⚠️  Unexpected status without auth: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error testing without auth: {str(e)}")
    
    def test_cors_headers(self):
        """Test CORS headers"""
        print("\n🌍 Testing CORS Headers")
        print("-" * 50)
        
        try:
            # Test preflight request
            headers = {
                "Origin": FRONTEND_URL,
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Authorization"
            }
            
            response = self.session.options(f"{BACKEND_URL}/events", headers=headers, timeout=10)
            
            cors_headers = {
                "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
                "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
                "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers"),
                "Access-Control-Allow-Credentials": response.headers.get("Access-Control-Allow-Credentials")
            }
            
            print(f"✅ CORS preflight: Status {response.status_code}")
            for header, value in cors_headers.items():
                if value:
                    print(f"   {header}: {value}")
                else:
                    print(f"   {header}: Not set")
                    
        except Exception as e:
            print(f"❌ CORS test error: {str(e)}")
    
    def test_multiple_requests(self):
        """Test multiple consecutive requests to check for rate limiting or connection issues"""
        print("\n🔄 Testing Multiple Consecutive Requests")
        print("-" * 50)
        
        if not self.auth_token:
            print("❌ No auth token available")
            return
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        successful_requests = 0
        failed_requests = 0
        
        for i in range(5):
            try:
                start_time = time.time()
                response = self.session.get(f"{BACKEND_URL}/events", headers=headers, timeout=15)
                end_time = time.time()
                
                if response.status_code == 200:
                    successful_requests += 1
                    print(f"✅ Request {i+1}: Success ({end_time - start_time:.2f}s)")
                else:
                    failed_requests += 1
                    print(f"❌ Request {i+1}: Failed with status {response.status_code}")
                    
            except Exception as e:
                failed_requests += 1
                print(f"❌ Request {i+1}: Exception - {str(e)}")
            
            time.sleep(0.5)  # Small delay between requests
        
        print(f"\n📊 Results: {successful_requests} successful, {failed_requests} failed")
    
    def test_different_user_agents(self):
        """Test with different user agents to simulate frontend requests"""
        print("\n🖥️  Testing Different User Agents")
        print("-" * 50)
        
        if not self.auth_token:
            print("❌ No auth token available")
            return
        
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",  # Chrome
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15",  # iPhone
            "Mozilla/5.0 (Android 10; Mobile; rv:81.0) Gecko/81.0 Firefox/81.0",  # Android
            "Expo/1.0 (React Native)"  # React Native/Expo
        ]
        
        headers_base = {"Authorization": f"Bearer {self.auth_token}"}
        
        for i, ua in enumerate(user_agents):
            try:
                headers = {**headers_base, "User-Agent": ua}
                response = self.session.get(f"{BACKEND_URL}/events", headers=headers, timeout=10)
                
                if response.status_code == 200:
                    print(f"✅ User Agent {i+1}: Success")
                else:
                    print(f"❌ User Agent {i+1}: Failed with status {response.status_code}")
                    
            except Exception as e:
                print(f"❌ User Agent {i+1}: Exception - {str(e)}")
    
    def run_network_tests(self):
        """Run all network tests"""
        print("🚀 NETWORK CONNECTIVITY TESTING FOR EVENTS API")
        print("Investigating 'Network request failed' issue")
        print("=" * 80)
        
        self.test_basic_connectivity()
        
        if self.authenticate():
            self.test_events_api_detailed()
            self.test_multiple_requests()
            self.test_different_user_agents()
        
        self.test_events_api_without_auth()
        self.test_cors_headers()
        
        print("\n" + "=" * 80)
        print("🎯 NETWORK TEST SUMMARY")
        print("=" * 80)
        print("If all tests above passed, the 'Network request failed' issue")
        print("is likely on the frontend side (React Native/Expo configuration)")
        print("or related to authentication token handling.")

if __name__ == "__main__":
    tester = NetworkTester()
    tester.run_network_tests()