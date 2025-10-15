"""
Subscription Management Service for Pookie4u
Handles trial, monthly, and half-yearly subscriptions with Razorpay integration
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pydantic import BaseModel


class SubscriptionInfo(BaseModel):
    """Subscription information model"""
    subscription_type: str  # none, trial, monthly, half_yearly
    subscription_status: str  # inactive, active, expired, cancelled
    subscription_start_date: Optional[datetime] = None
    subscription_end_date: Optional[datetime] = None
    trial_started: bool = False
    days_remaining: Optional[int] = None
    is_active: bool = False
    can_start_trial: bool = True
    razorpay_subscription_id: Optional[str] = None


class SubscriptionService:
    """Service for managing subscriptions"""
    
    TRIAL_DAYS = 14
    MONTHLY_PRICE = 7900  # in paise (₹79.00)
    HALF_YEARLY_PRICE = 45000  # in paise (₹450.00)
    
    SUBSCRIPTION_PLANS = {
        "trial": {
            "name": "14-Day Free Trial",
            "duration_days": 14,
            "price": 0,
            "description": "Try all premium features free for 14 days"
        },
        "monthly": {
            "name": "Monthly Plan",
            "duration_days": 30,
            "price": MONTHLY_PRICE,
            "description": "₹79 per month, billed monthly"
        },
        "half_yearly": {
            "name": "6-Month Plan",
            "duration_days": 180,
            "price": HALF_YEARLY_PRICE,
            "description": "₹450 for 6 months, save ₹24"
        }
    }
    
    @staticmethod
    def get_subscription_info(user_data: Dict[str, Any]) -> SubscriptionInfo:
        """Get subscription information for a user"""
        subscription_type = user_data.get("subscription_type", "none")
        subscription_status = user_data.get("subscription_status", "inactive")
        subscription_start_date = user_data.get("subscription_start_date")
        subscription_end_date = user_data.get("subscription_end_date")
        trial_started = user_data.get("trial_started", False)
        razorpay_subscription_id = user_data.get("razorpay_subscription_id")
        
        # Calculate days remaining
        days_remaining = None
        is_active = False
        
        if subscription_end_date and subscription_status == "active":
            if isinstance(subscription_end_date, str):
                subscription_end_date = datetime.fromisoformat(subscription_end_date.replace('Z', '+00:00'))
            
            now = datetime.utcnow()
            if subscription_end_date > now:
                days_remaining = (subscription_end_date - now).days
                is_active = True
            else:
                # Subscription expired
                subscription_status = "expired"
                is_active = False
        
        # Can start trial if never started before
        can_start_trial = not trial_started
        
        return SubscriptionInfo(
            subscription_type=subscription_type,
            subscription_status=subscription_status,
            subscription_start_date=subscription_start_date,
            subscription_end_date=subscription_end_date,
            trial_started=trial_started,
            days_remaining=days_remaining,
            is_active=is_active,
            can_start_trial=can_start_trial,
            razorpay_subscription_id=razorpay_subscription_id
        )
    
    @staticmethod
    def start_trial(user_id: str) -> Dict[str, Any]:
        """Start free trial for user"""
        now = datetime.utcnow()
        trial_end = now + timedelta(days=SubscriptionService.TRIAL_DAYS)
        
        return {
            "subscription_type": "trial",
            "subscription_status": "active",
            "subscription_start_date": now,
            "subscription_end_date": trial_end,
            "trial_started": True,
            "updated_at": now
        }
    
    @staticmethod
    def create_subscription(subscription_type: str, razorpay_subscription_id: str, razorpay_customer_id: str) -> Dict[str, Any]:
        """Create paid subscription"""
        now = datetime.utcnow()
        
        if subscription_type == "monthly":
            end_date = now + timedelta(days=30)
        elif subscription_type == "half_yearly":
            end_date = now + timedelta(days=180)
        else:
            raise ValueError(f"Invalid subscription type: {subscription_type}")
        
        return {
            "subscription_type": subscription_type,
            "subscription_status": "active",
            "subscription_start_date": now,
            "subscription_end_date": end_date,
            "razorpay_subscription_id": razorpay_subscription_id,
            "razorpay_customer_id": razorpay_customer_id,
            "updated_at": now
        }
    
    @staticmethod
    def cancel_subscription() -> Dict[str, Any]:
        """Cancel active subscription"""
        return {
            "subscription_status": "cancelled",
            "updated_at": datetime.utcnow()
        }
    
    @staticmethod
    def check_and_expire_subscriptions(user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check if subscription has expired and update status"""
        subscription_end_date = user_data.get("subscription_end_date")
        subscription_status = user_data.get("subscription_status")
        
        if subscription_end_date and subscription_status == "active":
            if isinstance(subscription_end_date, str):
                subscription_end_date = datetime.fromisoformat(subscription_end_date.replace('Z', '+00:00'))
            
            if datetime.utcnow() > subscription_end_date:
                return {
                    "subscription_status": "expired",
                    "updated_at": datetime.utcnow()
                }
        
        return None
    
    @staticmethod
    def get_display_text(subscription_info: SubscriptionInfo) -> str:
        """Get display text for subscription"""
        if subscription_info.subscription_status == "active":
            if subscription_info.subscription_type == "trial":
                return f"Free Trial - {subscription_info.days_remaining} days left"
            elif subscription_info.subscription_type == "monthly":
                return "Premium - ₹79/month"
            elif subscription_info.subscription_type == "half_yearly":
                return "Premium - ₹450/6 months"
        elif subscription_info.subscription_status == "expired":
            return "Subscription Expired"
        elif subscription_info.subscription_status == "cancelled":
            return "Subscription Cancelled"
        else:
            return "No Active Subscription"


# Initialize service
subscription_service = SubscriptionService()
