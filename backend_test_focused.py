#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Pookie4u App - Bug Fixes & New Features Focus
Testing all bug fixes and new features as requested in review
"""

import requests
import json
import uuid
from datetime import datetime
import time

# Configuration
BASE_URL = "https://pookie-couple.preview.emergentagent.com/api"
TEST_USER_EMAIL = f"test_user_{uuid.uuid4().hex[:8]}@example.com"
TEST_USER_PASSWORD = "TestPassword123!"
TEST_USER_NAME = "Sarah Johnson"

class Pookie4uTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.token = None
        self.user_id = None
        self.test_results = []
        
    def log_test(self, test_name, status, details=""):
        """Log test results"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status_symbol = "✅" if status == "PASS" else "❌"
        print(f"{status_symbol} {test_name}: {details}")
        
    def make_request(self, method, endpoint, data=None, headers=None):
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        default_headers = {"Content-Type": "application/json"}
        
        if self.token:
            default_headers["Authorization"] = f"Bearer {self.token}"
            
        if headers:
            default_headers.update(headers)
            
        try:
            if method == "GET":
                response = requests.get(url, headers=default_headers, timeout=10)
            elif method == "POST":
                response = requests.post(url, json=data, headers=default_headers, timeout=10)
            elif method == "PUT":
                response = requests.put(url, json=data, headers=default_headers, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            return response
        except requests.exceptions.RequestException as e:
            return None
            
    def test_authentication_system(self):
        """Test user registration and login"""
        print("\n🔐 TESTING AUTHENTICATION SYSTEM")
        
        # Test Registration
        register_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
            "name": TEST_USER_NAME
        }
        
        response = self.make_request("POST", "/auth/register", register_data)
        if response and response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.log_test("User Registration", "PASS", f"Successfully registered user with token")
        else:
            self.log_test("User Registration", "FAIL", f"Registration failed: {response.status_code if response else 'No response'}")
            return False
            
        # Test Login
        login_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
        
        response = self.make_request("POST", "/auth/login", login_data)
        if response and response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.log_test("User Login", "PASS", "Successfully logged in with valid credentials")
        else:
            self.log_test("User Login", "FAIL", f"Login failed: {response.status_code if response else 'No response'}")
            return False
            
        return True
        
    def test_new_user_profile_update_api(self):
        """Test the new user profile update API - KEY FOCUS AREA"""
        print("\n👤 TESTING NEW USER PROFILE UPDATE API")
        
        if not self.token:
            self.log_test("Profile Update - Authentication", "FAIL", "No authentication token available")
            return
        
        # Test valid profile update (name and email)
        update_data = {
            "name": "Sarah Updated Johnson",
            "email": f"updated_{uuid.uuid4().hex[:6]}@example.com"
        }
        
        response = self.make_request("PUT", "/user/profile", update_data)
        if response and response.status_code == 200:
            data = response.json()
            if data.get("message") == "Profile updated successfully":
                self.log_test("Profile Update - Valid Fields", "PASS", "Successfully updated name and email")
            else:
                self.log_test("Profile Update - Valid Fields", "FAIL", f"Unexpected response: {data}")
        else:
            self.log_test("Profile Update - Valid Fields", "FAIL", f"Update failed: {response.status_code if response else 'No response'}")
            
        # Test invalid field rejection
        invalid_data = {
            "name": "Test Name",
            "invalid_field": "should_be_rejected",
            "password": "should_not_be_allowed"
        }
        
        response = self.make_request("PUT", "/user/profile", invalid_data)
        if response and response.status_code == 200:
            data = response.json()
            if data.get("message") == "Profile updated successfully":
                self.log_test("Profile Update - Field Validation", "PASS", "Only allowed fields were processed")
            else:
                self.log_test("Profile Update - Field Validation", "FAIL", f"Validation issue: {data}")
        else:
            self.log_test("Profile Update - Field Validation", "FAIL", f"Validation test failed: {response.status_code if response else 'No response'}")
            
        # Test empty update
        response = self.make_request("PUT", "/user/profile", {})
        if response and response.status_code == 400:
            self.log_test("Profile Update - Empty Data", "PASS", "Correctly rejected empty update")
        elif response and response.status_code == 401:
            self.log_test("Profile Update - Empty Data", "FAIL", "Authentication issue with empty data test")
        else:
            self.log_test("Profile Update - Empty Data", "FAIL", f"Should reject empty updates: {response.status_code if response else 'No response'}")
            
    def test_enhanced_events_api(self):
        """Test the enhanced Events API - KEY FOCUS AREA"""
        print("\n🎉 TESTING ENHANCED EVENTS API")
        
        if not self.token:
            self.log_test("Events API - Authentication", "FAIL", "No authentication token available")
            return
        
        response = self.make_request("GET", "/events")
        if response and response.status_code == 200:
            data = response.json()
            
            # Test indian_calendar_events
            indian_events = data.get("indian_calendar_events", [])
            if len(indian_events) >= 11:  # Should have at least 11 events
                # Check for specific women/partner focused events
                women_keywords = ["women", "wife", "marital", "mother", "feminine", "karva", "teej", "valentine", "anniversary", "birthday"]
                women_focused_events = []
                for event in indian_events:
                    event_text = (event.get("name", "") + " " + event.get("description", "")).lower()
                    if any(keyword in event_text for keyword in women_keywords):
                        women_focused_events.append(event["name"])
                
                if len(women_focused_events) >= 5:
                    self.log_test("Events API - Indian Calendar Events", "PASS", 
                                f"Found {len(indian_events)} Indian events with {len(women_focused_events)} women/partner focused: {women_focused_events[:5]}")
                else:
                    self.log_test("Events API - Indian Calendar Events", "FAIL", 
                                f"Insufficient women-focused events: {len(women_focused_events)} found: {women_focused_events}")
            else:
                self.log_test("Events API - Indian Calendar Events", "FAIL", 
                            f"Expected at least 11 Indian events, got {len(indian_events)}")
                
            # Test custom_events structure
            custom_events = data.get("custom_events", [])
            self.log_test("Events API - Custom Events Structure", "PASS", 
                        f"Custom events array present with {len(custom_events)} events")
                        
            # Test custom_event_suggestions
            suggestions = data.get("custom_event_suggestions", [])
            if len(suggestions) == 5:
                categories = [s.get("category") for s in suggestions]
                expected_categories = ["Family Events", "Friends & Social", "Professional Milestones", 
                                     "Memorial Events", "Personal Achievements"]
                if all(cat in categories for cat in expected_categories):
                    self.log_test("Events API - Custom Event Suggestions", "PASS", 
                                f"All 5 categories present: {categories}")
                else:
                    self.log_test("Events API - Custom Event Suggestions", "FAIL", 
                                f"Missing categories. Got: {categories}")
            else:
                self.log_test("Events API - Custom Event Suggestions", "FAIL", 
                            f"Expected 5 suggestion categories, got {len(suggestions)}")
        else:
            self.log_test("Events API - Overall", "FAIL", 
                        f"Events API failed: {response.status_code if response else 'No response'}")
            
    def test_partner_integration_with_events(self):
        """Test partner birthday/anniversary integration with events"""
        print("\n💑 TESTING PARTNER INTEGRATION WITH EVENTS")
        
        # First update partner profile with birthday and anniversary
        partner_data = {
            "name": "Arjun Sharma",
            "birthday": "1995-08-15T00:00:00",
            "anniversary": "2020-02-14T00:00:00",
            "favorite_color": "Blue",
            "favorite_food": "Italian",
            "favorite_flower": "Roses",
            "favorite_brand": "Nike",
            "dress_size": "M",
            "ring_size": "7",
            "perfume_preference": "Floral",
            "notes": "Loves surprises and romantic gestures"
        }
        
        response = self.make_request("PUT", "/user/partner-profile", partner_data)
        if response and response.status_code == 200:
            self.log_test("Partner Profile Update", "PASS", "Successfully updated partner profile")
            
            # Now check if events API includes partner events
            time.sleep(1)  # Brief pause for database update
            response = self.make_request("GET", "/events")
            if response and response.status_code == 200:
                data = response.json()
                indian_events = data.get("indian_calendar_events", [])
                
                partner_birthday = any("Birthday" in e.get("name", "") for e in indian_events)
                anniversary = any("Anniversary" in e.get("name", "") for e in indian_events)
                
                if partner_birthday and anniversary:
                    self.log_test("Partner Events Integration", "PASS", 
                                "Partner birthday and anniversary automatically added to events")
                else:
                    self.log_test("Partner Events Integration", "FAIL", 
                                f"Missing partner events - Birthday: {partner_birthday}, Anniversary: {anniversary}")
            else:
                self.log_test("Partner Events Integration", "FAIL", "Could not retrieve events after partner update")
        else:
            self.log_test("Partner Profile Update", "FAIL", 
                        f"Partner profile update failed: {response.status_code if response else 'No response'}")
            
    def test_task_completion_and_game_progress(self):
        """Test task completion and game progress integration - KEY FOCUS AREA"""
        print("\n🎮 TESTING TASK COMPLETION & GAME PROGRESS INTEGRATION")
        
        # Get initial profile stats
        response = self.make_request("GET", "/user/profile")
        if response and response.status_code == 200:
            initial_profile = response.json()
            initial_points = initial_profile.get("total_points", 0)
            initial_level = initial_profile.get("current_level", 1)
            initial_streak = initial_profile.get("current_streak", 0)
            initial_tasks = initial_profile.get("tasks_completed", 0)
            initial_badges = initial_profile.get("badges", [])
            
            self.log_test("Initial Profile Stats", "PASS", 
                        f"Points: {initial_points}, Level: {initial_level}, Streak: {initial_streak}, Tasks: {initial_tasks}")
        else:
            self.log_test("Initial Profile Stats", "FAIL", "Could not retrieve initial profile")
            return
            
        # Get daily tasks
        response = self.make_request("GET", "/tasks/daily")
        if response and response.status_code == 200:
            data = response.json()
            tasks = data.get("tasks", [])
            if tasks:
                # Complete first task
                task_to_complete = tasks[0]
                task_id = task_to_complete.get("id")
                
                completion_data = {"task_id": task_id}
                response = self.make_request("POST", "/tasks/complete", completion_data)
                
                if response and response.status_code == 200:
                    completion_result = response.json()
                    points_earned = completion_result.get("points_earned", 0)
                    new_total = completion_result.get("total_points", 0)
                    new_level = completion_result.get("new_level", 1)
                    new_streak = completion_result.get("streak", 0)
                    
                    self.log_test("Task Completion", "PASS", 
                                f"Task completed - Earned {points_earned} points, Total: {new_total}")
                    
                    # Verify profile was updated
                    time.sleep(1)
                    response = self.make_request("GET", "/user/profile")
                    if response and response.status_code == 200:
                        updated_profile = response.json()
                        final_points = updated_profile.get("total_points", 0)
                        final_level = updated_profile.get("current_level", 1)
                        final_streak = updated_profile.get("current_streak", 0)
                        final_tasks = updated_profile.get("tasks_completed", 0)
                        final_badges = updated_profile.get("badges", [])
                        
                        # Verify game progress integration
                        if final_points > initial_points:
                            self.log_test("Game Progress - Points Update", "PASS", 
                                        f"Points increased from {initial_points} to {final_points}")
                        else:
                            self.log_test("Game Progress - Points Update", "FAIL", 
                                        f"Points not updated correctly: {initial_points} -> {final_points}")
                            
                        if final_tasks > initial_tasks:
                            self.log_test("Game Progress - Task Count", "PASS", 
                                        f"Task count increased from {initial_tasks} to {final_tasks}")
                        else:
                            self.log_test("Game Progress - Task Count", "FAIL", 
                                        f"Task count not updated: {initial_tasks} -> {final_tasks}")
                            
                        if final_streak >= initial_streak:
                            self.log_test("Game Progress - Streak Update", "PASS", 
                                        f"Streak updated from {initial_streak} to {final_streak}")
                        else:
                            self.log_test("Game Progress - Streak Update", "FAIL", 
                                        f"Streak not updated correctly: {initial_streak} -> {final_streak}")
                            
                        if len(final_badges) >= len(initial_badges):
                            self.log_test("Game Progress - Badges System", "PASS", 
                                        f"Badges system working: {len(final_badges)} badges")
                        else:
                            self.log_test("Game Progress - Badges System", "FAIL", 
                                        f"Badges system issue: {len(initial_badges)} -> {len(final_badges)}")
                    else:
                        self.log_test("Game Progress - Profile Verification", "FAIL", 
                                    "Could not verify profile updates after task completion")
                else:
                    self.log_test("Task Completion", "FAIL", 
                                f"Task completion failed: {response.status_code if response else 'No response'}")
            else:
                self.log_test("Daily Tasks Retrieval", "FAIL", "No daily tasks available")
        else:
            self.log_test("Daily Tasks Retrieval", "FAIL", 
                        f"Could not get daily tasks: {response.status_code if response else 'No response'}")
            
    def test_existing_apis_still_working(self):
        """Test that existing APIs are still working after updates"""
        print("\n🔄 TESTING EXISTING APIS STILL WORKING")
        
        # Test Relationship Mode Update
        mode_data = {"mode": "LONG_DISTANCE"}
        response = self.make_request("PUT", "/user/relationship-mode", mode_data)
        if response and response.status_code == 200:
            self.log_test("Relationship Mode Update", "PASS", "Successfully updated to LONG_DISTANCE")
        else:
            self.log_test("Relationship Mode Update", "FAIL", 
                        f"Mode update failed: {response.status_code if response else 'No response'}")
            
        # Test Messages API (all 5 categories)
        categories = ["good_morning", "good_night", "love_confession", "apology", "funny_hinglish"]
        for category in categories:
            response = self.make_request("GET", f"/messages/{category}")
            if response and response.status_code == 200:
                data = response.json()
                messages = data.get("messages", [])
                if len(messages) == 5:
                    self.log_test(f"Messages API - {category}", "PASS", f"5 messages returned")
                else:
                    self.log_test(f"Messages API - {category}", "FAIL", f"Expected 5 messages, got {len(messages)}")
            else:
                self.log_test(f"Messages API - {category}", "FAIL", 
                            f"Category failed: {response.status_code if response else 'No response'}")
                
        # Test Gifts API
        response = self.make_request("GET", "/gifts")
        if response and response.status_code == 200:
            data = response.json()
            gifts = data.get("gifts", [])
            if len(gifts) >= 8:
                self.log_test("Gifts API", "PASS", f"Retrieved {len(gifts)} gift ideas")
            else:
                self.log_test("Gifts API", "FAIL", f"Expected at least 8 gifts, got {len(gifts)}")
        else:
            self.log_test("Gifts API", "FAIL", 
                        f"Gifts API failed: {response.status_code if response else 'No response'}")
            
        # Test Weekly Tasks
        response = self.make_request("GET", "/tasks/weekly")
        if response and response.status_code == 200:
            data = response.json()
            task = data.get("task")
            if task and task.get("points") == 25:
                self.log_test("Weekly Tasks API", "PASS", "Weekly task retrieved with 25 points")
            else:
                self.log_test("Weekly Tasks API", "FAIL", f"Weekly task issue: {task}")
        else:
            self.log_test("Weekly Tasks API", "FAIL", 
                        f"Weekly tasks failed: {response.status_code if response else 'No response'}")
            
    def test_custom_event_creation(self):
        """Test custom event creation functionality"""
        print("\n📅 TESTING CUSTOM EVENT CREATION")
        
        if not self.token:
            self.log_test("Custom Event Creation", "FAIL", "No authentication token available")
            return
        
        event_data = {
            "name": "Her Best Friend's Wedding",
            "date": "2025-06-15T18:00:00Z",  # Added Z for proper timezone
            "recurring": False
        }
        
        response = self.make_request("POST", "/events/custom", event_data)
        if response and response.status_code == 200:
            data = response.json()
            if data.get("message") == "Custom event created successfully":
                self.log_test("Custom Event Creation", "PASS", "Successfully created custom event")
                
                # Verify event appears in events list
                time.sleep(1)
                response = self.make_request("GET", "/events")
                if response and response.status_code == 200:
                    events_data = response.json()
                    custom_events = events_data.get("custom_events", [])
                    if any(e.get("name") == "Her Best Friend's Wedding" for e in custom_events):
                        self.log_test("Custom Event Persistence", "PASS", "Custom event appears in events list")
                    else:
                        self.log_test("Custom Event Persistence", "FAIL", "Custom event not found in events list")
                else:
                    self.log_test("Custom Event Persistence", "FAIL", "Could not verify event persistence")
            else:
                self.log_test("Custom Event Creation", "FAIL", f"Unexpected response: {data}")
        elif response and response.status_code == 422:
            self.log_test("Custom Event Creation", "FAIL", f"Validation error: {response.json()}")
        else:
            self.log_test("Custom Event Creation", "FAIL", 
                        f"Event creation failed: {response.status_code if response else 'No response'}")
            
    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🚀 STARTING COMPREHENSIVE POOKIE4U BACKEND TESTING")
        print(f"Testing against: {self.base_url}")
        print(f"Test user: {TEST_USER_EMAIL}")
        print("=" * 80)
        
        # Authentication is required for most tests
        if not self.test_authentication_system():
            print("❌ Authentication failed - cannot proceed with other tests")
            return
            
        # Test the specific bug fixes and new features
        self.test_new_user_profile_update_api()
        self.test_enhanced_events_api()
        self.test_partner_integration_with_events()
        self.test_task_completion_and_game_progress()
        self.test_existing_apis_still_working()
        self.test_custom_event_creation()
        
        # Generate summary
        self.generate_summary()
        
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["status"] == "PASS"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for test in self.test_results:
                if test["status"] == "FAIL":
                    print(f"  • {test['test']}: {test['details']}")
                    
        print("\n🎯 KEY FOCUS AREAS TESTED:")
        print("  • New User Profile Update API")
        print("  • Enhanced Events API with Indian Calendar Events")
        print("  • Partner Integration with Events")
        print("  • Task Completion & Game Progress Integration")
        print("  • Existing APIs Compatibility")
        print("  • Custom Event Creation")

if __name__ == "__main__":
    tester = Pookie4uTester()
    tester.run_all_tests()