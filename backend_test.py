#!/usr/bin/env python3
"""
Backend Testing Script for Pookie4u - Razorpay Removal Verification
Tests subscription endpoints, authentication, and core functionality
"""

import requests
import json
import time
import random
import string
from datetime import datetime

# Configuration
BACKEND_URL = "https://streaky-couples-app.preview.emergentagent.com/api"
TEST_USER_EMAIL = f"testuser_{int(time.time())}@example.com"
TEST_USER_PASSWORD = "TestPassword123!"
TEST_USER_NAME = "Test User"

class EventCRUDTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.auth_token = None
        self.test_results = []
        self.created_events = []  # Track created events for cleanup
        
    async def log_result(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result with details"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        if response_data:
            result["response_data"] = response_data
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if not success and response_data:
            print(f"   Response: {response_data}")
        print()

    async def register_and_login(self) -> bool:
        """Register a test user and get authentication token"""
        try:
            # Try to register user
            register_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD,
                "name": TEST_USER_NAME
            }
            
            register_response = await self.client.post(
                f"{BACKEND_URL}/auth/register",
                json=register_data
            )
            
            # Login to get token (whether registration succeeded or user already exists)
            login_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            login_response = await self.client.post(
                f"{BACKEND_URL}/auth/login",
                json=login_data
            )
            
            if login_response.status_code == 200:
                login_result = login_response.json()
                self.auth_token = login_result.get("access_token")
                await self.log_result(
                    "User Authentication Setup",
                    True,
                    f"Successfully authenticated user: {TEST_USER_EMAIL}",
                    {"token_received": bool(self.auth_token)}
                )
                return True
            else:
                await self.log_result(
                    "User Authentication Setup",
                    False,
                    f"Login failed with status {login_response.status_code}",
                    login_response.text
                )
                return False
                
        except Exception as e:
            await self.log_result(
                "User Authentication Setup",
                False,
                f"Authentication error: {str(e)}"
            )
            return False

    def get_auth_headers(self) -> Dict[str, str]:
        """Get authorization headers"""
        if not self.auth_token:
            return {}
        return {"Authorization": f"Bearer {self.auth_token}"}

    async def test_get_events_endpoint(self):
        """Test GET /api/events - Fetch all events"""
        try:
            # Test without authentication (should fail)
            response = await self.client.get(f"{BACKEND_URL}/events")
            
            if response.status_code == 403:
                await self.log_result(
                    "GET /events - Authentication Required",
                    True,
                    "Correctly rejects unauthenticated requests with 403"
                )
            else:
                await self.log_result(
                    "GET /events - Authentication Required",
                    False,
                    f"Expected 403, got {response.status_code}",
                    response.text
                )
            
            # Test with authentication
            response = await self.client.get(
                f"{BACKEND_URL}/events",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                has_events_array = "events" in data and isinstance(data["events"], list)
                
                if has_events_array:
                    events = data["events"]
                    
                    # Check for proper event structure
                    event_structure_valid = True
                    custom_events_found = 0
                    prefilled_events_found = 0
                    
                    for event in events:
                        required_fields = ["id", "name", "date"]
                        if not all(field in event for field in required_fields):
                            event_structure_valid = False
                            break
                        
                        # Count event types
                        if event.get("category") == "custom":
                            custom_events_found += 1
                        if event.get("prefilled") == True:
                            prefilled_events_found += 1
                    
                    await self.log_result(
                        "GET /events - Response Structure",
                        event_structure_valid and has_events_array,
                        f"Events array with {len(events)} events. Custom: {custom_events_found}, Prefilled: {prefilled_events_found}",
                        {
                            "total_events": len(events),
                            "custom_events": custom_events_found,
                            "prefilled_events": prefilled_events_found,
                            "has_events_array": has_events_array
                        }
                    )
                else:
                    await self.log_result(
                        "GET /events - Response Structure",
                        False,
                        "Response missing 'events' array",
                        data
                    )
            else:
                await self.log_result(
                    "GET /events - Authenticated Request",
                    False,
                    f"Expected 200, got {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            await self.log_result(
                "GET /events - Exception",
                False,
                f"Error testing GET /events: {str(e)}"
            )

    async def test_create_custom_event(self) -> Optional[str]:
        """Test POST /api/events/custom - Create custom event"""
        try:
            # Test without authentication (should fail)
            event_data = {
                "name": "Test Event",
                "date": "2025-06-15T00:00:00Z",
                "recurring": False
            }
            
            response = await self.client.post(
                f"{BACKEND_URL}/events/custom",
                json=event_data
            )
            
            if response.status_code == 403:
                await self.log_result(
                    "POST /events/custom - Authentication Required",
                    True,
                    "Correctly rejects unauthenticated requests with 403"
                )
            else:
                await self.log_result(
                    "POST /events/custom - Authentication Required",
                    False,
                    f"Expected 403, got {response.status_code}",
                    response.text
                )
            
            # Test with authentication - valid event
            event_data = {
                "name": "Sarah's Birthday Party",
                "date": "2025-06-15T00:00:00Z",
                "recurring": False,
                "description": "Celebrating Sarah's special day with friends and family",
                "importance": "high"
            }
            
            response = await self.client.post(
                f"{BACKEND_URL}/events/custom",
                json=event_data,
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                has_event = "event" in data and isinstance(data["event"], dict)
                has_message = "message" in data
                
                if has_event:
                    event = data["event"]
                    event_id = event.get("id")
                    
                    # Verify event properties
                    correct_category = event.get("category") == "custom"
                    has_required_fields = all(
                        field in event for field in ["id", "name", "date", "category"]
                    )
                    
                    if event_id:
                        self.created_events.append(event_id)
                    
                    await self.log_result(
                        "POST /events/custom - Create Event",
                        has_event and has_message and correct_category and has_required_fields,
                        f"Created event '{event.get('name')}' with ID: {event_id}",
                        {
                            "event_id": event_id,
                            "category": event.get("category"),
                            "has_required_fields": has_required_fields
                        }
                    )
                    
                    return event_id
                else:
                    await self.log_result(
                        "POST /events/custom - Create Event",
                        False,
                        "Response missing event object",
                        data
                    )
            else:
                await self.log_result(
                    "POST /events/custom - Create Event",
                    False,
                    f"Expected 200, got {response.status_code}",
                    response.text
                )
            
            # Test validation - missing required fields
            invalid_event_data = {
                "description": "Event without name or date"
            }
            
            response = await self.client.post(
                f"{BACKEND_URL}/events/custom",
                json=invalid_event_data,
                headers=self.get_auth_headers()
            )
            
            validation_works = response.status_code in [400, 422]
            await self.log_result(
                "POST /events/custom - Validation",
                validation_works,
                f"Validation correctly rejects invalid data with status {response.status_code}" if validation_works else f"Expected 400/422, got {response.status_code}",
                response.text if not validation_works else None
            )
                
        except Exception as e:
            await self.log_result(
                "POST /events/custom - Exception",
                False,
                f"Error testing POST /events/custom: {str(e)}"
            )
        
        return None

    async def test_update_custom_event(self, event_id: str):
        """Test PATCH /api/events/custom/{event_id} - Update custom event"""
        if not event_id:
            await self.log_result(
                "PATCH /events/custom/{id} - Skipped",
                False,
                "No event ID available for update test"
            )
            return
            
        try:
            # Test without authentication (should fail)
            update_data = {
                "name": "Updated Event Name"
            }
            
            response = await self.client.patch(
                f"{BACKEND_URL}/events/custom/{event_id}",
                json=update_data
            )
            
            if response.status_code == 403:
                await self.log_result(
                    "PATCH /events/custom/{id} - Authentication Required",
                    True,
                    "Correctly rejects unauthenticated requests with 403"
                )
            else:
                await self.log_result(
                    "PATCH /events/custom/{id} - Authentication Required",
                    False,
                    f"Expected 403, got {response.status_code}",
                    response.text
                )
            
            # Test with authentication - valid update
            update_data = {
                "name": "Updated Birthday Celebration",
                "date": "2025-06-20T00:00:00Z",
                "description": "Updated description for the birthday party",
                "importance": "medium"
            }
            
            response = await self.client.patch(
                f"{BACKEND_URL}/events/custom/{event_id}",
                json=update_data,
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                has_event = "event" in data and isinstance(data["event"], dict)
                has_message = "message" in data
                
                if has_event:
                    event = data["event"]
                    
                    # Verify updates were applied
                    name_updated = event.get("name") == update_data["name"]
                    description_updated = event.get("description") == update_data["description"]
                    
                    await self.log_result(
                        "PATCH /events/custom/{id} - Update Event",
                        has_event and has_message and name_updated,
                        f"Updated event: name={name_updated}, description={description_updated}",
                        {
                            "updated_name": event.get("name"),
                            "updated_description": event.get("description")
                        }
                    )
                else:
                    await self.log_result(
                        "PATCH /events/custom/{id} - Update Event",
                        False,
                        "Response missing event object",
                        data
                    )
            else:
                await self.log_result(
                    "PATCH /events/custom/{id} - Update Event",
                    False,
                    f"Expected 200, got {response.status_code}",
                    response.text
                )
            
            # Test validation - empty update
            response = await self.client.patch(
                f"{BACKEND_URL}/events/custom/{event_id}",
                json={},
                headers=self.get_auth_headers()
            )
            
            validation_works = response.status_code == 400
            await self.log_result(
                "PATCH /events/custom/{id} - Empty Update Validation",
                validation_works,
                f"Correctly rejects empty update with status {response.status_code}" if validation_works else f"Expected 400, got {response.status_code}",
                response.text if not validation_works else None
            )
            
            # Test non-existent event
            fake_event_id = "fake_event_12345"
            response = await self.client.patch(
                f"{BACKEND_URL}/events/custom/{fake_event_id}",
                json={"name": "Test"},
                headers=self.get_auth_headers()
            )
            
            not_found_works = response.status_code == 404
            await self.log_result(
                "PATCH /events/custom/{id} - Non-existent Event",
                not_found_works,
                f"Correctly returns 404 for non-existent event" if not_found_works else f"Expected 404, got {response.status_code}",
                response.text if not not_found_works else None
            )
                
        except Exception as e:
            await self.log_result(
                "PATCH /events/custom/{id} - Exception",
                False,
                f"Error testing PATCH /events/custom: {str(e)}"
            )

    async def test_delete_custom_event(self, event_id: str):
        """Test DELETE /api/events/custom/{event_id} - Delete custom event"""
        if not event_id:
            await self.log_result(
                "DELETE /events/custom/{id} - Skipped",
                False,
                "No event ID available for delete test"
            )
            return
            
        try:
            # Test without authentication (should fail)
            response = await self.client.delete(f"{BACKEND_URL}/events/custom/{event_id}")
            
            if response.status_code == 403:
                await self.log_result(
                    "DELETE /events/custom/{id} - Authentication Required",
                    True,
                    "Correctly rejects unauthenticated requests with 403"
                )
            else:
                await self.log_result(
                    "DELETE /events/custom/{id} - Authentication Required",
                    False,
                    f"Expected 403, got {response.status_code}",
                    response.text
                )
            
            # Test non-existent event first
            fake_event_id = "fake_event_12345"
            response = await self.client.delete(
                f"{BACKEND_URL}/events/custom/{fake_event_id}",
                headers=self.get_auth_headers()
            )
            
            not_found_works = response.status_code == 404
            await self.log_result(
                "DELETE /events/custom/{id} - Non-existent Event",
                not_found_works,
                f"Correctly returns 404 for non-existent event" if not_found_works else f"Expected 404, got {response.status_code}",
                response.text if not not_found_works else None
            )
            
            # Test with authentication - valid delete
            response = await self.client.delete(
                f"{BACKEND_URL}/events/custom/{event_id}",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                has_message = "message" in data
                has_deleted_id = "deleted_event_id" in data
                correct_id = data.get("deleted_event_id") == event_id
                
                await self.log_result(
                    "DELETE /events/custom/{id} - Delete Event",
                    has_message and has_deleted_id and correct_id,
                    f"Successfully deleted event {event_id}",
                    {
                        "deleted_event_id": data.get("deleted_event_id"),
                        "message": data.get("message")
                    }
                )
                
                # Verify event no longer appears in GET /events
                await asyncio.sleep(1)  # Brief delay for consistency
                get_response = await self.client.get(
                    f"{BACKEND_URL}/events",
                    headers=self.get_auth_headers()
                )
                
                if get_response.status_code == 200:
                    events_data = get_response.json()
                    events = events_data.get("events", [])
                    
                    # Check if deleted event still exists
                    deleted_event_exists = any(
                        event.get("id") == event_id for event in events
                    )
                    
                    await self.log_result(
                        "DELETE /events/custom/{id} - Verification",
                        not deleted_event_exists,
                        f"Event {event_id} {'still exists' if deleted_event_exists else 'successfully removed'} from events list",
                        {"event_still_exists": deleted_event_exists}
                    )
                else:
                    await self.log_result(
                        "DELETE /events/custom/{id} - Verification",
                        False,
                        f"Could not verify deletion - GET /events failed with {get_response.status_code}"
                    )
            else:
                await self.log_result(
                    "DELETE /events/custom/{id} - Delete Event",
                    False,
                    f"Expected 200, got {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            await self.log_result(
                "DELETE /events/custom/{id} - Exception",
                False,
                f"Error testing DELETE /events/custom: {str(e)}"
            )

    async def test_event_crud_flow(self):
        """Test complete CRUD flow end-to-end"""
        try:
            # Create multiple events for comprehensive testing
            event1_data = {
                "name": "Anniversary Dinner",
                "date": "2025-07-15T19:00:00Z",
                "recurring": True,
                "description": "Romantic anniversary dinner at favorite restaurant",
                "importance": "high"
            }
            
            event2_data = {
                "name": "Weekend Getaway",
                "date": "2025-08-20T10:00:00Z",
                "recurring": False,
                "description": "Relaxing weekend trip to the mountains",
                "importance": "medium"
            }
            
            # Create first event
            response1 = await self.client.post(
                f"{BACKEND_URL}/events/custom",
                json=event1_data,
                headers=self.get_auth_headers()
            )
            
            # Create second event
            response2 = await self.client.post(
                f"{BACKEND_URL}/events/custom",
                json=event2_data,
                headers=self.get_auth_headers()
            )
            
            events_created = 0
            event_ids = []
            
            if response1.status_code == 200:
                events_created += 1
                event_ids.append(response1.json()["event"]["id"])
                
            if response2.status_code == 200:
                events_created += 1
                event_ids.append(response2.json()["event"]["id"])
            
            # Verify events appear in GET /events
            get_response = await self.client.get(
                f"{BACKEND_URL}/events",
                headers=self.get_auth_headers()
            )
            
            events_visible = 0
            if get_response.status_code == 200:
                events_data = get_response.json()
                events = events_data.get("events", [])
                
                for event_id in event_ids:
                    if any(event.get("id") == event_id for event in events):
                        events_visible += 1
            
            await self.log_result(
                "Event CRUD Flow - Create & List",
                events_created == 2 and events_visible == 2,
                f"Created {events_created}/2 events, {events_visible}/2 visible in list",
                {
                    "events_created": events_created,
                    "events_visible": events_visible,
                    "event_ids": event_ids
                }
            )
            
            # Update and delete events
            if event_ids:
                # Update first event
                update_response = await self.client.patch(
                    f"{BACKEND_URL}/events/custom/{event_ids[0]}",
                    json={"name": "Updated Anniversary Celebration"},
                    headers=self.get_auth_headers()
                )
                
                # Delete second event
                delete_response = await self.client.delete(
                    f"{BACKEND_URL}/events/custom/{event_ids[1]}",
                    headers=self.get_auth_headers()
                )
                
                update_success = update_response.status_code == 200
                delete_success = delete_response.status_code == 200
                
                await self.log_result(
                    "Event CRUD Flow - Update & Delete",
                    update_success and delete_success,
                    f"Update: {'success' if update_success else 'failed'}, Delete: {'success' if delete_success else 'failed'}",
                    {
                        "update_status": update_response.status_code,
                        "delete_status": delete_response.status_code
                    }
                )
                
                # Clean up remaining event
                if event_ids[0]:
                    await self.client.delete(
                        f"{BACKEND_URL}/events/custom/{event_ids[0]}",
                        headers=self.get_auth_headers()
                    )
                
        except Exception as e:
            await self.log_result(
                "Event CRUD Flow - Exception",
                False,
                f"Error in CRUD flow test: {str(e)}"
            )

    async def run_all_tests(self):
        """Run comprehensive Event CRUD API tests"""
        print("🚀 Starting Event CRUD Backend API Testing")
        print("=" * 60)
        
        # Setup authentication
        auth_success = await self.register_and_login()
        if not auth_success:
            print("❌ Authentication failed - cannot proceed with tests")
            return
        
        # Test individual endpoints
        await self.test_get_events_endpoint()
        
        # Create event and get ID for update/delete tests
        created_event_id = await self.test_create_custom_event()
        
        # Test update and delete with the created event
        await self.test_update_custom_event(created_event_id)
        await self.test_delete_custom_event(created_event_id)
        
        # Test complete CRUD flow
        await self.test_event_crud_flow()
        
        # Generate summary
        await self.generate_summary()

    async def generate_summary(self):
        """Generate test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 60)
        print("📊 EVENT CRUD API TESTING SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS ({failed_tests}):")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  • {result['test']}: {result['details']}")
        
        print(f"\n✅ PASSED TESTS ({passed_tests}):")
        for result in self.test_results:
            if result["success"]:
                print(f"  • {result['test']}")
        
        print("\n" + "=" * 60)

    async def cleanup(self):
        """Clean up resources"""
        await self.client.aclose()

async def main():
    """Main test execution"""
    tester = EventCRUDTester()
    try:
        await tester.run_all_tests()
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    asyncio.run(main())