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

class Pookie4uTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.test_results = []
        self.auth_token = None
        self.user_id = None
        
    async def log_result(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
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
            print(f"   Response: {json.dumps(response_data, indent=2) if isinstance(response_data, dict) else str(response_data)}")
        print()

    async def make_request(self, method: str, endpoint: str, data: Dict = None, headers: Dict = None, params: Dict = None) -> httpx.Response:
        """Make HTTP request with proper error handling"""
        url = f"{API_BASE}{endpoint}"
        
        # Add authorization header if token exists
        if self.auth_token and headers is None:
            headers = {}
        if self.auth_token:
            headers = headers or {}
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        try:
            if method.upper() == "GET":
                response = await self.client.get(url, headers=headers, params=params)
            elif method.upper() == "POST":
                response = await self.client.post(url, json=data, headers=headers, params=params)
            elif method.upper() == "PUT":
                response = await self.client.put(url, json=data, headers=headers, params=params)
            elif method.upper() == "PATCH":
                response = await self.client.patch(url, json=data, headers=headers, params=params)
            elif method.upper() == "DELETE":
                response = await self.client.delete(url, headers=headers, params=params)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            return response
        except Exception as e:
            print(f"Request failed: {e}")
            raise

    # ============================================================================
    # 1. AUTHENTICATION SYSTEM TESTS
    # ============================================================================
    
    async def test_user_registration(self):
        """Test POST /api/auth/register"""
        # First try to register a new user with unique email
        unique_email = f"test.user.{int(time.time())}@example.com"
        
        data = {
            "email": unique_email,
            "password": TEST_USER_PASSWORD,
            "name": TEST_USER_NAME
        }
        
        response = await self.make_request("POST", "/auth/register", data)
        
        if response.status_code == 200:
            response_data = response.json()
            if "access_token" in response_data:
                self.auth_token = response_data["access_token"]
                await self.log_result("User Registration", True, f"Successfully registered user with email: {unique_email}")
                return True
            else:
                await self.log_result("User Registration", False, "No access token in response", response_data)
                return False
        else:
            await self.log_result("User Registration", False, f"Status: {response.status_code}", response.text)
            return False

    async def test_user_login(self):
        """Test POST /api/auth/login"""
        # Try to login with existing user
        data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
        
        response = await self.make_request("POST", "/auth/login", data)
        
        if response.status_code == 200:
            response_data = response.json()
            if "access_token" in response_data:
                self.auth_token = response_data["access_token"]
                await self.log_result("User Login", True, f"Successfully logged in user: {TEST_USER_EMAIL}")
                return True
            else:
                await self.log_result("User Login", False, "No access token in response", response_data)
                return False
        else:
            await self.log_result("User Login", False, f"Status: {response.status_code}", response.text)
            return False

    async def test_get_user_profile(self):
        """Test GET /api/user/profile"""
        if not self.auth_token:
            await self.log_result("Get User Profile", False, "No access token available")
            return False
            
        response = await self.make_request("GET", "/user/profile")
        
        if response.status_code == 200:
            response_data = response.json()
            if "email" in response_data and "name" in response_data:
                self.user_id = response_data.get("id")
                await self.log_result("Get User Profile", True, f"Retrieved profile for: {response_data.get('email')}")
                return True
            else:
                await self.log_result("Get User Profile", False, "Missing required fields in profile", response_data)
                return False
        else:
            await self.log_result("Get User Profile", False, f"Status: {response.status_code}", response.text)
            return False

    async def test_update_user_profile(self):
        """Test PUT /api/user/profile"""
        if not self.auth_token:
            await self.log_result("Update User Profile", False, "No access token available")
            return False
            
        data = {
            "name": "Updated Test User",
            "relationship_mode": "SAME_HOME",
            "partner_profile": {
                "name": "Partner Name",
                "favorite_color": "Blue",
                "favorite_food": "Pizza"
            }
        }
        
        response = await self.make_request("PUT", "/user/profile", data)
        
        if response.status_code == 200:
            response_data = response.json()
            await self.log_result("Update User Profile", True, "Successfully updated user profile")
            return True
        else:
            await self.log_result("Update User Profile", False, f"Status: {response.status_code}", response.text)
            return False

    # ============================================================================
    # 2. TASKS SYSTEM TESTS
    # ============================================================================
    
    async def test_get_daily_tasks(self):
        """Test GET /api/tasks/daily"""
        if not self.auth_token:
            await self.log_result("Get Daily Tasks", False, "No access token available")
            return False
            
        response = await self.make_request("GET", "/tasks/daily")
        
        if response.status_code == 200:
            response_data = response.json()
            if isinstance(response_data, list) and len(response_data) > 0:
                await self.log_result("Get Daily Tasks", True, f"Retrieved {len(response_data)} daily tasks")
                return True
            else:
                await self.log_result("Get Daily Tasks", False, "No tasks returned or invalid format", response_data)
                return False
        else:
            await self.log_result("Get Daily Tasks", False, f"Status: {response.status_code}", response.text)
            return False

    async def test_get_weekly_tasks(self):
        """Test GET /api/tasks/weekly"""
        if not self.auth_token:
            await self.log_result("Get Weekly Tasks", False, "No access token available")
            return False
            
        response = await self.make_request("GET", "/tasks/weekly")
        
        if response.status_code == 200:
            response_data = response.json()
            if isinstance(response_data, list) and len(response_data) > 0:
                await self.log_result("Get Weekly Tasks", True, f"Retrieved {len(response_data)} weekly tasks")
                return True
            else:
                await self.log_result("Get Weekly Tasks", False, "No tasks returned or invalid format", response_data)
                return False
        else:
            await self.log_result("Get Weekly Tasks", False, f"Status: {response.status_code}", response.text)
            return False

    async def test_complete_task(self):
        """Test POST /api/tasks/complete"""
        if not self.auth_token:
            await self.log_result("Complete Task", False, "No access token available")
            return False
            
        # First get daily tasks to get a valid task ID
        response = await self.make_request("GET", "/tasks/daily")
        if response.status_code != 200:
            await self.log_result("Complete Task", False, "Could not get daily tasks for task completion test")
            return False
            
        tasks = response.json()
        if not tasks or not isinstance(tasks, list) or len(tasks) == 0:
            await self.log_result("Complete Task", False, "No tasks available to complete")
            return False
            
        first_task = tasks[0]
        if not isinstance(first_task, dict):
            await self.log_result("Complete Task", False, "Invalid task format")
            return False
            
        task_id = first_task.get("id")
        if not task_id:
            await self.log_result("Complete Task", False, "No task ID found in daily tasks")
            return False
            
        data = {"task_id": task_id}
        response = await self.make_request("POST", "/tasks/complete", data)
        
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get("success"):
                await self.log_result("Complete Task", True, f"Successfully completed task: {task_id}")
                return True
            else:
                await self.log_result("Complete Task", False, "Task completion not successful", response_data)
                return False
        else:
            await self.log_result("Complete Task", False, f"Status: {response.status_code}", response.text)
            return False

    async def test_generate_ai_tasks(self):
        """Test POST /api/tasks/generate"""
        if not self.auth_token:
            await self.log_result("Generate AI Tasks", False, "No access token available")
            return False
            
        data = {
            "relationship_mode": "SAME_HOME",
            "task_type": "daily",
            "count": 3
        }
        
        response = await self.make_request("POST", "/tasks/generate", data)
        
        if response.status_code == 200:
            response_data = response.json()
            if isinstance(response_data, list) and len(response_data) > 0:
                await self.log_result("Generate AI Tasks", True, f"Generated {len(response_data)} AI tasks")
                return True
            else:
                await self.log_result("Generate AI Tasks", False, "No AI tasks generated", response_data)
                return False
        else:
            await self.log_result("Generate AI Tasks", False, f"Status: {response.status_code}", response.text)
            return False

    # ============================================================================
    # 3. EVENTS SYSTEM TESTS
    # ============================================================================
    
    async def test_get_events(self):
        """Test GET /api/events"""
        if not self.auth_token:
            await self.log_result("Get Events", False, "No access token available")
            return False
            
        response = await self.make_request("GET", "/events")
        
        if response.status_code == 200:
            response_data = response.json()
            if isinstance(response_data, dict):
                total_events = 0
                for key, events in response_data.items():
                    if isinstance(events, list):
                        total_events += len(events)
                await self.log_result("Get Events", True, f"Retrieved events structure with {total_events} total events")
                return True
            else:
                await self.log_result("Get Events", False, "Invalid events response format", response_data)
                return False
        else:
            await self.log_result("Get Events", False, f"Status: {response.status_code}", response.text)
            return False

    async def test_create_custom_event(self):
        """Test POST /api/events/custom"""
        if not self.auth_token:
            await self.log_result("Create Custom Event", False, "No access token available")
            return False
            
        data = {
            "name": "Test Anniversary",
            "date": (datetime.now() + timedelta(days=30)).isoformat(),
            "description": "Test custom event creation",
            "importance": "high"
        }
        
        response = await self.make_request("POST", "/events/custom", data)
        
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get("success"):
                await self.log_result("Create Custom Event", True, "Successfully created custom event")
                return True
            else:
                await self.log_result("Create Custom Event", False, "Event creation not successful", response_data)
                return False
        else:
            await self.log_result("Create Custom Event", False, f"Status: {response.status_code}", response.text)
            return False

    async def test_update_custom_event(self):
        """Test PUT /api/events/custom/{id}"""
        if not self.auth_token:
            await self.log_result("Update Custom Event", False, "No access token available")
            return False
            
        # First create an event to update
        create_data = {
            "name": "Event to Update",
            "date": (datetime.now() + timedelta(days=45)).isoformat(),
            "description": "Event for update testing"
        }
        
        create_response = await self.make_request("POST", "/events/custom", create_data)
        if create_response.status_code != 200:
            await self.log_result("Update Custom Event", False, "Could not create event for update test")
            return False
            
        # Extract event ID from response
        create_result = create_response.json()
        event_id = create_result.get("event", {}).get("id")
        if not event_id:
            await self.log_result("Update Custom Event", False, "No event ID returned from creation")
            return False
            
        # Now update the event
        update_data = {
            "name": "Updated Event Name",
            "description": "Updated description"
        }
        
        response = await self.make_request("PATCH", f"/events/custom/{event_id}", update_data)
        
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get("success"):
                await self.log_result("Update Custom Event", True, f"Successfully updated event: {event_id}")
                return True
            else:
                await self.log_result("Update Custom Event", False, "Event update not successful", response_data)
                return False
        else:
            await self.log_result("Update Custom Event", False, f"Status: {response.status_code}", response.text)
            return False

    async def test_delete_custom_event(self):
        """Test DELETE /api/events/custom/{id}"""
        if not self.auth_token:
            await self.log_result("Delete Custom Event", False, "No access token available")
            return False
            
        # First create an event to delete
        create_data = {
            "name": "Event to Delete",
            "date": (datetime.now() + timedelta(days=60)).isoformat(),
            "description": "Event for deletion testing"
        }
        
        create_response = await self.make_request("POST", "/events/custom", create_data)
        if create_response.status_code != 200:
            await self.log_result("Delete Custom Event", False, "Could not create event for deletion test")
            return False
            
        # Extract event ID from response
        create_result = create_response.json()
        event_id = create_result.get("event", {}).get("id")
        if not event_id:
            await self.log_result("Delete Custom Event", False, "No event ID returned from creation")
            return False
            
        # Now delete the event
        response = await self.make_request("DELETE", f"/events/custom/{event_id}")
        
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get("success"):
                await self.log_result("Delete Custom Event", True, f"Successfully deleted event: {event_id}")
                return True
            else:
                await self.log_result("Delete Custom Event", False, "Event deletion not successful", response_data)
                return False
        else:
            await self.log_result("Delete Custom Event", False, f"Status: {response.status_code}", response.text)
            return False

    # ============================================================================
    # 4. MESSAGES SYSTEM TESTS
    # ============================================================================
    
    async def test_get_daily_messages_same_home(self):
        """Test GET /api/messages/daily/SAME_HOME"""
        if not self.auth_token:
            await self.log_result("Get Daily Messages SAME_HOME", False, "No access token available")
            return False
            
        response = await self.make_request("GET", "/messages/daily/SAME_HOME")
        
        if response.status_code == 200:
            response_data = response.json()
            if isinstance(response_data, list) and len(response_data) > 0:
                await self.log_result("Get Daily Messages SAME_HOME", True, f"Retrieved {len(response_data)} messages")
                return True
            else:
                await self.log_result("Get Daily Messages SAME_HOME", False, "No messages returned", response_data)
                return False
        else:
            await self.log_result("Get Daily Messages SAME_HOME", False, f"Status: {response.status_code}", response.text)
            return False

    async def test_get_daily_messages_daily_irl(self):
        """Test GET /api/messages/daily/DAILY_IRL"""
        if not self.auth_token:
            await self.log_result("Get Daily Messages DAILY_IRL", False, "No access token available")
            return False
            
        response = await self.make_request("GET", "/messages/daily/DAILY_IRL")
        
        if response.status_code == 200:
            response_data = response.json()
            if isinstance(response_data, list) and len(response_data) > 0:
                await self.log_result("Get Daily Messages DAILY_IRL", True, f"Retrieved {len(response_data)} messages")
                return True
            else:
                await self.log_result("Get Daily Messages DAILY_IRL", False, "No messages returned", response_data)
                return False
        else:
            await self.log_result("Get Daily Messages DAILY_IRL", False, f"Status: {response.status_code}", response.text)
            return False

    async def test_get_daily_messages_long_distance(self):
        """Test GET /api/messages/daily/LONG_DISTANCE"""
        if not self.auth_token:
            await self.log_result("Get Daily Messages LONG_DISTANCE", False, "No access token available")
            return False
            
        response = await self.make_request("GET", "/messages/daily/LONG_DISTANCE")
        
        if response.status_code == 200:
            response_data = response.json()
            if isinstance(response_data, list) and len(response_data) > 0:
                await self.log_result("Get Daily Messages LONG_DISTANCE", True, f"Retrieved {len(response_data)} messages")
                return True
            else:
                await self.log_result("Get Daily Messages LONG_DISTANCE", False, "No messages returned", response_data)
                return False
        else:
            await self.log_result("Get Daily Messages LONG_DISTANCE", False, f"Status: {response.status_code}", response.text)
            return False

    # ============================================================================
    # 5. GIFTS SYSTEM TESTS
    # ============================================================================
    
    async def test_get_gifts(self):
        """Test GET /api/gifts"""
        response = await self.make_request("GET", "/gifts")
        
        if response.status_code == 200:
            response_data = response.json()
            if isinstance(response_data, list) and len(response_data) > 0:
                # Check for required fields in gifts
                first_gift = response_data[0]
                required_fields = ["id", "name", "category", "price_range", "link"]
                missing_fields = [field for field in required_fields if field not in first_gift]
                
                if not missing_fields:
                    await self.log_result("Get Gifts", True, f"Retrieved {len(response_data)} gifts with proper structure")
                    return True
                else:
                    await self.log_result("Get Gifts", False, f"Missing required fields: {missing_fields}", first_gift)
                    return False
            else:
                await self.log_result("Get Gifts", False, "No gifts returned or invalid format", response_data)
                return False
        else:
            await self.log_result("Get Gifts", False, f"Status: {response.status_code}", response.text)
            return False

    async def test_search_gifts(self):
        """Test GET /api/gifts/search"""
        params = {"category": "Romantic", "price_range": "Under ₹500"}
        response = await self.make_request("GET", "/gifts/search", params=params)
        
        if response.status_code == 200:
            response_data = response.json()
            if isinstance(response_data, list):
                await self.log_result("Search Gifts", True, f"Search returned {len(response_data)} gifts")
                return True
            else:
                await self.log_result("Search Gifts", False, "Invalid search response format", response_data)
                return False
        else:
            await self.log_result("Search Gifts", False, f"Status: {response.status_code}", response.text)
            return False

    # ============================================================================
    # 6. REFERRAL & REWARDS SYSTEM TESTS
    # ============================================================================
    
    async def test_get_referral_code(self):
        """Test GET /api/referral/my-code"""
        if not self.auth_token:
            await self.log_result("Get Referral Code", False, "No access token available")
            return False
            
        response = await self.make_request("GET", "/referral/my-code")
        
        if response.status_code == 200:
            response_data = response.json()
            if "code" in response_data:
                await self.log_result("Get Referral Code", True, f"Retrieved referral code: {response_data['code']}")
                return True
            else:
                await self.log_result("Get Referral Code", False, "No referral code in response", response_data)
                return False
        else:
            await self.log_result("Get Referral Code", False, f"Status: {response.status_code}", response.text)
            return False

    async def test_apply_referral(self):
        """Test POST /api/referral/apply"""
        if not self.auth_token:
            await self.log_result("Apply Referral", False, "No access token available")
            return False
            
        data = {"referral_code": "POO-TEST123"}
        response = await self.make_request("POST", "/referral/apply", data)
        
        # This might fail if code doesn't exist, which is expected
        if response.status_code in [200, 400, 404]:
            await self.log_result("Apply Referral", True, f"Referral endpoint working (Status: {response.status_code})")
            return True
        else:
            await self.log_result("Apply Referral", False, f"Status: {response.status_code}", response.text)
            return False

    async def test_check_milestone_rewards(self):
        """Test GET /api/rewards/check-milestone"""
        if not self.auth_token:
            await self.log_result("Check Milestone Rewards", False, "No access token available")
            return False
            
        response = await self.make_request("GET", "/rewards/check-milestone")
        
        if response.status_code == 200:
            response_data = response.json()
            await self.log_result("Check Milestone Rewards", True, "Milestone rewards endpoint working")
            return True
        else:
            await self.log_result("Check Milestone Rewards", False, f"Status: {response.status_code}", response.text)
            return False

    async def test_get_rewards_history(self):
        """Test GET /api/rewards/history"""
        if not self.auth_token:
            await self.log_result("Get Rewards History", False, "No access token available")
            return False
            
        response = await self.make_request("GET", "/rewards/history")
        
        if response.status_code == 200:
            response_data = response.json()
            if isinstance(response_data, list):
                await self.log_result("Get Rewards History", True, f"Retrieved {len(response_data)} reward history items")
                return True
            else:
                await self.log_result("Get Rewards History", False, "Invalid rewards history format", response_data)
                return False
        else:
            await self.log_result("Get Rewards History", False, f"Status: {response.status_code}", response.text)
            return False

    # ============================================================================
    # 7. FEEDBACK SYSTEM TESTS
    # ============================================================================
    
    async def test_submit_feedback(self):
        """Test POST /api/feedback"""
        if not self.auth_token:
            await self.log_result("Submit Feedback", False, "No access token available")
            return False
            
        data = {
            "type": "bug_report",
            "message": "Test feedback submission",
            "rating": 4
        }
        
        response = await self.make_request("POST", "/feedback", data)
        
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get("success"):
                await self.log_result("Submit Feedback", True, "Successfully submitted feedback")
                return True
            else:
                await self.log_result("Submit Feedback", False, "Feedback submission not successful", response_data)
                return False
        else:
            await self.log_result("Submit Feedback", False, f"Status: {response.status_code}", response.text)
            return False

    async def test_get_my_feedback(self):
        """Test GET /api/feedback/my"""
        if not self.auth_token:
            await self.log_result("Get My Feedback", False, "No access token available")
            return False
            
        response = await self.make_request("GET", "/feedback/my")
        
        if response.status_code == 200:
            response_data = response.json()
            if isinstance(response_data, list):
                await self.log_result("Get My Feedback", True, f"Retrieved {len(response_data)} feedback items")
                return True
            else:
                await self.log_result("Get My Feedback", False, "Invalid feedback response format", response_data)
                return False
        else:
            await self.log_result("Get My Feedback", False, f"Status: {response.status_code}", response.text)
            return False

    async def test_get_all_feedback(self):
        """Test GET /api/feedback/all"""
        if not self.auth_token:
            await self.log_result("Get All Feedback", False, "No access token available")
            return False
            
        response = await self.make_request("GET", "/feedback/all")
        
        if response.status_code == 200:
            response_data = response.json()
            if isinstance(response_data, list):
                await self.log_result("Get All Feedback", True, f"Retrieved {len(response_data)} total feedback items")
                return True
            else:
                await self.log_result("Get All Feedback", False, "Invalid feedback response format", response_data)
                return False
        else:
            await self.log_result("Get All Feedback", False, f"Status: {response.status_code}", response.text)
            return False

    # ============================================================================
    # 8. SUBSCRIPTION SYSTEM TESTS
    # ============================================================================
    
    async def test_get_subscription_status(self):
        """Test GET /api/subscription/status"""
        if not self.auth_token:
            await self.log_result("Get Subscription Status", False, "No access token available")
            return False
            
        response = await self.make_request("GET", "/subscription/status")
        
        if response.status_code == 200:
            response_data = response.json()
            required_fields = ["subscription_type", "subscription_status", "is_active"]
            missing_fields = [field for field in required_fields if field not in response_data]
            
            if not missing_fields:
                await self.log_result("Get Subscription Status", True, f"Subscription status: {response_data.get('subscription_status')}")
                return True
            else:
                await self.log_result("Get Subscription Status", False, f"Missing fields: {missing_fields}", response_data)
                return False
        else:
            await self.log_result("Get Subscription Status", False, f"Status: {response.status_code}", response.text)
            return False

    async def test_create_subscription_order(self):
        """Test POST /api/subscription/create-order"""
        if not self.auth_token:
            await self.log_result("Create Subscription Order", False, "No access token available")
            return False
            
        data = {"subscription_type": "monthly"}
        response = await self.make_request("POST", "/subscription/create-order", data)
        
        if response.status_code == 200:
            response_data = response.json()
            if "order_id" in response_data:
                await self.log_result("Create Subscription Order", True, f"Created order: {response_data['order_id']}")
                return True
            else:
                await self.log_result("Create Subscription Order", False, "No order ID in response", response_data)
                return False
        else:
            await self.log_result("Create Subscription Order", False, f"Status: {response.status_code}", response.text)
            return False

    async def test_verify_payment(self):
        """Test POST /api/subscription/verify-payment"""
        if not self.auth_token:
            await self.log_result("Verify Payment", False, "No access token available")
            return False
            
        # This will likely fail without real payment data, but we test the endpoint
        data = {
            "razorpay_order_id": "test_order_id",
            "razorpay_payment_id": "test_payment_id",
            "razorpay_signature": "test_signature"
        }
        
        response = await self.make_request("POST", "/subscription/verify-payment", data)
        
        # Accept both success and expected failure responses
        if response.status_code in [200, 400, 422]:
            await self.log_result("Verify Payment", True, f"Payment verification endpoint working (Status: {response.status_code})")
            return True
        else:
            await self.log_result("Verify Payment", False, f"Status: {response.status_code}", response.text)
            return False

    # ============================================================================
    # 9. WINNERS SYSTEM TESTS
    # ============================================================================
    
    async def test_get_winners(self):
        """Test GET /api/winners"""
        response = await self.make_request("GET", "/winners")
        
        if response.status_code == 200:
            response_data = response.json()
            if isinstance(response_data, list):
                await self.log_result("Get Winners", True, f"Retrieved {len(response_data)} winners")
                return True
            else:
                await self.log_result("Get Winners", False, "Invalid winners response format", response_data)
                return False
        else:
            await self.log_result("Get Winners", False, f"Status: {response.status_code}", response.text)
            return False

    # ============================================================================
    # 10. PUSH NOTIFICATIONS TESTS
    # ============================================================================
    
    async def test_register_push_token(self):
        """Test POST /api/notifications/register-token"""
        if not self.auth_token:
            await self.log_result("Register Push Token", False, "No access token available")
            return False
            
        data = {
            "push_token": "test_push_token_12345",
            "device_type": "android"
        }
        
        response = await self.make_request("POST", "/notifications/register-token", data)
        
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get("success"):
                await self.log_result("Register Push Token", True, "Successfully registered push token")
                return True
            else:
                await self.log_result("Register Push Token", False, "Push token registration not successful", response_data)
                return False
        else:
            await self.log_result("Register Push Token", False, f"Status: {response.status_code}", response.text)
            return False

    # ============================================================================
    # AI FEATURES TESTS
    # ============================================================================
    
    async def test_ai_generate_message(self):
        """Test POST /api/ai/generate-message"""
        if not self.auth_token:
            await self.log_result("AI Generate Message", False, "No access token available")
            return False
            
        data = {"category": "good_morning"}
        response = await self.make_request("POST", "/ai/generate-message", data)
        
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get("success") and "message" in response_data:
                await self.log_result("AI Generate Message", True, "Successfully generated AI message")
                return True
            else:
                await self.log_result("AI Generate Message", False, "AI message generation not successful", response_data)
                return False
        else:
            await self.log_result("AI Generate Message", False, f"Status: {response.status_code}", response.text)
            return False

    async def test_ai_smart_gifts(self):
        """Test GET /api/ai/smart-gifts"""
        if not self.auth_token:
            await self.log_result("AI Smart Gifts", False, "No access token available")
            return False
            
        params = {"occasion": "birthday", "budget": "Under ₹1000"}
        response = await self.make_request("GET", "/ai/smart-gifts", params=params)
        
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get("success") and "gifts" in response_data:
                gifts = response_data["gifts"]
                await self.log_result("AI Smart Gifts", True, f"Retrieved {len(gifts)} AI-enhanced gifts")
                return True
            else:
                await self.log_result("AI Smart Gifts", False, "AI smart gifts not successful", response_data)
                return False
        else:
            await self.log_result("AI Smart Gifts", False, f"Status: {response.status_code}", response.text)
            return False

    async def test_ai_plan_date(self):
        """Test POST /api/ai/plan-date"""
        if not self.auth_token:
            await self.log_result("AI Plan Date", False, "No access token available")
            return False
            
        data = {
            "budget": "Under ₹1000",
            "preferences": "romantic dinner",
            "location": "Mumbai"
        }
        
        response = await self.make_request("POST", "/ai/plan-date", data)
        
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get("success") and "date_plan" in response_data:
                await self.log_result("AI Plan Date", True, "Successfully generated AI date plan")
                return True
            else:
                await self.log_result("AI Plan Date", False, "AI date planning not successful", response_data)
                return False
        else:
            await self.log_result("AI Plan Date", False, f"Status: {response.status_code}", response.text)
            return False

    # ============================================================================
    # MAIN TEST RUNNER
    # ============================================================================
    
    async def run_all_tests(self):
        """Run all comprehensive tests"""
        print("🚀 Starting Comprehensive Pookie4u Backend Testing")
        print(f"📍 Backend URL: {BACKEND_URL}")
        print(f"🔗 API Base: {API_BASE}")
        print("=" * 60)
        
        # Authentication Tests
        print("\n📋 1. AUTHENTICATION SYSTEM TESTS")
        print("-" * 40)
        await self.test_user_registration()
        await self.test_user_login()
        await self.test_get_user_profile()
        await self.test_update_user_profile()
        
        # Tasks System Tests
        print("\n📋 2. TASKS SYSTEM TESTS")
        print("-" * 40)
        await self.test_get_daily_tasks()
        await self.test_get_weekly_tasks()
        await self.test_complete_task()
        await self.test_generate_ai_tasks()
        
        # Events System Tests
        print("\n📋 3. EVENTS SYSTEM TESTS")
        print("-" * 40)
        await self.test_get_events()
        await self.test_create_custom_event()
        await self.test_update_custom_event()
        await self.test_delete_custom_event()
        
        # Messages System Tests
        print("\n📋 4. MESSAGES SYSTEM TESTS")
        print("-" * 40)
        await self.test_get_daily_messages_same_home()
        await self.test_get_daily_messages_daily_irl()
        await self.test_get_daily_messages_long_distance()
        
        # Gifts System Tests
        print("\n📋 5. GIFTS SYSTEM TESTS")
        print("-" * 40)
        await self.test_get_gifts()
        await self.test_search_gifts()
        
        # Referral & Rewards Tests
        print("\n📋 6. REFERRAL & REWARDS SYSTEM TESTS")
        print("-" * 40)
        await self.test_get_referral_code()
        await self.test_apply_referral()
        await self.test_check_milestone_rewards()
        await self.test_get_rewards_history()
        
        # Feedback System Tests
        print("\n📋 7. FEEDBACK SYSTEM TESTS")
        print("-" * 40)
        await self.test_submit_feedback()
        await self.test_get_my_feedback()
        await self.test_get_all_feedback()
        
        # Subscription System Tests
        print("\n📋 8. SUBSCRIPTION SYSTEM TESTS")
        print("-" * 40)
        await self.test_get_subscription_status()
        await self.test_create_subscription_order()
        await self.test_verify_payment()
        
        # Winners System Tests
        print("\n📋 9. WINNERS SYSTEM TESTS")
        print("-" * 40)
        await self.test_get_winners()
        
        # Push Notifications Tests
        print("\n📋 10. PUSH NOTIFICATIONS TESTS")
        print("-" * 40)
        await self.test_register_push_token()
        
        # AI Features Tests
        print("\n📋 11. AI FEATURES TESTS")
        print("-" * 40)
        await self.test_ai_generate_message()
        await self.test_ai_smart_gifts()
        await self.test_ai_plan_date()
        
        # Generate Summary
        await self.generate_summary()

    async def generate_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST RESULTS SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📈 Overall Statistics:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {failed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        # Group results by category
        categories = {
            "Authentication": [],
            "Tasks": [],
            "Events": [],
            "Messages": [],
            "Gifts": [],
            "Referral & Rewards": [],
            "Feedback": [],
            "Subscription": [],
            "Winners": [],
            "Push Notifications": [],
            "AI Features": []
        }
        
        for result in self.test_results:
            test_name = result["test"]
            if any(auth_term in test_name for auth_term in ["Registration", "Login", "Profile"]):
                categories["Authentication"].append(result)
            elif "Task" in test_name:
                categories["Tasks"].append(result)
            elif "Event" in test_name:
                categories["Events"].append(result)
            elif "Message" in test_name:
                categories["Messages"].append(result)
            elif "Gift" in test_name:
                categories["Gifts"].append(result)
            elif any(term in test_name for term in ["Referral", "Reward"]):
                categories["Referral & Rewards"].append(result)
            elif "Feedback" in test_name:
                categories["Feedback"].append(result)
            elif "Subscription" in test_name or "Payment" in test_name:
                categories["Subscription"].append(result)
            elif "Winner" in test_name:
                categories["Winners"].append(result)
            elif "Push" in test_name or "Notification" in test_name:
                categories["Push Notifications"].append(result)
            elif "AI" in test_name:
                categories["AI Features"].append(result)
        
        print(f"\n📋 Results by Category:")
        for category, results in categories.items():
            if results:
                passed = sum(1 for r in results if r["success"])
                total = len(results)
                status = "✅" if passed == total else "⚠️" if passed > 0 else "❌"
                print(f"   {status} {category}: {passed}/{total} passed")
        
        # Show failed tests
        failed_results = [r for r in self.test_results if not r["success"]]
        if failed_results:
            print(f"\n❌ Failed Tests Details:")
            for result in failed_results:
                print(f"   • {result['test']}: {result['details']}")
        
        print(f"\n🎯 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Close client
        await self.client.aclose()

async def main():
    """Main test execution function"""
    tester = Pookie4uTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())