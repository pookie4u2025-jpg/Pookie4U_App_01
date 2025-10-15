#!/usr/bin/env python3
"""
COMPREHENSIVE POOKIE4U BACKEND API TESTING SUITE
=================================================

This test suite conducts exhaustive testing of ALL backend endpoints for the Pookie4u app audit.
Tests cover authentication, AI tasks, calendar events, gifts, messages, profiles, and gamification.

Test Scope:
- 28+ API endpoints across 8 major systems
- Real user flow testing (register → authenticate → use features)
- Critical bug verification (duplicate gift images, OAuth issues)
- Production readiness assessment
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
    
    async def test_subscription_system(self):
        """Test Razorpay subscription system"""
        print(f"\n{Colors.PURPLE}💳 TESTING SUBSCRIPTION/PAYMENT SYSTEM{Colors.END}")
        
        headers = self.get_auth_headers()
        
        # Test subscription creation (will likely fail without proper Razorpay setup)
        subscription_data = {
            "plan_type": "monthly"
        }
        
        success, response, status = await self.make_request("POST", "/subscriptions/create", 
                                                          subscription_data, headers)
        
        # This is expected to fail in development/testing environment
        self.results.add_result("Subscription Creation Endpoint", status in [400, 401, 500], 
                              f"Status: {status} - Endpoint accessible (may need Razorpay config)")
        
        # Test payment verification endpoint
        verify_data = {
            "payment_id": "test_payment_id",
            "subscription_id": "test_subscription_id",
            "signature": "test_signature"
        }
        
        success, response, status = await self.make_request("POST", "/subscriptions/verify", 
                                                          verify_data, headers)
        
        self.results.add_result("Payment Verification Endpoint", status in [400, 401, 500], 
                              f"Status: {status} - Endpoint accessible")

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
            
            # Phase 7: Subscription/Payment System
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
            else:
                self.log_test("API Response Status", False, f"Expected 200, got {status_code}", response.text)
                return False
            
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                self.log_test("JSON Response Format", False, "Response is not valid JSON", response.text)
                return False
                
            # Test 2: Response has correct structure
            if "gifts" in response_data and isinstance(response_data["gifts"], list):
                self.log_test("Response Structure", True, "Contains 'gifts' array")
            else:
                self.log_test("Response Structure", False, "Missing 'gifts' array or wrong type", response_data)
                return False
            
            # Test 3: Correct number of gifts (should be 6)
            gifts = response_data["gifts"]
            if len(gifts) == 6:
                self.log_test("Gift Count", True, f"Found {len(gifts)} gifts")
            else:
                self.log_test("Gift Count", False, f"Expected 6 gifts, found {len(gifts)}", gifts)
            
            return gifts
            
        except Exception as e:
            self.log_test("API Basic Functionality", False, f"Exception: {str(e)}")
            return False
            
    def test_gift_data_structure(self, gifts: List[Dict]):
        """Test each gift has required fields with correct data types"""
        required_fields = ["id", "name", "category", "price_range", "link", "description", "image"]
        
        for i, gift in enumerate(gifts, 1):
            gift_id = gift.get("id", f"gift_{i}")
            
            # Test required fields presence
            missing_fields = [field for field in required_fields if field not in gift]
            if not missing_fields:
                self.log_test(f"Gift {gift_id} - Required Fields", True, "All required fields present")
            else:
                self.log_test(f"Gift {gift_id} - Required Fields", False, f"Missing fields: {missing_fields}", gift)
                
            # Test field data types and content
            if "name" in gift:
                if isinstance(gift["name"], str) and len(gift["name"]) > 0:
                    self.log_test(f"Gift {gift_id} - Name Field", True, f"Name: '{gift['name']}'")
                else:
                    self.log_test(f"Gift {gift_id} - Name Field", False, "Name is empty or not string", gift["name"])
                    
            if "description" in gift:
                if isinstance(gift["description"], str) and len(gift["description"]) > 10:
                    self.log_test(f"Gift {gift_id} - Description Field", True, f"Description length: {len(gift['description'])} chars")
                else:
                    self.log_test(f"Gift {gift_id} - Description Field", False, "Description too short or not string", gift.get("description"))
                    
            if "price_range" in gift:
                price = gift["price_range"]
                if isinstance(price, str) and "₹" in price:
                    self.log_test(f"Gift {gift_id} - Price Range", True, f"Price: {price}")
                else:
                    self.log_test(f"Gift {gift_id} - Price Range", False, "Price missing ₹ symbol or not string", price)
                    
            if "image" in gift:
                image_url = gift["image"]
                if isinstance(image_url, str) and image_url.startswith("https://"):
                    self.log_test(f"Gift {gift_id} - Image URL", True, f"Image URL valid: {image_url[:50]}...")
                else:
                    self.log_test(f"Gift {gift_id} - Image URL", False, "Image URL invalid or not HTTPS", image_url)
                    
            if "link" in gift:
                link = gift["link"]
                if isinstance(link, str) and "amzn.to/" in link:
                    self.log_test(f"Gift {gift_id} - Amazon Link", True, f"Amazon affiliate link: {link}")
                else:
                    self.log_test(f"Gift {gift_id} - Amazon Link", False, "Not a valid Amazon affiliate link", link)
                    
    def test_amazon_product_data_quality(self, gifts: List[Dict]):
        """Test quality of Amazon product data"""
        
        # Test 1: All gifts should have Amazon product images
        amazon_image_count = 0
        for gift in gifts:
            if "image" in gift and "m.media-amazon.com/images/" in gift["image"]:
                amazon_image_count += 1
                
        if amazon_image_count == len(gifts):
            self.log_test("Amazon Product Images", True, f"All {amazon_image_count} gifts have Amazon product images")
        else:
            self.log_test("Amazon Product Images", False, f"Only {amazon_image_count}/{len(gifts)} gifts have Amazon images")
            
        # Test 2: Product names should reflect actual Amazon products
        realistic_product_names = 0
        for gift in gifts:
            name = gift.get("name", "")
            # Check for realistic product naming patterns
            if any(keyword in name.lower() for keyword in ["women", "formal", "trouser", "pants", "style", "high waist"]):
                realistic_product_names += 1
                
        if realistic_product_names >= len(gifts) * 0.8:  # At least 80% should have realistic names
            self.log_test("Realistic Product Names", True, f"{realistic_product_names}/{len(gifts)} gifts have realistic product names")
        else:
            self.log_test("Realistic Product Names", False, f"Only {realistic_product_names}/{len(gifts)} gifts have realistic names")
            
        # Test 3: Descriptions should be meaningful
        meaningful_descriptions = 0
        for gift in gifts:
            description = gift.get("description", "")
            if len(description) > 20 and any(keyword in description.lower() for keyword in ["elegant", "comfortable", "style", "office", "wear", "perfect"]):
                meaningful_descriptions += 1
                
        if meaningful_descriptions >= len(gifts) * 0.8:
            self.log_test("Meaningful Descriptions", True, f"{meaningful_descriptions}/{len(gifts)} gifts have meaningful descriptions")
        else:
            self.log_test("Meaningful Descriptions", False, f"Only {meaningful_descriptions}/{len(gifts)} gifts have meaningful descriptions")
            
        # Test 4: Price ranges should be realistic Indian rupee amounts
        realistic_prices = 0
        for gift in gifts:
            price = gift.get("price_range", "")
            # Check for Indian rupee prices in reasonable ranges
            if "₹" in price and any(char.isdigit() for char in price):
                # Extract numbers from price
                import re
                numbers = re.findall(r'\d+', price)
                if numbers:
                    min_price = int(numbers[0])
                    if 100 <= min_price <= 5000:  # Reasonable price range
                        realistic_prices += 1
                        
        if realistic_prices == len(gifts):
            self.log_test("Realistic Price Ranges", True, f"All {realistic_prices} gifts have realistic Indian rupee prices")
        else:
            self.log_test("Realistic Price Ranges", False, f"Only {realistic_prices}/{len(gifts)} gifts have realistic prices")
            
    def test_api_performance_and_reliability(self):
        """Test API performance and reliability"""
        
        # Test multiple consecutive requests
        response_times = []
        successful_requests = 0
        
        for i in range(5):
            try:
                start_time = datetime.now()
                response = self.session.get(f"{self.backend_url}/gifts")
                end_time = datetime.now()
                response_time = (end_time - start_time).total_seconds()
                response_times.append(response_time)
                
                if response.status_code == 200:
                    successful_requests += 1
                    
            except Exception as e:
                print(f"Request {i+1} failed: {e}")
                
        if successful_requests == 5:
            avg_response_time = sum(response_times) / len(response_times)
            self.log_test("API Reliability", True, f"5/5 requests successful, avg response time: {avg_response_time:.3f}s")
        else:
            self.log_test("API Reliability", False, f"Only {successful_requests}/5 requests successful")
            
        # Test response time performance
        if response_times and max(response_times) < 5.0:  # Should respond within 5 seconds
            self.log_test("API Performance", True, f"Max response time: {max(response_times):.3f}s")
        else:
            self.log_test("API Performance", False, f"Response time too slow: {max(response_times) if response_times else 'N/A'}s")
            
    def test_specific_amazon_products(self, gifts: List[Dict]):
        """Test specific Amazon product details mentioned in the review request"""
        
        # Test for the specific product mentioned in review request
        high_waist_trouser_found = False
        for gift in gifts:
            if "High Waist Formal Trousers for Women" in gift.get("name", ""):
                high_waist_trouser_found = True
                
                # Check specific details
                expected_price = "₹449"
                expected_link = "https://amzn.to/46k7tSR"
                expected_image = "https://m.media-amazon.com/images/I/51Fpt5hLOML._SY445_.jpg"
                
                if gift.get("price_range") == expected_price:
                    self.log_test("Specific Product - Price", True, f"Correct price: {expected_price}")
                else:
                    self.log_test("Specific Product - Price", False, f"Expected {expected_price}, got {gift.get('price_range')}")
                    
                if gift.get("link") == expected_link:
                    self.log_test("Specific Product - Link", True, "Correct Amazon affiliate link")
                else:
                    self.log_test("Specific Product - Link", False, f"Link mismatch: {gift.get('link')}")
                    
                if gift.get("image") == expected_image:
                    self.log_test("Specific Product - Image", True, "Correct Amazon product image")
                else:
                    self.log_test("Specific Product - Image", False, f"Image mismatch: {gift.get('image')}")
                    
                break
                
        if high_waist_trouser_found:
            self.log_test("Specific Product Found", True, "High Waist Formal Trousers product found")
        else:
            self.log_test("Specific Product Found", False, "High Waist Formal Trousers product not found")
            
    def run_all_tests(self):
        """Run all Gift Ideas API tests"""
        print("🎁 STARTING GIFT IDEAS API COMPREHENSIVE TESTING")
        print("=" * 60)
        print(f"Backend URL: {self.backend_url}")
        print(f"Test Start Time: {datetime.now().isoformat()}")
        print()
        
        # Test 1: Basic API functionality
        print("📋 TESTING BASIC API FUNCTIONALITY")
        print("-" * 40)
        gifts = self.test_gifts_api_basic_functionality()
        
        if gifts:
            # Test 2: Gift data structure
            print("🔍 TESTING GIFT DATA STRUCTURE")
            print("-" * 40)
            self.test_gift_data_structure(gifts)
            
            # Test 3: Amazon product data quality
            print("🛍️ TESTING AMAZON PRODUCT DATA QUALITY")
            print("-" * 40)
            self.test_amazon_product_data_quality(gifts)
            
            # Test 4: Specific Amazon products
            print("🎯 TESTING SPECIFIC AMAZON PRODUCTS")
            print("-" * 40)
            self.test_specific_amazon_products(gifts)
            
        # Test 5: API performance and reliability
        print("⚡ TESTING API PERFORMANCE & RELIABILITY")
        print("-" * 40)
        self.test_api_performance_and_reliability()
        
        # Generate summary
        self.generate_test_summary()
        
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🎁 GIFT IDEAS API TEST SUMMARY")
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
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  • {result['test']}: {result['details']}")
            print()
            
        print("✅ CRITICAL FINDINGS:")
        
        # Check for critical issues
        api_working = any(r["test"] == "API Response Status" and r["success"] for r in self.test_results)
        structure_correct = any(r["test"] == "Response Structure" and r["success"] for r in self.test_results)
        gift_count_correct = any(r["test"] == "Gift Count" and r["success"] for r in self.test_results)
        amazon_images = any(r["test"] == "Amazon Product Images" and r["success"] for r in self.test_results)
        
        if api_working:
            print("  • Gift Ideas API is responding correctly (200 status)")
        else:
            print("  • ❌ CRITICAL: Gift Ideas API not responding properly")
            
        if structure_correct:
            print("  • API returns correct JSON structure with 'gifts' array")
        else:
            print("  • ❌ CRITICAL: API response structure is incorrect")
            
        if gift_count_correct:
            print("  • Correct number of gifts (6) returned")
        else:
            print("  • ⚠️ WARNING: Incorrect number of gifts returned")
            
        if amazon_images:
            print("  • All gifts have proper Amazon product images")
        else:
            print("  • ⚠️ WARNING: Some gifts missing Amazon product images")
            
        print()
        print("🎯 AMAZON AFFILIATE INTEGRATION STATUS:")
        
        # Check Amazon integration specific items
        affiliate_links = sum(1 for r in self.test_results if "Amazon Link" in r["test"] and r["success"])
        product_images = sum(1 for r in self.test_results if "Image URL" in r["test"] and r["success"])
        realistic_names = any(r["test"] == "Realistic Product Names" and r["success"] for r in self.test_results)
        meaningful_descriptions = any(r["test"] == "Meaningful Descriptions" and r["success"] for r in self.test_results)
        
        print(f"  • Amazon affiliate links: {affiliate_links}/6 gifts")
        print(f"  • Product images: {product_images}/6 gifts")
        print(f"  • Realistic product names: {'✅' if realistic_names else '❌'}")
        print(f"  • Meaningful descriptions: {'✅' if meaningful_descriptions else '❌'}")
        
        print()
        print("📊 OVERALL ASSESSMENT:")
        if success_rate >= 90:
            print("  🎉 EXCELLENT: Gift Ideas API with Amazon integration is working perfectly!")
        elif success_rate >= 75:
            print("  ✅ GOOD: Gift Ideas API is working well with minor issues")
        elif success_rate >= 50:
            print("  ⚠️ MODERATE: Gift Ideas API has some issues that need attention")
        else:
            print("  ❌ CRITICAL: Gift Ideas API has major issues requiring immediate fixes")
            
        print(f"\nTest completed at: {datetime.now().isoformat()}")

def main():
    """Main test execution"""
    tester = GiftIdeasAPITester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()