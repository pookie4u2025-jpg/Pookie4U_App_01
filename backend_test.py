#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Pookie4u Referral & Reward System
Testing Agent - Referral & Reward System Backend Endpoints
"""

import asyncio
import httpx
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# Backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://couple-referrals.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class ReferralRewardTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.test_results = []
        self.auth_token = None
        self.test_user_email = None
        
    async def log_result(self, test_name: str, success: bool, details: str, response_data: Any = None):
        """Log test result with details"""
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
        if not success:
            print(f"   Details: {details}")
        if response_data and not success:
            print(f"   Response: {json.dumps(response_data, indent=2)}")
    
    async def setup_test_user(self) -> bool:
        """Create and authenticate a test user for referral/reward testing"""
        try:
            # Create unique test user
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.test_user_email = f"referral_test_{timestamp}@example.com"
            
            # Register test user
            register_data = {
                "email": self.test_user_email,
                "password": "TestPass123!",
                "name": f"Referral Test User {timestamp}"
            }
            
            response = await self.client.post(f"{API_BASE}/register", json=register_data)
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                await self.log_result(
                    "User Registration for Testing", 
                    True, 
                    f"Successfully registered test user: {self.test_user_email}",
                    {"email": self.test_user_email, "token_received": bool(self.auth_token)}
                )
                return True
            else:
                await self.log_result(
                    "User Registration for Testing", 
                    False, 
                    f"Failed to register test user. Status: {response.status_code}",
                    response.json() if response.content else None
                )
                return False
                
        except Exception as e:
            await self.log_result(
                "User Registration for Testing", 
                False, 
                f"Exception during user registration: {str(e)}"
            )
            return False
    
    async def test_referral_my_code_authenticated(self):
        """Test GET /api/referral/my-code with valid JWT token"""
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = await self.client.get(f"{API_BASE}/referral/my-code", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = ["success", "code", "referrals_count", "points_earned"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    await self.log_result(
                        "Referral My Code - Response Structure",
                        False,
                        f"Missing required fields: {missing_fields}",
                        data
                    )
                    return False
                
                # Verify data types and values
                if not isinstance(data["success"], bool) or not data["success"]:
                    await self.log_result(
                        "Referral My Code - Success Field",
                        False,
                        f"Success field should be True boolean, got: {data['success']}",
                        data
                    )
                    return False
                
                # Verify referral code format (POO-XXXXXX)
                code = data["code"]
                if not isinstance(code, str) or not code.startswith("POO-") or len(code) != 10:
                    await self.log_result(
                        "Referral My Code - Code Format",
                        False,
                        f"Invalid referral code format. Expected POO-XXXXXX, got: {code}",
                        data
                    )
                    return False
                
                # Verify numeric fields
                if not isinstance(data["referrals_count"], int) or data["referrals_count"] < 0:
                    await self.log_result(
                        "Referral My Code - Referrals Count",
                        False,
                        f"Invalid referrals_count. Expected non-negative integer, got: {data['referrals_count']}",
                        data
                    )
                    return False
                
                if not isinstance(data["points_earned"], int) or data["points_earned"] < 0:
                    await self.log_result(
                        "Referral My Code - Points Earned",
                        False,
                        f"Invalid points_earned. Expected non-negative integer, got: {data['points_earned']}",
                        data
                    )
                    return False
                
                # Verify points calculation (referrals_count * 50)
                expected_points = data["referrals_count"] * 50
                if data["points_earned"] != expected_points:
                    await self.log_result(
                        "Referral My Code - Points Calculation",
                        False,
                        f"Points calculation incorrect. Expected {expected_points} (count * 50), got: {data['points_earned']}",
                        data
                    )
                    return False
                
                await self.log_result(
                    "Referral My Code - Authenticated Request",
                    True,
                    f"Successfully retrieved referral code: {code}, referrals: {data['referrals_count']}, points: {data['points_earned']}",
                    data
                )
                return True
                
            else:
                await self.log_result(
                    "Referral My Code - Authenticated Request",
                    False,
                    f"Unexpected status code: {response.status_code}",
                    response.json() if response.content else None
                )
                return False
                
        except Exception as e:
            await self.log_result(
                "Referral My Code - Authenticated Request",
                False,
                f"Exception during request: {str(e)}"
            )
            return False
    
    async def test_referral_my_code_consistency(self):
        """Test that GET /api/referral/my-code returns same code on multiple calls"""
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # First call
            response1 = await self.client.get(f"{API_BASE}/referral/my-code", headers=headers)
            if response1.status_code != 200:
                await self.log_result(
                    "Referral Code Consistency - First Call",
                    False,
                    f"First call failed with status: {response1.status_code}",
                    response1.json() if response1.content else None
                )
                return False
            
            code1 = response1.json()["code"]
            
            # Second call
            response2 = await self.client.get(f"{API_BASE}/referral/my-code", headers=headers)
            if response2.status_code != 200:
                await self.log_result(
                    "Referral Code Consistency - Second Call",
                    False,
                    f"Second call failed with status: {response2.status_code}",
                    response2.json() if response2.content else None
                )
                return False
            
            code2 = response2.json()["code"]
            
            # Verify codes are identical
            if code1 == code2:
                await self.log_result(
                    "Referral Code Consistency",
                    True,
                    f"Referral code consistent across calls: {code1}",
                    {"first_call": code1, "second_call": code2}
                )
                return True
            else:
                await self.log_result(
                    "Referral Code Consistency",
                    False,
                    f"Referral code changed between calls. First: {code1}, Second: {code2}",
                    {"first_call": code1, "second_call": code2}
                )
                return False
                
        except Exception as e:
            await self.log_result(
                "Referral Code Consistency",
                False,
                f"Exception during consistency test: {str(e)}"
            )
            return False
    
    async def test_referral_my_code_unauthenticated(self):
        """Test GET /api/referral/my-code without authentication (should return 401/403)"""
        try:
            # Test without Authorization header
            response = await self.client.get(f"{API_BASE}/referral/my-code")
            
            if response.status_code in [401, 403]:
                await self.log_result(
                    "Referral My Code - No Authentication",
                    True,
                    f"Correctly rejected unauthenticated request with status: {response.status_code}",
                    {"status_code": response.status_code}
                )
                return True
            else:
                await self.log_result(
                    "Referral My Code - No Authentication",
                    False,
                    f"Should reject unauthenticated request with 401/403, got: {response.status_code}",
                    response.json() if response.content else None
                )
                return False
                
        except Exception as e:
            await self.log_result(
                "Referral My Code - No Authentication",
                False,
                f"Exception during unauthenticated test: {str(e)}"
            )
            return False
    
    async def test_referral_my_code_invalid_token(self):
        """Test GET /api/referral/my-code with invalid JWT token (should return 401)"""
        try:
            # Test with invalid token
            headers = {"Authorization": "Bearer invalid_token_12345"}
            response = await self.client.get(f"{API_BASE}/referral/my-code", headers=headers)
            
            if response.status_code == 401:
                await self.log_result(
                    "Referral My Code - Invalid Token",
                    True,
                    f"Correctly rejected invalid token with status: {response.status_code}",
                    {"status_code": response.status_code}
                )
                return True
            else:
                await self.log_result(
                    "Referral My Code - Invalid Token",
                    False,
                    f"Should reject invalid token with 401, got: {response.status_code}",
                    response.json() if response.content else None
                )
                return False
                
        except Exception as e:
            await self.log_result(
                "Referral My Code - Invalid Token",
                False,
                f"Exception during invalid token test: {str(e)}"
            )
            return False
    
    async def test_rewards_check_milestone_authenticated(self):
        """Test GET /api/rewards/check-milestone with valid JWT token"""
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = await self.client.get(f"{API_BASE}/rewards/check-milestone", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = ["success", "eligible", "current_points", "points_to_milestone", "cycles_completed"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    await self.log_result(
                        "Rewards Check Milestone - Response Structure",
                        False,
                        f"Missing required fields: {missing_fields}",
                        data
                    )
                    return False
                
                # Verify data types and values
                if not isinstance(data["success"], bool) or not data["success"]:
                    await self.log_result(
                        "Rewards Check Milestone - Success Field",
                        False,
                        f"Success field should be True boolean, got: {data['success']}",
                        data
                    )
                    return False
                
                if not isinstance(data["eligible"], bool):
                    await self.log_result(
                        "Rewards Check Milestone - Eligible Field",
                        False,
                        f"Eligible field should be boolean, got: {type(data['eligible'])} - {data['eligible']}",
                        data
                    )
                    return False
                
                if not isinstance(data["current_points"], int) or data["current_points"] < 0:
                    await self.log_result(
                        "Rewards Check Milestone - Current Points",
                        False,
                        f"Current points should be non-negative integer, got: {data['current_points']}",
                        data
                    )
                    return False
                
                if not isinstance(data["points_to_milestone"], int) or data["points_to_milestone"] < 0:
                    await self.log_result(
                        "Rewards Check Milestone - Points to Milestone",
                        False,
                        f"Points to milestone should be non-negative integer, got: {data['points_to_milestone']}",
                        data
                    )
                    return False
                
                if not isinstance(data["cycles_completed"], int) or data["cycles_completed"] < 0:
                    await self.log_result(
                        "Rewards Check Milestone - Cycles Completed",
                        False,
                        f"Cycles completed should be non-negative integer, got: {data['cycles_completed']}",
                        data
                    )
                    return False
                
                # Verify milestone logic
                current_points = data["current_points"]
                eligible = data["eligible"]
                points_to_milestone = data["points_to_milestone"]
                
                # If points >= 1000, should be eligible and points_to_milestone should be 0
                if current_points >= 1000:
                    if not eligible:
                        await self.log_result(
                            "Rewards Check Milestone - Eligibility Logic (>=1000)",
                            False,
                            f"User with {current_points} points should be eligible, but eligible={eligible}",
                            data
                        )
                        return False
                    
                    if points_to_milestone != 0:
                        await self.log_result(
                            "Rewards Check Milestone - Points to Milestone Logic (>=1000)",
                            False,
                            f"User with {current_points} points should have 0 points_to_milestone, got: {points_to_milestone}",
                            data
                        )
                        return False
                else:
                    # If points < 1000, should not be eligible and points_to_milestone should be (1000 - current_points)
                    if eligible:
                        await self.log_result(
                            "Rewards Check Milestone - Eligibility Logic (<1000)",
                            False,
                            f"User with {current_points} points should not be eligible, but eligible={eligible}",
                            data
                        )
                        return False
                    
                    expected_points_to_milestone = 1000 - current_points
                    if points_to_milestone != expected_points_to_milestone:
                        await self.log_result(
                            "Rewards Check Milestone - Points to Milestone Logic (<1000)",
                            False,
                            f"User with {current_points} points should have {expected_points_to_milestone} points_to_milestone, got: {points_to_milestone}",
                            data
                        )
                        return False
                
                await self.log_result(
                    "Rewards Check Milestone - Authenticated Request",
                    True,
                    f"Successfully checked milestone: eligible={eligible}, current_points={current_points}, points_to_milestone={points_to_milestone}, cycles={data['cycles_completed']}",
                    data
                )
                return True
                
            else:
                await self.log_result(
                    "Rewards Check Milestone - Authenticated Request",
                    False,
                    f"Unexpected status code: {response.status_code}",
                    response.json() if response.content else None
                )
                return False
                
        except Exception as e:
            await self.log_result(
                "Rewards Check Milestone - Authenticated Request",
                False,
                f"Exception during request: {str(e)}"
            )
            return False
    
    async def test_rewards_check_milestone_unauthenticated(self):
        """Test GET /api/rewards/check-milestone without authentication (should return 401/403)"""
        try:
            # Test without Authorization header
            response = await self.client.get(f"{API_BASE}/rewards/check-milestone")
            
            if response.status_code in [401, 403]:
                await self.log_result(
                    "Rewards Check Milestone - No Authentication",
                    True,
                    f"Correctly rejected unauthenticated request with status: {response.status_code}",
                    {"status_code": response.status_code}
                )
                return True
            else:
                await self.log_result(
                    "Rewards Check Milestone - No Authentication",
                    False,
                    f"Should reject unauthenticated request with 401/403, got: {response.status_code}",
                    response.json() if response.content else None
                )
                return False
                
        except Exception as e:
            await self.log_result(
                "Rewards Check Milestone - No Authentication",
                False,
                f"Exception during unauthenticated test: {str(e)}"
            )
            return False
    
    async def test_rewards_check_milestone_invalid_token(self):
        """Test GET /api/rewards/check-milestone with invalid JWT token (should return 401)"""
        try:
            # Test with invalid token
            headers = {"Authorization": "Bearer invalid_token_12345"}
            response = await self.client.get(f"{API_BASE}/rewards/check-milestone", headers=headers)
            
            if response.status_code == 401:
                await self.log_result(
                    "Rewards Check Milestone - Invalid Token",
                    True,
                    f"Correctly rejected invalid token with status: {response.status_code}",
                    {"status_code": response.status_code}
                )
                return True
            else:
                await self.log_result(
                    "Rewards Check Milestone - Invalid Token",
                    False,
                    f"Should reject invalid token with 401, got: {response.status_code}",
                    response.json() if response.content else None
                )
                return False
                
        except Exception as e:
            await self.log_result(
                "Rewards Check Milestone - Invalid Token",
                False,
                f"Exception during invalid token test: {str(e)}"
            )
            return False
    
    async def test_user_profile_total_points_field(self):
        """Test GET /api/user/profile to verify total_points field is returned"""
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = await self.client.get(f"{API_BASE}/user/profile", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify total_points field exists
                if "total_points" not in data:
                    await self.log_result(
                        "User Profile - Total Points Field",
                        False,
                        "total_points field missing from user profile response",
                        data
                    )
                    return False
                
                # Verify total_points is a valid integer
                total_points = data["total_points"]
                if not isinstance(total_points, int) or total_points < 0:
                    await self.log_result(
                        "User Profile - Total Points Value",
                        False,
                        f"total_points should be non-negative integer, got: {total_points} (type: {type(total_points)})",
                        data
                    )
                    return False
                
                # Verify other expected fields exist
                expected_fields = ["id", "email", "name", "relationship_mode", "current_level", "current_streak", "tasks_completed"]
                missing_fields = [field for field in expected_fields if field not in data]
                
                if missing_fields:
                    await self.log_result(
                        "User Profile - Expected Fields",
                        False,
                        f"Missing expected fields: {missing_fields}",
                        data
                    )
                    return False
                
                await self.log_result(
                    "User Profile - Total Points Integration",
                    True,
                    f"Successfully retrieved user profile with total_points: {total_points}",
                    {"total_points": total_points, "email": data.get("email"), "name": data.get("name")}
                )
                return True
                
            else:
                await self.log_result(
                    "User Profile - Total Points Integration",
                    False,
                    f"Unexpected status code: {response.status_code}",
                    response.json() if response.content else None
                )
                return False
                
        except Exception as e:
            await self.log_result(
                "User Profile - Total Points Integration",
                False,
                f"Exception during request: {str(e)}"
            )
            return False
    
    async def test_user_profile_unauthenticated(self):
        """Test GET /api/user/profile without authentication (should return 401/403)"""
        try:
            # Test without Authorization header
            response = await self.client.get(f"{API_BASE}/user/profile")
            
            if response.status_code in [401, 403]:
                await self.log_result(
                    "User Profile - No Authentication",
                    True,
                    f"Correctly rejected unauthenticated request with status: {response.status_code}",
                    {"status_code": response.status_code}
                )
                return True
            else:
                await self.log_result(
                    "User Profile - No Authentication",
                    False,
                    f"Should reject unauthenticated request with 401/403, got: {response.status_code}",
                    response.json() if response.content else None
                )
                return False
                
        except Exception as e:
            await self.log_result(
                "User Profile - No Authentication",
                False,
                f"Exception during unauthenticated test: {str(e)}"
            )
            return False
    
    async def test_referral_code_uniqueness(self):
        """Test that referral codes are unique across users"""
        try:
            # Create a second test user
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            second_user_email = f"referral_test_2_{timestamp}@example.com"
            
            # Register second test user
            register_data = {
                "email": second_user_email,
                "password": "TestPass123!",
                "name": f"Referral Test User 2 {timestamp}"
            }
            
            response = await self.client.post(f"{API_BASE}/register", json=register_data)
            
            if response.status_code != 200:
                await self.log_result(
                    "Referral Code Uniqueness - Second User Registration",
                    False,
                    f"Failed to register second test user. Status: {response.status_code}",
                    response.json() if response.content else None
                )
                return False
            
            second_user_token = response.json().get("access_token")
            
            # Get referral codes for both users
            headers1 = {"Authorization": f"Bearer {self.auth_token}"}
            headers2 = {"Authorization": f"Bearer {second_user_token}"}
            
            response1 = await self.client.get(f"{API_BASE}/referral/my-code", headers=headers1)
            response2 = await self.client.get(f"{API_BASE}/referral/my-code", headers=headers2)
            
            if response1.status_code != 200 or response2.status_code != 200:
                await self.log_result(
                    "Referral Code Uniqueness - Code Retrieval",
                    False,
                    f"Failed to retrieve referral codes. Status1: {response1.status_code}, Status2: {response2.status_code}",
                    {"response1": response1.json() if response1.content else None, "response2": response2.json() if response2.content else None}
                )
                return False
            
            code1 = response1.json()["code"]
            code2 = response2.json()["code"]
            
            # Verify codes are different
            if code1 != code2:
                await self.log_result(
                    "Referral Code Uniqueness",
                    True,
                    f"Referral codes are unique. User1: {code1}, User2: {code2}",
                    {"user1_code": code1, "user2_code": code2}
                )
                return True
            else:
                await self.log_result(
                    "Referral Code Uniqueness",
                    False,
                    f"Referral codes are not unique! Both users have: {code1}",
                    {"user1_code": code1, "user2_code": code2}
                )
                return False
                
        except Exception as e:
            await self.log_result(
                "Referral Code Uniqueness",
                False,
                f"Exception during uniqueness test: {str(e)}"
            )
            return False
    
    async def run_all_tests(self):
        """Run all referral and reward system tests"""
        print("🚀 Starting Comprehensive Referral & Reward System Backend Testing")
        print(f"📍 Backend URL: {BACKEND_URL}")
        print(f"🔗 API Base: {API_BASE}")
        print("=" * 80)
        
        # Setup test user
        if not await self.setup_test_user():
            print("❌ Failed to setup test user. Aborting tests.")
            return
        
        print("\n🔐 Testing Authentication & Authorization...")
        
        # Test authentication failures first
        await self.test_referral_my_code_unauthenticated()
        await self.test_referral_my_code_invalid_token()
        await self.test_rewards_check_milestone_unauthenticated()
        await self.test_rewards_check_milestone_invalid_token()
        await self.test_user_profile_unauthenticated()
        
        print("\n📋 Testing Referral System Endpoints...")
        
        # Test referral endpoints
        await self.test_referral_my_code_authenticated()
        await self.test_referral_my_code_consistency()
        await self.test_referral_code_uniqueness()
        
        print("\n🎁 Testing Reward System Endpoints...")
        
        # Test reward endpoints
        await self.test_rewards_check_milestone_authenticated()
        
        print("\n👤 Testing User Profile Integration...")
        
        # Test user profile
        await self.test_user_profile_total_points_field()
        
        # Generate summary
        await self.generate_summary()
    
    async def generate_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 80)
        print("📊 REFERRAL & REWARD SYSTEM TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📈 Overall Results: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}% success rate)")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        
        if failed_tests > 0:
            print(f"\n🚨 FAILED TESTS ({failed_tests}):")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   ❌ {result['test']}: {result['details']}")
        
        print(f"\n✅ PASSED TESTS ({passed_tests}):")
        for result in self.test_results:
            if result["success"]:
                print(f"   ✅ {result['test']}")
        
        # Categorize results
        categories = {
            "Authentication & Security": [],
            "Referral System": [],
            "Reward System": [],
            "User Profile Integration": [],
            "Data Integrity": []
        }
        
        for result in self.test_results:
            test_name = result["test"]
            if "Authentication" in test_name or "Invalid Token" in test_name or "No Authentication" in test_name:
                categories["Authentication & Security"].append(result)
            elif "Referral" in test_name:
                categories["Referral System"].append(result)
            elif "Reward" in test_name or "Milestone" in test_name:
                categories["Reward System"].append(result)
            elif "Profile" in test_name:
                categories["User Profile Integration"].append(result)
            elif "Uniqueness" in test_name or "Consistency" in test_name:
                categories["Data Integrity"].append(result)
        
        print(f"\n📋 RESULTS BY CATEGORY:")
        for category, results in categories.items():
            if results:
                passed = sum(1 for r in results if r["success"])
                total = len(results)
                print(f"   {category}: {passed}/{total} passed")
        
        print("\n" + "=" * 80)
        
        # Close client
        await self.client.aclose()

async def main():
    """Main test execution function"""
    tester = ReferralRewardTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())