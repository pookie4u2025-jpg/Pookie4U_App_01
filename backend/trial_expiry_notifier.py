"""
Trial Expiry Notification Service - Phase 4
Checks for users whose trial is expiring in 2 days and sends push notifications
"""

from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
from push_notification_service import push_notification_service
import os
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration - resilient to missing env vars
mongo_url = os.environ.get('MONGO_URL')
if not mongo_url:
    logger.warning("⚠️ MONGO_URL not set in trial_expiry_notifier")
    mongo_url = "mongodb://localhost:27017"  # Fallback

try:
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ.get('DB_NAME', 'pookie4u')]
    logger.info("✅ Trial expiry notifier: MongoDB client initialized")
except Exception as e:
    logger.error(f"⚠️ Trial expiry notifier: Error initializing MongoDB: {e}")
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client[os.environ.get('DB_NAME', 'pookie4u')]

async def check_and_notify_trial_expiry():
    """
    Check for users whose trial expires in 2 days and send push notifications
    This should be run daily via cron job
    """
    try:
        logger.info("🔍 Starting trial expiry check...")
        
        # Calculate the target date (2 days from now)
        target_date = datetime.utcnow() + timedelta(days=2)
        # Get start and end of target day
        target_day_start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        target_day_end = target_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # Find users with trial expiring in 2 days
        users_query = {
            "subscription_type": "trial",
            "subscription_status": "active",
            "subscription_end_date": {
                "$gte": target_day_start,
                "$lte": target_day_end
            },
            "push_token": {"$exists": True, "$ne": None}
        }
        
        users_expiring = await db.users.find(users_query).to_list(length=1000)
        
        logger.info(f"📊 Found {len(users_expiring)} users with trial expiring in 2 days")
        
        notifications_sent = 0
        notifications_failed = 0
        
        for user in users_expiring:
            try:
                push_token = user.get("push_token")
                user_name = user.get("name", "User")
                partner_name = user.get("partner_profile", {}).get("name", "your partner")
                
                # Check if notification was already sent for this expiry
                notification_sent_key = f"trial_expiry_notified_{user['subscription_end_date'].strftime('%Y-%m-%d')}"
                
                if user.get(notification_sent_key):
                    logger.info(f"⏭️  Skipping {user['email']} - notification already sent")
                    continue
                
                # Create notification
                title = "⏰ Your Free Trial is Ending Soon!"
                body = f"Hi {user_name}! Your 14-day free trial expires in 2 days. Keep strengthening your relationship with {partner_name} by upgrading to premium."
                
                # Send push notification
                success = push_notification_service.send_push_notification(
                    push_token=push_token,
                    title=title,
                    body=body,
                    data={
                        "type": "trial_expiry",
                        "days_remaining": 2,
                        "screen": "subscription"
                    },
                    priority="high"
                )
                
                if success:
                    # Mark notification as sent
                    await db.users.update_one(
                        {"_id": user["_id"]},
                        {
                            "$set": {
                                notification_sent_key: True,
                                "last_trial_notification_sent": datetime.utcnow()
                            }
                        }
                    )
                    notifications_sent += 1
                    logger.info(f"✅ Notification sent to {user['email']}")
                else:
                    notifications_failed += 1
                    logger.warning(f"⚠️  Failed to send notification to {user['email']}")
                    
            except Exception as e:
                logger.error(f"❌ Error sending notification to {user.get('email', 'unknown')}: {e}")
                notifications_failed += 1
        
        logger.info(f"📤 Trial expiry check complete: {notifications_sent} sent, {notifications_failed} failed")
        
        return {
            "checked_at": datetime.utcnow().isoformat(),
            "users_found": len(users_expiring),
            "notifications_sent": notifications_sent,
            "notifications_failed": notifications_failed
        }
        
    except Exception as e:
        logger.error(f"❌ Error in trial expiry check: {e}")
        return {
            "error": str(e),
            "checked_at": datetime.utcnow().isoformat()
        }

async def main():
    """Main function to run the trial expiry checker"""
    result = await check_and_notify_trial_expiry()
    print(f"Result: {result}")
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
