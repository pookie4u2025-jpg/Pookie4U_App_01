"""
Enhanced Calendar Service for Pookie4u
Comprehensive event management with Indian + International calendars, 
auto-generated personal events, reminders, and event-specific tips/tasks
"""

import os
from datetime import datetime, timedelta, date
from typing import List, Dict, Any, Optional
import uuid
from dateutil import parser
import calendar

class EnhancedCalendarService:
    """Comprehensive calendar service for relationship events"""
    
    def __init__(self):
        self.current_year = datetime.now().year
        self.next_year = self.current_year + 1
    
    def get_merged_calendar_events(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Get complete merged calendar with all event types"""
        
        # Get all event categories
        indian_festivals = self._get_indian_festivals()
        international_holidays = self._get_international_holidays()
        romantic_calendar = self._get_romantic_calendar()
        seasonal_events = self._get_seasonal_events()
        
        # Auto-generate personal events from user profile
        personal_events = self._generate_personal_events(user_profile)
        
        # Get custom events from user
        custom_events = user_profile.get("custom_events", [])
        
        # Add prefilled flag to system events
        for event in indian_festivals + international_holidays + romantic_calendar + seasonal_events:
            event["prefilled"] = True
        
        # Merge all events
        all_events = (
            indian_festivals + 
            international_holidays + 
            romantic_calendar + 
            seasonal_events + 
            personal_events + 
            custom_events
        )
        
        # Sort by upcoming dates first
        sorted_events = self._sort_events_upcoming_first(all_events)
        
        # Add reminders (10-day default)
        events_with_reminders = self._add_default_reminders(sorted_events)
        
        return {
            "events": events_with_reminders,
            "total_count": len(events_with_reminders),
            "categories": self._get_event_categories(),
            "upcoming_count": len([e for e in events_with_reminders if self._is_upcoming(e["date"])]),
            "this_month_count": len([e for e in events_with_reminders if self._is_this_month(e["date"])]),
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def _get_indian_festivals(self) -> List[Dict[str, Any]]:
        """Comprehensive Indian festivals with relationship focus"""
        return [
            # Major Women-Centric Festivals
            {
                "id": "karwa_chauth_2025",
                "name": "Karva Chauth",
                "date": f"{self.current_year}-10-09",
                "category": "indian_festival",
                "type": "religious",
                "importance": "high",
                "description": "Sacred fast kept by wives for husband's long life and prosperity",
                "cultural_significance": "Celebrates marital devotion and love",
                "prefilled": True,
                "tips": [
                    "Book a romantic moonlit dinner for after the fast",
                    "Gift her beautiful traditional jewelry",
                    "Arrange mehendi artist for intricate henna designs",
                    "Plan a surprise moonlight celebration on the terrace",
                    "Gift elegant saree or lehenga for the occasion"
                ],
                "tasks": [
                    {"task": "Book romantic restaurant for evening", "category": "planning", "points": 10},
                    {"task": "Buy beautiful jewelry as Karva Chauth gift", "category": "shopping", "points": 15},
                    {"task": "Arrange mehendi artist booking", "category": "arrangements", "points": 10},
                    {"task": "Plan moonlight dinner setup at home", "category": "romantic", "points": 20}
                ],
                "gift_suggestions": ["Gold jewelry", "Traditional sarees", "Mehendi design books", "Romantic dinner setup"],
                "traditional_colors": ["Red", "Pink", "Gold"],
                "celebration_time": "evening_to_night",
                "duration_days": 1
            },
            
            {
                "id": "teej_2025",
                "name": "Hariyali Teej", 
                "date": f"{self.current_year}-08-07",
                "category": "indian_festival",
                "type": "seasonal",
                "importance": "medium",
                "description": "Festival celebrating marital bliss, monsoon, and nature's beauty",
                "cultural_significance": "Honors married women and celebrates monsoon season",
                "tips": [
                    "Plan a romantic nature outing or garden visit",
                    "Gift green bangles and traditional jewelry",
                    "Organize traditional sweets and monsoon treats",
                    "Book couples swing experience if available",
                    "Arrange rain dance or monsoon-themed date"
                ],
                "tasks": [
                    {"task": "Plan nature/garden date", "category": "experience", "points": 15},
                    {"task": "Buy green bangles and jewelry", "category": "shopping", "points": 10},
                    {"task": "Order traditional Teej sweets", "category": "food", "points": 10}
                ],
                "gift_suggestions": ["Green bangles", "Monsoon-themed jewelry", "Traditional sweets", "Nature experience"],
                "traditional_colors": ["Green", "Yellow", "Red"],
                "celebration_time": "full_day",
                "duration_days": 1
            },
            
            {
                "id": "diwali_2025",
                "name": "Diwali - Festival of Lights",
                "date": f"{self.current_year}-10-21",
                "category": "indian_festival", 
                "type": "religious",
                "importance": "high",
                "description": "Festival of lights celebrating victory of light over darkness",
                "cultural_significance": "New beginnings, prosperity, and family togetherness",
                "tips": [
                    "Shop for matching traditional outfits together",
                    "Plan home decoration with diyas and rangoli",
                    "Exchange meaningful gifts and sweets",
                    "Plan family gatherings and video calls",
                    "Book couples photoshoot in traditional attire"
                ],
                "tasks": [
                    {"task": "Shop for traditional outfits together", "category": "shopping", "points": 15},
                    {"task": "Create rangoli design together", "category": "creative", "points": 20},
                    {"task": "Plan Diwali home decoration", "category": "decorating", "points": 15},
                    {"task": "Arrange family video calls", "category": "family", "points": 10}
                ],
                "gift_suggestions": ["Gold jewelry", "Traditional clothes", "Decorative diyas", "Sweet hampers"],
                "traditional_colors": ["Gold", "Red", "Yellow", "Orange"],
                "celebration_time": "evening_to_night",
                "duration_days": 5
            },
            
            {
                "id": "navratri_2025", 
                "name": "Navratri",
                "date": f"{self.current_year}-10-03",
                "category": "indian_festival",
                "type": "religious",
                "importance": "high", 
                "description": "Nine nights celebrating divine feminine power and energy",
                "cultural_significance": "Worships goddess Durga and celebrates feminine strength",
                "tips": [
                    "Join garba and dandiya dance events together",
                    "Gift colorful chaniya choli or traditional wear",
                    "Plan temple visits for each of the nine days",
                    "Participate in community celebrations",
                    "Learn traditional dance steps together"
                ],
                "tasks": [
                    {"task": "Book garba/dandiya event tickets", "category": "entertainment", "points": 15},
                    {"task": "Shop for traditional chaniya choli", "category": "shopping", "points": 20},
                    {"task": "Plan temple visits schedule", "category": "spiritual", "points": 10},
                    {"task": "Learn garba dance steps together", "category": "learning", "points": 25}
                ],
                "gift_suggestions": ["Chaniya choli", "Traditional jewelry", "Garba accessories", "Religious items"],
                "traditional_colors": ["Red", "Yellow", "Green", "Blue", "Pink", "Orange", "Purple", "Gray", "Peacock"],
                "celebration_time": "evening_to_night",
                "duration_days": 9
            },
            
            {
                "id": "raksha_bandhan_2025",
                "name": "Raksha Bandhan", 
                "date": f"{self.current_year}-08-09",
                "category": "indian_festival",
                "type": "family",
                "importance": "medium",
                "description": "Celebrating sacred bond between siblings",
                "cultural_significance": "Brother-sister love and protection promises", 
                "tips": [
                    "Help her shop for gifts for her brothers",
                    "Plan family gatherings and celebrations",
                    "Arrange video calls with distant family members",
                    "Support her in rakhi preparations",
                    "Join family traditions respectfully"
                ],
                "tasks": [
                    {"task": "Help shop for brother's gifts", "category": "family", "points": 15},
                    {"task": "Arrange family video call setup", "category": "technology", "points": 10},
                    {"task": "Plan family gathering logistics", "category": "planning", "points": 10}
                ],
                "gift_suggestions": ["Rakhi sets", "Sweets and dry fruits", "Brother's gifts", "Family photo frames"],
                "traditional_colors": ["Red", "Gold", "Yellow"],
                "celebration_time": "morning_to_afternoon", 
                "duration_days": 1
            },
            
            {
                "id": "holi_2025",
                "name": "Holi - Festival of Colors", 
                "date": f"{self.current_year}-03-14",
                "category": "indian_festival",
                "type": "seasonal",
                "importance": "high",
                "description": "Joyous festival celebrating spring, colors, and love",
                "cultural_significance": "Triumph of good over evil, welcoming spring",
                "tips": [
                    "Play colors together in safe environment",
                    "Plan Holi party with friends and family", 
                    "Share traditional gujiya and thandai",
                    "Wear white clothes for better color effect",
                    "Use natural, skin-safe colors only"
                ],
                "tasks": [
                    {"task": "Buy natural, safe Holi colors", "category": "shopping", "points": 10},
                    {"task": "Plan Holi celebration with friends", "category": "social", "points": 15},
                    {"task": "Prepare traditional Holi treats", "category": "cooking", "points": 20},
                    {"task": "Arrange post-Holi cleanup supplies", "category": "practical", "points": 10}
                ],
                "gift_suggestions": ["Natural color packets", "Traditional sweets", "Water guns", "White celebration clothes"],
                "traditional_colors": ["All colors - Rainbow celebration"],
                "celebration_time": "morning_to_afternoon",
                "duration_days": 1
            }
        ]
    
    def _get_international_holidays(self) -> List[Dict[str, Any]]:
        """International holidays with relationship relevance"""
        return [
            {
                "id": "new_year_2025",
                "name": "New Year's Day",
                "date": f"{self.current_year}-01-01", 
                "category": "international_holiday",
                "type": "celebration",
                "importance": "high",
                "description": "Fresh start and new beginnings for the year",
                "tips": [
                    "Plan romantic midnight celebration together",
                    "Set relationship goals for the new year",
                    "Exchange meaningful new year gifts",
                    "Plan first date of the year"
                ],
                "tasks": [
                    {"task": "Plan midnight celebration", "category": "romantic", "points": 20},
                    {"task": "Set couple goals for new year", "category": "planning", "points": 15},
                    {"task": "Plan first romantic date of year", "category": "experience", "points": 15}
                ],
                "gift_suggestions": ["New year calendar", "Goal-setting journal", "Champagne", "Experience vouchers"],
                "celebration_time": "midnight_to_next_day",
                "duration_days": 1
            },
            
            {
                "id": "national_womens_day_india_2025",
                "name": "National Women's Day (India)",
                "date": f"{self.current_year}-02-13",
                "category": "international_holiday",
                "type": "appreciation",
                "importance": "high",
                "description": "Commemorates birth anniversary of Sarojini Naidu, celebrating Indian women's contributions",
                "tips": [
                    "Celebrate her Indian heritage and culture",
                    "Learn about inspiring Indian women together",
                    "Plan activities that honor her roots",
                    "Cook traditional Indian dishes she loves",
                    "Gift her something that connects to Indian culture"
                ],
                "tasks": [
                    {"task": "Research inspiring Indian women stories", "category": "learning", "points": 15},
                    {"task": "Cook her favorite Indian dish together", "category": "cooking", "points": 20},
                    {"task": "Plan cultural activity or museum visit", "category": "experience", "points": 15},
                    {"task": "Write appreciation note about her strength", "category": "romantic", "points": 20}
                ],
                "gift_suggestions": ["Indian classical music", "Traditional jewelry", "Books by Indian women authors", "Indian art or crafts"],
                "celebration_time": "full_day",
                "duration_days": 1,
                "cultural_significance": "Honors Sarojini Naidu and celebrates Indian women's achievements and contributions to society"
            },
            
            {
                "id": "womens_day_2025",
                "name": "International Women's Day",
                "date": f"{self.current_year}-03-08",
                "category": "international_holiday", 
                "type": "appreciation",
                "importance": "high",
                "description": "Global observance of women's rights and achievements",
                "tips": [
                    "Appreciate her achievements and strengths",
                    "Plan her favorite activities for the day",
                    "Give her a completely relaxing day",
                    "Support women-owned businesses in gifts",
                    "Write heartfelt letter about her impact"
                ],
                "tasks": [
                    {"task": "Write appreciation letter for her", "category": "romantic", "points": 20},
                    {"task": "Plan her favorite relaxing activities", "category": "experience", "points": 15},
                    {"task": "Shop from women-owned businesses", "category": "shopping", "points": 10},
                    {"task": "Book spa or wellness session", "category": "wellness", "points": 15}
                ],
                "gift_suggestions": ["Spa vouchers", "Books by women authors", "Personalized gifts", "Experience gifts"],
                "celebration_time": "full_day",
                "duration_days": 1
            },
            
            {
                "id": "mothers_day_2025",
                "name": "Mother's Day", 
                "date": f"{self.current_year}-05-11",
                "category": "international_holiday",
                "type": "family",
                "importance": "medium",
                "description": "Honoring mothers and mother figures in our lives",
                "tips": [
                    "Help her connect with her mother",
                    "Plan family time and gatherings",
                    "Appreciate her nurturing qualities",
                    "Support her in gifts for her mother",
                    "Arrange family photo session"
                ],
                "tasks": [
                    {"task": "Help plan gifts for her mother", "category": "family", "points": 15},
                    {"task": "Arrange family video call or visit", "category": "family", "points": 10},
                    {"task": "Plan family photo session", "category": "photography", "points": 20}
                ],
                "gift_suggestions": ["Flowers for mothers", "Family photo session", "Traditional sweets", "Spa day for moms"],
                "celebration_time": "full_day", 
                "duration_days": 1
            },
            
            {
                "id": "girlfriends_day_2025",
                "name": "Girlfriend's Day / National Girlfriend Day",
                "date": f"{self.current_year}-08-01",
                "category": "international_holiday",
                "type": "appreciation",
                "importance": "high",
                "description": "Commonly observed as a day to appreciate your girlfriend",
                "tips": [
                    "Plan a special surprise just for her",
                    "Write a heartfelt love letter expressing your feelings",
                    "Recreate your first date or a memorable moment",
                    "Give her your complete attention throughout the day",
                    "Plan activities she's been wanting to do"
                ],
                "tasks": [
                    {"task": "Plan surprise activity she loves", "category": "romantic", "points": 25},
                    {"task": "Write heartfelt appreciation letter", "category": "romantic", "points": 20},
                    {"task": "Recreate a special memory together", "category": "experience", "points": 20},
                    {"task": "Plan her favorite meal or restaurant", "category": "dining", "points": 15}
                ],
                "gift_suggestions": ["Personalized photo album", "Her favorite flowers", "Handwritten love letters", "Experience she's mentioned wanting"],
                "celebration_time": "full_day",
                "duration_days": 1,
                "cultural_significance": "A day dedicated to celebrating and appreciating girlfriends in relationships"
            },
            
            {
                "id": "christmas_2025",
                "name": "Christmas Day",
                "date": f"{self.current_year}-12-25",
                "category": "international_holiday",
                "type": "religious",
                "importance": "medium", 
                "description": "Christian celebration of love, giving, and togetherness",
                "tips": [
                    "Exchange thoughtful Christmas gifts",
                    "Plan cozy indoor celebration",
                    "Cook special meal together",
                    "Enjoy Christmas movies and music"
                ],
                "tasks": [
                    {"task": "Plan Christmas gift exchange", "category": "gifts", "points": 15},
                    {"task": "Decorate space with Christmas theme", "category": "decorating", "points": 10},
                    {"task": "Plan special Christmas dinner", "category": "cooking", "points": 20}
                ],
                "gift_suggestions": ["Thoughtful personal gifts", "Christmas decoration items", "Special dinner ingredients"],
                "celebration_time": "full_day",
                "duration_days": 1
            },
            
            # Next year events for continuity
            {
                "id": "national_womens_day_india_2026",
                "name": "National Women's Day (India)",
                "date": f"{self.next_year}-02-13",
                "category": "international_holiday",
                "type": "appreciation",
                "importance": "high",
                "description": "Commemorates birth anniversary of Sarojini Naidu, celebrating Indian women's contributions",
                "tips": [
                    "Celebrate her Indian heritage and culture",
                    "Learn about inspiring Indian women together",
                    "Plan activities that honor her roots",
                    "Cook traditional Indian dishes she loves",
                    "Gift her something that connects to Indian culture"
                ],
                "tasks": [
                    {"task": "Research inspiring Indian women stories", "category": "learning", "points": 15},
                    {"task": "Cook her favorite Indian dish together", "category": "cooking", "points": 20},
                    {"task": "Plan cultural activity or museum visit", "category": "experience", "points": 15},
                    {"task": "Write appreciation note about her strength", "category": "romantic", "points": 20}
                ],
                "gift_suggestions": ["Indian classical music", "Traditional jewelry", "Books by Indian women authors", "Indian art or crafts"],
                "celebration_time": "full_day",
                "duration_days": 1,
                "cultural_significance": "Honors Sarojini Naidu and celebrates Indian women's achievements and contributions to society"
            },
            
            {
                "id": "womens_day_2026",
                "name": "International Women's Day",
                "date": f"{self.next_year}-03-08",
                "category": "international_holiday", 
                "type": "appreciation",
                "importance": "high",
                "description": "Global observance of women's rights and achievements",
                "tips": [
                    "Appreciate her achievements and strengths",
                    "Plan her favorite activities for the day",
                    "Give her a completely relaxing day",
                    "Support women-owned businesses in gifts",
                    "Write heartfelt letter about her impact"
                ],
                "tasks": [
                    {"task": "Write appreciation letter for her", "category": "romantic", "points": 20},
                    {"task": "Plan her favorite relaxing activities", "category": "experience", "points": 15},
                    {"task": "Shop from women-owned businesses", "category": "shopping", "points": 10},
                    {"task": "Book spa or wellness session", "category": "wellness", "points": 15}
                ],
                "gift_suggestions": ["Spa vouchers", "Books by women authors", "Personalized gifts", "Experience gifts"],
                "celebration_time": "full_day",
                "duration_days": 1
            },
            
            {
                "id": "girlfriends_day_2026",
                "name": "Girlfriend's Day / National Girlfriend Day",
                "date": f"{self.next_year}-08-01",
                "category": "international_holiday",
                "type": "appreciation",
                "importance": "high",
                "description": "Commonly observed as a day to appreciate your girlfriend",
                "tips": [
                    "Plan a special surprise just for her",
                    "Write a heartfelt love letter expressing your feelings",
                    "Recreate your first date or a memorable moment",
                    "Give her your complete attention throughout the day",
                    "Plan activities she's been wanting to do"
                ],
                "tasks": [
                    {"task": "Plan surprise activity she loves", "category": "romantic", "points": 25},
                    {"task": "Write heartfelt appreciation letter", "category": "romantic", "points": 20},
                    {"task": "Recreate a special memory together", "category": "experience", "points": 20},
                    {"task": "Plan her favorite meal or restaurant", "category": "dining", "points": 15}
                ],
                "gift_suggestions": ["Personalized photo album", "Her favorite flowers", "Handwritten love letters", "Experience she's mentioned wanting"],
                "celebration_time": "full_day",
                "duration_days": 1,
                "cultural_significance": "A day dedicated to celebrating and appreciating girlfriends in relationships"
            }
        ]
    
    def _get_romantic_calendar(self) -> List[Dict[str, Any]]:
        """Valentine's week and other romantic celebrations"""
        return [
            # Valentine's Week - Complete 7-day celebration
            {
                "id": "rose_day_2025",
                "name": "Rose Day",
                "date": f"{self.current_year}-02-07",
                "category": "romantic_week",
                "type": "romantic",
                "importance": "medium",
                "description": "Start of Valentine's week with beautiful roses",
                "tips": [
                    "Surprise her with different colored roses",
                    "Each color has meaning - research and choose thoughtfully",
                    "Plan a garden visit or rose farm trip",
                    "Write sweet notes to accompany roses"
                ],
                "tasks": [
                    {"task": "Research rose color meanings", "category": "learning", "points": 5},
                    {"task": "Buy meaningful colored roses", "category": "shopping", "points": 10},
                    {"task": "Plan garden or rose farm visit", "category": "experience", "points": 15}
                ],
                "gift_suggestions": ["Fresh roses", "Rose-themed gifts", "Garden date plan", "Rose perfume"],
                "celebration_time": "full_day",
                "duration_days": 1
            },
            
            {
                "id": "propose_day_2025", 
                "name": "Propose Day",
                "date": f"{self.current_year}-02-08",
                "category": "romantic_week",
                "type": "romantic", 
                "importance": "high",
                "description": "Perfect day for proposals and relationship commitments",
                "tips": [
                    "Express deeper feelings and commitment",
                    "Propose next steps in relationship",
                    "Plan intimate and meaningful gesture",
                    "Choose perfect romantic location"
                ],
                "tasks": [
                    {"task": "Plan meaningful proposal gesture", "category": "romantic", "points": 25},
                    {"task": "Choose perfect romantic location", "category": "planning", "points": 15},
                    {"task": "Prepare heartfelt speech", "category": "communication", "points": 20}
                ],
                "gift_suggestions": ["Promise ring", "Handwritten letter", "Romantic location booking", "Memory book"],
                "celebration_time": "evening",
                "duration_days": 1
            },
            
            {
                "id": "chocolate_day_2025",
                "name": "Chocolate Day", 
                "date": f"{self.current_year}-02-09",
                "category": "romantic_week",
                "type": "romantic",
                "importance": "medium",
                "description": "Sweet day celebrating love with chocolates",
                "tips": [
                    "Gift her favorite premium chocolates",
                    "Plan chocolate-making date activity",
                    "Visit chocolate cafe or factory",
                    "Create custom chocolate messages"
                ],
                "tasks": [
                    {"task": "Buy premium chocolate collection", "category": "shopping", "points": 10},
                    {"task": "Plan chocolate making activity", "category": "experience", "points": 20},
                    {"task": "Visit chocolate cafe together", "category": "food", "points": 15}
                ],
                "gift_suggestions": ["Premium chocolates", "Chocolate hamper", "DIY chocolate kit", "Chocolate spa"],
                "celebration_time": "full_day",
                "duration_days": 1
            },
            
            {
                "id": "teddy_day_2025",
                "name": "Teddy Day",
                "date": f"{self.current_year}-02-10", 
                "category": "romantic_week",
                "type": "romantic",
                "importance": "low",
                "description": "Cute day for gifting teddy bears and soft toys",
                "tips": [
                    "Gift a cuddly teddy bear she'll love",
                    "Choose one that matches her personality",
                    "Add personalized message or clothing",
                    "Plan cozy cuddling time"
                ],
                "tasks": [
                    {"task": "Shop for perfect teddy bear", "category": "shopping", "points": 10},
                    {"task": "Personalize teddy with message", "category": "creative", "points": 10},
                    {"task": "Plan cozy movie night", "category": "experience", "points": 15}
                ],
                "gift_suggestions": ["Personalized teddy bear", "Cute soft toys", "Cozy blankets", "Matching pillows"],
                "celebration_time": "evening",
                "duration_days": 1
            },
            
            {
                "id": "promise_day_valentine_2025",
                "name": "Promise Day",
                "date": f"{self.current_year}-02-11",
                "category": "romantic_week", 
                "type": "romantic",
                "importance": "high",
                "description": "Day to make heartfelt promises and commitments",
                "tips": [
                    "Make meaningful and achievable promises",
                    "Promise about future goals together", 
                    "Write down promises for accountability",
                    "Plan how to fulfill each promise"
                ],
                "tasks": [
                    {"task": "Write down meaningful promises", "category": "communication", "points": 20},
                    {"task": "Plan promise fulfillment timeline", "category": "planning", "points": 15},
                    {"task": "Create promise ceremony", "category": "romantic", "points": 15}
                ],
                "gift_suggestions": ["Promise ring", "Handwritten promise book", "Future experience bookings", "Commitment jewelry"],
                "celebration_time": "evening",
                "duration_days": 1
            },
            
            {
                "id": "hug_day_2025",
                "name": "Hug Day",
                "date": f"{self.current_year}-02-12",
                "category": "romantic_week",
                "type": "romantic", 
                "importance": "medium",
                "description": "Day to express love through warm, meaningful hugs",
                "tips": [
                    "Give her multiple long, warm hugs",
                    "Plan dedicated cuddling time",
                    "Create cozy atmosphere at home",
                    "Focus on physical affection and closeness"
                ],
                "tasks": [
                    {"task": "Plan cozy cuddling session", "category": "romantic", "points": 15},
                    {"task": "Create comfortable hugging space", "category": "setup", "points": 10},
                    {"task": "Give surprise hugs throughout day", "category": "affection", "points": 20}
                ],
                "gift_suggestions": ["Soft teddy bear", "Cozy blankets", "Couple pillows", "Comfortable loungewear"],
                "celebration_time": "full_day",
                "duration_days": 1
            },
            
            {
                "id": "kiss_day_2025",
                "name": "Kiss Day", 
                "date": f"{self.current_year}-02-13",
                "category": "romantic_week",
                "type": "romantic",
                "importance": "high",
                "description": "Day of romantic kisses and intimate affection",
                "tips": [
                    "Plan romantic and intimate moments",
                    "Create perfect atmosphere with candles",
                    "Focus on emotional and physical closeness",
                    "Respect boundaries while being affectionate"
                ],
                "tasks": [
                    {"task": "Plan romantic dinner setup", "category": "romantic", "points": 20},
                    {"task": "Create intimate atmosphere", "category": "ambiance", "points": 15},
                    {"task": "Write romantic love notes", "category": "communication", "points": 10}
                ],
                "gift_suggestions": ["Romantic dinner", "Scented candles", "Love notes", "Intimate setting"],
                "celebration_time": "evening_to_night",
                "duration_days": 1
            },
            
            {
                "id": "valentine_day_2025",
                "name": "Valentine's Day",
                "date": f"{self.current_year}-02-14", 
                "category": "romantic_week",
                "type": "romantic",
                "importance": "high",
                "description": "Ultimate day of love, romance, and celebration",
                "tips": [
                    "Plan the perfect romantic date",
                    "Write heartfelt love letter",
                    "Book her favorite restaurant",
                    "Give meaningful, thoughtful gifts",
                    "Create lasting romantic memories"
                ],
                "tasks": [
                    {"task": "Plan perfect Valentine's date", "category": "romantic", "points": 30},
                    {"task": "Write heartfelt love letter", "category": "communication", "points": 25},
                    {"task": "Book special restaurant", "category": "planning", "points": 20},
                    {"task": "Prepare meaningful gifts", "category": "gifts", "points": 20}
                ],
                "gift_suggestions": ["Roses and chocolates", "Jewelry", "Romantic dinner", "Couple spa", "Love letters"],
                "celebration_time": "full_day_to_night",
                "duration_days": 1
            }
        ]
    
    def _get_seasonal_events(self) -> List[Dict[str, Any]]:
        """Seasonal celebrations and monthly themes"""
        return [
            {
                "id": "spring_equinox_2025",
                "name": "Spring Equinox",
                "date": f"{self.current_year}-03-20",
                "category": "seasonal",
                "type": "nature",
                "importance": "low", 
                "description": "Celebrating new beginnings and spring season",
                "tips": [
                    "Plan outdoor activities and nature walks",
                    "Start gardening project together",
                    "Plan spring cleaning as a couple activity",
                    "Enjoy fresh flowers and blooming nature"
                ],
                "tasks": [
                    {"task": "Plan nature walk or hike", "category": "outdoor", "points": 15},
                    {"task": "Start couples gardening project", "category": "hobby", "points": 20},
                    {"task": "Plan spring cleaning together", "category": "home", "points": 10}
                ],
                "gift_suggestions": ["Plant seeds", "Gardening tools", "Outdoor activity gear", "Nature books"],
                "celebration_time": "full_day",
                "duration_days": 1
            },
            
            {
                "id": "summer_solstice_2025",
                "name": "Summer Solstice",
                "date": f"{self.current_year}-06-21",
                "category": "seasonal", 
                "type": "nature",
                "importance": "low",
                "description": "Longest day of the year - celebrate light and warmth",
                "tips": [
                    "Plan sunrise or sunset watching",
                    "Organize beach or water activities",
                    "Have outdoor picnic or barbecue",
                    "Enjoy summer fruits and refreshments"
                ],
                "tasks": [
                    {"task": "Plan sunrise/sunset watching", "category": "romantic", "points": 15},
                    {"task": "Organize beach or water date", "category": "outdoor", "points": 20},
                    {"task": "Plan outdoor picnic", "category": "food", "points": 15}
                ],
                "gift_suggestions": ["Beach accessories", "Picnic supplies", "Summer drinks", "Outdoor games"],
                "celebration_time": "full_day",
                "duration_days": 1
            }
        ]
    
    def _generate_personal_events(self, user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Auto-generate personal events from user profile data"""
        personal_events = []
        
        # Get partner profile
        partner = user_profile.get("partner_profile", {})
        
        # Generate partner's birthday event
        if partner.get("birthday"):
            try:
                birthday_str = partner["birthday"]
                if isinstance(birthday_str, str):
                    # Try different date formats
                    try:
                        birthday_date = datetime.strptime(birthday_str, "%d/%m/%Y")
                    except ValueError:
                        try:
                            birthday_date = datetime.strptime(birthday_str, "%Y-%m-%d")
                        except ValueError:
                            birthday_date = parser.parse(birthday_str)
                else:
                    birthday_date = birthday_str
                
                # Create for current and next year
                for year in [self.current_year, self.next_year]:
                    birthday_event = {
                        "id": f"partner_birthday_{year}",
                        "name": f"{partner.get('name', 'Partner')}'s Birthday",
                        "date": birthday_date.replace(year=year).strftime("%Y-%m-%d"),
                        "category": "personal_birthday", 
                        "type": "celebration",
                        "importance": "high",
                        "description": f"Your beloved {partner.get('name', 'partner')}'s special day",
                        "auto_generated": True,
                        "tips": [
                            "Plan surprise birthday celebration",
                            "Book her favorite restaurant", 
                            "Organize cake and decorations",
                            "Invite her close friends and family",
                            "Prepare thoughtful birthday gift",
                            "Create birthday photo/video montage"
                        ],
                        "tasks": [
                            {"task": "Plan surprise birthday party", "category": "planning", "points": 30},
                            {"task": "Book birthday dinner reservation", "category": "booking", "points": 15},
                            {"task": "Order custom birthday cake", "category": "food", "points": 15},
                            {"task": "Prepare birthday gift", "category": "gifts", "points": 20},
                            {"task": "Organize birthday decorations", "category": "decorating", "points": 10}
                        ],
                        "gift_suggestions": [
                            "Personalized jewelry", 
                            "Experience vouchers", 
                            "Custom photo album", 
                            "Her favorite perfume",
                            "Surprise weekend getaway"
                        ],
                        "celebration_time": "full_day",
                        "duration_days": 1,
                        "reminder_days": 14  # Extra reminder for important personal events
                    }
                    personal_events.append(birthday_event)
                    
            except (ValueError, KeyError) as e:
                print(f"Error parsing partner birthday: {e}")
        
        # Generate anniversary event  
        if partner.get("anniversary"):
            try:
                anniversary_str = partner["anniversary"]
                if isinstance(anniversary_str, str):
                    # Try different date formats
                    try:
                        anniversary_date = datetime.strptime(anniversary_str, "%d/%m/%Y")
                    except ValueError:
                        try:
                            anniversary_date = datetime.strptime(anniversary_str, "%Y-%m-%d")
                        except ValueError:
                            anniversary_date = parser.parse(anniversary_str)
                else:
                    anniversary_date = anniversary_str
                
                # Create for current and next year
                for year in [self.current_year, self.next_year]:
                    anniversary_event = {
                        "id": f"anniversary_{year}",
                        "name": "Our Anniversary",
                        "date": anniversary_date.replace(year=year).strftime("%Y-%m-%d"),
                        "category": "personal_anniversary",
                        "type": "celebration", 
                        "importance": "high",
                        "description": "Celebrating your beautiful love story and journey together",
                        "auto_generated": True,
                        "tips": [
                            "Plan romantic anniversary getaway",
                            "Recreate your first date", 
                            "Exchange anniversary gifts",
                            "Write love letters to each other",
                            "Create memory book or photo album",
                            "Plan intimate candlelight dinner"
                        ],
                        "tasks": [
                            {"task": "Plan romantic anniversary celebration", "category": "romantic", "points": 35},
                            {"task": "Recreate first date experience", "category": "nostalgia", "points": 25},
                            {"task": "Prepare anniversary gifts", "category": "gifts", "points": 20},
                            {"task": "Write anniversary love letter", "category": "communication", "points": 15},
                            {"task": "Create anniversary memory book", "category": "creative", "points": 20}
                        ],
                        "gift_suggestions": [
                            "Anniversary jewelry",
                            "Romantic getaway booking", 
                            "Custom photo album",
                            "Couples spa package",
                            "Personalized star map"
                        ],
                        "celebration_time": "full_day_to_night",
                        "duration_days": 1,
                        "reminder_days": 21  # Even more advance notice for anniversary
                    }
                    personal_events.append(anniversary_event)
                    
            except (ValueError, KeyError) as e:
                print(f"Error parsing anniversary date: {e}")
        
        # Generate monthly relationship check-in events
        for month in range(1, 13):
            monthly_checkin = {
                "id": f"monthly_checkin_{self.current_year}_{month}",
                "name": f"Monthly Love Check-in - {calendar.month_name[month]}",
                "date": f"{self.current_year}-{month:02d}-15",  # 15th of each month
                "category": "relationship_maintenance",
                "type": "communication",
                "importance": "medium",
                "description": "Regular relationship health check and quality time",
                "auto_generated": True,
                "prefilled": True,
                "tips": [
                    "Have deep conversation about relationship",
                    "Share appreciation and gratitude",
                    "Discuss goals for upcoming month",
                    "Plan special activities together",
                    "Address any concerns lovingly"
                ],
                "tasks": [
                    {"task": "Schedule quality conversation time", "category": "communication", "points": 15},
                    {"task": "Share monthly appreciations", "category": "gratitude", "points": 10},
                    {"task": "Plan next month activities", "category": "planning", "points": 10}
                ],
                "gift_suggestions": ["Quality time", "Thoughtful conversation", "Planning activities"],
                "celebration_time": "evening", 
                "duration_days": 1,
                "reminder_days": 3
            }
            personal_events.append(monthly_checkin)
        
        return personal_events
    
    def _sort_events_upcoming_first(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort events with upcoming dates first, then chronologically"""
        today = datetime.now().date()
        
        def event_sort_key(event):
            event_date = datetime.strptime(event["date"], "%Y-%m-%d").date()
            
            # If event is today or in future, sort by date ascending
            if event_date >= today:
                return (0, event_date)
            # If event is in past, sort by date descending (most recent first)
            else:
                return (1, -event_date.toordinal())
        
        return sorted(events, key=event_sort_key)
    
    def _add_default_reminders(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add 10-day default reminders to all events"""
        for event in events:
            if "reminder_days" not in event:
                event["reminder_days"] = 10
            
            # Calculate reminder date
            event_date = datetime.strptime(event["date"], "%Y-%m-%d")
            reminder_date = event_date - timedelta(days=event["reminder_days"])
            event["reminder_date"] = reminder_date.strftime("%Y-%m-%d")
            
            # Add reminder status
            today = datetime.now().date()
            reminder_date_obj = reminder_date.date()
            event_date_obj = event_date.date()
            
            if today == reminder_date_obj:
                event["reminder_status"] = "due_today"
            elif today > reminder_date_obj and today < event_date_obj:
                event["reminder_status"] = "in_reminder_period"
            elif today >= event_date_obj:
                event["reminder_status"] = "past_event"
            else:
                event["reminder_status"] = "future_reminder"
        
        return events
    
    def _is_upcoming(self, date_str: str) -> bool:
        """Check if event is upcoming (today or future)"""
        event_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        return event_date >= datetime.now().date()
    
    def _is_this_month(self, date_str: str) -> bool:
        """Check if event is in current month"""
        event_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        today = datetime.now().date()
        return event_date.month == today.month and event_date.year == today.year
    
    def _get_event_categories(self) -> List[Dict[str, str]]:
        """Get all available event categories"""
        return [
            {"id": "indian_festival", "name": "Indian Festivals", "color": "#FF6B35"},
            {"id": "international_holiday", "name": "International Holidays", "color": "#4ECDC4"},
            {"id": "romantic_week", "name": "Valentine's Week", "color": "#FF1744"},
            {"id": "seasonal", "name": "Seasonal Celebrations", "color": "#8BC34A"},
            {"id": "personal_birthday", "name": "Birthdays", "color": "#9C27B0"},
            {"id": "personal_anniversary", "name": "Anniversaries", "color": "#E91E63"},
            {"id": "relationship_maintenance", "name": "Relationship Check-ins", "color": "#607D8B"},
            {"id": "custom", "name": "Custom Events", "color": "#795548"}
        ]

    def get_event_details(self, event_id: str, events_list: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific event"""
        for event in events_list:
            if event["id"] == event_id:
                # Add additional computed details
                event_date = datetime.strptime(event["date"], "%Y-%m-%d")
                today = datetime.now()
                
                days_until = (event_date.date() - today.date()).days
                
                enhanced_event = {
                    **event,
                    "days_until": days_until,
                    "is_upcoming": days_until >= 0,
                    "is_today": days_until == 0,
                    "is_this_week": 0 <= days_until <= 7,
                    "is_this_month": event_date.month == today.month and event_date.year == today.year,
                    "formatted_date": event_date.strftime("%A, %B %d, %Y"),
                    "day_of_week": event_date.strftime("%A"),
                    "month_name": event_date.strftime("%B")
                }
                
                return enhanced_event
        
        return None

# Global instance
enhanced_calendar_service = EnhancedCalendarService()