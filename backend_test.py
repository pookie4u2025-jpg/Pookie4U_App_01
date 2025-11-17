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
BACKEND_URL = "https://love-tasks-1.preview.emergentagent.com/api"
TEST_USER_EMAIL = f"test.user.{int(time.time())}@example.com"
TEST_USER_PASSWORD = "SecurePass123!"
TEST_USER_NAME = "Test User"

class Pookie4uAPITester:
    def __init__(self):
        # Use the production URL from frontend .env
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_user_email = TEST_USER_EMAIL
        self.test_user_password = TEST_USER_PASSWORD
        self.test_user_name = TEST_USER_NAME
        self.access_token = None
        self.user_id = None
        
        # Test results tracking
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = []
        
        print(f"🚀 Initializing Pookie4u API Tester")
        print(f"📍 Base URL: {self.base_url}")
        print(f"👤 Test User: {self.test_user_email}")
        print("=" * 80)

    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            print(f"✅ {test_name}: PASSED {details}")
        else:
            self.failed_tests.append(f"{test_name}: {details}")
            print(f"❌ {test_name}: FAILED {details}")

    def make_request(self, method: str, endpoint: str, data: Dict = None, headers: Dict = None) -> Dict[str, Any]:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        
        # Add authorization header if token exists
        if self.access_token and headers is None:
            headers = {"Authorization": f"Bearer {self.access_token}"}
        elif self.access_token and headers:
            headers["Authorization"] = f"Bearer {self.access_token}"
            
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers, timeout=10)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=headers, timeout=10)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers=headers, timeout=10)
            elif method.upper() == "PATCH":
                response = self.session.patch(url, json=data, headers=headers, timeout=10)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=headers, timeout=10)
            else:
                return {"error": f"Unsupported method: {method}"}
                
            return {
                "status_code": response.status_code,
                "data": response.json() if response.content else {},
                "headers": dict(response.headers)
            }
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
        except json.JSONDecodeError:
            return {
                "status_code": response.status_code,
                "data": response.text,
                "headers": dict(response.headers)
            }

    def test_health_endpoint(self):
        """Test deployment health check endpoint"""
        print("\n🏥 Testing Health Check Endpoint")
        
        # Health endpoint is at root level, not /api/health
        health_url = f"{self.base_url.replace('/api', '')}/health"
        
        try:
            response = self.session.get(health_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log_test("Health Check", True, f"Service healthy, database: {data.get('database', 'unknown')}")
                    return True
                else:
                    self.log_test("Health Check", False, f"Service unhealthy: {data}")
                    return False
            else:
                self.log_test("Health Check", False, f"Status {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, f"Request failed: {str(e)}")
            return False

    def test_user_registration(self):
        """Test user registration endpoint"""
        print("\n👤 Testing User Registration")
        
        # Test valid registration
        registration_data = {
            "email": self.test_user_email,
            "password": self.test_user_password,
            "name": self.test_user_name
        }
        
        response = self.make_request("POST", "/auth/register", registration_data)
        
        if "error" in response:
            self.log_test("User Registration - Valid Data", False, f"Request failed: {response['error']}")
            return False
            
        if response["status_code"] == 200:
            data = response["data"]
            if "access_token" in data:
                self.access_token = data["access_token"]
                self.log_test("User Registration - Valid Data", True, "Registration successful with token")
                
                # Test duplicate email registration
                duplicate_response = self.make_request("POST", "/auth/register", registration_data)
                if duplicate_response["status_code"] == 400:
                    self.log_test("User Registration - Duplicate Email", True, "Properly rejected duplicate email")
                else:
                    self.log_test("User Registration - Duplicate Email", False, f"Status {duplicate_response['status_code']}")
                
                return True
            else:
                self.log_test("User Registration - Valid Data", False, f"No access token in response: {data}")
                return False
        else:
            self.log_test("User Registration - Valid Data", False, f"Status {response['status_code']}: {response.get('data', {})}")
            return False

    def test_user_login(self):
        """Test user login endpoint"""
        print("\n🔐 Testing User Login")
        
        # Test valid login
        login_data = {
            "email": self.test_user_email,
            "password": self.test_user_password
        }
        
        response = self.make_request("POST", "/auth/login", login_data)
        
        if "error" in response:
            self.log_test("User Login - Valid Credentials", False, f"Request failed: {response['error']}")
            return False
            
        if response["status_code"] == 200:
            data = response["data"]
            if "access_token" in data:
                self.access_token = data["access_token"]
                self.log_test("User Login - Valid Credentials", True, "Login successful with token")
                
                # Test invalid credentials
                invalid_login = {
                    "email": self.test_user_email,
                    "password": "wrongpassword"
                }
                invalid_response = self.make_request("POST", "/auth/login", invalid_login)
                if invalid_response["status_code"] == 401:
                    self.log_test("User Login - Invalid Credentials", True, "Properly rejected invalid credentials")
                else:
                    self.log_test("User Login - Invalid Credentials", False, f"Status {invalid_response['status_code']}")
                
                return True
            else:
                self.log_test("User Login - Valid Credentials", False, f"No access token in response: {data}")
                return False
        else:
            self.log_test("User Login - Valid Credentials", False, f"Status {response['status_code']}: {response.get('data', {})}")
            return False

    def test_user_profile_endpoints(self):
        """Test user profile endpoints"""
        print("\n👤 Testing User Profile Endpoints")
        
        if not self.access_token:
            self.log_test("User Profile - Get Profile", False, "No access token available")
            return False
        
        # Test get profile
        response = self.make_request("GET", "/user/profile")
        
        if "error" in response:
            self.log_test("User Profile - Get Profile", False, f"Request failed: {response['error']}")
            return False
            
        if response["status_code"] == 200:
            data = response["data"]
            if "email" in data and "name" in data:
                self.user_id = data.get("id")
                self.log_test("User Profile - Get Profile", True, f"Profile retrieved: {data.get('name')} ({data.get('email')})")
                
                # Test update profile
                update_data = {
                    "name": "Updated Test User",
                    "email": self.test_user_email
                }
                
                update_response = self.make_request("PUT", "/user/profile", update_data)
                if update_response["status_code"] == 200:
                    self.log_test("User Profile - Update Profile", True, "Profile updated successfully")
                else:
                    self.log_test("User Profile - Update Profile", False, f"Status {update_response['status_code']}")
                
                # Test update partner profile
                partner_data = {
                    "name": "Test Partner",
                    "birthday": "15/06/1995",
                    "anniversary": "14/02/2020",
                    "favorite_color": "Blue",
                    "favorite_food": "Pizza"
                }
                
                partner_response = self.make_request("PUT", "/user/partner-profile", partner_data)
                if partner_response["status_code"] == 200:
                    self.log_test("User Profile - Update Partner Profile", True, "Partner profile updated successfully")
                else:
                    self.log_test("User Profile - Update Partner Profile", False, f"Status {partner_response['status_code']}")
                
                return True
            else:
                self.log_test("User Profile - Get Profile", False, f"Missing required fields in response: {data}")
                return False
        elif response["status_code"] == 401 or response["status_code"] == 403:
            self.log_test("User Profile - Get Profile", False, "Authentication failed - token may be invalid")
            return False
        else:
            self.log_test("User Profile - Get Profile", False, f"Status {response['status_code']}: {response.get('data', {})}")
            return False

    def test_task_management_endpoints(self):
        """Test task management endpoints"""
        print("\n📋 Testing Task Management Endpoints")
        
        if not self.access_token:
            self.log_test("Task Management", False, "No access token available")
            return False
        
        # Test get daily tasks
        daily_response = self.make_request("GET", "/tasks/daily")
        
        if "error" in daily_response:
            self.log_test("Task Management - Get Daily Tasks", False, f"Request failed: {daily_response['error']}")
        elif daily_response["status_code"] == 200:
            daily_data = daily_response["data"]
            # Handle the actual response format which has 'tasks' array
            if isinstance(daily_data, dict) and "tasks" in daily_data:
                tasks = daily_data["tasks"]
                if isinstance(tasks, list) and len(tasks) > 0:
                    self.log_test("Task Management - Get Daily Tasks", True, f"Retrieved {len(tasks)} daily tasks")
                    
                    # Test task completion with first task
                    first_task = tasks[0]
                    task_id = first_task.get("id")
                    
                    if task_id:
                        complete_data = {"task_id": task_id}
                        complete_response = self.make_request("POST", "/tasks/complete", complete_data)
                        
                        if complete_response["status_code"] == 200:
                            complete_result = complete_response["data"]
                            if complete_result.get("success") and "points_earned" in complete_result:
                                self.log_test("Task Management - Complete Task", True, 
                                            f"Task completed, earned {complete_result['points_earned']} points")
                            else:
                                self.log_test("Task Management - Complete Task", False, f"Unexpected response: {complete_result}")
                        else:
                            self.log_test("Task Management - Complete Task", False, f"Status {complete_response['status_code']}")
                    else:
                        self.log_test("Task Management - Complete Task", False, "No task ID found in daily tasks")
                else:
                    self.log_test("Task Management - Get Daily Tasks", False, f"No tasks in response: {tasks}")
            else:
                self.log_test("Task Management - Get Daily Tasks", False, f"Unexpected response format: {daily_data}")
        else:
            self.log_test("Task Management - Get Daily Tasks", False, f"Status {daily_response['status_code']}")
        
        # Test get weekly tasks
        weekly_response = self.make_request("GET", "/tasks/weekly")
        
        if "error" in weekly_response:
            self.log_test("Task Management - Get Weekly Tasks", False, f"Request failed: {weekly_response['error']}")
        elif weekly_response["status_code"] == 200:
            weekly_data = weekly_response["data"]
            # Handle the actual response format which has 'tasks' array
            if isinstance(weekly_data, dict) and "tasks" in weekly_data:
                tasks = weekly_data["tasks"]
                if isinstance(tasks, list) and len(tasks) > 0:
                    self.log_test("Task Management - Get Weekly Tasks", True, f"Retrieved {len(tasks)} weekly tasks")
                else:
                    self.log_test("Task Management - Get Weekly Tasks", False, f"No weekly tasks in response: {tasks}")
            else:
                self.log_test("Task Management - Get Weekly Tasks", False, f"Unexpected response format: {weekly_data}")
        else:
            self.log_test("Task Management - Get Weekly Tasks", False, f"Status {weekly_response['status_code']}")
        
        # Test task regeneration
        regen_response = self.make_request("POST", "/tasks/regenerate")
        
        if "error" in regen_response:
            self.log_test("Task Management - Regenerate Tasks", False, f"Request failed: {regen_response['error']}")
        elif regen_response["status_code"] == 200:
            self.log_test("Task Management - Regenerate Tasks", True, "Tasks regenerated successfully")
        else:
            self.log_test("Task Management - Regenerate Tasks", False, f"Status {regen_response['status_code']}")

    def test_events_endpoints(self):
        """Test events endpoints"""
        print("\n📅 Testing Events Endpoints")
        
        if not self.access_token:
            self.log_test("Events", False, "No access token available")
            return False
        
        # Test get events
        events_response = self.make_request("GET", "/events")
        
        if "error" in events_response:
            self.log_test("Events - Get Events", False, f"Request failed: {events_response['error']}")
            return False
        elif events_response["status_code"] == 200:
            events_data = events_response["data"]
            # Handle the actual response format which has 'events' array
            if isinstance(events_data, dict) and "events" in events_data:
                events = events_data["events"]
                if isinstance(events, list):
                    self.log_test("Events - Get Events", True, f"Retrieved {len(events)} events")
                else:
                    self.log_test("Events - Get Events", False, f"Events not a list: {events}")
                    return False
            elif isinstance(events_data, list):
                # Fallback for direct array response
                self.log_test("Events - Get Events", True, f"Retrieved {len(events_data)} events")
            else:
                self.log_test("Events - Get Events", False, f"Unexpected response format: {events_data}")
                return False
        else:
            self.log_test("Events - Get Events", False, f"Status {events_response['status_code']}")
            return False
        
        # Test create custom event
        event_data = {
            "name": "Test Anniversary",
            "date": (datetime.now() + timedelta(days=30)).isoformat(),
            "description": "Test event for API testing",
            "importance": "high"
        }
        
        create_response = self.make_request("POST", "/events/custom", event_data)
        
        if "error" in create_response:
            self.log_test("Events - Create Event", False, f"Request failed: {create_response['error']}")
            return False
        elif create_response["status_code"] == 200:
            create_result = create_response["data"]
            if "event" in create_result and "id" in create_result["event"]:
                event_id = create_result["event"]["id"]
                self.log_test("Events - Create Event", True, f"Event created with ID: {event_id}")
                
                # Test delete event
                delete_response = self.make_request("DELETE", f"/events/custom/{event_id}")
                
                if delete_response["status_code"] == 200:
                    self.log_test("Events - Delete Event", True, "Event deleted successfully")
                else:
                    self.log_test("Events - Delete Event", False, f"Status {delete_response['status_code']}")
            else:
                self.log_test("Events - Create Event", False, f"No event ID in response: {create_result}")
        else:
            self.log_test("Events - Create Event", False, f"Status {create_response['status_code']}")

    def test_gamification_system(self):
        """Test gamification features (points, streaks, levels)"""
        print("\n🎮 Testing Gamification System")
        
        if not self.access_token:
            self.log_test("Gamification", False, "No access token available")
            return False
        
        # Get initial profile state
        initial_response = self.make_request("GET", "/user/profile")
        
        if initial_response["status_code"] != 200:
            self.log_test("Gamification - Get Initial State", False, f"Status {initial_response['status_code']}")
            return False
        
        initial_data = initial_response["data"]
        initial_points = initial_data.get("total_points", 0)
        initial_level = initial_data.get("current_level", 1)
        initial_streak = initial_data.get("current_streak", 0)
        initial_tasks_completed = initial_data.get("tasks_completed", 0)
        
        self.log_test("Gamification - Get Initial State", True, 
                     f"Points: {initial_points}, Level: {initial_level}, Streak: {initial_streak}, Tasks: {initial_tasks_completed}")
        
        # Get daily tasks and complete one to test point system
        tasks_response = self.make_request("GET", "/tasks/daily")
        
        if tasks_response["status_code"] == 200:
            tasks_data = tasks_response["data"]
            # Handle the actual response format which has 'tasks' array
            if isinstance(tasks_data, dict) and "tasks" in tasks_data:
                tasks = tasks_data["tasks"]
                if isinstance(tasks, list) and len(tasks) > 0:
                    # Find an uncompleted task
                    uncompleted_task = None
                    for task in tasks:
                        if not task.get("completed", False):
                            uncompleted_task = task
                            break
                else:
                    self.log_test("Gamification - Get Tasks for Testing", False, "No tasks in response")
                    return
            else:
                self.log_test("Gamification - Get Tasks for Testing", False, "Unexpected response format")
                return
            
            if uncompleted_task:
                task_id = uncompleted_task.get("id")
                expected_points = uncompleted_task.get("points", 5)
                
                # Complete the task
                complete_response = self.make_request("POST", "/tasks/complete", {"task_id": task_id})
                
                if complete_response["status_code"] == 200:
                    complete_result = complete_response["data"]
                    points_earned = complete_result.get("points_earned", 0)
                    
                    if points_earned == expected_points:
                        self.log_test("Gamification - Points Award", True, f"Correctly awarded {points_earned} points")
                        
                        # Check updated profile
                        updated_response = self.make_request("GET", "/user/profile")
                        if updated_response["status_code"] == 200:
                            updated_data = updated_response["data"]
                            new_points = updated_data.get("total_points", 0)
                            new_level = updated_data.get("current_level", 1)
                            new_streak = updated_data.get("current_streak", 0)
                            new_tasks_completed = updated_data.get("tasks_completed", 0)
                            
                            # Verify points increased
                            if new_points >= initial_points + points_earned:
                                self.log_test("Gamification - Points Persistence", True, 
                                            f"Points updated: {initial_points} → {new_points}")
                            else:
                                self.log_test("Gamification - Points Persistence", False, 
                                            f"Points not updated correctly: {initial_points} → {new_points}")
                            
                            # Verify level calculation (level = points/100 + 1)
                            expected_level = (new_points // 100) + 1
                            if new_level == expected_level:
                                self.log_test("Gamification - Level Calculation", True, 
                                            f"Level correctly calculated: {new_level}")
                            else:
                                self.log_test("Gamification - Level Calculation", False, 
                                            f"Level incorrect: expected {expected_level}, got {new_level}")
                            
                            # Verify task count increased
                            if new_tasks_completed > initial_tasks_completed:
                                self.log_test("Gamification - Task Count", True, 
                                            f"Task count updated: {initial_tasks_completed} → {new_tasks_completed}")
                            else:
                                self.log_test("Gamification - Task Count", False, 
                                            f"Task count not updated: {initial_tasks_completed} → {new_tasks_completed}")
                            
                            # Streak verification (should be at least 1 after completing a task)
                            if new_streak >= 1:
                                self.log_test("Gamification - Streak Tracking", True, 
                                            f"Streak maintained/increased: {initial_streak} → {new_streak}")
                            else:
                                self.log_test("Gamification - Streak Tracking", False, 
                                            f"Streak not working: {initial_streak} → {new_streak}")
                        else:
                            self.log_test("Gamification - Profile Update Check", False, "Could not fetch updated profile")
                    else:
                        self.log_test("Gamification - Points Award", False, 
                                    f"Incorrect points: expected {expected_points}, got {points_earned}")
                else:
                    self.log_test("Gamification - Task Completion", False, f"Status {complete_response['status_code']}")
            else:
                self.log_test("Gamification - Find Uncompleted Task", False, "No uncompleted tasks available")
        else:
            self.log_test("Gamification - Get Tasks for Testing", False, "Could not retrieve daily tasks")

    def test_authentication_edge_cases(self):
        """Test authentication edge cases and error handling"""
        print("\n🔒 Testing Authentication Edge Cases")
        
        # Test missing fields in registration
        invalid_registration_cases = [
            ({}, "Empty body"),
            ({"email": self.test_user_email}, "Missing password and name"),
            ({"password": "test123"}, "Missing email and name"),
            ({"name": "Test"}, "Missing email and password"),
            ({"email": "invalid-email", "password": "test123", "name": "Test"}, "Invalid email format")
        ]
        
        for case_data, case_name in invalid_registration_cases:
            response = self.make_request("POST", "/auth/register", case_data)
            if response["status_code"] == 422 or response["status_code"] == 400:
                self.log_test(f"Auth Edge Case - {case_name}", True, f"Properly rejected with status {response['status_code']}")
            else:
                self.log_test(f"Auth Edge Case - {case_name}", False, f"Status {response['status_code']}")
        
        # Test unauthorized access
        old_token = self.access_token
        self.access_token = "invalid_token"
        
        unauthorized_response = self.make_request("GET", "/user/profile")
        if unauthorized_response["status_code"] == 401 or unauthorized_response["status_code"] == 403:
            self.log_test("Auth Edge Case - Invalid Token", True, "Properly rejected invalid token")
        else:
            self.log_test("Auth Edge Case - Invalid Token", False, f"Status {unauthorized_response['status_code']}")
        
        # Restore valid token
        self.access_token = old_token

    def run_comprehensive_test_suite(self):
        """Run all tests in sequence"""
        print("🧪 Starting Comprehensive Backend API Testing for Production Readiness")
        print("=" * 80)
        
        start_time = time.time()
        
        # Core functionality tests
        self.test_health_endpoint()
        self.test_user_registration()
        self.test_user_login()
        self.test_user_profile_endpoints()
        self.test_task_management_endpoints()
        self.test_events_endpoints()
        self.test_gamification_system()
        self.test_authentication_edge_cases()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Print comprehensive summary
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE TEST RESULTS SUMMARY")
        print("=" * 80)
        print(f"⏱️  Total Test Duration: {duration:.2f} seconds")
        print(f"📈 Total Tests Run: {self.total_tests}")
        print(f"✅ Tests Passed: {self.passed_tests}")
        print(f"❌ Tests Failed: {len(self.failed_tests)}")
        print(f"📊 Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        
        if self.failed_tests:
            print("\n❌ FAILED TESTS:")
            for i, failure in enumerate(self.failed_tests, 1):
                print(f"   {i}. {failure}")
        
        print("\n🎯 PRODUCTION READINESS ASSESSMENT:")
        success_rate = (self.passed_tests/self.total_tests*100)
        
        if success_rate >= 95:
            print("🟢 EXCELLENT: System is production-ready with excellent reliability")
        elif success_rate >= 90:
            print("🟡 GOOD: System is mostly production-ready with minor issues")
        elif success_rate >= 80:
            print("🟠 FAIR: System needs attention before production deployment")
        else:
            print("🔴 POOR: System requires significant fixes before production")
        
        print("=" * 80)
        
        return {
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": len(self.failed_tests),
            "success_rate": success_rate,
            "duration": duration,
            "failures": self.failed_tests
        }

if __name__ == "__main__":
    tester = Pookie4uAPITester()
    results = tester.run_comprehensive_test_suite()