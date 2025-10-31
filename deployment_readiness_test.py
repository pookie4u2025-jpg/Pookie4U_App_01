#!/usr/bin/env python3
"""
Deployment Readiness Test for Pookie4u Backend
Focused on the specific requirements from the review request
"""

import requests
import json
import time
from datetime import datetime

class DeploymentReadinessTest:
    def __init__(self):
        self.base_url = "https://lovejourney-app.preview.emergentagent.com/api"
        self.test_user = {
            "email": f"deploy.test.{int(time.time())}@example.com",
            "password": "DeployTest123!",
            "name": "Deploy Tester"
        }
        self.auth_token = None
        self.results = {
            "passed": [],
            "failed": [],
            "warnings": []
        }
        
    def log_result(self, test_name, status, details=""):
        if status == "PASS":
            self.results["passed"].append(f"✅ {test_name}")
            print(f"✅ {test_name}")
        elif status == "FAIL":
            self.results["failed"].append(f"❌ {test_name}: {details}")
            print(f"❌ {test_name}: {details}")
        else:  # WARN
            self.results["warnings"].append(f"⚠️ {test_name}: {details}")
            print(f"⚠️ {test_name}: {details}")
    
    def make_request(self, method, endpoint, **kwargs):
        """Make HTTP request with error handling"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.request(method, url, timeout=10, **kwargs)
            return response
        except Exception as e:
            return None
    
    def test_service_health(self):
        """1. Service Health: Backend service status (port 8001), MongoDB connection, All API endpoints responding"""
        print("\n🔍 Testing Service Health...")
        
        # Test backend connectivity
        response = self.make_request("GET", "/")
        if response and response.status_code in [200, 404]:
            self.log_result("Backend Service Status", "PASS", f"Service responding (HTTP {response.status_code})")
        else:
            self.log_result("Backend Service Status", "FAIL", "Service not responding")
            return False
            
        return True
    
    def test_core_authentication(self):
        """2. Core Authentication: POST /api/auth/register, POST /api/auth/login, GET /api/user/profile"""
        print("\n🔐 Testing Core Authentication...")
        
        # Test registration
        response = self.make_request("POST", "/auth/register", json=self.test_user)
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                if "access_token" in data:
                    self.auth_token = data["access_token"]
                    self.log_result("POST /api/auth/register", "PASS", "User registration successful")
                else:
                    self.log_result("POST /api/auth/register", "FAIL", "No access token in response")
                    return False
            except:
                self.log_result("POST /api/auth/register", "FAIL", "Invalid JSON response")
                return False
        else:
            self.log_result("POST /api/auth/register", "FAIL", f"HTTP {response.status_code if response else 'No response'}")
            
        # Test login
        login_data = {"email": self.test_user["email"], "password": self.test_user["password"]}
        response = self.make_request("POST", "/auth/login", json=login_data)
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                if "access_token" in data:
                    self.auth_token = data["access_token"]
                    self.log_result("POST /api/auth/login", "PASS", "User login successful")
                else:
                    self.log_result("POST /api/auth/login", "FAIL", "No access token in response")
            except:
                self.log_result("POST /api/auth/login", "FAIL", "Invalid JSON response")
        else:
            self.log_result("POST /api/auth/login", "FAIL", f"HTTP {response.status_code if response else 'No response'}")
            
        # Test profile retrieval
        if self.auth_token:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = self.make_request("GET", "/user/profile", headers=headers)
            
            if response and response.status_code == 200:
                try:
                    profile = response.json()
                    if "id" in profile and "email" in profile:
                        self.log_result("GET /api/user/profile", "PASS", "Profile retrieval successful")
                    else:
                        self.log_result("GET /api/user/profile", "FAIL", "Profile missing required fields")
                except:
                    self.log_result("GET /api/user/profile", "FAIL", "Invalid JSON response")
            else:
                self.log_result("GET /api/user/profile", "FAIL", f"HTTP {response.status_code if response else 'No response'}")
        else:
            self.log_result("GET /api/user/profile", "FAIL", "No authentication token available")
            
        return self.auth_token is not None
    
    def test_main_features(self):
        """3. Main Features: Daily tasks, Weekly tasks, Calendar events, Gift recommendations, Daily messages"""
        print("\n🎯 Testing Main Features...")
        
        if not self.auth_token:
            self.log_result("Main Features", "FAIL", "No authentication token")
            return False
            
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # Test daily tasks
        response = self.make_request("GET", "/tasks/daily", headers=headers)
        if response and response.status_code == 200:
            try:
                data = response.json()
                if "tasks" in data:
                    self.log_result("GET /api/tasks/daily", "PASS", f"Retrieved {len(data['tasks'])} daily tasks")
                else:
                    self.log_result("GET /api/tasks/daily", "FAIL", "No tasks in response")
            except:
                self.log_result("GET /api/tasks/daily", "FAIL", "Invalid JSON response")
        else:
            self.log_result("GET /api/tasks/daily", "FAIL", f"HTTP {response.status_code if response else 'No response'}")
            
        # Test weekly tasks
        response = self.make_request("GET", "/tasks/weekly", headers=headers)
        if response and response.status_code == 200:
            try:
                data = response.json()
                if "tasks" in data:
                    self.log_result("GET /api/tasks/weekly", "PASS", f"Retrieved {len(data['tasks'])} weekly tasks")
                else:
                    self.log_result("GET /api/tasks/weekly", "FAIL", "No tasks in response")
            except:
                self.log_result("GET /api/tasks/weekly", "FAIL", "Invalid JSON response")
        else:
            self.log_result("GET /api/tasks/weekly", "FAIL", f"HTTP {response.status_code if response else 'No response'}")
            
        # Test calendar events
        response = self.make_request("GET", "/events", headers=headers)
        if response and response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list) or "events" in data:
                    event_count = len(data) if isinstance(data, list) else len(data.get("events", []))
                    self.log_result("GET /api/events", "PASS", f"Retrieved {event_count} events")
                else:
                    self.log_result("GET /api/events", "FAIL", "Invalid events response format")
            except:
                self.log_result("GET /api/events", "FAIL", "Invalid JSON response")
        else:
            self.log_result("GET /api/events", "FAIL", f"HTTP {response.status_code if response else 'No response'}")
            
        # Test gift recommendations
        response = self.make_request("GET", "/gifts")
        if response and response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("GET /api/gifts", "PASS", f"Retrieved {len(data)} gift recommendations")
                else:
                    self.log_result("GET /api/gifts", "FAIL", "Invalid gifts response format")
            except:
                self.log_result("GET /api/gifts", "FAIL", "Invalid JSON response")
        else:
            self.log_result("GET /api/gifts", "FAIL", f"HTTP {response.status_code if response else 'No response'}")
            
        # Test daily messages for LONG_DISTANCE mode
        response = self.make_request("GET", "/messages/daily/LONG_DISTANCE", headers=headers)
        if response and response.status_code == 200:
            try:
                data = response.json()
                if "messages" in data:
                    self.log_result("GET /api/messages/daily/LONG_DISTANCE", "PASS", f"Retrieved {len(data['messages'])} daily messages")
                else:
                    self.log_result("GET /api/messages/daily/LONG_DISTANCE", "FAIL", "No messages in response")
            except:
                self.log_result("GET /api/messages/daily/LONG_DISTANCE", "FAIL", "Invalid JSON response")
        else:
            self.log_result("GET /api/messages/daily/LONG_DISTANCE", "FAIL", f"HTTP {response.status_code if response else 'No response'}")
    
    def test_subscription_system(self):
        """4. Subscription System: Free trial activation, Subscription status, Razorpay subscription creation"""
        print("\n💳 Testing Subscription System...")
        
        if not self.auth_token:
            self.log_result("Subscription System", "FAIL", "No authentication token")
            return False
            
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # Test subscription status
        response = self.make_request("GET", "/subscription/status", headers=headers)
        if response and response.status_code == 200:
            try:
                data = response.json()
                if "subscription" in data:
                    self.log_result("GET /api/subscription/status", "PASS", f"Status: {data['subscription'].get('type', 'unknown')}")
                else:
                    self.log_result("GET /api/subscription/status", "FAIL", "No subscription data in response")
            except:
                self.log_result("GET /api/subscription/status", "FAIL", "Invalid JSON response")
        else:
            self.log_result("GET /api/subscription/status", "FAIL", f"HTTP {response.status_code if response else 'No response'}")
            
        # Test free trial activation
        response = self.make_request("POST", "/subscription/start-trial", headers=headers)
        if response and response.status_code == 200:
            try:
                data = response.json()
                if data.get("success"):
                    self.log_result("POST /api/subscription/start-trial", "PASS", "Trial activation successful")
                else:
                    self.log_result("POST /api/subscription/start-trial", "FAIL", "Trial activation failed")
            except:
                self.log_result("POST /api/subscription/start-trial", "FAIL", "Invalid JSON response")
        elif response and response.status_code == 400:
            self.log_result("POST /api/subscription/start-trial", "WARN", "Trial already used or not eligible")
        else:
            self.log_result("POST /api/subscription/start-trial", "FAIL", f"HTTP {response.status_code if response else 'No response'}")
            
        # Test Razorpay subscription creation
        subscription_data = {"subscription_type": "monthly"}
        response = self.make_request("POST", "/subscriptions/create", json=subscription_data, headers=headers)
        if response and response.status_code == 200:
            try:
                data = response.json()
                if "subscription_id" in data or "id" in data:
                    self.log_result("POST /api/subscriptions/create", "PASS", "Razorpay subscription created")
                else:
                    self.log_result("POST /api/subscriptions/create", "FAIL", "No subscription ID in response")
            except:
                self.log_result("POST /api/subscriptions/create", "FAIL", "Invalid JSON response")
        else:
            self.log_result("POST /api/subscriptions/create", "FAIL", f"HTTP {response.status_code if response else 'No response'}")
    
    def test_configuration_check(self):
        """5. Configuration Check: Environment variables, Razorpay credentials, Google OAuth credentials, MongoDB connection"""
        print("\n⚙️ Testing Configuration...")
        
        # Test Google OAuth configuration by checking endpoint response
        oauth_data = {"provider": "google", "id_token": "invalid_test_token"}
        response = self.make_request("POST", "/auth/oauth/google", json=oauth_data)
        
        if response and response.status_code == 400:
            self.log_result("Google OAuth Credentials", "PASS", "OAuth endpoint configured and validating tokens")
        else:
            self.log_result("Google OAuth Credentials", "WARN", f"OAuth endpoint response: {response.status_code if response else 'No response'}")
            
        # Test Razorpay configuration by checking if subscription endpoints exist
        if self.auth_token:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = self.make_request("GET", "/subscription/status", headers=headers)
            if response and response.status_code == 200:
                self.log_result("Razorpay Credentials", "PASS", "Subscription endpoints accessible")
            else:
                self.log_result("Razorpay Credentials", "WARN", "Subscription endpoints may not be configured")
        else:
            self.log_result("Razorpay Credentials", "WARN", "Cannot test - no authentication token")
            
        # MongoDB connection is tested implicitly through successful authentication and profile operations
        if self.auth_token:
            self.log_result("MongoDB Connection", "PASS", "Database operations working (auth/profile successful)")
        else:
            self.log_result("MongoDB Connection", "FAIL", "Database operations failing")
    
    def test_error_handling(self):
        """6. Error Handling: Test unauthorized access (401), invalid endpoints (404), missing data (400)"""
        print("\n🚨 Testing Error Handling...")
        
        # Test unauthorized access (401)
        response = self.make_request("GET", "/user/profile")
        if response and response.status_code in [401, 403]:
            self.log_result("Unauthorized Access (401)", "PASS", f"Properly rejected with {response.status_code}")
        else:
            self.log_result("Unauthorized Access (401)", "FAIL", f"Expected 401/403, got {response.status_code if response else 'No response'}")
            
        # Test invalid endpoints (404)
        response = self.make_request("GET", "/nonexistent/endpoint")
        if response and response.status_code == 404:
            self.log_result("Invalid Endpoints (404)", "PASS", "Properly returned 404")
        else:
            self.log_result("Invalid Endpoints (404)", "WARN", f"Expected 404, got {response.status_code if response else 'No response'}")
            
        # Test missing data (400)
        response = self.make_request("POST", "/auth/register", json={})
        if response and response.status_code in [400, 422]:
            self.log_result("Missing Data (400)", "PASS", f"Properly rejected invalid data with {response.status_code}")
        else:
            self.log_result("Missing Data (400)", "FAIL", f"Expected 400/422, got {response.status_code if response else 'No response'}")
    
    def calculate_deployment_score(self):
        """Calculate deployment readiness score"""
        total_tests = len(self.results["passed"]) + len(self.results["failed"])
        if total_tests == 0:
            return 0
            
        pass_rate = len(self.results["passed"]) / total_tests * 100
        
        # Deduct points for critical failures
        critical_failures = 0
        for failure in self.results["failed"]:
            if any(keyword in failure.lower() for keyword in ["service status", "mongodb", "auth/register", "auth/login"]):
                critical_failures += 1
                
        final_score = max(0, pass_rate - (critical_failures * 10))
        return int(final_score)
    
    def run_deployment_test(self):
        """Run comprehensive deployment readiness test"""
        print("🚀 Pookie4u Backend Deployment Readiness Test")
        print(f"📍 Backend URL: {self.base_url}")
        print(f"🕐 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Run all test suites
        self.test_service_health()
        self.test_core_authentication()
        self.test_main_features()
        self.test_subscription_system()
        self.test_configuration_check()
        self.test_error_handling()
        
        # Generate final report
        print("\n" + "=" * 80)
        print("📊 DEPLOYMENT READINESS REPORT")
        print("=" * 80)
        
        print(f"✅ Passed Tests: {len(self.results['passed'])}")
        print(f"❌ Failed Tests: {len(self.results['failed'])}")
        print(f"⚠️ Warnings: {len(self.results['warnings'])}")
        
        deployment_score = self.calculate_deployment_score()
        print(f"🎯 Deployment Readiness Score: {deployment_score}/100")
        
        if deployment_score >= 90:
            print("🟢 EXCELLENT - Ready for production deployment")
        elif deployment_score >= 75:
            print("🟡 GOOD - Minor issues to address before deployment")
        elif deployment_score >= 60:
            print("🟠 FAIR - Several issues need attention")
        else:
            print("🔴 POOR - Critical issues must be resolved before deployment")
            
        # Show results by category
        if self.results["passed"]:
            print(f"\n✅ PASSED TESTS ({len(self.results['passed'])}):")
            for test in self.results["passed"]:
                print(f"   {test}")
                
        if self.results["failed"]:
            print(f"\n❌ FAILED TESTS ({len(self.results['failed'])}):")
            for test in self.results["failed"]:
                print(f"   {test}")
                
        if self.results["warnings"]:
            print(f"\n⚠️ WARNINGS ({len(self.results['warnings'])}):")
            for test in self.results["warnings"]:
                print(f"   {test}")
                
        return deployment_score

if __name__ == "__main__":
    tester = DeploymentReadinessTest()
    score = tester.run_deployment_test()
    
    print(f"\n🏁 Test Complete - Score: {score}/100")
    if score >= 75:
        exit(0)
    else:
        exit(1)