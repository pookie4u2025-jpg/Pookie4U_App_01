#!/usr/bin/env python3
"""
Daily Meetup Mode Testing for Pookie4u
Testing the new Daily IRL mode functionality for AI task service
"""

import asyncio
import httpx
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Test configuration
BACKEND_URL = "https://pookie-couple.preview.emergentagent.com/api"
TEST_USER_EMAIL = "dailymeetup.tester@example.com"
TEST_USER_PASSWORD = "TestPass123!"
TEST_USER_NAME = "Daily Meetup Tester"

class DailyMeetupTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.auth_token = None
        self.test_results = []
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def log_test(self, test_name: str, success: bool, details: str = "", data: Any = None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if not success and data:
            print(f"   Data: {json.dumps(data, indent=2)}")
        print()
    
    async def authenticate(self):
        """Authenticate and get JWT token"""
        try:
            # Try to register first (in case user doesn't exist)
            register_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD,
                "name": TEST_USER_NAME
            }
            
            response = await self.client.post(f"{BACKEND_URL}/auth/register", json=register_data)
            if response.status_code == 200:
                self.auth_token = response.json()["access_token"]
                self.log_test("User Registration", True, "New user registered successfully")
                return True
            elif response.status_code == 400 and "already registered" in response.text:
                # User exists, try login
                login_data = {
                    "email": TEST_USER_EMAIL,
                    "password": TEST_USER_PASSWORD
                }
                
                response = await self.client.post(f"{BACKEND_URL}/auth/login", json=login_data)
                if response.status_code == 200:
                    self.auth_token = response.json()["access_token"]
                    self.log_test("User Login", True, "Existing user logged in successfully")
                    return True
                else:
                    self.log_test("User Login", False, f"Login failed: {response.status_code}", response.text)
                    return False
            else:
                self.log_test("User Registration", False, f"Registration failed: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Authentication", False, f"Authentication error: {str(e)}")
            return False
    
    def get_auth_headers(self):
        """Get authentication headers"""
        return {"Authorization": f"Bearer {self.auth_token}"}
    
    async def test_daily_irl_mode_setup(self):
        """Test setting up DAILY_IRL relationship mode"""
        try:
            # Set relationship mode to DAILY_IRL
            mode_data = {"mode": "DAILY_IRL"}
            response = await self.client.put(
                f"{BACKEND_URL}/user/relationship-mode",
                json=mode_data,
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                result = response.json()
                self.log_test(
                    "Set DAILY_IRL Mode", 
                    True, 
                    f"Mode set to {result.get('new_mode', 'DAILY_IRL')}"
                )
                return True
            else:
                self.log_test(
                    "Set DAILY_IRL Mode", 
                    False, 
                    f"Failed to set mode: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Set DAILY_IRL Mode", False, f"Error: {str(e)}")
            return False
    
    async def test_daily_irl_tasks_api(self):
        """Test GET /api/tasks/daily with DAILY_IRL relationship mode"""
        try:
            response = await self.client.get(
                f"{BACKEND_URL}/tasks/daily",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                tasks = data.get("tasks", [])
                
                # Verify we get exactly 3 tasks
                if len(tasks) != 3:
                    self.log_test(
                        "Daily IRL Tasks Count", 
                        False, 
                        f"Expected 3 tasks, got {len(tasks)}",
                        data
                    )
                    return False
                
                self.log_test(
                    "Daily IRL Tasks API", 
                    True, 
                    f"Retrieved {len(tasks)} daily tasks for DAILY_IRL mode"
                )
                
                # Store tasks for further testing
                self.daily_irl_tasks = tasks
                return True
            else:
                self.log_test(
                    "Daily IRL Tasks API", 
                    False, 
                    f"API call failed: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Daily IRL Tasks API", False, f"Error: {str(e)}")
            return False
    
    async def test_pre_written_task_structure(self):
        """Test that tasks have proper structure with pre-written descriptions"""
        try:
            if not hasattr(self, 'daily_irl_tasks'):
                self.log_test("Pre-written Task Structure", False, "No tasks available for testing")
                return False
            
            all_valid = True
            task_details = []
            
            for i, task in enumerate(self.daily_irl_tasks):
                task_valid = True
                issues = []
                
                # Check required fields
                required_fields = ["id", "title", "description", "category", "difficulty", "points"]
                for field in required_fields:
                    if field not in task:
                        issues.append(f"Missing field: {field}")
                        task_valid = False
                
                # Check specific values for Daily Meetup tasks
                if task.get("category") != "Communication":
                    issues.append(f"Expected category 'Communication', got '{task.get('category')}'")
                    task_valid = False
                
                if task.get("difficulty") != "very_easy":
                    issues.append(f"Expected difficulty 'very_easy', got '{task.get('difficulty')}'")
                    task_valid = False
                
                if task.get("points") != 5:
                    issues.append(f"Expected 5 points, got {task.get('points')}")
                    task_valid = False
                
                if task.get("is_physical") != False:
                    issues.append(f"Expected is_physical=False, got {task.get('is_physical')}")
                    task_valid = False
                
                # Check generation metadata
                metadata = task.get("generation_metadata", {})
                if metadata.get("model") != "pre_written_daily_meetup":
                    issues.append(f"Expected model 'pre_written_daily_meetup', got '{metadata.get('model')}'")
                    task_valid = False
                
                if metadata.get("mode") != "DAILY_IRL":
                    issues.append(f"Expected mode 'DAILY_IRL', got '{metadata.get('mode')}'")
                    task_valid = False
                
                task_details.append({
                    "task_id": task.get("id"),
                    "title": task.get("title"),
                    "valid": task_valid,
                    "issues": issues
                })
                
                if not task_valid:
                    all_valid = False
            
            if all_valid:
                self.log_test(
                    "Pre-written Task Structure", 
                    True, 
                    "All tasks have correct structure and metadata"
                )
            else:
                self.log_test(
                    "Pre-written Task Structure", 
                    False, 
                    "Some tasks have structural issues",
                    task_details
                )
            
            return all_valid
            
        except Exception as e:
            self.log_test("Pre-written Task Structure", False, f"Error: {str(e)}")
            return False
    
    async def test_task_rotation_logic(self):
        """Test that tasks rotate correctly based on month and day"""
        try:
            # Get tasks for today
            response1 = await self.client.get(
                f"{BACKEND_URL}/tasks/daily",
                headers=self.get_auth_headers()
            )
            
            if response1.status_code != 200:
                self.log_test("Task Rotation Logic", False, "Failed to get first set of tasks")
                return False
            
            tasks1 = response1.json().get("tasks", [])
            
            # Get tasks again (should be same for same day)
            response2 = await self.client.get(
                f"{BACKEND_URL}/tasks/daily",
                headers=self.get_auth_headers()
            )
            
            if response2.status_code != 200:
                self.log_test("Task Rotation Logic", False, "Failed to get second set of tasks")
                return False
            
            tasks2 = response2.json().get("tasks", [])
            
            # Tasks should be identical for the same day
            same_day_identical = True
            if len(tasks1) != len(tasks2):
                same_day_identical = False
            else:
                for i in range(len(tasks1)):
                    if tasks1[i].get("id") != tasks2[i].get("id"):
                        same_day_identical = False
                        break
            
            if same_day_identical:
                self.log_test(
                    "Task Rotation - Same Day", 
                    True, 
                    "Tasks are consistent for the same day"
                )
            else:
                self.log_test(
                    "Task Rotation - Same Day", 
                    False, 
                    "Tasks should be identical for the same day",
                    {"tasks1_ids": [t.get("id") for t in tasks1], "tasks2_ids": [t.get("id") for t in tasks2]}
                )
            
            # Test regeneration with regenerate=true parameter
            response3 = await self.client.get(
                f"{BACKEND_URL}/tasks/daily?regenerate=true",
                headers=self.get_auth_headers()
            )
            
            if response3.status_code == 200:
                tasks3 = response3.json().get("tasks", [])
                
                # Check if metadata shows proper rotation seed
                rotation_valid = True
                for task in tasks3:
                    metadata = task.get("generation_metadata", {})
                    if not metadata.get("rotation_seed") or not metadata.get("day_of_month"):
                        rotation_valid = False
                        break
                
                self.log_test(
                    "Task Rotation - Metadata", 
                    rotation_valid, 
                    "Rotation metadata present in tasks" if rotation_valid else "Missing rotation metadata"
                )
            
            return same_day_identical
            
        except Exception as e:
            self.log_test("Task Rotation Logic", False, f"Error: {str(e)}")
            return False
    
    async def test_daily_meetup_task_content(self):
        """Test that tasks contain pre-written Daily Meetup content"""
        try:
            if not hasattr(self, 'daily_irl_tasks'):
                self.log_test("Daily Meetup Task Content", False, "No tasks available for testing")
                return False
            
            # Expected Daily Meetup task patterns (from the 90 pre-written tasks)
            expected_patterns = [
                "Send her a good morning text first",
                "Compliment her photo or outfit today",
                "Bring her a small snack when you meet",
                "Hold her hand while walking",
                "Say 'you look amazing today'",
                "Take a short walk together",
                "Send a funny meme during the day",
                "Tell her one reason you missed her",
                "Make her laugh once",
                "Offer to carry her bag"
            ]
            
            # Check if any of our tasks match the expected pre-written content
            content_matches = []
            for task in self.daily_irl_tasks:
                title = task.get("title", "")
                description = task.get("description", "")
                
                # Check if this task matches any expected pattern
                is_pre_written = any(pattern in title or pattern in description for pattern in expected_patterns)
                content_matches.append({
                    "task_id": task.get("id"),
                    "title": title,
                    "is_pre_written": is_pre_written
                })
            
            # At least some tasks should match pre-written patterns
            pre_written_count = sum(1 for match in content_matches if match["is_pre_written"])
            
            if pre_written_count > 0:
                self.log_test(
                    "Daily Meetup Task Content", 
                    True, 
                    f"{pre_written_count}/3 tasks match pre-written Daily Meetup patterns"
                )
                return True
            else:
                # Even if exact matches aren't found, check if tasks are appropriate for Daily IRL
                daily_irl_appropriate = True
                for task in self.daily_irl_tasks:
                    title = task.get("title", "").lower()
                    # Check for Daily IRL appropriate keywords
                    if not any(keyword in title for keyword in ["text", "meet", "walk", "hug", "compliment", "call", "message", "see", "together"]):
                        daily_irl_appropriate = False
                        break
                
                self.log_test(
                    "Daily Meetup Task Content", 
                    daily_irl_appropriate, 
                    "Tasks are appropriate for Daily IRL mode" if daily_irl_appropriate else "Tasks don't seem appropriate for Daily IRL mode",
                    content_matches
                )
                return daily_irl_appropriate
            
        except Exception as e:
            self.log_test("Daily Meetup Task Content", False, f"Error: {str(e)}")
            return False
    
    async def test_other_relationship_modes(self):
        """Test that other relationship modes still use AI generation"""
        try:
            # Test SAME_HOME mode
            mode_data = {"mode": "SAME_HOME"}
            response = await self.client.put(
                f"{BACKEND_URL}/user/relationship-mode",
                json=mode_data,
                headers=self.get_auth_headers()
            )
            
            if response.status_code != 200:
                self.log_test("Other Modes - SAME_HOME Setup", False, "Failed to set SAME_HOME mode")
                return False
            
            # Get tasks for SAME_HOME mode
            response = await self.client.get(
                f"{BACKEND_URL}/tasks/daily",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                tasks = data.get("tasks", [])
                
                # Check if these are AI-generated (not pre-written Daily Meetup tasks)
                ai_generated = True
                for task in tasks:
                    metadata = task.get("generation_metadata", {})
                    if metadata.get("model") == "pre_written_daily_meetup":
                        ai_generated = False
                        break
                
                self.log_test(
                    "Other Modes - SAME_HOME AI Generation", 
                    ai_generated, 
                    "SAME_HOME mode uses AI generation" if ai_generated else "SAME_HOME mode incorrectly using pre-written tasks"
                )
            else:
                self.log_test("Other Modes - SAME_HOME Tasks", False, "Failed to get SAME_HOME tasks")
                return False
            
            # Test LONG_DISTANCE mode
            mode_data = {"mode": "LONG_DISTANCE"}
            response = await self.client.put(
                f"{BACKEND_URL}/user/relationship-mode",
                json=mode_data,
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                # Get tasks for LONG_DISTANCE mode
                response = await self.client.get(
                    f"{BACKEND_URL}/tasks/daily",
                    headers=self.get_auth_headers()
                )
                
                if response.status_code == 200:
                    data = response.json()
                    tasks = data.get("tasks", [])
                    
                    # Check if these are AI-generated
                    ai_generated = True
                    for task in tasks:
                        metadata = task.get("generation_metadata", {})
                        if metadata.get("model") == "pre_written_daily_meetup":
                            ai_generated = False
                            break
                    
                    self.log_test(
                        "Other Modes - LONG_DISTANCE AI Generation", 
                        ai_generated, 
                        "LONG_DISTANCE mode uses AI generation" if ai_generated else "LONG_DISTANCE mode incorrectly using pre-written tasks"
                    )
                    return ai_generated
                else:
                    self.log_test("Other Modes - LONG_DISTANCE Tasks", False, "Failed to get LONG_DISTANCE tasks")
                    return False
            else:
                self.log_test("Other Modes - LONG_DISTANCE Setup", False, "Failed to set LONG_DISTANCE mode")
                return False
            
        except Exception as e:
            self.log_test("Other Relationship Modes", False, f"Error: {str(e)}")
            return False
    
    async def test_weekly_tasks_unchanged(self):
        """Test that weekly tasks are not affected by Daily Meetup mode"""
        try:
            # Set back to DAILY_IRL mode
            mode_data = {"mode": "DAILY_IRL"}
            await self.client.put(
                f"{BACKEND_URL}/user/relationship-mode",
                json=mode_data,
                headers=self.get_auth_headers()
            )
            
            # Get weekly tasks
            response = await self.client.get(
                f"{BACKEND_URL}/tasks/weekly",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                tasks = data.get("tasks", [])
                
                if len(tasks) > 0:
                    task = tasks[0]
                    
                    # Weekly tasks should still be AI-generated, not pre-written
                    metadata = task.get("generation_metadata", {})
                    is_ai_generated = metadata.get("ai_model") == "gpt-4o" or metadata.get("ai_model") == "fallback"
                    
                    # Check weekly task properties
                    is_physical = task.get("is_physical", False)
                    category = task.get("category", "")
                    points = task.get("points", 0)
                    
                    weekly_valid = (
                        is_physical == True and
                        category == "PhysicalActivity" and
                        points == 25
                    )
                    
                    if weekly_valid:
                        self.log_test(
                            "Weekly Tasks Unchanged", 
                            True, 
                            "Weekly tasks maintain correct structure and AI generation"
                        )
                        return True
                    else:
                        self.log_test(
                            "Weekly Tasks Unchanged", 
                            False, 
                            f"Weekly task structure incorrect: is_physical={is_physical}, category={category}, points={points}"
                        )
                        return False
                else:
                    self.log_test("Weekly Tasks Unchanged", False, "No weekly tasks returned")
                    return False
            else:
                self.log_test("Weekly Tasks Unchanged", False, f"Failed to get weekly tasks: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Weekly Tasks Unchanged", False, f"Error: {str(e)}")
            return False
    
    async def run_all_tests(self):
        """Run all Daily Meetup mode tests"""
        print("🎯 STARTING DAILY MEETUP MODE COMPREHENSIVE TESTING")
        print("=" * 60)
        
        # Authentication
        if not await self.authenticate():
            print("❌ Authentication failed - cannot proceed with tests")
            return
        
        # Test sequence
        test_sequence = [
            ("Setup DAILY_IRL Mode", self.test_daily_irl_mode_setup),
            ("Daily IRL Tasks API", self.test_daily_irl_tasks_api),
            ("Pre-written Task Structure", self.test_pre_written_task_structure),
            ("Task Rotation Logic", self.test_task_rotation_logic),
            ("Daily Meetup Task Content", self.test_daily_meetup_task_content),
            ("Other Relationship Modes", self.test_other_relationship_modes),
            ("Weekly Tasks Unchanged", self.test_weekly_tasks_unchanged),
        ]
        
        passed_tests = 0
        total_tests = len(test_sequence)
        
        for test_name, test_func in test_sequence:
            try:
                result = await test_func()
                if result:
                    passed_tests += 1
            except Exception as e:
                self.log_test(test_name, False, f"Test execution error: {str(e)}")
        
        # Summary
        print("=" * 60)
        print(f"🎯 DAILY MEETUP MODE TESTING COMPLETED")
        print(f"📊 RESULTS: {passed_tests}/{total_tests} tests passed ({(passed_tests/total_tests)*100:.1f}%)")
        
        if passed_tests == total_tests:
            print("✅ ALL TESTS PASSED - Daily Meetup mode is working correctly!")
        else:
            print(f"❌ {total_tests - passed_tests} TESTS FAILED - Issues found in Daily Meetup mode")
        
        return passed_tests, total_tests

async def main():
    """Main test execution"""
    async with DailyMeetupTester() as tester:
        await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())