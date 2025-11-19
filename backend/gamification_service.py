"""
Gamification Service for Pookie4u
Handles points, levels, streaks, and in-app store logic
"""

from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# LEVEL SYSTEM CONFIGURATION
# ============================================================================

LEVEL_THRESHOLDS = {
    1: {"name": "The Newcomer", "points": 0, "unlock": "Start your journey"},
    2: {"name": "The Beginner", "points": 1000, "unlock": "Badge: First Steps"},
    3: {"name": "The Committed", "points": 3000, "unlock": "Task History View"},
    4: {"name": "The Caring Partner", "points": 6000, "unlock": "Weekly Summary"},
    5: {"name": "The Consistent Partner", "points": 10000, "unlock": "Partner's Mood Tracker & Love Language Selection"},
    6: {"name": "The Dedicated", "points": 15000, "unlock": "Custom Task Notes"},
    7: {"name": "The Devoted", "points": 21000, "unlock": "Relationship Milestones Tracker"},
    8: {"name": "The Attentive", "points": 28000, "unlock": "Advanced Reminder Options"},
    9: {"name": "The Romantic", "points": 36000, "unlock": "Romantic Quote of the Day"},
    10: {"name": "The Thoughtful Pro", "points": 50000, "unlock": "Advanced Date Generator"},
    11: {"name": "The Effort Master", "points": 65000, "unlock": "Partner Appreciation Badge"},
    12: {"name": "The Relationship Guru", "points": 80000, "unlock": "Monthly Relationship Report"},
    13: {"name": "The Love Expert", "points": 90000, "unlock": "Personalized Task Themes"},
    14: {"name": "The Commitment King", "points": 95000, "unlock": "Priority Support"},
    15: {"name": "The Relationship Architect", "points": 100000, "unlock": "Love Language Task Filtering"},
    16: {"name": "The Devotion Champion", "points": 125000, "unlock": "Exclusive Event Templates"},
    17: {"name": "The Partnership Pro", "points": 150000, "unlock": "Advanced Analytics Dashboard"},
    18: {"name": "The Love Legend", "points": 175000, "unlock": "Lifetime Achievement Badge"},
    19: {"name": "The Romance Master", "points": 190000, "unlock": "VIP Features Access"},
    20: {"name": "The Effort Legend", "points": 200000, "unlock": "Anniversary Planning Toolkit & Hall of Fame"},
}

# ============================================================================
# POINTS CONFIGURATION
# ============================================================================

POINTS_DAILY_TASK = 50
POINTS_WEEKLY_TASK = 200
POINTS_BONUS_FAST_COMPLETION = 25  # Within 1 hour of reminder
POINTS_SPECIAL_EVENT = 500  # Birthday, Anniversary, etc.

# ============================================================================
# IN-APP STORE CONFIGURATION
# ============================================================================

STORE_ITEMS = {
    "doover_pass": {
        "name": "Do-Over Pass",
        "description": "Re-roll a generated task you can't or don't want to complete",
        "cost": 1000,
        "type": "consumable"
    },
    "advanced_message_pack": {
        "name": "Advanced Message Pack",
        "description": "Unlock 10 new, exclusive, high-impact pre-written messages",
        "cost": 2500,
        "type": "permanent"
    },
    "bailout_streak_save": {
        "name": "Bailout Streak Save",
        "description": "Save a lost streak once per month (returns to last completed day)",
        "cost": 10000,
        "type": "monthly_limited"
    }
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def calculate_level(total_points: int) -> Tuple[int, Dict]:
    """
    Calculate current level based on total points
    Returns: (level_number, level_info)
    """
    current_level = 1
    for level, info in LEVEL_THRESHOLDS.items():
        if total_points >= info["points"]:
            current_level = level
        else:
            break
    
    return current_level, LEVEL_THRESHOLDS[current_level]

def get_next_level_info(current_level: int) -> Optional[Dict]:
    """Get info about the next level"""
    next_level = current_level + 1
    if next_level in LEVEL_THRESHOLDS:
        return LEVEL_THRESHOLDS[next_level]
    return None

def calculate_points_for_task(
    task_type: str,
    is_special_event: bool = False,
    completed_within_hour: bool = False
) -> int:
    """
    Calculate points earned for completing a task
    
    Args:
        task_type: "daily" or "weekly"
        is_special_event: True if task is for birthday/anniversary
        completed_within_hour: True if completed within 1 hour of reminder
    
    Returns:
        Total points earned
    """
    base_points = 0
    
    if is_special_event:
        base_points = POINTS_SPECIAL_EVENT
    elif task_type == "daily":
        base_points = POINTS_DAILY_TASK
    elif task_type == "weekly":
        base_points = POINTS_WEEKLY_TASK
    
    bonus = POINTS_BONUS_FAST_COMPLETION if completed_within_hour else 0
    
    return base_points + bonus

def check_streak_status(
    last_completion_date: Optional[datetime],
    current_streak: int,
    daily_tasks_completed_today: int
) -> Tuple[int, bool]:
    """
    Check and update streak status
    
    Args:
        last_completion_date: Last time ALL 3 daily tasks were completed
        current_streak: Current streak count
        daily_tasks_completed_today: Number of daily tasks completed today
    
    Returns:
        (new_streak, streak_increased)
    """
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # If all 3 daily tasks completed today
    if daily_tasks_completed_today >= 3:
        # Check if last completion was yesterday
        if last_completion_date:
            last_completion_day = last_completion_date.replace(hour=0, minute=0, second=0, microsecond=0)
            yesterday = today_start - timedelta(days=1)
            
            if last_completion_day == yesterday:
                # Consecutive day - increase streak
                return current_streak + 1, True
            elif last_completion_day == today_start:
                # Already completed today - no change
                return current_streak, False
            else:
                # Gap in days - reset streak to 1
                return 1, True
        else:
            # First time completing - start streak
            return 1, True
    
    # Not all 3 tasks completed yet - check if streak should reset
    if last_completion_date:
        last_completion_day = last_completion_date.replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday = today_start - timedelta(days=1)
        
        # If last completion was before yesterday, streak is broken
        if last_completion_day < yesterday:
            return 0, False
    
    return current_streak, False

def is_eligible_for_weekly_draw(current_streak: int) -> bool:
    """Check if user is eligible for weekly cash prize draw"""
    return current_streak >= 7

def is_eligible_for_monthly_draw(current_streak: int) -> bool:
    """Check if user is eligible for monthly trip draw"""
    return current_streak >= 30

def can_purchase_item(
    item_id: str,
    available_points: int,
    bailout_used_this_month: bool,
    last_bailout_date: Optional[datetime]
) -> Tuple[bool, str]:
    """
    Check if user can purchase an item
    
    Returns:
        (can_purchase, reason_if_not)
    """
    if item_id not in STORE_ITEMS:
        return False, "Item not found"
    
    item = STORE_ITEMS[item_id]
    
    # Check points
    if available_points < item["cost"]:
        return False, f"Not enough points. Need {item['cost']}, have {available_points}"
    
    # Check monthly limitation for bailout
    if item_id == "bailout_streak_save":
        if bailout_used_this_month:
            return False, "Bailout Streak Save can only be used once per month"
        
        # Check if we're in a new month
        if last_bailout_date:
            now = datetime.utcnow()
            if last_bailout_date.year == now.year and last_bailout_date.month == now.month:
                return False, "Bailout Streak Save already used this month"
    
    return True, ""

def apply_bailout_streak_save(
    current_streak: int,
    last_completion_date: Optional[datetime]
) -> Tuple[int, datetime]:
    """
    Apply bailout streak save - returns streak to last completed day
    
    Returns:
        (restored_streak, restored_date)
    """
    if last_completion_date and current_streak == 0:
        # Return to the day before the missed day
        return max(1, current_streak), last_completion_date
    
    # If streak isn't broken, no change
    return current_streak, last_completion_date or datetime.utcnow()

def should_filter_by_love_language(user_level: int, love_language: Optional[str]) -> bool:
    """Check if task generation should filter by love language"""
    return user_level >= 15 and love_language is not None

# ============================================================================
# GAMIFICATION SERVICE CLASS
# ============================================================================

class GamificationService:
    """Main service for all gamification logic"""
    
    def __init__(self, db):
        self.db = db
    
    async def award_points_for_task(
        self,
        user_id: str,
        task_type: str,
        is_special_event: bool = False,
        completed_within_hour: bool = False
    ) -> Dict:
        """
        Award points for completing a task and update user stats
        
        Returns:
            {
                "points_earned": int,
                "total_points": int,
                "level_up": bool,
                "new_level": int,
                "new_level_info": dict,
                "streak_update": bool,
                "new_streak": int,
                "weekly_draw_eligible": bool,
                "monthly_draw_eligible": bool
            }
        """
        # Calculate points
        points_earned = calculate_points_for_task(
            task_type,
            is_special_event,
            completed_within_hour
        )
        
        # Get current user stats
        user = await self.db.users.find_one({"_id": user_id})
        if not user:
            raise ValueError("User not found")
        
        # Update points
        new_total_points = user.get("total_points", 0) + points_earned
        points_spent = user.get("points_spent", 0)
        new_available_points = new_total_points - points_spent
        
        # Check for level up
        old_level = user.get("current_level", 1)
        new_level, level_info = calculate_level(new_total_points)
        level_up = new_level > old_level
        
        # Update streak if daily task
        streak_update = False
        new_streak = user.get("current_streak", 0)
        if task_type == "daily":
            daily_count = user.get("daily_tasks_completed_today", 0) + 1
            
            new_streak, streak_update = check_streak_status(
                user.get("last_task_completion_date"),
                user.get("current_streak", 0),
                daily_count
            )
            
            # Update daily task count
            await self.db.users.update_one(
                {"_id": user_id},
                {"$set": {"daily_tasks_completed_today": daily_count}}
            )
            
            # If all 3 completed, update last_completion_date
            if daily_count >= 3:
                await self.db.users.update_one(
                    {"_id": user_id},
                    {"$set": {"last_task_completion_date": datetime.utcnow()}}
                )
        
        # Update user document
        update_doc = {
            "total_points": new_total_points,
            "available_points": new_available_points,
            "current_level": new_level,
            "current_streak": new_streak,
            "longest_streak": max(new_streak, user.get("longest_streak", 0)),
            "tasks_completed": user.get("tasks_completed", 0) + 1,
            "updated_at": datetime.utcnow()
        }
        
        await self.db.users.update_one(
            {"_id": user_id},
            {"$set": update_doc}
        )
        
        return {
            "points_earned": points_earned,
            "total_points": new_total_points,
            "available_points": new_available_points,
            "level_up": level_up,
            "new_level": new_level,
            "new_level_info": level_info if level_up else None,
            "streak_update": streak_update,
            "new_streak": new_streak,
            "weekly_draw_eligible": is_eligible_for_weekly_draw(new_streak),
            "monthly_draw_eligible": is_eligible_for_monthly_draw(new_streak)
        }
    
    async def purchase_store_item(
        self,
        user_id: str,
        item_id: str
    ) -> Dict:
        """
        Purchase an item from the in-app store
        
        Returns:
            {
                "success": bool,
                "message": str,
                "item": dict,
                "new_available_points": int
            }
        """
        user = await self.db.users.find_one({"_id": user_id})
        if not user:
            raise ValueError("User not found")
        
        # Check if can purchase
        can_purchase, reason = can_purchase_item(
            item_id,
            user.get("available_points", 0),
            user.get("bailout_used_this_month", False),
            user.get("last_bailout_date")
        )
        
        if not can_purchase:
            return {
                "success": False,
                "message": reason,
                "item": None,
                "new_available_points": user.get("available_points", 0)
            }
        
        item = STORE_ITEMS[item_id]
        
        # Deduct points
        new_points_spent = user.get("points_spent", 0) + item["cost"]
        new_available_points = user.get("total_points", 0) - new_points_spent
        
        update_doc = {
            "points_spent": new_points_spent,
            "available_points": new_available_points,
            "updated_at": datetime.utcnow()
        }
        
        # Special handling for bailout
        if item_id == "bailout_streak_save":
            update_doc["bailout_used_this_month"] = True
            update_doc["last_bailout_date"] = datetime.utcnow()
        
        await self.db.users.update_one(
            {"_id": user_id},
            {"$set": update_doc}
        )
        
        return {
            "success": True,
            "message": f"Successfully purchased {item['name']}",
            "item": item,
            "new_available_points": new_available_points
        }

# Initialize service (will be imported in server.py)
gamification_service = None

def init_gamification_service(db):
    """Initialize the gamification service with database"""
    global gamification_service
    gamification_service = GamificationService(db)
    return gamification_service
