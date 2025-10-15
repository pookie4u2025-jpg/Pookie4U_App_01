#!/usr/bin/env python3
"""
COMPREHENSIVE POOKIE4U BACKEND API TESTING SUITE - SUBSCRIPTION SYSTEM + ALL FEATURES
=====================================================================================

This test suite conducts exhaustive testing of ALL backend endpoints for the Pookie4u app audit.
Tests cover subscription system, authentication, AI tasks, calendar events, gifts, messages, profiles, and gamification.

Test Scope:
- 35+ API endpoints across 9 major systems including NEW SUBSCRIPTION SYSTEM
- Real user flow testing (register → authenticate → subscription → use features)
- Critical subscription flow verification (trial, mockup payments, status checks)
- Production readiness assessment for subscription monetization
"""

import asyncio
import aiohttp
import json
import uuid
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import sys
import traceback

# Configuration
BASE_URL = "https://romance-inspect.preview.emergentagent.com/api"
TEST_USER_EMAIL = f"test.user.{uuid.uuid4().hex[:8]}@example.com"
TEST_USER_NAME = "Sarah Johnson"
TEST_USER_PASSWORD = "SecurePass123!"

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

class TestResult:
    """Test result tracking"""
    def __init__(self):
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.results = []
        self.critical_issues = []
        self.working_features = []
        self.broken_features = []
        
    def add_result(self, test_name: str, success: bool, details: str = "", is_critical: bool = False):
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            self.working_features.append(f"✅ {test_name}")
            print(f"{Colors.GREEN}✅ PASS{Colors.END}: {test_name}")
        else:
            self.failed_tests += 1
            if is_critical:
                self.critical_issues.append(f"❌ CRITICAL: {test_name} - {details}")
            self.broken_features.append(f"❌ {test_name} - {details}")
            print(f"{Colors.RED}❌ FAIL{Colors.END}: {test_name} - {details}")
        
        self.results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "critical": is_critical
        })
    
    def get_success_rate(self) -> float:
        if self.total_tests == 0:
            return 0.0
        return (self.passed_tests / self.total_tests) * 100

class Pookie4uAPITester:
    """Comprehensive API testing class for Pookie4u backend"""
    
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.user_id = None
        self.results = TestResult()
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authorization headers"""
        if self.auth_token:
            return {"Authorization": f"Bearer {self.auth_token}"}
        return {}
    
    async def make_request(self, method: str, endpoint: str, data: Dict = None, headers: Dict = None) -> tuple:
        """Make HTTP request and return (success, response_data, status_code)"""
        url = f"{BASE_URL}{endpoint}"
        request_headers = headers or {}
        
        try:
            async with self.session.request(method, url, json=data, headers=request_headers) as response:
                try:
                    response_data = await response.json()
                except:
                    response_data = {"error": "Invalid JSON response"}
                
                return response.status < 400, response_data, response.status
        except Exception as e:
            return False, {"error": str(e)}, 0

    # ============================================================================
    # AUTHENTICATION SYSTEM TESTS
    # ============================================================================
    
    async def test_user_registration(self):
        """Test user registration with email/password"""
        print(f"\n{Colors.BLUE}🔐 TESTING AUTHENTICATION SYSTEM{Colors.END}")
        
        # Test valid registration
        registration_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
            "name": TEST_USER_NAME
        }
        
        success, response, status = await self.make_request("POST", "/auth/register", registration_data)
        
        if success and "access_token" in response:
            self.auth_token = response["access_token"]
            self.results.add_result("User Registration (Email/Password)", True, f"Status: {status}")
        else:
            self.results.add_result("User Registration (Email/Password)", False, 
                                  f"Status: {status}, Response: {response}", is_critical=True)
            return
        
        # Test duplicate email registration
        success, response, status = await self.make_request("POST", "/auth/register", registration_data)
        if status == 400 and "already registered" in str(response.get("detail", "")).lower():
            self.results.add_result("Duplicate Email Validation", True, "Properly rejected duplicate email")
        else:
            self.results.add_result("Duplicate Email Validation", False, 
                                  f"Expected 400 error, got {status}: {response}")
    
    async def test_user_login(self):
        """Test user login functionality"""
        login_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
        
        success, response, status = await self.make_request("POST", "/auth/login", login_data)
        
        if success and "access_token" in response:
            self.auth_token = response["access_token"]  # Update token
            self.results.add_result("User Login (Email/Password)", True, f"Status: {status}")
        else:
            self.results.add_result("User Login (Email/Password)", False, 
                                  f"Status: {status}, Response: {response}", is_critical=True)
        
        # Test invalid credentials
        invalid_login = {
            "email": TEST_USER_EMAIL,
            "password": "WrongPassword123!"
        }
        
        success, response, status = await self.make_request("POST", "/auth/login", invalid_login)
        if status == 401:
            self.results.add_result("Invalid Credentials Handling", True, "Properly rejected invalid password")
        else:
            self.results.add_result("Invalid Credentials Handling", False, 
                                  f"Expected 401 error, got {status}: {response}")
    
    async def test_mobile_otp_system(self):
        """Test mobile OTP authentication (mocked)"""
        mobile_number = "+919876543210"
        
        # Test send OTP
        otp_data = {"mobile": mobile_number}
        success, response, status = await self.make_request("POST", "/auth/send-otp", otp_data)
        
        if success:
            self.results.add_result("Mobile OTP Send", True, f"Status: {status} - Development mode")
        else:
            self.results.add_result("Mobile OTP Send", False, f"Status: {status}, Response: {response}")
        
        # Test verify OTP (using development OTP from logs)
        # Note: In development mode, OTP is printed to console
        verify_data = {
            "mobile": mobile_number,
            "otp": "123456",  # Mock OTP for testing
            "name": "Test Mobile User"
        }
        
        success, response, status = await self.make_request("POST", "/auth/verify-otp", verify_data)
        # This might fail in development mode without real OTP, which is expected
        self.results.add_result("Mobile OTP Verification", success, 
                              f"Status: {status} - {'MOCKED' if not success else 'Working'}")
    
    async def test_google_oauth_endpoints(self):
        """Test Google OAuth endpoints (structure validation)"""
        # Test Google OAuth endpoint with invalid token
        oauth_data = {
            "provider": "google",
            "id_token": "invalid_token_for_testing"
        }
        
        success, response, status = await self.make_request("POST", "/auth/oauth/google", oauth_data)
        
        # Should return 400 for invalid token
        if status == 400 and "invalid" in str(response.get("detail", "")).lower():
            self.results.add_result("Google OAuth Endpoint Structure", True, 
                                  "Properly validates Google tokens")
        else:
            self.results.add_result("Google OAuth Endpoint Structure", False, 
                                  f"Unexpected response: {status} - {response}")
        
        # Test account linking endpoint (requires auth)
        headers = self.get_auth_headers()
        link_data = {
            "provider": "google",
            "credential": {"id_token": "test_token"}
        }
        
        success, response, status = await self.make_request("POST", "/auth/link-account", link_data, headers)
        # Should fail with invalid token but endpoint should be accessible
        self.results.add_result("Account Linking Endpoint", status in [400, 401, 403], 
                              f"Status: {status} - Endpoint accessible")
        
        # Test account unlinking
        unlink_data = {"provider": "google"}
        success, response, status = await self.make_request("POST", "/auth/unlink-account", unlink_data, headers)
        self.results.add_result("Account Unlinking Endpoint", status in [400, 401, 403], 
                              f"Status: {status} - Endpoint accessible")

    # ============================================================================
    # USER PROFILE MANAGEMENT TESTS
    # ============================================================================
    
    async def test_user_profile_management(self):
        """Test user profile retrieval and updates"""
        print(f"\n{Colors.PURPLE}👤 TESTING USER PROFILE MANAGEMENT{Colors.END}")
        
        headers = self.get_auth_headers()
        
        # Test profile retrieval
        success, response, status = await self.make_request("GET", "/user/profile", headers=headers)
        
        if success and "id" in response:
            self.user_id = response["id"]
            self.results.add_result("User Profile Retrieval", True, f"Status: {status}")
        else:
            self.results.add_result("User Profile Retrieval", False, 
                                  f"Status: {status}, Response: {response}", is_critical=True)
            return
        
        # Test profile update
        profile_update = {
            "name": "Sarah Johnson Updated",
            "email": TEST_USER_EMAIL
        }
        
        success, response, status = await self.make_request("PUT", "/user/profile", profile_update, headers)
        self.results.add_result("User Profile Update", success, f"Status: {status}")
        
        # Test partner profile update
        partner_data = {
            "name": "Alex Johnson",
            "birthday": "15/03/1995",
            "anniversary": "14/02/2020",
            "favorite_color": "Blue",
            "favorite_food": "Italian",
            "favorite_flower": "Roses",
            "favorite_brand": "Nike",
            "dress_size": "M",
            "ring_size": "7",
            "perfume_preference": "Floral",
            "notes": "Loves surprises and romantic gestures"
        }
        
        success, response, status = await self.make_request("PUT", "/user/partner-profile", partner_data, headers)
        self.results.add_result("Partner Profile Update", success, f"Status: {status}")
        
        # Test relationship mode update
        for mode in ["SAME_HOME", "DAILY_IRL", "LONG_DISTANCE"]:
            mode_data = {"mode": mode}
            success, response, status = await self.make_request("PUT", "/user/relationship-mode", mode_data, headers)
            self.results.add_result(f"Relationship Mode Update ({mode})", success, f"Status: {status}")

    # ============================================================================
    # AI TASK GENERATION SYSTEM TESTS
    # ============================================================================
    
    async def test_ai_task_system(self):
        """Test AI-powered task generation system"""
        print(f"\n{Colors.CYAN}🤖 TESTING AI TASK GENERATION SYSTEM{Colors.END}")
        
        headers = self.get_auth_headers()
        
        # Test daily tasks for each relationship mode
        for mode in ["SAME_HOME", "DAILY_IRL", "LONG_DISTANCE"]:
            # Set relationship mode first
            mode_data = {"mode": mode}
            await self.make_request("PUT", "/user/relationship-mode", mode_data, headers)
            
            # Get daily tasks
            success, response, status = await self.make_request("GET", "/tasks/daily", headers=headers)
            
            if success and "tasks" in response and len(response["tasks"]) == 3:
                self.results.add_result(f"Daily Tasks Generation ({mode})", True, 
                                      f"Status: {status}, Tasks: {len(response['tasks'])}")
            else:
                self.results.add_result(f"Daily Tasks Generation ({mode})", False, 
                                      f"Status: {status}, Response: {response}")
            
            # Get weekly tasks
            success, response, status = await self.make_request("GET", "/tasks/weekly", headers=headers)
            
            if success and "tasks" in response and len(response["tasks"]) >= 1:
                self.results.add_result(f"Weekly Tasks Generation ({mode})", True, 
                                      f"Status: {status}, Tasks: {len(response['tasks'])}")
            else:
                self.results.add_result(f"Weekly Tasks Generation ({mode})", False, 
                                      f"Status: {status}, Response: {response}")
        
        # Test task regeneration
        success, response, status = await self.make_request("GET", "/tasks/daily?regenerate=true", headers=headers)
        self.results.add_result("Task Regeneration", success, f"Status: {status}")
        
        # Test manual task generation
        generation_data = {
            "relationship_mode": "SAME_HOME",
            "task_type": "daily",
            "count": 3
        }
        
        success, response, status = await self.make_request("POST", "/tasks/generate", generation_data, headers)
        self.results.add_result("Manual Task Generation", success, f"Status: {status}")
    
    async def test_task_completion_system(self):
        """Test task completion and gamification"""
        print(f"\n{Colors.YELLOW}🎯 TESTING TASK COMPLETION & GAMIFICATION{Colors.END}")
        
        headers = self.get_auth_headers()
        
        # Get daily tasks first
        success, response, status = await self.make_request("GET", "/tasks/daily", headers=headers)
        
        if success and "tasks" in response and len(response["tasks"]) > 0:
            task_id = response["tasks"][0].get("id")
            
            if task_id:
                # Complete a task
                completion_data = {"task_id": task_id}
                success, response, status = await self.make_request("POST", "/tasks/complete", completion_data, headers)
                
                if success and "points_earned" in response:
                    self.results.add_result("Task Completion", True, 
                                          f"Status: {status}, Points: {response.get('points_earned')}")
                else:
                    self.results.add_result("Task Completion", False, f"Status: {status}, Response: {response}")
            else:
                self.results.add_result("Task Completion", False, "No task ID available")
        else:
            self.results.add_result("Task Completion", False, "No tasks available for completion")
        
        # Test winners API
        success, response, status = await self.make_request("GET", "/winners")
        
        if success and "winners" in response:
            self.results.add_result("Winners API", True, f"Status: {status}, Winners: {len(response['winners'])}")
        else:
            self.results.add_result("Winners API", False, f"Status: {status}, Response: {response}")

    # ============================================================================
    # ENHANCED CALENDAR & EVENTS TESTS
    # ============================================================================
    
    async def test_enhanced_calendar_system(self):
        """Test comprehensive calendar and events system"""
        print(f"\n{Colors.GREEN}📅 TESTING ENHANCED CALENDAR & EVENTS SYSTEM{Colors.END}")
        
        headers = self.get_auth_headers()
        
        # Test events retrieval
        success, response, status = await self.make_request("GET", "/events", headers=headers)
        
        if success and isinstance(response, list):
            total_events = len(response)
            self.results.add_result("Events Retrieval", True, f"Status: {status}, Events: {total_events}")
            
            # Check for 40+ events as mentioned in requirements
            if total_events >= 40:
                self.results.add_result("Comprehensive Events Count", True, f"Found {total_events} events")
            else:
                self.results.add_result("Comprehensive Events Count", False, 
                                      f"Expected 40+ events, found {total_events}")
        else:
            self.results.add_result("Events Retrieval", False, f"Status: {status}, Response: {response}")
            return
        
        # Test events pagination
        success, response, status = await self.make_request("GET", "/events?limit=10&offset=0", headers=headers)
        
        if success and len(response) <= 10:
            self.results.add_result("Events Pagination", True, f"Status: {status}, Limited results: {len(response)}")
        else:
            self.results.add_result("Events Pagination", False, f"Status: {status}, Response: {response}")
        
        # Test event details
        if success and len(response) > 0:
            event_id = response[0].get("id")
            if event_id:
                success, response, status = await self.make_request("GET", f"/events/{event_id}/details", headers=headers)
                self.results.add_result("Event Details", success, f"Status: {status}")
        
        # Test custom event creation
        custom_event = {
            "name": "Test Anniversary",
            "date": (datetime.now() + timedelta(days=30)).isoformat(),
            "description": "Test custom event",
            "importance": "high",
            "reminder_settings": {
                "enabled": True,
                "days_before": 7,
                "times_per_day": 2,
                "reminder_times": ["10:00", "18:00"]
            }
        }
        
        success, response, status = await self.make_request("POST", "/events/custom", custom_event, headers)
        
        if success and "id" in response:
            event_id = response["id"]
            self.results.add_result("Custom Event Creation", True, f"Status: {status}")
            
            # Test event editing
            update_data = {
                "name": "Updated Test Anniversary",
                "description": "Updated description"
            }
            
            success, response, status = await self.make_request("PATCH", f"/events/custom/{event_id}", 
                                                              update_data, headers)
            self.results.add_result("Custom Event Editing", success, f"Status: {status}")
            
            # Test event deletion
            success, response, status = await self.make_request("DELETE", f"/events/custom/{event_id}", headers=headers)
            self.results.add_result("Custom Event Deletion", success, f"Status: {status}")
            
        else:
            self.results.add_result("Custom Event Creation", False, f"Status: {status}, Response: {response}")

    # ============================================================================
    # GIFTS API TESTS (Critical - User Reported Issues)
    # ============================================================================
    
    async def test_gifts_api_comprehensive(self):
        """Test Gifts API with focus on user-reported duplicate images issue"""
        print(f"\n{Colors.RED}🎁 TESTING GIFTS API (CRITICAL - USER REPORTED ISSUES){Colors.END}")
        
        success, response, status = await self.make_request("GET", "/gifts")
        
        if success and isinstance(response, list):
            gifts_count = len(response)
            self.results.add_result("Gifts API Response", True, f"Status: {status}, Gifts: {gifts_count}")
            
            # Critical test: Check for duplicate images (user reported issue)
            images = []
            unique_images = set()
            products_with_images = 0
            
            for gift in response:
                if "image" in gift and gift["image"]:
                    images.append(gift["image"])
                    unique_images.add(gift["image"])
                    products_with_images += 1
            
            # Check if all products have unique images
            if len(images) == len(unique_images) and products_with_images == gifts_count:
                self.results.add_result("CRITICAL: Unique Product Images", True, 
                                      f"All {gifts_count} products have unique images")
            else:
                self.results.add_result("CRITICAL: Unique Product Images", False, 
                                      f"Duplicate images found! {len(images)} total, {len(unique_images)} unique", 
                                      is_critical=True)
            
            # Verify Amazon product data structure
            required_fields = ["id", "name", "category", "price_range", "link", "description", "image"]
            valid_products = 0
            
            for gift in response:
                if all(field in gift for field in required_fields):
                    valid_products += 1
            
            if valid_products == gifts_count:
                self.results.add_result("Amazon Product Data Structure", True, 
                                      f"All {gifts_count} products have complete data")
            else:
                self.results.add_result("Amazon Product Data Structure", False, 
                                      f"Only {valid_products}/{gifts_count} products have complete data")
            
            # Check for specific product mentioned in requirements
            high_waist_trouser_found = False
            for gift in response:
                if "High Waist Formal Trousers" in gift.get("name", ""):
                    high_waist_trouser_found = True
                    # Verify specific details
                    expected_price = "₹449"
                    expected_link = "https://amzn.to/46k7tSR"
                    
                    if gift.get("price_range") == expected_price and gift.get("link") == expected_link:
                        self.results.add_result("Specific Product Verification", True, 
                                              "High Waist Formal Trousers product verified")
                    else:
                        self.results.add_result("Specific Product Verification", False, 
                                              f"Product details mismatch: {gift}")
                    break
            
            if not high_waist_trouser_found:
                self.results.add_result("Specific Product Verification", False, 
                                      "High Waist Formal Trousers product not found")
                
        else:
            self.results.add_result("Gifts API Response", False, 
                                  f"Status: {status}, Response: {response}", is_critical=True)

    # ============================================================================
    # MESSAGES SYSTEM TESTS
    # ============================================================================
    
    async def test_messages_system(self):
        """Test romantic messages system"""
        print(f"\n{Colors.BLUE}💌 TESTING MESSAGES SYSTEM{Colors.END}")
        
        headers = self.get_auth_headers()
        
        # Test message categories
        categories = ["good_morning", "good_night", "love_confession", "apology", "funny_hinglish"]
        
        for category in categories:
            success, response, status = await self.make_request("GET", f"/messages/{category}")
            
            if success and isinstance(response, list) and len(response) > 0:
                self.results.add_result(f"Messages Category ({category})", True, 
                                      f"Status: {status}, Messages: {len(response)}")
            else:
                self.results.add_result(f"Messages Category ({category})", False, 
                                      f"Status: {status}, Response: {response}")
        
        # Test daily messages by relationship mode
        for mode in ["SAME_HOME", "DAILY_IRL", "LONG_DISTANCE"]:
            success, response, status = await self.make_request("GET", f"/messages/daily/{mode}", headers=headers)
            
            if success and isinstance(response, list) and len(response) == 15:  # 3 per category × 5 categories
                self.results.add_result(f"Daily Messages ({mode})", True, 
                                      f"Status: {status}, Messages: {len(response)}")
            else:
                self.results.add_result(f"Daily Messages ({mode})", False, 
                                      f"Status: {status}, Expected 15 messages, got: {response}")

    # ============================================================================
    # SUBSCRIPTION/PAYMENT TESTS
    # ============================================================================
    
    # ============================================================================
    # AI PERSONALIZATION TESTS (NEW FEATURES)
    # ============================================================================
    
    async def test_ai_personalization_features(self):
        """Test NEW AI Personalization Features - Messages, Gifts, Date Planning"""
        print(f"\n{Colors.PURPLE}🤖 TESTING AI PERSONALIZATION FEATURES (NEW){Colors.END}")
        
        if not self.auth_token:
            self.results.add_result("AI Features - Auth Required", False, "No auth token available")
            return
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # Test 1: AI-Powered Personalized Messages
        print(f"   🎯 Testing AI Message Generation...")
        message_categories = ["good_morning", "good_night", "love_confession", "apology", "funny_hinglish", "missing_you", "appreciation", "encouragement"]
        
        message_success_count = 0
        for category in message_categories:
            success, response, status = await self.make_request(
                "POST", f"/ai/generate-message?category={category}", headers=headers
            )
            
            if success and status == 200:
                message = response.get("message", "")
                ai_generated = response.get("ai_generated", False)
                if message and ai_generated:
                    message_success_count += 1
                    self.results.add_result(f"AI Message - {category}", True, 
                                          f"Generated: '{message[:30]}...'")
                else:
                    self.results.add_result(f"AI Message - {category}", False, 
                                          f"Invalid response structure")
            else:
                self.results.add_result(f"AI Message - {category}", False, 
                                      f"Status: {status}")
        
        # Test auth protection for messages
        success, response, status = await self.make_request("POST", "/ai/generate-message?category=good_morning")
        self.results.add_result("AI Message - Auth Protection", status in [401, 403], 
                              f"Unauthorized status: {status}")
        
        # Test 2: AI-Enhanced Smart Gifts
        print(f"   🎁 Testing AI Smart Gifts...")
        gift_test_cases = [
            {"occasion": "anniversary", "budget": "Under ₹1000"},
            {"occasion": "birthday", "budget": "₹500-₹1500"},
            {"occasion": "general", "budget": "Under ₹500"}
        ]
        
        gift_success_count = 0
        for case in gift_test_cases:
            params = "&".join([f"{k}={v}" for k, v in case.items()])
            success, response, status = await self.make_request(
                "GET", f"/ai/smart-gifts?{params}", headers=headers
            )
            
            if success and status == 200:
                gifts = response.get("gifts", [])
                ai_enhanced = response.get("ai_enhanced", False)
                
                # Verify unique images (critical user-reported bug)
                images = [gift.get("image") for gift in gifts if gift.get("image")]
                unique_images = len(set(images))
                
                if len(gifts) == 6 and unique_images == len(images):
                    gift_success_count += 1
                    self.results.add_result(f"Smart Gifts - {case['occasion']}", True, 
                                          f"6 gifts, {unique_images} unique images, AI: {ai_enhanced}")
                else:
                    self.results.add_result(f"Smart Gifts - {case['occasion']}", False, 
                                          f"Expected 6 unique gifts, got {len(gifts)} with {unique_images} unique images")
            else:
                self.results.add_result(f"Smart Gifts - {case['occasion']}", False, 
                                      f"Status: {status}")
        
        # Test auth protection for gifts
        success, response, status = await self.make_request("GET", "/ai/smart-gifts")
        self.results.add_result("Smart Gifts - Auth Protection", status in [401, 403], 
                              f"Unauthorized status: {status}")
        
        # Test 3: AI Date Planner
        print(f"   💕 Testing AI Date Planner...")
        date_test_cases = [
            {"budget": "Under ₹1000", "preferences": "outdoor activities", "location": "Mumbai"},
            {"budget": "₹1000-₹2000", "preferences": "romantic dinner", "location": "Delhi"},
            {"budget": "Under ₹500"}
        ]
        
        date_success_count = 0
        for case in date_test_cases:
            success, response, status = await self.make_request(
                "POST", "/ai/plan-date", case, headers
            )
            
            if success and status == 200:
                date_plan = response.get("date_plan", {})
                ai_generated = response.get("ai_generated", False)
                
                # Verify required fields
                required_fields = ["title", "time", "duration", "activity", "why_romantic", "tips", "estimated_cost"]
                has_all_fields = all(field in date_plan for field in required_fields)
                
                if has_all_fields and ai_generated:
                    date_success_count += 1
                    self.results.add_result(f"Date Plan - {case['budget']}", True, 
                                          f"Complete plan: '{date_plan.get('title', '')}', AI: {ai_generated}")
                else:
                    missing_fields = [f for f in required_fields if f not in date_plan]
                    self.results.add_result(f"Date Plan - {case['budget']}", False, 
                                          f"Missing fields: {missing_fields}, AI: {ai_generated}")
            else:
                self.results.add_result(f"Date Plan - {case['budget']}", False, 
                                      f"Status: {status}")
        
        # Test auth protection for date planner
        success, response, status = await self.make_request("POST", "/ai/plan-date", {"budget": "Under ₹1000"})
        self.results.add_result("Date Plan - Auth Protection", status in [401, 403], 
                              f"Unauthorized status: {status}")
        
        # Test 4: Complete AI Flow
        print(f"   🔄 Testing Complete AI Flow...")
        try:
            # Generate message -> Get gifts -> Plan date
            msg_success, _, _ = await self.make_request("POST", "/ai/generate-message?category=love_confession", headers=headers)
            gift_success, _, _ = await self.make_request("GET", "/ai/smart-gifts?occasion=anniversary", headers=headers)
            date_success, _, _ = await self.make_request("POST", "/ai/plan-date", {"budget": "Under ₹1000"}, headers)
            
            flow_success = msg_success and gift_success and date_success
            self.results.add_result("Complete AI Flow", flow_success, 
                                  f"Message→Gifts→Date: {msg_success}→{gift_success}→{date_success}")
        except Exception as e:
            self.results.add_result("Complete AI Flow", False, f"Error: {str(e)}")
        
        # Summary
        total_ai_features = message_success_count + gift_success_count + date_success_count
        print(f"   📊 AI Features Summary: {total_ai_features}/11 core features working")
        
        # Critical verification
        if message_success_count >= 6:  # At least 6/8 message categories
            self.results.working_features.append("AI Personalized Messages")
        else:
            self.results.broken_features.append("AI Personalized Messages")
        
        if gift_success_count >= 2:  # At least 2/3 gift scenarios
            self.results.working_features.append("AI Smart Gifts")
        else:
            self.results.broken_features.append("AI Smart Gifts")
        
        if date_success_count >= 2:  # At least 2/3 date scenarios
            self.results.working_features.append("AI Date Planner")
        else:
            self.results.broken_features.append("AI Date Planner")

    async def test_subscription_system(self):
        """Test comprehensive subscription system - PRIMARY FOCUS"""
        print(f"\n{Colors.PURPLE}💳 TESTING SUBSCRIPTION SYSTEM - COMPREHENSIVE{Colors.END}")
        
        headers = self.get_auth_headers()
        
        # ============================================================================
        # 1. SUBSCRIPTION STATUS ENDPOINT
        # ============================================================================
        print(f"{Colors.CYAN}📊 Testing Subscription Status Endpoint{Colors.END}")
        
        # Test with authentication
        success, response, status = await self.make_request("GET", "/subscription/status", None, headers)
        
        if success and status == 200:
            required_fields = ["success", "subscription"]
            subscription_fields = ["type", "status", "is_active", "days_remaining", "can_start_trial"]
            
            if all(field in response for field in required_fields):
                subscription = response["subscription"]
                if all(field in subscription for field in subscription_fields):
                    self.results.add_result("Subscription Status - With Auth", True, 
                                          f"Type: {subscription['type']}, Status: {subscription['status']}")
                    print(f"   ✅ Initial subscription status: {subscription['type']} ({subscription['status']})")
                    print(f"   ✅ Can start trial: {subscription['can_start_trial']}")
                else:
                    self.results.add_result("Subscription Status - With Auth", False, 
                                          f"Missing subscription fields: {subscription}")
            else:
                self.results.add_result("Subscription Status - With Auth", False, 
                                      f"Missing required fields: {response}")
        else:
            self.results.add_result("Subscription Status - With Auth", False, 
                                  f"Status: {status}, Response: {response}")

        # Test without authentication (should fail)
        success, response, status = await self.make_request("GET", "/subscription/status", None, {})
        
        if status in [401, 403]:
            self.results.add_result("Subscription Status - No Auth", True, 
                                  f"Correctly rejected with status {status}")
        else:
            self.results.add_result("Subscription Status - No Auth", False, 
                                  f"Should reject unauthorized access, got {status}")

        # ============================================================================
        # 2. START FREE TRIAL
        # ============================================================================
        print(f"{Colors.CYAN}🆓 Testing Free Trial System{Colors.END}")
        
        # Get current subscription status first
        success, status_response, status_code = await self.make_request("GET", "/subscription/status", None, headers)
        
        if success and status_code == 200:
            can_start_trial = status_response["subscription"]["can_start_trial"]
            
            # Test starting trial
            success, response, status = await self.make_request("POST", "/subscription/start-trial", None, headers)
            
            if can_start_trial:
                if success and status == 200:
                    if (response.get("success") and 
                        response.get("subscription", {}).get("type") == "trial" and
                        response.get("subscription", {}).get("status") == "active" and
                        response.get("subscription", {}).get("days_remaining") == 14):
                        self.results.add_result("Start Free Trial", True, 
                                              f"Trial started: {response['subscription']}")
                        print(f"   ✅ Free trial activated: 14 days remaining")
                    else:
                        self.results.add_result("Start Free Trial", False, 
                                              f"Invalid trial data: {response}")
                else:
                    self.results.add_result("Start Free Trial", False, 
                                          f"Status: {status}, Response: {response}")
            else:
                # Trial already used, should fail
                if status == 400:
                    self.results.add_result("Start Free Trial - Already Used", True, 
                                          f"Correctly rejected: {response}")
                    print(f"   ✅ Trial already used - correctly rejected")
                else:
                    self.results.add_result("Start Free Trial - Already Used", False, 
                                          f"Should reject with 400, got {status}")

            # Test without authentication
            success, response, status = await self.make_request("POST", "/subscription/start-trial", None, {})
            if status in [401, 403]:
                self.results.add_result("Start Trial - No Auth", True, 
                                      f"Correctly rejected with status {status}")
            else:
                self.results.add_result("Start Trial - No Auth", False, 
                                      f"Should reject unauthorized access, got {status}")

        # ============================================================================
        # 3. START MOCKUP SUBSCRIPTION
        # ============================================================================
        print(f"{Colors.CYAN}💰 Testing Mockup Subscription System{Colors.END}")
        
        # Test monthly subscription
        monthly_data = {"subscription_type": "monthly"}
        success, response, status = await self.make_request("POST", "/subscription/start-mockup", 
                                                          monthly_data, headers)
        
        if success and status == 200:
            if (response.get("success") and 
                response.get("subscription", {}).get("type") == "monthly" and
                response.get("subscription", {}).get("status") == "active" and
                response.get("subscription", {}).get("days_remaining") == 30):
                self.results.add_result("Start Mockup Monthly", True, 
                                      f"Monthly subscription: ₹79, 30 days")
                print(f"   ✅ Monthly subscription activated: ₹79, 30 days")
            else:
                self.results.add_result("Start Mockup Monthly", False, 
                                      f"Invalid monthly data: {response}")
        else:
            self.results.add_result("Start Mockup Monthly", False, 
                                  f"Status: {status}, Response: {response}")

        # Test half-yearly subscription
        half_yearly_data = {"subscription_type": "half_yearly"}
        success, response, status = await self.make_request("POST", "/subscription/start-mockup", 
                                                          half_yearly_data, headers)
        
        if success and status == 200:
            if (response.get("success") and 
                response.get("subscription", {}).get("type") == "half_yearly" and
                response.get("subscription", {}).get("status") == "active" and
                response.get("subscription", {}).get("days_remaining") == 180):
                self.results.add_result("Start Mockup Half-Yearly", True, 
                                      f"Half-yearly subscription: ₹450, 180 days")
                print(f"   ✅ Half-yearly subscription activated: ₹450, 180 days")
            else:
                self.results.add_result("Start Mockup Half-Yearly", False, 
                                      f"Invalid half-yearly data: {response}")
        else:
            self.results.add_result("Start Mockup Half-Yearly", False, 
                                  f"Status: {status}, Response: {response}")

        # Test invalid subscription type
        invalid_data = {"subscription_type": "invalid"}
        success, response, status = await self.make_request("POST", "/subscription/start-mockup", 
                                                          invalid_data, headers)
        
        if status == 400:
            self.results.add_result("Start Mockup Invalid Type", True, 
                                  f"Correctly rejected invalid type")
            print(f"   ✅ Invalid subscription type correctly rejected")
        else:
            self.results.add_result("Start Mockup Invalid Type", False, 
                                  f"Should reject invalid type with 400, got {status}")

        # Test without authentication
        success, response, status = await self.make_request("POST", "/subscription/start-mockup", 
                                                          monthly_data, {})
        
        if status in [401, 403]:
            self.results.add_result("Start Mockup - No Auth", True, 
                                  f"Correctly rejected with status {status}")
        else:
            self.results.add_result("Start Mockup - No Auth", False, 
                                  f"Should reject unauthorized access, got {status}")

        # ============================================================================
        # 4. USER PROFILE WITH SUBSCRIPTION FIELDS
        # ============================================================================
        print(f"{Colors.CYAN}👤 Testing User Profile Subscription Integration{Colors.END}")
        
        success, response, status = await self.make_request("GET", "/user/profile", None, headers)
        
        if success and status == 200:
            subscription_fields = [
                "subscription_type", "subscription_status", "subscription_start_date",
                "subscription_end_date", "trial_started"
            ]
            
            if all(field in response for field in subscription_fields):
                self.results.add_result("User Profile Subscription Fields", True, 
                                      f"All subscription fields present: {response['subscription_type']}")
                print(f"   ✅ Profile includes subscription data: {response['subscription_type']}")
            else:
                missing_fields = [field for field in subscription_fields if field not in response]
                self.results.add_result("User Profile Subscription Fields", False, 
                                      f"Missing fields: {missing_fields}")
        else:
            self.results.add_result("User Profile Subscription Fields", False, 
                                  f"Status: {status}, Response: {response}")

        # ============================================================================
        # 5. COMPLETE USER FLOW TEST
        # ============================================================================
        print(f"{Colors.CYAN}🔄 Testing Complete New User Subscription Flow{Colors.END}")
        
        # Create a new user for flow testing
        flow_email = f"flow.test.{datetime.now().timestamp()}@pookie4u.com"
        
        # Register new user
        flow_user_data = {
            "email": flow_email,
            "password": "FlowTest123!",
            "name": "Flow Tester"
        }
        
        success, response, status = await self.make_request("POST", "/auth/register", flow_user_data, {})
        
        if success and status == 200:
            flow_token = response.get("access_token")
            flow_headers = {"Authorization": f"Bearer {flow_token}"}
            
            self.results.add_result("Flow - User Registration", True, "New user registered")
            print(f"   ✅ New user registered for flow test")
            
            # Check initial subscription status
            success, response, status = await self.make_request("GET", "/subscription/status", None, flow_headers)
            
            if success and status == 200:
                subscription = response["subscription"]
                if (subscription["type"] == "none" and 
                    subscription["status"] == "inactive" and
                    subscription["can_start_trial"]):
                    
                    self.results.add_result("Flow - Initial Status", True, 
                                          "Initial status correct: no subscription, can start trial")
                    print(f"   ✅ Initial status: no subscription, can start trial")
                    
                    # Start free trial
                    success, response, status = await self.make_request("POST", "/subscription/start-trial", 
                                                                      None, flow_headers)
                    
                    if success and status == 200:
                        trial_data = response
                        if (trial_data["subscription"]["type"] == "trial" and
                            trial_data["subscription"]["status"] == "active" and
                            trial_data["subscription"]["days_remaining"] == 14):
                            
                            self.results.add_result("Flow - Start Trial", True, 
                                                  "Trial started successfully")
                            print(f"   ✅ Trial started: 14 days active")
                            
                            # Try starting trial again (should fail)
                            success, response, status = await self.make_request("POST", "/subscription/start-trial", 
                                                                              None, flow_headers)
                            
                            if status == 400:
                                self.results.add_result("Flow - Duplicate Trial", True, 
                                                      "Correctly rejected duplicate trial")
                                print(f"   ✅ Duplicate trial correctly rejected")
                            else:
                                self.results.add_result("Flow - Duplicate Trial", False, 
                                                      f"Should reject duplicate trial, got {status}")
                        else:
                            self.results.add_result("Flow - Start Trial", False, 
                                                  f"Trial start failed: {trial_data}")
                    else:
                        self.results.add_result("Flow - Start Trial", False, 
                                              f"Trial request failed: {status}")
                else:
                    self.results.add_result("Flow - Initial Status", False, 
                                          f"Incorrect initial status: {subscription}")
            else:
                self.results.add_result("Flow - Initial Status", False, 
                                      f"Status request failed: {status}")
        else:
            self.results.add_result("Flow - User Registration", False, 
                                  f"Registration failed: {status}")

        print(f"{Colors.GREEN}✅ Subscription system testing completed{Colors.END}")

    # ============================================================================
    # COMPREHENSIVE TESTING ORCHESTRATION
    # ============================================================================
    
    async def run_comprehensive_audit(self):
        """Run complete backend audit as requested"""
        print(f"{Colors.BOLD}{Colors.WHITE}")
        print("=" * 80)
        print("🔍 POOKIE4U COMPREHENSIVE BACKEND API AUDIT - PHASE 1")
        print("=" * 80)
        print(f"{Colors.END}")
        print(f"📊 Testing ALL backend endpoints for production readiness")
        print(f"🎯 Focus: User-reported issues, OAuth, gift images, full feature coverage")
        print(f"🌐 Backend URL: {BASE_URL}")
        print(f"👤 Test User: {TEST_USER_EMAIL}")
        
        try:
            # Phase 1: Authentication & User Setup
            await self.test_user_registration()
            await self.test_user_login()
            await self.test_mobile_otp_system()
            await self.test_google_oauth_endpoints()
            
            # Phase 2: User Profile Management
            await self.test_user_profile_management()
            
            # Phase 3: AI Task System (Core Feature)
            await self.test_ai_task_system()
            await self.test_task_completion_system()
            
            # Phase 4: Enhanced Calendar & Events
            await self.test_enhanced_calendar_system()
            
            # Phase 5: Critical - Gifts API (User Reported Issues)
            await self.test_gifts_api_comprehensive()
            
            # Phase 6: Messages System
            await self.test_messages_system()
            
            # Phase 7: AI Personalization Features (NEW)
            await self.test_ai_personalization_features()
            
            # Phase 8: Subscription/Payment System
            await self.test_subscription_system()
            
        except Exception as e:
            print(f"{Colors.RED}❌ CRITICAL ERROR during testing: {str(e)}{Colors.END}")
            traceback.print_exc()
            self.results.add_result("Test Suite Execution", False, str(e), is_critical=True)
    
    def generate_audit_report(self):
        """Generate comprehensive audit report"""
        print(f"\n{Colors.BOLD}{Colors.WHITE}")
        print("=" * 80)
        print("📋 COMPREHENSIVE BACKEND AUDIT REPORT")
        print("=" * 80)
        print(f"{Colors.END}")
        
        success_rate = self.results.get_success_rate()
        
        print(f"📊 {Colors.BOLD}OVERALL RESULTS:{Colors.END}")
        print(f"   Total Tests: {self.results.total_tests}")
        print(f"   Passed: {Colors.GREEN}{self.results.passed_tests}{Colors.END}")
        print(f"   Failed: {Colors.RED}{self.results.failed_tests}{Colors.END}")
        print(f"   Success Rate: {Colors.GREEN if success_rate >= 80 else Colors.YELLOW if success_rate >= 60 else Colors.RED}{success_rate:.1f}%{Colors.END}")
        
        if self.results.critical_issues:
            print(f"\n🚨 {Colors.RED}{Colors.BOLD}CRITICAL ISSUES FOUND:{Colors.END}")
            for issue in self.results.critical_issues:
                print(f"   {issue}")
        
        print(f"\n✅ {Colors.GREEN}{Colors.BOLD}WORKING FEATURES ({len(self.results.working_features)}):{Colors.END}")
        for feature in self.results.working_features[:10]:  # Show first 10
            print(f"   {feature}")
        if len(self.results.working_features) > 10:
            print(f"   ... and {len(self.results.working_features) - 10} more")
        
        if self.results.broken_features:
            print(f"\n❌ {Colors.RED}{Colors.BOLD}BROKEN/ISSUES FOUND ({len(self.results.broken_features)}):{Colors.END}")
            for feature in self.results.broken_features:
                print(f"   {feature}")
        
        # System-wise breakdown
        print(f"\n📋 {Colors.BOLD}SYSTEM-WISE ASSESSMENT:{Colors.END}")
        
        systems = {
            "Authentication System": ["User Registration", "User Login", "Mobile OTP", "Google OAuth"],
            "AI Task Generation": ["Daily Tasks Generation", "Weekly Tasks Generation", "Task Completion"],
            "Calendar & Events": ["Events Retrieval", "Custom Event Creation", "Events Pagination"],
            "Gifts API": ["Gifts API Response", "Unique Product Images", "Amazon Product Data"],
            "Messages System": ["Messages Category", "Daily Messages"],
            "Profile Management": ["User Profile Retrieval", "Partner Profile Update"],
            "Subscription System": ["Subscription Creation", "Payment Verification"]
        }
        
        for system, tests in systems.items():
            system_results = [r for r in self.results.results if any(test in r["test"] for test in tests)]
            if system_results:
                passed = sum(1 for r in system_results if r["success"])
                total = len(system_results)
                rate = (passed / total * 100) if total > 0 else 0
                status = "🟢 WORKING" if rate >= 80 else "🟡 PARTIAL" if rate >= 50 else "🔴 BROKEN"
                print(f"   {status} {system}: {passed}/{total} ({rate:.0f}%)")
        
        print(f"\n🎯 {Colors.BOLD}KEY FINDINGS:{Colors.END}")
        
        # Check specific user-reported issues
        gift_images_ok = any("Unique Product Images" in r["test"] and r["success"] for r in self.results.results)
        oauth_ok = any("Google OAuth" in r["test"] and r["success"] for r in self.results.results)
        
        print(f"   🎁 Gift Images Issue: {'✅ RESOLVED' if gift_images_ok else '❌ STILL BROKEN'}")
        print(f"   🔐 Google OAuth: {'✅ WORKING' if oauth_ok else '❌ NEEDS SETUP'}")
        
        # Production readiness assessment
        critical_systems_working = (
            success_rate >= 70 and
            not any(r["critical"] and not r["success"] for r in self.results.results)
        )
        
        print(f"\n🚀 {Colors.BOLD}PRODUCTION READINESS:{Colors.END}")
        if critical_systems_working:
            print(f"   {Colors.GREEN}✅ READY FOR PRODUCTION{Colors.END} - Core systems functional")
        else:
            print(f"   {Colors.RED}❌ NOT READY{Colors.END} - Critical issues need resolution")
        
        return {
            "success_rate": success_rate,
            "total_tests": self.results.total_tests,
            "passed_tests": self.results.passed_tests,
            "failed_tests": self.results.failed_tests,
            "critical_issues": self.results.critical_issues,
            "working_features": self.results.working_features,
            "broken_features": self.results.broken_features,
            "production_ready": critical_systems_working
        }

async def main():
    """Main testing function"""
    async with Pookie4uAPITester() as tester:
        await tester.run_comprehensive_audit()
        report = tester.generate_audit_report()
        
        # Return summary for test_result.md update
        return {
            "success_rate": report["success_rate"],
            "total_tests": report["total_tests"],
            "critical_issues": report["critical_issues"],
            "working_features": len(report["working_features"]),
            "broken_features": len(report["broken_features"]),
            "production_ready": report["production_ready"]
        }

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        print(f"\n{Colors.BOLD}🏁 AUDIT COMPLETE{Colors.END}")
        print(f"Success Rate: {result['success_rate']:.1f}%")
        print(f"Production Ready: {'Yes' if result['production_ready'] else 'No'}")
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Testing interrupted by user{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}❌ Fatal error: {str(e)}{Colors.END}")
        sys.exit(1)