"""
Push Notification Service for Pookie4u
Handles Expo push notifications for event reminders, tasks, streaks, etc.
"""

from exponent_server_sdk import (
    DeviceNotRegisteredError,
    PushClient,
    PushMessage,
    PushServerError,
    PushTicketError,
)
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class PushNotificationService:
    """Service for sending push notifications via Expo"""
    
    def __init__(self):
        self.client = PushClient()
    
    def send_push_notification(
        self,
        push_token: str,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
        sound: str = "default",
        badge: Optional[int] = None,
        category: Optional[str] = None,
        priority: str = "default"
    ) -> bool:
        """
        Send a push notification to a single device
        
        Args:
            push_token: Expo push token
            title: Notification title
            body: Notification body
            data: Custom data to send with notification
            sound: Sound to play (default, null, or custom)
            badge: Badge count
            category: Notification category
            priority: default or high
            
        Returns:
            bool: True if sent successfully
        """
        try:
            # Validate token format
            if not PushClient.is_exponent_push_token(push_token):
                logger.error(f"Invalid push token format: {push_token}")
                return False
            
            # Create message
            message = PushMessage(
                to=push_token,
                title=title,
                body=body,
                data=data or {},
                sound=sound,
                badge=badge,
                category_id=category,
                priority=priority
            )
            
            # Send notification
            response = self.client.publish(message)
            
            # Check for errors
            if response.push_ticket:
                if response.push_ticket.status == 'error':
                    logger.error(f"Push notification error: {response.push_ticket.message}")
                    # Handle DeviceNotRegistered error
                    if response.push_ticket.details and \
                       response.push_ticket.details.get('error') == 'DeviceNotRegistered':
                        logger.warning(f"Device not registered: {push_token}")
                        return False
                    return False
                return True
            
            return True
            
        except PushServerError as e:
            logger.error(f"Push server error: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending push notification: {e}")
            return False
    
    def send_bulk_notifications(
        self,
        notifications: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """
        Send multiple push notifications
        
        Args:
            notifications: List of notification dicts with keys:
                - push_token (required)
                - title (required)
                - body (required)
                - data (optional)
                - sound (optional)
                - badge (optional)
                - category (optional)
                
        Returns:
            Dict with success and failure counts
        """
        results = {"success": 0, "failed": 0}
        
        for notif in notifications:
            success = self.send_push_notification(
                push_token=notif.get("push_token"),
                title=notif.get("title"),
                body=notif.get("body"),
                data=notif.get("data"),
                sound=notif.get("sound", "default"),
                badge=notif.get("badge"),
                category=notif.get("category")
            )
            
            if success:
                results["success"] += 1
            else:
                results["failed"] += 1
        
        return results
    
    # Predefined notification templates
    
    def send_event_reminder(
        self,
        push_token: str,
        event_name: str,
        days_until: int,
        event_date: str
    ) -> bool:
        """Send event reminder notification"""
        
        if days_until == 0:
            title = f"🎉 Today: {event_name}"
            body = f"Don't forget! {event_name} is today!"
        elif days_until == 1:
            title = f"📅 Tomorrow: {event_name}"
            body = f"{event_name} is tomorrow! Time to prepare!"
        elif days_until <= 3:
            title = f"⏰ {event_name} in {days_until} days"
            body = f"Coming up soon: {event_name}"
        else:
            title = f"📆 {event_name} in {days_until} days"
            body = f"Mark your calendar: {event_name} on {event_date}"
        
        return self.send_push_notification(
            push_token=push_token,
            title=title,
            body=body,
            data={
                "type": "event_reminder",
                "event_name": event_name,
                "days_until": days_until,
                "event_date": event_date
            },
            category="event_reminder",
            priority="high" if days_until <= 1 else "default"
        )
    
    def send_daily_tasks_notification(
        self,
        push_token: str,
        task_count: int = 3
    ) -> bool:
        """Send daily tasks available notification"""
        
        return self.send_push_notification(
            push_token=push_token,
            title="💕 New Daily Tasks!",
            body=f"{task_count} new relationship tasks are waiting for you!",
            data={
                "type": "daily_tasks",
                "task_count": task_count
            },
            category="new_tasks"
        )
    
    def send_streak_warning(
        self,
        push_token: str,
        streak_count: int,
        hours_remaining: int
    ) -> bool:
        """Send streak ending warning"""
        
        return self.send_push_notification(
            push_token=push_token,
            title=f"⚡ Don't lose your {streak_count}-day streak!",
            body=f"Complete a task in the next {hours_remaining} hours to keep your streak alive!",
            data={
                "type": "streak_warning",
                "streak_count": streak_count,
                "hours_remaining": hours_remaining
            },
            category="streak_ending",
            priority="high"
        )
    
    def send_love_message_notification(
        self,
        push_token: str,
        message_preview: str
    ) -> bool:
        """Send daily love message notification"""
        
        return self.send_push_notification(
            push_token=push_token,
            title="❤️ New Love Message",
            body=message_preview[:50] + "..." if len(message_preview) > 50 else message_preview,
            data={
                "type": "love_message"
            },
            category="daily_love_message"
        )
    
    def send_gift_idea_notification(
        self,
        push_token: str,
        occasion: str
    ) -> bool:
        """Send gift idea notification"""
        
        return self.send_push_notification(
            push_token=push_token,
            title=f"🎁 Perfect Gift Idea!",
            body=f"We found the perfect gift for {occasion}!",
            data={
                "type": "gift_idea",
                "occasion": occasion
            },
            category="gift_ideas"
        )
    
    def send_weekly_winner_notification(
        self,
        push_token: str,
        points: int,
        rank: int
    ) -> bool:
        """Send weekly winner notification"""
        
        return self.send_push_notification(
            push_token=push_token,
            title="🏆 You're a Weekly Winner!",
            body=f"Congratulations! You earned {points} points this week! Rank #{rank}",
            data={
                "type": "weekly_winner",
                "points": points,
                "rank": rank
            },
            category="weekly_winner",
            priority="high"
        )
    
    def send_subscription_expiring_notification(
        self,
        push_token: str,
        days_remaining: int,
        subscription_type: str
    ) -> bool:
        """Send subscription expiring notification"""
        
        return self.send_push_notification(
            push_token=push_token,
            title="⏰ Subscription Expiring Soon",
            body=f"Your {subscription_type} subscription expires in {days_remaining} days",
            data={
                "type": "subscription_expiring",
                "days_remaining": days_remaining,
                "subscription_type": subscription_type
            },
            category="subscription",
            priority="high" if days_remaining <= 3 else "default"
        )


# Initialize service
push_notification_service = PushNotificationService()
