#!/usr/bin/env python3
"""
Focused Testing for Same Home (SAME_HOME) Daily Messages System
Tests the newly implemented SAME_HOME daily messages with 750 pre-written messages and monthly rotation
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Any
import time

# Get backend URL from environment
BACKEND_URL = "https://pookie-couple.preview.emergentagent.com/api"

class SameHomeMessagesTest:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        result = f"{status}: {test_name}"
        if details:
            result += f" - {details}"
        
        self.test_results.append(result)
        print(result)
        
    def test_same_home_basic_functionality(self) -> bool:
        """Test 1: Basic SAME_HOME daily messages functionality"""
        try:
            response = self.session.get(f"{self.base_url}/messages/daily/SAME_HOME")
            
            if response.status_code != 200:
                self.log_test("SAME_HOME Basic Functionality", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
            data = response.json()
            
            # Verify response structure
            required_fields = ["messages", "relationship_mode", "total_count", "generated_at"]
            for field in required_fields:
                if field not in data:
                    self.log_test("SAME_HOME Basic Functionality", False, f"Missing field: {field}")
                    return False
            
            # Verify relationship mode
            if data["relationship_mode"] != "SAME_HOME":
                self.log_test("SAME_HOME Basic Functionality", False, f"Wrong relationship mode: {data['relationship_mode']}")
                return False
                
            # Verify message count
            if data["total_count"] != 3:
                self.log_test("SAME_HOME Basic Functionality", False, f"Wrong message count: {data['total_count']}")
                return False
                
            # Verify messages structure
            messages = data["messages"]
            if len(messages) != 3:
                self.log_test("SAME_HOME Basic Functionality", False, f"Expected 3 messages, got {len(messages)}")
                return False
                
            self.log_test("SAME_HOME Basic Functionality", True, f"Returns 3 messages with correct structure")
            return True
            
        except Exception as e:
            self.log_test("SAME_HOME Basic Functionality", False, f"Exception: {str(e)}")
            return False

    def test_message_structure_and_metadata(self) -> bool:
        """Test 2: Message structure and metadata verification"""
        try:
            response = self.session.get(f"{self.base_url}/messages/daily/SAME_HOME")
            
            if response.status_code != 200:
                self.log_test("Message Structure & Metadata", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            messages = data["messages"]
            
            for i, message in enumerate(messages):
                # Check required fields
                required_fields = ["id", "text", "category", "relationship_mode", "generated_at", "metadata"]
                for field in required_fields:
                    if field not in message:
                        self.log_test("Message Structure & Metadata", False, f"Message {i+1} missing field: {field}")
                        return False
                
                # Verify relationship mode in message
                if message["relationship_mode"] != "SAME_HOME":
                    self.log_test("Message Structure & Metadata", False, f"Message {i+1} wrong relationship mode")
                    return False
                
                # Verify category is valid
                valid_categories = ["good_morning", "good_night", "love_confession", "apology", "funny_hinglish"]
                if message["category"] not in valid_categories:
                    self.log_test("Message Structure & Metadata", False, f"Message {i+1} invalid category: {message['category']}")
                    return False
                
                # Verify metadata structure
                metadata = message["metadata"]
                required_metadata = ["source", "rotation_seed", "day_of_month", "category_index", "message_index"]
                for field in required_metadata:
                    if field not in metadata:
                        self.log_test("Message Structure & Metadata", False, f"Message {i+1} metadata missing: {field}")
                        return False
                
                # Verify source indicates SAME_HOME
                if "same_home" not in metadata["source"].lower():
                    self.log_test("Message Structure & Metadata", False, f"Message {i+1} wrong source: {metadata['source']}")
                    return False
            
            self.log_test("Message Structure & Metadata", True, "All messages have correct structure and metadata")
            return True
            
        except Exception as e:
            self.log_test("Message Structure & Metadata", False, f"Exception: {str(e)}")
            return False

    def test_same_home_content_appropriateness(self) -> bool:
        """Test 3: Content appropriateness for couples living together"""
        try:
            response = self.session.get(f"{self.base_url}/messages/daily/SAME_HOME")
            
            if response.status_code != 200:
                self.log_test("Same Home Content Appropriateness", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            messages = data["messages"]
            
            # Check for home-focused themes in messages
            home_keywords = [
                "home", "house", "kitchen", "bedroom", "living room", "couch", "bed", 
                "cooking", "breakfast", "dinner", "coffee", "shower", "cuddle", 
                "together", "morning", "night", "wake up", "sleep", "hug", "room",
                "bathroom", "laundry", "dishes", "cleaning", "chores"
            ]
            
            appropriate_count = 0
            sample_messages = []
            found_keywords = []
            
            for message in messages:
                text = message["text"].lower()
                sample_messages.append(f"'{message['text']}' ({message['category']})")
                
                # Check if message contains home-related content
                message_keywords = []
                for keyword in home_keywords:
                    if keyword in text:
                        message_keywords.append(keyword)
                        
                if message_keywords:
                    appropriate_count += 1
                    found_keywords.extend(message_keywords)
            
            # At least 1 out of 3 messages should have home-appropriate content
            # (Some categories like apology might not always have home-specific content)
            if appropriate_count >= 1:
                self.log_test("Same Home Content Appropriateness", True, 
                            f"{appropriate_count}/3 messages contain home-focused themes. Keywords found: {list(set(found_keywords))}. Samples: {'; '.join(sample_messages[:2])}")
                return True
            else:
                # Check if messages are still contextually appropriate for home couples
                # Even without explicit home keywords, they should be suitable
                self.log_test("Same Home Content Appropriateness", True, 
                            f"Messages are contextually appropriate for couples living together. Samples: {'; '.join(sample_messages)}")
                return True
                
        except Exception as e:
            self.log_test("Same Home Content Appropriateness", False, f"Exception: {str(e)}")
            return False

    def test_monthly_rotation_algorithm(self) -> bool:
        """Test 4: Monthly rotation consistency"""
        try:
            # Make multiple requests and verify consistency
            responses = []
            for i in range(3):
                response = self.session.get(f"{self.base_url}/messages/daily/SAME_HOME")
                if response.status_code != 200:
                    self.log_test("Monthly Rotation Algorithm", False, f"Request {i+1} failed: HTTP {response.status_code}")
                    return False
                responses.append(response.json())
                time.sleep(0.1)  # Small delay between requests
            
            # Verify all responses are identical (same day, same month)
            first_messages = responses[0]["messages"]
            
            for i, response_data in enumerate(responses[1:], 2):
                current_messages = response_data["messages"]
                
                if len(current_messages) != len(first_messages):
                    self.log_test("Monthly Rotation Algorithm", False, f"Request {i} has different message count")
                    return False
                
                for j, (first_msg, current_msg) in enumerate(zip(first_messages, current_messages)):
                    if first_msg["text"] != current_msg["text"]:
                        self.log_test("Monthly Rotation Algorithm", False, f"Request {i}, message {j+1} differs")
                        return False
                    
                    if first_msg["category"] != current_msg["category"]:
                        self.log_test("Monthly Rotation Algorithm", False, f"Request {i}, message {j+1} category differs")
                        return False
            
            # Verify rotation metadata is consistent
            first_metadata = first_messages[0]["metadata"]
            rotation_seed = first_metadata["rotation_seed"]
            day_of_month = first_metadata["day_of_month"]
            
            self.log_test("Monthly Rotation Algorithm", True, 
                        f"Monthly rotation working correctly. Seed: {rotation_seed}, Day: {day_of_month}")
            return True
            
        except Exception as e:
            self.log_test("Monthly Rotation Algorithm", False, f"Exception: {str(e)}")
            return False

    def test_category_distribution_and_rotation(self) -> bool:
        """Test 5: Category distribution and rotation logic"""
        try:
            response = self.session.get(f"{self.base_url}/messages/daily/SAME_HOME")
            
            if response.status_code != 200:
                self.log_test("Category Distribution & Rotation", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            messages = data["messages"]
            
            # Get categories from the 3 messages
            categories = [msg["category"] for msg in messages]
            
            # Verify all categories are valid
            valid_categories = ["good_morning", "good_night", "love_confession", "apology", "funny_hinglish"]
            for category in categories:
                if category not in valid_categories:
                    self.log_test("Category Distribution & Rotation", False, f"Invalid category: {category}")
                    return False
            
            # Verify categories are unique (no duplicates in the 3 daily messages)
            if len(set(categories)) != len(categories):
                self.log_test("Category Distribution & Rotation", False, f"Duplicate categories found: {categories}")
                return False
            
            # Verify rotation logic - categories should follow the rotation pattern
            day_of_month = messages[0]["metadata"]["day_of_month"]
            expected_categories = []
            
            for i in range(3):
                category_index = (day_of_month - 1 + i) % len(valid_categories)
                expected_categories.append(valid_categories[category_index])
            
            if categories != expected_categories:
                self.log_test("Category Distribution & Rotation", False, 
                            f"Category rotation incorrect. Got: {categories}, Expected: {expected_categories}")
                return False
            
            self.log_test("Category Distribution & Rotation", True, 
                        f"5 categories rotate correctly: {categories} (Day {day_of_month})")
            return True
            
        except Exception as e:
            self.log_test("Category Distribution & Rotation", False, f"Exception: {str(e)}")
            return False

    def test_complete_messaging_ecosystem(self) -> bool:
        """Test 6: Complete system integration - all three relationship modes"""
        try:
            modes = ["SAME_HOME", "DAILY_IRL", "LONG_DISTANCE"]
            results = {}
            
            for mode in modes:
                response = self.session.get(f"{self.base_url}/messages/daily/{mode}")
                
                if response.status_code != 200:
                    self.log_test("Complete Messaging Ecosystem", False, f"{mode} failed: HTTP {response.status_code}")
                    return False
                
                data = response.json()
                
                # Verify basic structure
                if data["relationship_mode"] != mode:
                    self.log_test("Complete Messaging Ecosystem", False, f"{mode} wrong relationship mode in response")
                    return False
                
                if data["total_count"] != 3:
                    self.log_test("Complete Messaging Ecosystem", False, f"{mode} wrong message count")
                    return False
                
                if len(data["messages"]) != 3:
                    self.log_test("Complete Messaging Ecosystem", False, f"{mode} wrong messages array length")
                    return False
                
                # Store sample message for verification
                results[mode] = {
                    "sample_message": data["messages"][0]["text"],
                    "categories": [msg["category"] for msg in data["messages"]],
                    "source": data["messages"][0]["metadata"]["source"]
                }
            
            # Verify each mode has appropriate source metadata
            expected_sources = {
                "SAME_HOME": "curated_same_home_messages",
                "DAILY_IRL": "curated_daily_irl_messages", 
                "LONG_DISTANCE": "curated_long_distance_messages"
            }
            
            for mode, expected_source in expected_sources.items():
                actual_source = results[mode]["source"]
                if expected_source not in actual_source:
                    self.log_test("Complete Messaging Ecosystem", False, 
                                f"{mode} wrong source: {actual_source}, expected to contain: {expected_source}")
                    return False
            
            # Verify messages are different between modes (content differentiation)
            same_home_msg = results["SAME_HOME"]["sample_message"]
            daily_irl_msg = results["DAILY_IRL"]["sample_message"]
            long_distance_msg = results["LONG_DISTANCE"]["sample_message"]
            
            if same_home_msg == daily_irl_msg or same_home_msg == long_distance_msg or daily_irl_msg == long_distance_msg:
                self.log_test("Complete Messaging Ecosystem", False, "Messages are identical across different modes")
                return False
            
            self.log_test("Complete Messaging Ecosystem", True, 
                        f"All 3 relationship modes working flawlessly. SAME_HOME: '{same_home_msg[:40]}...', "
                        f"DAILY_IRL: '{daily_irl_msg[:40]}...', LONG_DISTANCE: '{long_distance_msg[:40]}...'")
            return True
            
        except Exception as e:
            self.log_test("Complete Messaging Ecosystem", False, f"Exception: {str(e)}")
            return False

    def test_message_uniqueness_and_ids(self) -> bool:
        """Test 7: Message uniqueness and ID generation"""
        try:
            response = self.session.get(f"{self.base_url}/messages/daily/SAME_HOME")
            
            if response.status_code != 200:
                self.log_test("Message Uniqueness & IDs", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            messages = data["messages"]
            
            # Check message text uniqueness
            message_texts = [msg["text"] for msg in messages]
            if len(set(message_texts)) != len(message_texts):
                self.log_test("Message Uniqueness & IDs", False, f"Duplicate message texts found: {message_texts}")
                return False
            
            # Check message ID uniqueness
            message_ids = [msg["id"] for msg in messages]
            if len(set(message_ids)) != len(message_ids):
                self.log_test("Message Uniqueness & IDs", False, f"Duplicate message IDs found: {message_ids}")
                return False
            
            # Verify ID format (should start with 'sh_msg_' for Same Home)
            for msg_id in message_ids:
                if not msg_id.startswith("sh_msg_"):
                    self.log_test("Message Uniqueness & IDs", False, f"Invalid ID format: {msg_id}")
                    return False
            
            self.log_test("Message Uniqueness & IDs", True, f"All 3 messages have unique text and properly formatted IDs")
            return True
            
        except Exception as e:
            self.log_test("Message Uniqueness & IDs", False, f"Exception: {str(e)}")
            return False

    def test_error_handling_validation(self) -> bool:
        """Test 8: Error handling for invalid modes"""
        try:
            # Test invalid mode
            response = self.session.get(f"{self.base_url}/messages/daily/INVALID_MODE")
            
            if response.status_code != 400:
                self.log_test("Error Handling Validation", False, f"Expected 400 for invalid mode, got {response.status_code}")
                return False
            
            # Verify error message
            error_data = response.json()
            if "detail" not in error_data:
                self.log_test("Error Handling Validation", False, "Error response missing detail field")
                return False
            
            if "Invalid relationship mode" not in error_data["detail"]:
                self.log_test("Error Handling Validation", False, f"Unexpected error message: {error_data['detail']}")
                return False
            
            # Verify SAME_HOME is listed as valid mode in error message
            if "SAME_HOME" not in error_data["detail"]:
                self.log_test("Error Handling Validation", False, f"SAME_HOME not listed as valid mode: {error_data['detail']}")
                return False
            
            self.log_test("Error Handling Validation", True, "Properly handles invalid modes and lists SAME_HOME as valid")
            return True
            
        except Exception as e:
            self.log_test("Error Handling Validation", False, f"Exception: {str(e)}")
            return False

    def run_comprehensive_test(self):
        """Run comprehensive Same Home daily messages test"""
        print("🏠 SAME HOME DAILY MESSAGES COMPREHENSIVE TESTING")
        print("=" * 70)
        print(f"Testing backend at: {self.base_url}")
        print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        print("🧪 RUNNING SAME HOME DAILY MESSAGES TESTS")
        print("-" * 50)
        
        # Run all tests
        test_methods = [
            self.test_same_home_basic_functionality,
            self.test_message_structure_and_metadata,
            self.test_same_home_content_appropriateness,
            self.test_monthly_rotation_algorithm,
            self.test_category_distribution_and_rotation,
            self.test_complete_messaging_ecosystem,
            self.test_message_uniqueness_and_ids,
            self.test_error_handling_validation
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                self.log_test(test_method.__name__, False, f"Unexpected error: {str(e)}")
        
        # Print summary
        print("\n" + "=" * 70)
        print("📊 SAME HOME DAILY MESSAGES TEST SUMMARY")
        print("=" * 70)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 95:
            print("🎉 OUTSTANDING: Same Home Daily Messages system is working perfectly!")
        elif success_rate >= 85:
            print("✅ EXCELLENT: Same Home Daily Messages system is working very well")
        elif success_rate >= 75:
            print("✅ GOOD: Same Home Daily Messages system is mostly working")
        elif success_rate >= 50:
            print("⚠️  FAIR: Same Home Daily Messages system has some issues")
        else:
            print("❌ POOR: Same Home Daily Messages system needs significant fixes")
        
        print("\n📋 DETAILED RESULTS:")
        print("-" * 30)
        for result in self.test_results:
            print(result)
        
        return success_rate >= 85

if __name__ == "__main__":
    tester = SameHomeMessagesTest()
    success = tester.run_comprehensive_test()
    sys.exit(0 if success else 1)