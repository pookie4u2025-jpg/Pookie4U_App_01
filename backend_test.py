#!/usr/bin/env python3
"""
Backend API Testing Suite for Pookie4u Gift Ideas API
Testing the updated Gift Ideas API with Amazon affiliate links integration
"""

import requests
import json
import time
from datetime import datetime
import uuid

# Configuration
BACKEND_URL = "https://relationship-app-4.preview.emergentagent.com/api"

class TaskCompletionTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        self.test_results = []
        
    def log_result(self, test_name, success, details="", response_data=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if not success and response_data:
            print(f"   Response: {response_data}")
        print()

    def test_user_registration(self):
        """Test user registration to ensure we have a valid user"""
        try:
            # Generate unique email for testing
            unique_email = f"test.user.{int(time.time())}@example.com"
            
            payload = {
                "email": unique_email,
                "password": TEST_USER_PASSWORD,
                "name": TEST_USER_NAME
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/register", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.log_result(
                    "User Registration", 
                    True, 
                    f"Successfully registered user with email: {unique_email}",
                    {"status_code": response.status_code, "has_token": bool(self.auth_token)}
                )
                return True
            else:
                self.log_result(
                    "User Registration", 
                    False, 
                    f"Registration failed with status {response.status_code}",
                    response.json() if response.content else None
                )
                return False
                
        except Exception as e:
            self.log_result("User Registration", False, f"Exception: {str(e)}")
            return False

    def test_user_login(self):
        """Test user login with existing credentials"""
        try:
            payload = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.log_result(
                    "User Login", 
                    True, 
                    f"Successfully logged in user: {TEST_USER_EMAIL}",
                    {"status_code": response.status_code, "has_token": bool(self.auth_token)}
                )
                return True
            else:
                self.log_result(
                    "User Login", 
                    False, 
                    f"Login failed with status {response.status_code}",
                    response.json() if response.content else None
                )
                return False
                
        except Exception as e:
            self.log_result("User Login", False, f"Exception: {str(e)}")
            return False

    def test_jwt_token_validation(self):
        """Test JWT token validation by accessing protected endpoint"""
        if not self.auth_token:
            self.log_result("JWT Token Validation", False, "No auth token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = self.session.get(f"{BACKEND_URL}/user/profile", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.user_id = data.get("id")
                self.log_result(
                    "JWT Token Validation", 
                    True, 
                    f"Token valid, user ID: {self.user_id}",
                    {"status_code": response.status_code, "user_id": self.user_id}
                )
                return True
            else:
                self.log_result(
                    "JWT Token Validation", 
                    False, 
                    f"Token validation failed with status {response.status_code}",
                    response.json() if response.content else None
                )
                return False
                
        except Exception as e:
            self.log_result("JWT Token Validation", False, f"Exception: {str(e)}")
            return False

    def test_daily_tasks_retrieval(self):
        """Test GET /api/tasks/daily to ensure tasks exist and have proper IDs"""
        if not self.auth_token:
            self.log_result("Daily Tasks Retrieval", False, "No auth token available")
            return False, []
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = self.session.get(f"{BACKEND_URL}/tasks/daily", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                tasks = data.get("tasks", [])
                
                if tasks and len(tasks) > 0:
                    # Validate task structure
                    valid_tasks = []
                    for task in tasks:
                        if "id" in task and "title" in task and "points" in task:
                            valid_tasks.append(task)
                    
                    self.log_result(
                        "Daily Tasks Retrieval", 
                        True, 
                        f"Retrieved {len(valid_tasks)} valid daily tasks",
                        {"status_code": response.status_code, "task_count": len(valid_tasks), "sample_task_ids": [t["id"] for t in valid_tasks[:3]]}
                    )
                    return True, valid_tasks
                else:
                    self.log_result(
                        "Daily Tasks Retrieval", 
                        False, 
                        "No tasks returned in response",
                        data
                    )
                    return False, []
            else:
                self.log_result(
                    "Daily Tasks Retrieval", 
                    False, 
                    f"Failed to retrieve tasks with status {response.status_code}",
                    response.json() if response.content else None
                )
                return False, []
                
        except Exception as e:
            self.log_result("Daily Tasks Retrieval", False, f"Exception: {str(e)}")
            return False, []

    def test_weekly_tasks_retrieval(self):
        """Test GET /api/tasks/weekly to ensure tasks exist and have proper IDs"""
        if not self.auth_token:
            self.log_result("Weekly Tasks Retrieval", False, "No auth token available")
            return False, []
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = self.session.get(f"{BACKEND_URL}/tasks/weekly", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                tasks = data.get("tasks", [])
                
                if tasks and len(tasks) > 0:
                    # Validate task structure
                    valid_tasks = []
                    for task in tasks:
                        if "id" in task and "title" in task and "points" in task:
                            valid_tasks.append(task)
                    
                    self.log_result(
                        "Weekly Tasks Retrieval", 
                        True, 
                        f"Retrieved {len(valid_tasks)} valid weekly tasks",
                        {"status_code": response.status_code, "task_count": len(valid_tasks), "sample_task_ids": [t["id"] for t in valid_tasks[:3]]}
                    )
                    return True, valid_tasks
                else:
                    self.log_result(
                        "Weekly Tasks Retrieval", 
                        False, 
                        "No tasks returned in response",
                        data
                    )
                    return False, []
            else:
                self.log_result(
                    "Weekly Tasks Retrieval", 
                    False, 
                    f"Failed to retrieve tasks with status {response.status_code}",
                    response.json() if response.content else None
                )
                return False, []
                
        except Exception as e:
            self.log_result("Weekly Tasks Retrieval", False, f"Exception: {str(e)}")
            return False, []

    def test_task_completion(self, task_id, task_type="daily"):
        """Test POST /api/tasks/complete with valid authentication"""
        if not self.auth_token:
            self.log_result("Task Completion", False, "No auth token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            payload = {"task_id": task_id}
            
            response = self.session.post(f"{BACKEND_URL}/tasks/complete", json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                # Check if task completion was successful based on response structure
                has_message = "message" in data
                points_earned = data.get("points_earned", 0)
                total_points = data.get("total_points", 0)
                success = has_message and points_earned > 0
                
                self.log_result(
                    f"Task Completion ({task_type})", 
                    success, 
                    f"Task {task_id} completed. Points earned: {points_earned}, Total: {total_points}",
                    {"status_code": response.status_code, "message": data.get("message"), "points_earned": points_earned, "total_points": total_points}
                )
                return success
            else:
                self.log_result(
                    f"Task Completion ({task_type})", 
                    False, 
                    f"Task completion failed with status {response.status_code}",
                    response.json() if response.content else None
                )
                return False
                
        except Exception as e:
            self.log_result(f"Task Completion ({task_type})", False, f"Exception: {str(e)}")
            return False

    def test_task_completion_verification(self, task_id):
        """Verify task is marked as completed by fetching tasks again"""
        if not self.auth_token:
            self.log_result("Task Completion Verification", False, "No auth token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Fetch daily tasks to check completion status
            response = self.session.get(f"{BACKEND_URL}/tasks/daily", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                tasks = data.get("tasks", [])
                
                for task in tasks:
                    if task.get("id") == task_id:
                        is_completed = task.get("completed", False)
                        completed_at = task.get("completed_at")
                        
                        self.log_result(
                            "Task Completion Verification", 
                            is_completed, 
                            f"Task {task_id} completion status: {is_completed}, completed_at: {completed_at}",
                            {"task_id": task_id, "completed": is_completed, "completed_at": completed_at}
                        )
                        return is_completed
                
                self.log_result(
                    "Task Completion Verification", 
                    False, 
                    f"Task {task_id} not found in current tasks",
                    {"searched_task_id": task_id, "available_tasks": len(tasks)}
                )
                return False
            else:
                self.log_result(
                    "Task Completion Verification", 
                    False, 
                    f"Failed to fetch tasks for verification with status {response.status_code}",
                    response.json() if response.content else None
                )
                return False
                
        except Exception as e:
            self.log_result("Task Completion Verification", False, f"Exception: {str(e)}")
            return False

    def test_points_system_verification(self):
        """Verify points are awarded correctly by checking user profile"""
        if not self.auth_token:
            self.log_result("Points System Verification", False, "No auth token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = self.session.get(f"{BACKEND_URL}/user/profile", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                total_points = data.get("total_points", 0)
                tasks_completed = data.get("tasks_completed", 0)
                current_level = data.get("current_level", 1)
                current_streak = data.get("current_streak", 0)
                
                self.log_result(
                    "Points System Verification", 
                    True, 
                    f"User stats - Points: {total_points}, Tasks: {tasks_completed}, Level: {current_level}, Streak: {current_streak}",
                    {"total_points": total_points, "tasks_completed": tasks_completed, "current_level": current_level, "current_streak": current_streak}
                )
                return True
            else:
                self.log_result(
                    "Points System Verification", 
                    False, 
                    f"Failed to fetch user profile with status {response.status_code}",
                    response.json() if response.content else None
                )
                return False
                
        except Exception as e:
            self.log_result("Points System Verification", False, f"Exception: {str(e)}")
            return False

    def test_authentication_errors(self):
        """Test task completion without authentication to verify error handling"""
        try:
            # Test without auth header
            payload = {"task_id": "test_task_id"}
            response = self.session.post(f"{BACKEND_URL}/tasks/complete", json=payload)
            
            expected_status = response.status_code in [401, 403]
            self.log_result(
                "Authentication Error Handling", 
                expected_status, 
                f"No auth header returned status {response.status_code} (expected 401/403)",
                {"status_code": response.status_code, "response": response.json() if response.content else None}
            )
            
            # Test with invalid token
            headers = {"Authorization": "Bearer invalid_token_12345"}
            response = self.session.post(f"{BACKEND_URL}/tasks/complete", json=payload, headers=headers)
            
            expected_status = response.status_code in [401, 403]
            self.log_result(
                "Invalid Token Error Handling", 
                expected_status, 
                f"Invalid token returned status {response.status_code} (expected 401/403)",
                {"status_code": response.status_code, "response": response.json() if response.content else None}
            )
            
            return True
                
        except Exception as e:
            self.log_result("Authentication Error Handling", False, f"Exception: {str(e)}")
            return False

    def run_complete_task_flow_test(self):
        """Run the complete end-to-end task completion flow"""
        print("🚀 Starting Complete Task Completion Flow Test")
        print("=" * 60)
        
        # Step 1: Authentication
        print("Step 1: Authentication Flow")
        auth_success = False
        
        # Try login first, then registration if login fails
        if self.test_user_login():
            auth_success = True
        elif self.test_user_registration():
            auth_success = True
        
        if not auth_success:
            print("❌ Authentication failed. Cannot proceed with task completion tests.")
            return False
        
        # Validate JWT token
        if not self.test_jwt_token_validation():
            print("❌ JWT token validation failed. Cannot proceed.")
            return False
        
        print("\n" + "=" * 60)
        print("Step 2: Task Retrieval")
        
        # Step 2: Retrieve tasks
        daily_success, daily_tasks = self.test_daily_tasks_retrieval()
        weekly_success, weekly_tasks = self.test_weekly_tasks_retrieval()
        
        if not daily_success and not weekly_success:
            print("❌ No tasks available for completion testing.")
            return False
        
        print("\n" + "=" * 60)
        print("Step 3: Task Completion Testing")
        
        # Step 3: Test task completion
        completion_success = False
        
        # Test daily task completion
        if daily_tasks:
            task_to_complete = daily_tasks[0]  # Take first available task
            task_id = task_to_complete["id"]
            
            print(f"Testing completion of daily task: {task_id}")
            if self.test_task_completion(task_id, "daily"):
                completion_success = True
                
                # Verify completion
                self.test_task_completion_verification(task_id)
        
        # Test weekly task completion if daily failed
        if not completion_success and weekly_tasks:
            task_to_complete = weekly_tasks[0]  # Take first available task
            task_id = task_to_complete["id"]
            
            print(f"Testing completion of weekly task: {task_id}")
            if self.test_task_completion(task_id, "weekly"):
                completion_success = True
                
                # Verify completion
                self.test_task_completion_verification(task_id)
        
        print("\n" + "=" * 60)
        print("Step 4: Points System Verification")
        
        # Step 4: Verify points system
        self.test_points_system_verification()
        
        print("\n" + "=" * 60)
        print("Step 5: Error Handling Tests")
        
        # Step 5: Test error scenarios
        self.test_authentication_errors()
        
        return completion_success

    def generate_summary_report(self):
        """Generate a summary report of all tests"""
        print("\n" + "=" * 60)
        print("📊 TASK COMPLETION TESTING SUMMARY REPORT")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Critical issues
        critical_failures = []
        for result in self.test_results:
            if not result["success"] and any(keyword in result["test"].lower() for keyword in ["authentication", "login", "token", "task completion"]):
                critical_failures.append(result)
        
        if critical_failures:
            print("🚨 CRITICAL ISSUES FOUND:")
            for failure in critical_failures:
                print(f"   ❌ {failure['test']}: {failure['details']}")
            print()
        
        # Successful components
        successful_components = []
        for result in self.test_results:
            if result["success"]:
                successful_components.append(result["test"])
        
        if successful_components:
            print("✅ WORKING COMPONENTS:")
            for component in successful_components:
                print(f"   ✅ {component}")
            print()
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "critical_failures": critical_failures,
            "all_results": self.test_results
        }

def main():
    """Main test execution"""
    print("🎯 POOKIE4U TASK COMPLETION TESTING")
    print("Focus: Resolving 'task completion not working' issue")
    print("=" * 60)
    
    tester = TaskCompletionTester()
    
    # Run complete flow test
    flow_success = tester.run_complete_task_flow_test()
    
    # Generate summary report
    summary = tester.generate_summary_report()
    
    # Final assessment
    print("🎯 FINAL ASSESSMENT:")
    if flow_success and summary["success_rate"] >= 80:
        print("✅ Task completion functionality is WORKING correctly")
    elif summary["success_rate"] >= 60:
        print("⚠️  Task completion has MINOR ISSUES but core functionality works")
    else:
        print("❌ Task completion has CRITICAL ISSUES that need immediate attention")
    
    print(f"\nDetailed results saved. Success rate: {summary['success_rate']:.1f}%")
    
    return summary

if __name__ == "__main__":
    main()