#!/usr/bin/env python3
"""
Backend Testing Script for Pookie4u App - Critical Bug Fixes Testing
Testing 4 critical bug fixes as requested:
1. Authentication Login Fix
2. Task Completion 
3. Subscription Payment Endpoints
4. Push Notification Registration
"""

import requests
import json
import time
import random
import string
from datetime import datetime

# Configuration
BASE_URL = "https://couple-referrals.preview.emergentagent.com/api"
HEADERS = {"Content-Type": "application/json"}

class BackendTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.headers = HEADERS.copy()
        self.access_token = None
        self.test_user_email = None
        self.test_user_password = None
        self.test_results = []
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
        if details:
            print(f"   Details: {details}")
        print()

    def generate_test_user_data(self):
        """Generate realistic test user data"""
        random_suffix = ''.join(random.choices(string.digits, k=6))
        self.test_user_email = f"emma.wilson{random_suffix}@example.com"
        self.test_user_password = "SecurePass123!"
        return {
            "email": self.test_user_email,
            "password": self.test_user_password,
            "name": "Emma Wilson"
        }

    def make_request(self, method, endpoint, data=None, auth_required=False):
        """Make HTTP request with proper error handling"""
        url = f"{self.base_url}{endpoint}"
        headers = self.headers.copy()
        
        if auth_required and self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        
        try:
            print(f"Making {method} request to: {url}")
            if data:
                print(f"Request data: {json.dumps(data, indent=2)}")
            
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=30)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=data, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            print(f"Response status: {response.status_code}")
            return response
        except requests.exceptions.Timeout as e:
            print(f"Request timeout: {e}")
            return None
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error: {e}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None

    def test_1_authentication_login_fix(self):
        """Test 1: Authentication Login Fix"""
        print("🔐 TESTING AUTHENTICATION LOGIN FIX")
        print("=" * 50)
        
        # Step 1: Register a new user
        user_data = self.generate_test_user_data()
        response = self.make_request("POST", "/auth/register", user_data)
        
        if not response:
            self.log_result("1.1 User Registration", False, "Network error during registration")
            return False
            
        if response.status_code == 200:
            try:
                reg_data = response.json()
                if "access_token" in reg_data and "token_type" in reg_data:
                    self.log_result("1.1 User Registration", True, 
                                  f"User registered successfully with token", 
                                  {"email": self.test_user_email, "token_type": reg_data.get("token_type")})
                else:
                    self.log_result("1.1 User Registration", False, 
                                  "Registration response missing required fields",
                                  {"response": reg_data})
                    return False
            except json.JSONDecodeError:
                self.log_result("1.1 User Registration", False, "Invalid JSON response from registration")
                return False
        else:
            try:
                error_data = response.json()
                self.log_result("1.1 User Registration", False, 
                              f"Registration failed with status {response.status_code}",
                              {"error": error_data})
            except:
                self.log_result("1.1 User Registration", False, 
                              f"Registration failed with status {response.status_code}")
            return False

        # Step 2: Login with the same credentials
        login_data = {
            "email": self.test_user_email,
            "password": self.test_user_password
        }
        
        response = self.make_request("POST", "/login", login_data)
        
        if not response:
            self.log_result("1.2 User Login", False, "Network error during login")
            return False
            
        if response.status_code == 200:
            try:
                login_response = response.json()
                if "access_token" in login_response and "token_type" in login_response:
                    self.access_token = login_response["access_token"]
                    self.log_result("1.2 User Login", True, 
                                  "Login successful with access token",
                                  {"token_type": login_response.get("token_type")})
                else:
                    self.log_result("1.2 User Login", False, 
                                  "Login response missing required fields",
                                  {"response": login_response})
                    return False
            except json.JSONDecodeError:
                self.log_result("1.2 User Login", False, "Invalid JSON response from login")
                return False
        else:
            try:
                error_data = response.json()
                self.log_result("1.2 User Login", False, 
                              f"Login failed with status {response.status_code}",
                              {"error": error_data})
            except:
                self.log_result("1.2 User Login", False, 
                              f"Login failed with status {response.status_code}")
            return False

        # Step 3: Test token validity with authenticated endpoint
        response = self.make_request("GET", "/user/profile", auth_required=True)
        
        if not response:
            self.log_result("1.3 Token Validation", False, "Network error during token validation")
            return False
            
        if response.status_code == 200:
            try:
                profile_data = response.json()
                if "email" in profile_data and profile_data["email"] == self.test_user_email:
                    self.log_result("1.3 Token Validation", True, 
                                  "Token is valid and can access authenticated endpoints",
                                  {"profile_email": profile_data["email"]})
                    return True
                else:
                    self.log_result("1.3 Token Validation", False, 
                                  "Profile data doesn't match expected user",
                                  {"expected": self.test_user_email, "got": profile_data.get("email")})
                    return False
            except json.JSONDecodeError:
                self.log_result("1.3 Token Validation", False, "Invalid JSON response from profile")
                return False
        else:
            self.log_result("1.3 Token Validation", False, 
                          f"Token validation failed with status {response.status_code}")
            return False

    def test_2_task_completion(self):
        """Test 2: Task Completion"""
        print("📋 TESTING TASK COMPLETION")
        print("=" * 50)
        
        if not self.access_token:
            self.log_result("2.0 Prerequisites", False, "No access token available for task completion test")
            return False

        # Step 1: Get daily tasks
        response = self.make_request("GET", "/tasks/daily", auth_required=True)
        
        if not response:
            self.log_result("2.1 Get Daily Tasks", False, "Network error getting daily tasks")
            return False
            
        if response.status_code == 200:
            try:
                tasks_data = response.json()
                if isinstance(tasks_data, list) and len(tasks_data) > 0:
                    task_to_complete = tasks_data[0]
                    task_id = task_to_complete.get("id")
                    if task_id:
                        self.log_result("2.1 Get Daily Tasks", True, 
                                      f"Retrieved {len(tasks_data)} daily tasks",
                                      {"first_task_id": task_id, "task_title": task_to_complete.get("title", "N/A")})
                    else:
                        self.log_result("2.1 Get Daily Tasks", False, 
                                      "Tasks missing required 'id' field",
                                      {"task_structure": task_to_complete})
                        return False
                else:
                    self.log_result("2.1 Get Daily Tasks", False, 
                                  "No daily tasks returned or invalid format",
                                  {"response": tasks_data})
                    return False
            except json.JSONDecodeError:
                self.log_result("2.1 Get Daily Tasks", False, "Invalid JSON response from daily tasks")
                return False
        else:
            self.log_result("2.1 Get Daily Tasks", False, 
                          f"Failed to get daily tasks with status {response.status_code}")
            return False

        # Step 2: Complete the first task
        complete_data = {"task_id": task_id}
        response = self.make_request("POST", "/tasks/complete", complete_data, auth_required=True)
        
        if not response:
            self.log_result("2.2 Complete Task", False, "Network error completing task")
            return False
            
        if response.status_code == 200:
            try:
                completion_data = response.json()
                if "points_earned" in completion_data and "success" in completion_data:
                    points_earned = completion_data["points_earned"]
                    if completion_data["success"] and points_earned > 0:
                        self.log_result("2.2 Complete Task", True, 
                                      f"Task completed successfully with {points_earned} points earned",
                                      {"task_id": task_id, "points": points_earned})
                    else:
                        self.log_result("2.2 Complete Task", False, 
                                      "Task completion returned success=false or 0 points",
                                      {"response": completion_data})
                        return False
                else:
                    self.log_result("2.2 Complete Task", False, 
                                  "Task completion response missing required fields",
                                  {"response": completion_data})
                    return False
            except json.JSONDecodeError:
                self.log_result("2.2 Complete Task", False, "Invalid JSON response from task completion")
                return False
        else:
            try:
                error_data = response.json()
                self.log_result("2.2 Complete Task", False, 
                              f"Task completion failed with status {response.status_code}",
                              {"error": error_data})
            except:
                self.log_result("2.2 Complete Task", False, 
                              f"Task completion failed with status {response.status_code}")
            return False

        # Step 3: Verify points are updated in user profile
        response = self.make_request("GET", "/user/profile", auth_required=True)
        
        if not response:
            self.log_result("2.3 Verify Points Update", False, "Network error getting updated profile")
            return False
            
        if response.status_code == 200:
            try:
                profile_data = response.json()
                total_points = profile_data.get("total_points", 0)
                tasks_completed = profile_data.get("tasks_completed", 0)
                
                if total_points >= points_earned and tasks_completed >= 1:
                    self.log_result("2.3 Verify Points Update", True, 
                                  f"Points updated correctly in profile",
                                  {"total_points": total_points, "tasks_completed": tasks_completed})
                    return True
                else:
                    self.log_result("2.3 Verify Points Update", False, 
                                  "Points not properly updated in profile",
                                  {"total_points": total_points, "tasks_completed": tasks_completed, "expected_points": points_earned})
                    return False
            except json.JSONDecodeError:
                self.log_result("2.3 Verify Points Update", False, "Invalid JSON response from profile")
                return False
        else:
            self.log_result("2.3 Verify Points Update", False, 
                          f"Failed to get updated profile with status {response.status_code}")
            return False

    def test_3_subscription_payment_endpoints(self):
        """Test 3: Subscription Payment Endpoints"""
        print("💳 TESTING SUBSCRIPTION PAYMENT ENDPOINTS")
        print("=" * 50)
        
        if not self.access_token:
            self.log_result("3.0 Prerequisites", False, "No access token available for subscription test")
            return False

        # Step 1: Test create-order endpoint
        order_data = {"plan_type": "monthly"}
        response = self.make_request("POST", "/subscription/create-order", order_data, auth_required=True)
        
        if not response:
            self.log_result("3.1 Create Order", False, "Network error creating subscription order")
            return False
            
        if response.status_code == 200:
            try:
                order_response = response.json()
                required_fields = ["subscription_id", "plan_id", "status"]
                missing_fields = [field for field in required_fields if field not in order_response]
                
                if not missing_fields:
                    subscription_id = order_response["subscription_id"]
                    plan_id = order_response["plan_id"]
                    status = order_response["status"]
                    
                    self.log_result("3.1 Create Order", True, 
                                  "Subscription order created successfully",
                                  {"subscription_id": subscription_id, "plan_id": plan_id, "status": status})
                else:
                    self.log_result("3.1 Create Order", False, 
                                  f"Create order response missing required fields: {missing_fields}",
                                  {"response": order_response})
                    return False
            except json.JSONDecodeError:
                self.log_result("3.1 Create Order", False, "Invalid JSON response from create order")
                return False
        else:
            try:
                error_data = response.json()
                self.log_result("3.1 Create Order", False, 
                              f"Create order failed with status {response.status_code}",
                              {"error": error_data})
            except:
                self.log_result("3.1 Create Order", False, 
                              f"Create order failed with status {response.status_code}")
            return False

        # Step 2: Test verify-payment endpoint (with mock data)
        payment_data = {
            "razorpay_payment_id": "pay_mock123456789",
            "razorpay_subscription_id": subscription_id,
            "razorpay_signature": "mock_signature_12345"
        }
        
        response = self.make_request("POST", "/subscription/verify-payment", payment_data, auth_required=True)
        
        if not response:
            self.log_result("3.2 Verify Payment", False, "Network error verifying payment")
            return False
            
        # For verify-payment, we expect it to handle gracefully (may fail validation but endpoint should exist)
        if response.status_code in [200, 400, 422]:  # Accept these as valid responses
            try:
                verify_response = response.json()
                if response.status_code == 200:
                    self.log_result("3.2 Verify Payment", True, 
                                  "Payment verification endpoint working (success response)",
                                  {"response": verify_response})
                else:
                    # 400/422 is expected for mock data, but endpoint exists and handles gracefully
                    self.log_result("3.2 Verify Payment", True, 
                                  f"Payment verification endpoint working (graceful failure with status {response.status_code})",
                                  {"response": verify_response})
                return True
            except json.JSONDecodeError:
                self.log_result("3.2 Verify Payment", False, "Invalid JSON response from verify payment")
                return False
        else:
            try:
                error_data = response.json()
                self.log_result("3.2 Verify Payment", False, 
                              f"Verify payment failed with unexpected status {response.status_code}",
                              {"error": error_data})
            except:
                self.log_result("3.2 Verify Payment", False, 
                              f"Verify payment failed with unexpected status {response.status_code}")
            return False

    def test_4_push_notification_registration(self):
        """Test 4: Push Notification Registration"""
        print("🔔 TESTING PUSH NOTIFICATION REGISTRATION")
        print("=" * 50)
        
        if not self.access_token:
            self.log_result("4.0 Prerequisites", False, "No access token available for push notification test")
            return False

        # Step 1: Test push notification registration
        push_data = {
            "push_token": f"ExponentPushToken[mock_token_{random.randint(100000, 999999)}]",
            "device_type": "ios",
            "app_version": "1.0.0"
        }
        
        response = self.make_request("POST", "/notifications/register", push_data, auth_required=True)
        
        if not response:
            self.log_result("4.1 Register Push Token", False, "Network error registering push token")
            return False
            
        if response.status_code == 200:
            try:
                register_response = response.json()
                if "success" in register_response and register_response["success"]:
                    self.log_result("4.1 Register Push Token", True, 
                                  "Push token registered successfully",
                                  {"push_token": push_data["push_token"], "response": register_response})
                else:
                    self.log_result("4.1 Register Push Token", False, 
                                  "Push token registration returned success=false",
                                  {"response": register_response})
                    return False
            except json.JSONDecodeError:
                self.log_result("4.1 Register Push Token", False, "Invalid JSON response from push registration")
                return False
        else:
            try:
                error_data = response.json()
                self.log_result("4.1 Register Push Token", False, 
                              f"Push registration failed with status {response.status_code}",
                              {"error": error_data})
            except:
                self.log_result("4.1 Register Push Token", False, 
                              f"Push registration failed with status {response.status_code}")
            return False

        # Step 2: Verify token is saved to user document
        response = self.make_request("GET", "/user/profile", auth_required=True)
        
        if not response:
            self.log_result("4.2 Verify Token Saved", False, "Network error getting profile to verify token")
            return False
            
        if response.status_code == 200:
            try:
                profile_data = response.json()
                saved_push_token = profile_data.get("push_token")
                
                if saved_push_token == push_data["push_token"]:
                    self.log_result("4.2 Verify Token Saved", True, 
                                  "Push token correctly saved to user document",
                                  {"saved_token": saved_push_token})
                    return True
                else:
                    self.log_result("4.2 Verify Token Saved", False, 
                                  "Push token not properly saved to user document",
                                  {"expected": push_data["push_token"], "saved": saved_push_token})
                    return False
            except json.JSONDecodeError:
                self.log_result("4.2 Verify Token Saved", False, "Invalid JSON response from profile")
                return False
        else:
            self.log_result("4.2 Verify Token Saved", False, 
                          f"Failed to get profile to verify token with status {response.status_code}")
            return False

    def run_all_tests(self):
        """Run all critical bug fix tests"""
        print("🚀 STARTING CRITICAL BUG FIXES TESTING")
        print("=" * 60)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print("=" * 60)
        print()
        
        test_results = []
        
        # Test 1: Authentication Login Fix
        test_results.append(self.test_1_authentication_login_fix())
        print()
        
        # Test 2: Task Completion
        test_results.append(self.test_2_task_completion())
        print()
        
        # Test 3: Subscription Payment Endpoints
        test_results.append(self.test_3_subscription_payment_endpoints())
        print()
        
        # Test 4: Push Notification Registration
        test_results.append(self.test_4_push_notification_registration())
        print()
        
        # Summary
        self.print_summary(test_results)
        
        return test_results

    def print_summary(self, test_results):
        """Print test summary"""
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed_tests = sum(1 for result in test_results if result)
        total_tests = len(test_results)
        
        print(f"Total Critical Bug Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        # Individual test results
        test_names = [
            "1. Authentication Login Fix",
            "2. Task Completion", 
            "3. Subscription Payment Endpoints",
            "4. Push Notification Registration"
        ]
        
        for i, (name, result) in enumerate(zip(test_names, test_results)):
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status}: {name}")
        
        print()
        print("=" * 60)
        print(f"Test Completed: {datetime.now().isoformat()}")
        
        # Detailed results
        if self.test_results:
            print("\n📋 DETAILED TEST RESULTS:")
            print("-" * 40)
            for result in self.test_results:
                status = "✅" if result["success"] else "❌"
                print(f"{status} {result['test']}: {result['message']}")
                if result["details"]:
                    print(f"   Details: {result['details']}")

if __name__ == "__main__":
    tester = BackendTester()
    results = tester.run_all_tests()