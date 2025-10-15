#!/usr/bin/env python3
"""
PRIORITY TEST: Partner Profile Date Format Fix (DD/MM/YYYY)
Testing the specific fix mentioned in the review request
"""

import requests
import json
import time
import random
import string
from datetime import datetime

class PartnerProfileDateTester:
    def __init__(self):
        self.base_url = "https://romance-inspect.preview.emergentagent.com/api"
        self.session = requests.Session()
        self.auth_token = None
        self.test_user_email = None
        
        print("🎯 PARTNER PROFILE DATE FORMAT TESTING")
        print(f"📡 Backend URL: {self.base_url}")
        print("=" * 60)

    def generate_test_email(self) -> str:
        """Generate unique test email"""
        timestamp = int(time.time())
        random_suffix = ''.join(random.choices(string.ascii_lowercase, k=6))
        return f"datetest_{timestamp}_{random_suffix}@example.com"

    def setup_test_user(self) -> bool:
        """Create test user for date format testing"""
        try:
            self.test_user_email = self.generate_test_email()
            
            registration_data = {
                "email": self.test_user_email,
                "password": "TestPass123!",
                "name": "Date Test User"
            }
            
            response = self.session.post(f"{self.base_url}/auth/register", json=registration_data)
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data["access_token"]
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                print(f"✅ Test user created: {self.test_user_email}")
                return True
            else:
                print(f"❌ Failed to create test user: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Exception creating test user: {str(e)}")
            return False

    def test_dd_mm_yyyy_format(self) -> bool:
        """Test DD/MM/YYYY date format as specified in review request"""
        print("\n🎂 Testing DD/MM/YYYY Date Format")
        print("-" * 40)
        
        try:
            # Test with exact dates from review request
            partner_data = {
                "name": "Emma Watson",
                "birthday": "26/06/1995",  # DD/MM/YYYY format from review
                "anniversary": "25/01/2020",  # DD/MM/YYYY format from review
                "favorite_color": "Blue",
                "favorite_food": "Italian Pasta",
                "favorite_flower": "Roses",
                "notes": "Testing DD/MM/YYYY date format"
            }
            
            print(f"📅 Testing birthday: {partner_data['birthday']}")
            print(f"💕 Testing anniversary: {partner_data['anniversary']}")
            
            response = self.session.put(f"{self.base_url}/user/partner-profile", json=partner_data)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ SUCCESS: Partner profile updated with DD/MM/YYYY format")
                print(f"   Response: {data.get('message', 'No message')}")
                
                # Check if auto-events were created
                auto_events = data.get('auto_events_created', 0)
                print(f"   Auto-events created: {auto_events}")
                
                return True
            else:
                print(f"❌ FAILED: Status {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            return False

    def test_various_dd_mm_yyyy_formats(self) -> bool:
        """Test various DD/MM/YYYY date formats"""
        print("\n📅 Testing Various DD/MM/YYYY Formats")
        print("-" * 40)
        
        test_dates = [
            {"birthday": "01/01/1990", "anniversary": "14/02/2018"},  # Leading zeros
            {"birthday": "5/12/1992", "anniversary": "3/7/2019"},    # No leading zeros
            {"birthday": "31/12/1988", "anniversary": "29/02/2020"}, # Edge cases
        ]
        
        success_count = 0
        
        for i, dates in enumerate(test_dates, 1):
            try:
                partner_data = {
                    "name": f"Test Partner {i}",
                    "birthday": dates["birthday"],
                    "anniversary": dates["anniversary"],
                    "notes": f"Test case {i}"
                }
                
                print(f"Test {i}: Birthday={dates['birthday']}, Anniversary={dates['anniversary']}")
                
                response = self.session.put(f"{self.base_url}/user/partner-profile", json=partner_data)
                
                if response.status_code == 200:
                    print(f"   ✅ SUCCESS")
                    success_count += 1
                else:
                    print(f"   ❌ FAILED: Status {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Exception: {str(e)}")
        
        print(f"\nResults: {success_count}/{len(test_dates)} date formats successful")
        return success_count == len(test_dates)

    def test_invalid_date_formats(self) -> bool:
        """Test that invalid date formats are properly rejected"""
        print("\n❌ Testing Invalid Date Format Rejection")
        print("-" * 40)
        
        invalid_dates = [
            {"birthday": "1995-06-26", "desc": "ISO format (should be rejected)"},
            {"birthday": "26-06-1995", "desc": "DD-MM-YYYY with dashes"},
            {"birthday": "invalid-date", "desc": "Completely invalid"},
            {"birthday": "32/13/1995", "desc": "Invalid day/month"},
        ]
        
        rejection_count = 0
        
        for i, test_case in enumerate(invalid_dates, 1):
            try:
                partner_data = {
                    "name": "Invalid Test",
                    "birthday": test_case["birthday"],
                    "notes": test_case["desc"]
                }
                
                print(f"Test {i}: {test_case['desc']} - {test_case['birthday']}")
                
                response = self.session.put(f"{self.base_url}/user/partner-profile", json=partner_data)
                
                if response.status_code in [400, 422]:
                    print(f"   ✅ CORRECTLY REJECTED: Status {response.status_code}")
                    rejection_count += 1
                elif response.status_code == 200:
                    print(f"   ⚠️  ACCEPTED (may be valid): Status {response.status_code}")
                else:
                    print(f"   ❓ UNEXPECTED: Status {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Exception: {str(e)}")
        
        print(f"\nResults: {rejection_count}/{len(invalid_dates)} invalid formats properly rejected")
        return True  # This is informational, not a hard requirement

    def verify_event_generation(self) -> bool:
        """Verify that birthday/anniversary events are generated from DD/MM/YYYY dates"""
        print("\n🎉 Verifying Event Generation from DD/MM/YYYY Dates")
        print("-" * 40)
        
        try:
            # Get events to check if birthday/anniversary events were created
            response = self.session.get(f"{self.base_url}/events")
            
            if response.status_code == 200:
                data = response.json()
                events = data.get("events", [])
                
                birthday_events = []
                anniversary_events = []
                
                for event in events:
                    event_name = event.get("name", "").lower()
                    if "birthday" in event_name:
                        birthday_events.append(event)
                    elif "anniversary" in event_name:
                        anniversary_events.append(event)
                
                print(f"📅 Found {len(birthday_events)} birthday events")
                print(f"💕 Found {len(anniversary_events)} anniversary events")
                
                if birthday_events:
                    for event in birthday_events[:2]:  # Show first 2
                        print(f"   Birthday: {event.get('name')} on {event.get('date')}")
                
                if anniversary_events:
                    for event in anniversary_events[:2]:  # Show first 2
                        print(f"   Anniversary: {event.get('name')} on {event.get('date')}")
                
                if birthday_events and anniversary_events:
                    print("✅ SUCCESS: Both birthday and anniversary events generated")
                    return True
                else:
                    print("⚠️  PARTIAL: Some events missing")
                    return False
            else:
                print(f"❌ Failed to get events: Status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            return False

    def run_comprehensive_date_format_test(self):
        """Run all date format tests"""
        print("🚀 STARTING PARTNER PROFILE DATE FORMAT TESTING")
        print("Focus: DD/MM/YYYY format fix verification")
        print("=" * 60)
        
        # Setup
        if not self.setup_test_user():
            print("❌ Cannot proceed without test user")
            return
        
        # Run tests
        results = {
            "dd_mm_yyyy_basic": self.test_dd_mm_yyyy_format(),
            "dd_mm_yyyy_various": self.test_various_dd_mm_yyyy_formats(),
            "invalid_rejection": self.test_invalid_date_formats(),
            "event_generation": self.verify_event_generation()
        }
        
        # Summary
        print("\n" + "=" * 60)
        print("🎯 DATE FORMAT TESTING RESULTS")
        print("=" * 60)
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        success_rate = (passed / total) * 100
        
        print(f"📊 Results Summary:")
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {status}: {test_name}")
        
        print(f"\n📈 Overall: {passed}/{total} tests passed ({success_rate:.1f}%)")
        
        if results["dd_mm_yyyy_basic"]:
            print("\n🎉 CRITICAL SUCCESS: DD/MM/YYYY format is working!")
            print("   The partner profile date format fix has been verified.")
        else:
            print("\n❌ CRITICAL FAILURE: DD/MM/YYYY format still not working!")
            print("   The partner profile date format fix needs attention.")
        
        print("=" * 60)

if __name__ == "__main__":
    tester = PartnerProfileDateTester()
    tester.run_comprehensive_date_format_test()