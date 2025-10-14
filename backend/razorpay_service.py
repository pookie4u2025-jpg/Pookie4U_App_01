"""
Razorpay Subscription Service
Handles subscription creation, verification, and management
"""

import razorpay
import os
from dotenv import load_dotenv
from typing import Dict, Any, Optional
import hmac
import hashlib

load_dotenv()

# Initialize Razorpay client
RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID')
RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET')
RAZORPAY_MONTHLY_PLAN_ID = os.getenv('RAZORPAY_MONTHLY_PLAN_ID')
RAZORPAY_SIXMONTH_PLAN_ID = os.getenv('RAZORPAY_SIXMONTH_PLAN_ID')

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))


class RazorpaySubscriptionService:
    """Service for handling Razorpay subscriptions"""
    
    @staticmethod
    def create_subscription(plan_type: str, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new subscription
        
        Args:
            plan_type: 'monthly' or 'sixmonth'
            customer_data: User information (email, name, phone)
            
        Returns:
            Subscription details including subscription_id and payment link
        """
        try:
            # Get plan ID based on type
            plan_id = RAZORPAY_MONTHLY_PLAN_ID if plan_type == 'monthly' else RAZORPAY_SIXMONTH_PLAN_ID
            
            if not plan_id:
                raise ValueError(f"Plan ID not configured for {plan_type}")
            
            # Create subscription payload
            subscription_data = {
                'plan_id': plan_id,
                'customer_notify': 1,  # Send email/SMS to customer
                'quantity': 1,
                'total_count': 12 if plan_type == 'monthly' else 2,  # 12 months or 2 x 6-month cycles
                'start_at': None,  # Start immediately after trial
                'addons': [],
                'notes': {
                    'app_name': 'Pookie4u',
                    'user_email': customer_data.get('email', ''),
                    'plan_type': plan_type
                }
            }
            
            # Add customer details if available
            if customer_data.get('email'):
                subscription_data['customer_notify'] = 1
            
            # Create subscription
            subscription = razorpay_client.subscription.create(subscription_data)
            
            return {
                'success': True,
                'subscription_id': subscription['id'],
                'plan_id': plan_id,
                'status': subscription['status'],
                'short_url': subscription.get('short_url'),
                'customer_notify': subscription['customer_notify'],
                'start_at': subscription.get('start_at'),
                'end_at': subscription.get('end_at'),
                'current_start': subscription.get('current_start'),
                'current_end': subscription.get('current_end'),
            }
            
        except Exception as e:
            print(f"❌ Error creating subscription: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def verify_payment_signature(payment_id: str, subscription_id: str, signature: str) -> bool:
        """
        Verify Razorpay payment signature
        
        Args:
            payment_id: Razorpay payment ID
            subscription_id: Razorpay subscription ID
            signature: Signature to verify
            
        Returns:
            True if signature is valid, False otherwise
        """
        try:
            # Create expected signature
            message = f"{subscription_id}|{payment_id}"
            generated_signature = hmac.new(
                RAZORPAY_KEY_SECRET.encode(),
                message.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures
            return hmac.compare_digest(generated_signature, signature)
            
        except Exception as e:
            print(f"❌ Error verifying signature: {str(e)}")
            return False
    
    @staticmethod
    def get_subscription_details(subscription_id: str) -> Optional[Dict[str, Any]]:
        """
        Get subscription details
        
        Args:
            subscription_id: Razorpay subscription ID
            
        Returns:
            Subscription details or None if error
        """
        try:
            subscription = razorpay_client.subscription.fetch(subscription_id)
            
            return {
                'id': subscription['id'],
                'plan_id': subscription['plan_id'],
                'status': subscription['status'],
                'quantity': subscription['quantity'],
                'start_at': subscription.get('start_at'),
                'end_at': subscription.get('end_at'),
                'customer_notify': subscription['customer_notify'],
                'created_at': subscription['created_at'],
                'paid_count': subscription['paid_count'],
                'remaining_count': subscription['remaining_count'],
                'short_url': subscription.get('short_url'),
            }
            
        except Exception as e:
            print(f"❌ Error fetching subscription: {str(e)}")
            return None
    
    @staticmethod
    def cancel_subscription(subscription_id: str, cancel_at_cycle_end: bool = False) -> Dict[str, Any]:
        """
        Cancel a subscription
        
        Args:
            subscription_id: Razorpay subscription ID
            cancel_at_cycle_end: If True, cancel at end of billing cycle
            
        Returns:
            Cancellation result
        """
        try:
            subscription = razorpay_client.subscription.cancel(
                subscription_id,
                {'cancel_at_cycle_end': 1 if cancel_at_cycle_end else 0}
            )
            
            return {
                'success': True,
                'subscription_id': subscription['id'],
                'status': subscription['status'],
                'ended_at': subscription.get('ended_at'),
            }
            
        except Exception as e:
            print(f"❌ Error cancelling subscription: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def pause_subscription(subscription_id: str) -> Dict[str, Any]:
        """
        Pause a subscription
        
        Args:
            subscription_id: Razorpay subscription ID
            
        Returns:
            Pause result
        """
        try:
            subscription = razorpay_client.subscription.pause(subscription_id)
            
            return {
                'success': True,
                'subscription_id': subscription['id'],
                'status': subscription['status'],
            }
            
        except Exception as e:
            print(f"❌ Error pausing subscription: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def resume_subscription(subscription_id: str) -> Dict[str, Any]:
        """
        Resume a paused subscription
        
        Args:
            subscription_id: Razorpay subscription ID
            
        Returns:
            Resume result
        """
        try:
            subscription = razorpay_client.subscription.resume(subscription_id)
            
            return {
                'success': True,
                'subscription_id': subscription['id'],
                'status': subscription['status'],
            }
            
        except Exception as e:
            print(f"❌ Error resuming subscription: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def get_plan_details(plan_type: str) -> Optional[Dict[str, Any]]:
        """
        Get plan details
        
        Args:
            plan_type: 'monthly' or 'sixmonth'
            
        Returns:
            Plan details or None if error
        """
        try:
            plan_id = RAZORPAY_MONTHLY_PLAN_ID if plan_type == 'monthly' else RAZORPAY_SIXMONTH_PLAN_ID
            
            if not plan_id:
                return None
            
            plan = razorpay_client.plan.fetch(plan_id)
            
            return {
                'id': plan['id'],
                'name': plan.get('item', {}).get('name', ''),
                'amount': plan['item']['amount'],
                'currency': plan['item']['currency'],
                'period': plan['period'],
                'interval': plan['interval'],
                'description': plan.get('description', ''),
            }
            
        except Exception as e:
            print(f"❌ Error fetching plan: {str(e)}")
            return None


# Export service instance
razorpay_service = RazorpaySubscriptionService()
