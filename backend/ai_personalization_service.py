"""
AI Personalization Service for Pookie4u
Provides AI-powered personalized messages, gift recommendations, and date planning
Uses GPT-3.5 Turbo for cost optimization (~₹7/user/month)
"""

import os
import json
import asyncio
from datetime import datetime
from typing import List, Dict, Optional, Any
from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage

# Load environment variables
load_dotenv()

# Message categories
MESSAGE_CATEGORIES = {
    "good_morning": "Start the day with love",
    "good_night": "End the day sweetly",
    "love_confession": "Express deep feelings",
    "apology": "Make things right",
    "funny_hinglish": "Lighthearted and fun",
    "missing_you": "Express longing",
    "appreciation": "Show gratitude",
    "encouragement": "Boost confidence"
}

# Relationship mode contexts
RELATIONSHIP_CONTEXTS = {
    "SAME_HOME": "living together in the same home, see each other daily",
    "DAILY_IRL": "meeting daily but living separately",
    "LONG_DISTANCE": "in a long-distance relationship, communicate mainly through messages/calls"
}


class AIPersonalizationService:
    """Service for AI-powered personalization features"""
    
    def __init__(self):
        # Get Emergent LLM key
        self.api_key = os.getenv("EMERGENT_LLM_KEY")
        if not self.api_key:
            raise ValueError("EMERGENT_LLM_KEY not found in environment variables")
        
        # Initialize LLM chat with GPT-3.5 Turbo for cost optimization
        self.llm = LlmChat(
            api_key=self.api_key,
            session_id="personalization",
            system_message="You are a relationship assistant helping create personalized romantic content."
        ).with_model("openai", "gpt-3.5-turbo")
    
    async def generate_personalized_message(
        self,
        category: str,
        user_name: str,
        partner_name: str,
        relationship_mode: str,
        context: Optional[Dict] = None
    ) -> str:
        """
        Generate a personalized romantic message using AI
        
        Cost-optimized prompt: ~150 tokens input + ~50 tokens output = 200 tokens
        Cost per call: ~₹0.02 with GPT-3.5 Turbo
        """
        
        # Build efficient context
        mode_context = RELATIONSHIP_CONTEXTS.get(relationship_mode, "in a relationship")
        category_desc = MESSAGE_CATEGORIES.get(category, "romantic message")
        
        # Ultra-efficient prompt (minimizes tokens)
        prompt = f"""Write 1 short romantic {category} message from {user_name} to {partner_name}.
Context: They're {mode_context}.
Style: Warm, personal, 1-2 sentences.
Tone: {category_desc}.
No emojis. Direct and heartfelt."""

        try:
            response = await asyncio.to_thread(
                self.llm.run_chat,
                [UserMessage(content=prompt)],
                model="gpt-3.5-turbo",  # Cost-optimized
                temperature=0.8,
                max_tokens=60  # Limit output tokens
            )
            
            message = response.choices[0].message.content.strip()
            # Remove quotes if present
            message = message.strip('"\'')
            return message
            
        except Exception as e:
            # Fallback to generic message
            fallbacks = {
                "good_morning": f"Good morning {partner_name}! Thinking of you ☀️",
                "good_night": f"Sweet dreams {partner_name}. Sleep well 🌙",
                "love_confession": f"I love you {partner_name}. You mean everything to me ❤️",
                "apology": f"I'm sorry {partner_name}. You matter more than being right.",
                "funny_hinglish": f"Baby, you're my favorite distraction! 😄"
            }
            return fallbacks.get(category, f"Thinking of you, {partner_name} ❤️")
    
    async def generate_gift_recommendations(
        self,
        partner_profile: Dict,
        occasion: str,
        budget: str,
        available_gifts: List[Dict]
    ) -> List[Dict]:
        """
        AI-enhanced gift filtering based on partner profile
        
        Cost-optimized: ~200 tokens input + ~100 tokens output = 300 tokens
        Cost per call: ~₹0.03 with GPT-3.5 Turbo
        """
        
        # Extract key info
        interests = partner_profile.get('favorite_activities', 'various interests')
        fav_food = partner_profile.get('favorite_food', 'treats')
        
        # Build gift list string efficiently
        gift_list = "\n".join([
            f"{g['id']}. {g['name']} ({g['category']}, {g['price_range']})"
            for g in available_gifts
        ])
        
        # Efficient prompt
        prompt = f"""Partner likes: {interests}, loves {fav_food}.
Occasion: {occasion}. Budget: {budget}.

Gifts available:
{gift_list}

Rank top 3 gift IDs that match best. Format: Just IDs comma-separated.
Example: 2,5,1"""

        try:
            response = await asyncio.to_thread(
                self.llm.run_chat,
                [UserMessage(content=prompt)],
                model="gpt-3.5-turbo",
                temperature=0.3,  # More deterministic
                max_tokens=20  # Just need IDs
            )
            
            # Parse response
            result = response.choices[0].message.content.strip()
            recommended_ids = [id.strip() for id in result.split(',')]
            
            # Return gifts in recommended order
            recommended_gifts = []
            for gift_id in recommended_ids:
                for gift in available_gifts:
                    if gift['id'] == gift_id:
                        recommended_gifts.append(gift)
                        break
            
            # Fill remaining with other gifts
            for gift in available_gifts:
                if gift not in recommended_gifts:
                    recommended_gifts.append(gift)
            
            return recommended_gifts[:6]  # Return top 6
            
        except Exception as e:
            # Fallback: return gifts as-is
            return available_gifts
    
    async def generate_date_plan(
        self,
        relationship_mode: str,
        budget: str,
        preferences: Optional[str] = None,
        location: Optional[str] = None
    ) -> Dict:
        """
        Generate AI-powered date plan
        
        Cost-optimized: ~250 tokens input + ~200 tokens output = 450 tokens
        Cost per call: ~₹0.05 with GPT-3.5 Turbo
        """
        
        mode_context = RELATIONSHIP_CONTEXTS.get(relationship_mode, "in a relationship")
        pref_text = f"Preferences: {preferences}." if preferences else ""
        location_text = f"Location: {location}." if location else ""
        
        # Efficient prompt
        prompt = f"""Create a date plan for couple {mode_context}.
Budget: {budget}. {pref_text} {location_text}

Provide in this exact format:
Title: [creative 3-4 word title]
Time: [best time]
Duration: [hours]
Activity: [main activity description, 2-3 sentences]
Why: [why it's romantic, 1 sentence]
Tips: [2 quick tips]
Budget: [estimated cost]"""

        try:
            response = await asyncio.to_thread(
                self.llm.run_chat,
                [UserMessage(content=prompt)],
                model="gpt-3.5-turbo",
                temperature=0.9,  # More creative
                max_tokens=250
            )
            
            result = response.choices[0].message.content.strip()
            
            # Parse response
            date_plan = {
                "title": "",
                "time": "",
                "duration": "",
                "activity": "",
                "why_romantic": "",
                "tips": [],
                "estimated_cost": budget
            }
            
            lines = result.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('Title:'):
                    date_plan['title'] = line.replace('Title:', '').strip()
                elif line.startswith('Time:'):
                    date_plan['time'] = line.replace('Time:', '').strip()
                elif line.startswith('Duration:'):
                    date_plan['duration'] = line.replace('Duration:', '').strip()
                elif line.startswith('Activity:'):
                    date_plan['activity'] = line.replace('Activity:', '').strip()
                elif line.startswith('Why:'):
                    date_plan['why_romantic'] = line.replace('Why:', '').strip()
                elif line.startswith('Tips:'):
                    tips_text = line.replace('Tips:', '').strip()
                    date_plan['tips'] = [t.strip() for t in tips_text.split('.') if t.strip()]
                elif line.startswith('Budget:'):
                    date_plan['estimated_cost'] = line.replace('Budget:', '').strip()
            
            return date_plan
            
        except Exception as e:
            # Fallback date plan
            fallback_plans = {
                "SAME_HOME": {
                    "title": "Cozy Home Date Night",
                    "time": "Evening after dinner",
                    "duration": "2-3 hours",
                    "activity": "Cook a special meal together, set up candles, play favorite music, and watch a romantic movie on the couch with homemade snacks.",
                    "why_romantic": "Creating special moments in your everyday space strengthens intimacy and shows effort.",
                    "tips": ["Turn off phones for distraction-free time", "Dress up a bit to make it special"],
                    "estimated_cost": budget
                },
                "DAILY_IRL": {
                    "title": "Sunset Walk & Treats",
                    "time": "Late afternoon/early evening",
                    "duration": "1-2 hours",
                    "activity": "Take a relaxed walk in a nearby park or scenic spot during sunset. Stop by a favorite café or ice cream place for treats while chatting about dreams and memories.",
                    "why_romantic": "Simple moments together create lasting memories and deepen connection.",
                    "tips": ["Hold hands throughout", "Take a photo at sunset together"],
                    "estimated_cost": budget
                },
                "LONG_DISTANCE": {
                    "title": "Virtual Movie Night",
                    "time": "Evening at convenient time for both",
                    "duration": "2-3 hours",
                    "activity": "Schedule a video call and watch the same movie simultaneously using a streaming service. Prepare matching snacks beforehand and chat during breaks.",
                    "why_romantic": "Sharing experiences despite distance maintains closeness and creates shared memories.",
                    "tips": ["Count down to press play together", "Share reactions throughout the movie"],
                    "estimated_cost": budget
                }
            }
            return fallback_plans.get(relationship_mode, fallback_plans["DAILY_IRL"])


# Initialize service
ai_personalization_service = AIPersonalizationService()


# Helper functions for easy access
async def generate_ai_message(category: str, user_name: str, partner_name: str, 
                              relationship_mode: str, context: Optional[Dict] = None) -> str:
    """Generate personalized message"""
    return await ai_personalization_service.generate_personalized_message(
        category, user_name, partner_name, relationship_mode, context
    )


async def get_ai_gift_recommendations(partner_profile: Dict, occasion: str, 
                                     budget: str, available_gifts: List[Dict]) -> List[Dict]:
    """Get AI-enhanced gift recommendations"""
    return await ai_personalization_service.generate_gift_recommendations(
        partner_profile, occasion, budget, available_gifts
    )


async def plan_ai_date(relationship_mode: str, budget: str, 
                      preferences: Optional[str] = None, 
                      location: Optional[str] = None) -> Dict:
    """Generate AI date plan"""
    return await ai_personalization_service.generate_date_plan(
        relationship_mode, budget, preferences, location
    )
