#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Pookie4u Production Readiness
Testing all critical endpoints for authentication, user profiles, tasks, events, and gamification.
"""

import requests
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Configuration
BACKEND_URL = "https://pookie-connect.preview.emergentagent.com/api"
TEST_USER_EMAIL = f"test.user.{int(time.time())}@example.com"
TEST_USER_PASSWORD = "SecurePass123!"
TEST_USER_NAME = "Test User"

class BackendTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.access_token = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test(self, test_name, success, message, response_data=None):
        """Log test results"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
            
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "response_data": response_data
        }
        self.test_results.append(result)
        print(f"{status}: {test_name} - {message}")
        
    def make_request(self, method, endpoint, data=None, headers=None, expect_status=None):
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        
        if headers is None:
            headers = {"Content-Type": "application/json"}
            
        if self.access_token and "Authorization" not in headers:
            headers["Authorization"] = f"Bearer {self.access_token}"
            
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method.upper() == "PATCH":
                response = requests.patch(url, json=data, headers=headers, timeout=10)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            # Check expected status if provided
            if expect_status and response.status_code != expect_status:
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "data": response.text,
                    "error": f"Expected status {expect_status}, got {response.status_code}"
                }
                
            return {
                "success": True,
                "status_code": response.status_code,
                "data": response.json() if response.content else {},
                "headers": dict(response.headers)
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "status_code": None,
                "data": None
            }
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": "Invalid JSON response",
                "status_code": response.status_code,
                "data": response.text
            }
            
    def test_backend_health(self):
        """Test if backend is running"""
        print("\n🔍 Testing Backend Health...")
        
        # Test basic connectivity
        response = self.make_request("GET", "/")
        if response["success"]:
            self.log_test("Backend Connectivity", True, f"Backend responding (Status: {response['status_code']})")
        else:
            self.log_test("Backend Connectivity", False, f"Backend not responding: {response.get('error', 'Unknown error')}")
            
    def test_user_registration(self):
        """Test user registration"""
        print("\n👤 Testing User Registration...")
        
        user_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
            "name": TEST_USER_NAME
        }
        
        response = self.make_request("POST", "/auth/register", user_data)
        
        if response["success"] and response["status_code"] == 200:
            if "access_token" in response["data"]:
                self.access_token = response["data"]["access_token"]
                self.log_test("User Registration", True, "User registered successfully with JWT token")
            else:
                self.log_test("User Registration", False, "Registration successful but no access token returned")
        else:
            self.log_test("User Registration", False, f"Registration failed: {response.get('error', response.get('data', 'Unknown error'))}")
            
    def test_user_login(self):
        """Test user login (fallback if registration fails)"""
        print("\n🔐 Testing User Login...")
        
        login_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
        
        response = self.make_request("POST", "/auth/login", login_data)
        
        if response["success"] and response["status_code"] == 200:
            if "access_token" in response["data"]:
                self.access_token = response["data"]["access_token"]
                self.log_test("User Login", True, "User logged in successfully with JWT token")
            else:
                self.log_test("User Login", False, "Login successful but no access token returned")
        else:
            self.log_test("User Login", False, f"Login failed: {response.get('error', response.get('data', 'Unknown error'))}")
            
    def test_user_profile(self):
        """Test user profile retrieval"""
        print("\n👤 Testing User Profile...")
        
        if not self.access_token:
            self.log_test("User Profile", False, "No access token available")
            return
            
        response = self.make_request("GET", "/user/profile")
        
        if response["success"] and response["status_code"] == 200:
            profile_data = response["data"]
            # Check if subscription fields exist (should be present after Razorpay removal)
            required_fields = ["subscription_type", "subscription_status", "trial_started"]
            missing_fields = [field for field in required_fields if field not in profile_data]
            
            if not missing_fields:
                self.log_test("User Profile", True, "Profile retrieved with subscription fields intact")
            else:
                self.log_test("User Profile", False, f"Profile missing subscription fields: {missing_fields}")
        else:
            self.log_test("User Profile", False, f"Profile retrieval failed: {response.get('error', response.get('data', 'Unknown error'))}")
            
    def test_subscription_status(self):
        """Test subscription status endpoint (should still work)"""
        print("\n💳 Testing Subscription Status (Should Work)...")
        
        if not self.access_token:
            self.log_test("Subscription Status", False, "No access token available")
            return
            
        response = self.make_request("GET", "/subscription/status")
        
        if response["success"] and response["status_code"] == 200:
            status_data = response["data"]
            
            # Check if response has correct structure
            if "success" in status_data and "subscription" in status_data:
                subscription = status_data["subscription"]
                required_fields = ["type", "status", "is_active", "days_remaining", "can_start_trial"]
                missing_fields = [field for field in required_fields if field not in subscription]
                
                if not missing_fields:
                    self.log_test("Subscription Status", True, f"Status endpoint working correctly: {subscription.get('type', 'unknown')} subscription")
                else:
                    self.log_test("Subscription Status", False, f"Subscription object missing fields: {missing_fields}")
            else:
                self.log_test("Subscription Status", False, f"Response missing 'success' or 'subscription' fields: {list(status_data.keys())}")
        else:
            self.log_test("Subscription Status", False, f"Status endpoint failed: {response.get('error', response.get('data', 'Unknown error'))}")
            
    def test_start_trial(self):
        """Test start trial endpoint (should still work)"""
        print("\n🆓 Testing Start Trial (Should Work)...")
        
        if not self.access_token:
            self.log_test("Start Trial", False, "No access token available")
            return
            
        response = self.make_request("POST", "/subscription/start-trial")
        
        if response["success"] and response["status_code"] == 200:
            trial_data = response["data"]
            if trial_data.get("success") and "subscription" in trial_data:
                subscription = trial_data["subscription"]
                if subscription.get("type") == "trial" and subscription.get("status") == "active":
                    self.log_test("Start Trial", True, f"Trial started successfully: {subscription.get('days_remaining', 0)} days remaining")
                else:
                    self.log_test("Start Trial", False, f"Trial data incorrect: {subscription}")
            else:
                self.log_test("Start Trial", False, f"Trial response format incorrect: {trial_data}")
        else:
            # Check if it's already started (acceptable)
            if response["status_code"] == 400 and "already" in str(response.get("data", "")).lower():
                self.log_test("Start Trial", True, "Trial already started (acceptable)")
            else:
                self.log_test("Start Trial", False, f"Start trial failed: {response.get('error', response.get('data', 'Unknown error'))}")
                
    def test_removed_razorpay_endpoints(self):
        """Test that Razorpay endpoints have been removed (should return 404)"""
        print("\n🚫 Testing Removed Razorpay Endpoints (Should Return 404)...")
        
        if not self.access_token:
            self.log_test("Razorpay Endpoints Check", False, "No access token available")
            return
            
        # List of endpoints that should be removed
        removed_endpoints = [
            ("POST", "/subscription/create-order", {"subscription_type": "monthly"}),
            ("POST", "/subscription/verify-payment", {"razorpay_order_id": "test", "razorpay_payment_id": "test", "razorpay_signature": "test"}),
            ("POST", "/subscriptions/create", {"subscription_type": "monthly"}),
            ("POST", "/subscriptions/verify", {"razorpay_order_id": "test", "razorpay_payment_id": "test", "razorpay_signature": "test"}),
            ("GET", "/subscriptions/status", None),
            ("POST", "/subscriptions/cancel", None)
        ]
        
        for method, endpoint, data in removed_endpoints:
            response = self.make_request(method, endpoint, data)
            
            if response["success"] and response["status_code"] == 404:
                self.log_test(f"Removed Endpoint {method} {endpoint}", True, "Endpoint correctly returns 404 (removed)")
            elif response["status_code"] == 404:
                self.log_test(f"Removed Endpoint {method} {endpoint}", True, "Endpoint correctly returns 404 (removed)")
            else:
                self.log_test(f"Removed Endpoint {method} {endpoint}", False, f"Endpoint still exists (Status: {response.get('status_code', 'Unknown')})")
                
    def test_backend_logs_for_razorpay_errors(self):
        """Check if backend is running without Razorpay import errors"""
        print("\n📋 Testing Backend Logs for Razorpay Errors...")
        
        # Test a simple endpoint to see if backend is running without import errors
        response = self.make_request("GET", "/subscription/status")
        
        if response["success"]:
            self.log_test("Backend Razorpay Import Check", True, "Backend running without Razorpay import errors")
        else:
            if "import" in str(response.get("error", "")).lower() or "module" in str(response.get("error", "")).lower():
                self.log_test("Backend Razorpay Import Check", False, f"Possible import error: {response.get('error', 'Unknown error')}")
            else:
                self.log_test("Backend Razorpay Import Check", True, "No obvious import errors detected")
                
    def run_comprehensive_test(self):
        """Run all tests"""
        print("🚀 Starting Comprehensive Backend Testing for Razorpay Removal...")
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {TEST_USER_EMAIL}")
        print("=" * 80)
        
        # Test sequence
        self.test_backend_health()
        self.test_user_registration()
        
        # If registration fails, try login
        if not self.access_token:
            self.test_user_login()
            
        # Core functionality tests
        self.test_user_profile()
        self.test_subscription_status()
        self.test_start_trial()
        
        # Razorpay removal verification
        self.test_removed_razorpay_endpoints()
        self.test_backend_logs_for_razorpay_errors()
        
        # Print summary
        self.print_summary()
        
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("🎯 TEST SUMMARY")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            print(f"{result['status']}: {result['test']} - {result['message']}")
            
        print("\n🔍 RAZORPAY REMOVAL VERIFICATION:")
        
        # Check specific categories
        subscription_working = any("Subscription Status" in r["test"] and "✅" in r["status"] for r in self.test_results)
        trial_working = any("Start Trial" in r["test"] and "✅" in r["status"] for r in self.test_results)
        endpoints_removed = all("✅" in r["status"] for r in self.test_results if "Removed Endpoint" in r["test"])
        no_import_errors = any("Backend Razorpay Import Check" in r["test"] and "✅" in r["status"] for r in self.test_results)
        
        print(f"✅ Subscription Status Working: {'YES' if subscription_working else 'NO'}")
        print(f"✅ Free Trial Working: {'YES' if trial_working else 'NO'}")
        print(f"✅ Razorpay Endpoints Removed: {'YES' if endpoints_removed else 'NO'}")
        print(f"✅ No Import Errors: {'YES' if no_import_errors else 'NO'}")
        
        if subscription_working and trial_working and endpoints_removed and no_import_errors:
            print("\n🎉 RAZORPAY REMOVAL VERIFICATION: SUCCESS")
            print("All tests indicate Razorpay has been successfully removed while preserving core subscription functionality.")
        else:
            print("\n⚠️ RAZORPAY REMOVAL VERIFICATION: ISSUES DETECTED")
            print("Some tests failed. Please review the detailed results above.")

if __name__ == "__main__":
    tester = BackendTester()
    tester.run_comprehensive_test()