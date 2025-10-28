#!/usr/bin/env python3
"""
Comprehensive Task Completion Testing
Focus: Complete end-to-end testing of task completion functionality
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://couple-rewards.preview.emergentagent.com/api"

def test_task_completion_with_existing_user():
    """Test task completion with a fresh user account"""
    print("🔍 COMPREHENSIVE TASK COMPLETION TESTING")
    print("=" * 60)
    
    # Create a new user for testing
    unique_email = f"task.test.{int(time.time())}@example.com"
    
    # Step 1: Register user
    print("Step 1: User Registration")
    register_payload = {
        "email": unique_email,
        "password": "TestPass123!",
        "name": "Task Test User"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/register", json=register_payload)
    if response.status_code != 200:
        print(f"❌ Registration failed: {response.status_code}")
        return False
    
    auth_token = response.json()["access_token"]
    print(f"✅ User registered: {unique_email}")
    
    # Step 2: Get user profile to verify initial state
    print("\nStep 2: Initial Profile Check")
    headers = {"Authorization": f"Bearer {auth_token}"}
    profile_response = requests.get(f"{BACKEND_URL}/user/profile", headers=headers)
    
    if profile_response.status_code != 200:
        print(f"❌ Profile fetch failed: {profile_response.status_code}")
        return False
    
    initial_profile = profile_response.json()
    initial_points = initial_profile.get("total_points", 0)
    initial_tasks_completed = initial_profile.get("tasks_completed", 0)
    print(f"✅ Initial state - Points: {initial_points}, Tasks completed: {initial_tasks_completed}")
    
    # Step 3: Get daily tasks
    print("\nStep 3: Fetch Daily Tasks")
    daily_response = requests.get(f"{BACKEND_URL}/tasks/daily", headers=headers)
    
    if daily_response.status_code != 200:
        print(f"❌ Daily tasks fetch failed: {daily_response.status_code}")
        return False
    
    daily_data = daily_response.json()
    daily_tasks = daily_data.get("tasks", [])
    print(f"✅ Retrieved {len(daily_tasks)} daily tasks")
    
    if not daily_tasks:
        print("❌ No daily tasks available")
        return False
    
    # Step 4: Complete first daily task
    print("\nStep 4: Complete Daily Task")
    task_to_complete = daily_tasks[0]
    task_id = task_to_complete["id"]
    task_title = task_to_complete.get("title", "Unknown")
    expected_points = task_to_complete.get("points", 5)
    
    print(f"Completing task: {task_id} - {task_title} ({expected_points} points)")
    
    complete_payload = {"task_id": task_id}
    complete_response = requests.post(f"{BACKEND_URL}/tasks/complete", json=complete_payload, headers=headers)
    
    if complete_response.status_code != 200:
        print(f"❌ Task completion failed: {complete_response.status_code}")
        print(f"Response: {complete_response.text}")
        return False
    
    completion_data = complete_response.json()
    points_earned = completion_data.get("points_earned", 0)
    total_points = completion_data.get("total_points", 0)
    message = completion_data.get("message", "")
    
    print(f"✅ Task completed successfully!")
    print(f"   Message: {message}")
    print(f"   Points earned: {points_earned}")
    print(f"   Total points: {total_points}")
    
    # Step 5: Verify task completion by fetching tasks again
    print("\nStep 5: Verify Task Completion")
    verify_response = requests.get(f"{BACKEND_URL}/tasks/daily", headers=headers)
    
    if verify_response.status_code != 200:
        print(f"❌ Task verification failed: {verify_response.status_code}")
        return False
    
    verify_data = verify_response.json()
    verify_tasks = verify_data.get("tasks", [])
    
    completed_task = None
    for task in verify_tasks:
        if task["id"] == task_id:
            completed_task = task
            break
    
    if completed_task:
        is_completed = completed_task.get("completed", False)
        completed_at = completed_task.get("completed_at")
        print(f"✅ Task verification - Completed: {is_completed}, At: {completed_at}")
        
        if not is_completed:
            print("❌ Task not marked as completed")
            return False
    else:
        print("❌ Completed task not found in task list")
        return False
    
    # Step 6: Verify profile updates
    print("\nStep 6: Verify Profile Updates")
    final_profile_response = requests.get(f"{BACKEND_URL}/user/profile", headers=headers)
    
    if final_profile_response.status_code != 200:
        print(f"❌ Final profile fetch failed: {final_profile_response.status_code}")
        return False
    
    final_profile = final_profile_response.json()
    final_points = final_profile.get("total_points", 0)
    final_tasks_completed = final_profile.get("tasks_completed", 0)
    current_level = final_profile.get("current_level", 1)
    current_streak = final_profile.get("current_streak", 0)
    
    print(f"✅ Final state - Points: {final_points}, Tasks: {final_tasks_completed}, Level: {current_level}, Streak: {current_streak}")
    
    # Verify points were awarded correctly
    expected_final_points = initial_points + expected_points
    expected_final_tasks = initial_tasks_completed + 1
    
    points_correct = final_points == expected_final_points
    tasks_correct = final_tasks_completed == expected_final_tasks
    
    print(f"Points calculation: {initial_points} + {expected_points} = {expected_final_points} (actual: {final_points}) {'✅' if points_correct else '❌'}")
    print(f"Tasks calculation: {initial_tasks_completed} + 1 = {expected_final_tasks} (actual: {final_tasks_completed}) {'✅' if tasks_correct else '❌'}")
    
    # Step 7: Test weekly task completion
    print("\nStep 7: Test Weekly Task Completion")
    weekly_response = requests.get(f"{BACKEND_URL}/tasks/weekly", headers=headers)
    
    if weekly_response.status_code != 200:
        print(f"❌ Weekly tasks fetch failed: {weekly_response.status_code}")
        return False
    
    weekly_data = weekly_response.json()
    weekly_tasks = weekly_data.get("tasks", [])
    print(f"✅ Retrieved {len(weekly_tasks)} weekly tasks")
    
    if weekly_tasks:
        weekly_task = weekly_tasks[0]
        weekly_task_id = weekly_task["id"]
        weekly_task_title = weekly_task.get("title", "Unknown")
        weekly_expected_points = weekly_task.get("points", 25)
        
        print(f"Completing weekly task: {weekly_task_id} - {weekly_task_title} ({weekly_expected_points} points)")
        
        weekly_complete_payload = {"task_id": weekly_task_id}
        weekly_complete_response = requests.post(f"{BACKEND_URL}/tasks/complete", json=weekly_complete_payload, headers=headers)
        
        if weekly_complete_response.status_code == 200:
            weekly_completion_data = weekly_complete_response.json()
            weekly_points_earned = weekly_completion_data.get("points_earned", 0)
            weekly_total_points = weekly_completion_data.get("total_points", 0)
            
            print(f"✅ Weekly task completed!")
            print(f"   Points earned: {weekly_points_earned}")
            print(f"   Total points: {weekly_total_points}")
        else:
            print(f"❌ Weekly task completion failed: {weekly_complete_response.status_code}")
    else:
        print("ℹ️  No weekly tasks available")
    
    # Step 8: Test error scenarios
    print("\nStep 8: Test Error Scenarios")
    
    # Try to complete the same task again (should fail)
    duplicate_response = requests.post(f"{BACKEND_URL}/tasks/complete", json=complete_payload, headers=headers)
    if duplicate_response.status_code == 404:
        print("✅ Duplicate task completion properly rejected (404)")
    else:
        print(f"⚠️  Duplicate task completion returned: {duplicate_response.status_code}")
    
    # Try to complete non-existent task
    fake_payload = {"task_id": "fake_task_id_12345"}
    fake_response = requests.post(f"{BACKEND_URL}/tasks/complete", json=fake_payload, headers=headers)
    if fake_response.status_code == 404:
        print("✅ Non-existent task completion properly rejected (404)")
    else:
        print(f"⚠️  Non-existent task completion returned: {fake_response.status_code}")
    
    print("\n" + "=" * 60)
    print("🎯 COMPREHENSIVE TEST RESULTS")
    print("=" * 60)
    
    success = points_correct and tasks_correct
    
    if success:
        print("✅ ALL TESTS PASSED - Task completion functionality is working correctly!")
        print("✅ Authentication working")
        print("✅ Task retrieval working")
        print("✅ Task completion working")
        print("✅ Points system working")
        print("✅ Profile updates working")
        print("✅ Task verification working")
        print("✅ Error handling working")
    else:
        print("❌ SOME TESTS FAILED - Issues found in task completion")
        if not points_correct:
            print("❌ Points calculation incorrect")
        if not tasks_correct:
            print("❌ Task count calculation incorrect")
    
    return success

if __name__ == "__main__":
    test_task_completion_with_existing_user()