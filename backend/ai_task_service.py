"""
AI Task Generation Service for Pookie4u
Generates personalized relationship tasks using OpenAI GPT-4
"""

import os
import json
import asyncio
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dotenv import load_dotenv

from emergentintegrations.llm.chat import LlmChat, UserMessage

# Load environment variables
load_dotenv()

# Task categories as per requirements
DAILY_TASK_CATEGORIES = [
    "Communication",
    "ThoughtfulGesture", 
    "MicroActivity"
]

WEEKLY_TASK_CATEGORIES = [
    "PhysicalActivity"
]

# Difficulty levels
DAILY_DIFFICULTY = "very_easy"  # 2-5 minute actions
WEEKLY_DIFFICULTY = "easy"  # Physical actions, safe to execute

# Relationship modes
RELATIONSHIP_MODES = {
    "SAME_HOME": "Living together in the same home",
    "DAILY_IRL": "Meeting daily in real life but not living together", 
    "LONG_DISTANCE": "In a long-distance relationship"
}

# Daily Meetup Mode - 90 pre-written tasks that rotate monthly
DAILY_MEETUP_TASKS = [
    "Send her a good morning text first",
    "Compliment her photo or outfit today", 
    "Bring her a small snack when you meet",
    "Hold her hand while walking",
    "Say 'you look amazing today'",
    "Take a short walk together",
    "Send a funny meme during the day",
    "Tell her one reason you missed her",
    "Make her laugh once",
    "Offer to carry her bag",
    "Say 'I'm happy to see you'",
    "Take one selfie together",
    "Ask about her day with full attention",
    "Play her favorite song in your car or phone",
    "Offer her water or juice",
    "Give her a soft hug before leaving",
    "Compliment her eyes",
    "Text her 'reached home safe?'",
    "Ask if she's eaten properly",
    "Write her name creatively somewhere",
    "Praise her publicly",
    "Call her 'my girl' affectionately",
    "Bring her favorite chocolate",
    "Let her pick the meeting spot",
    "Share your earphones for a song",
    "Take a short video memory",
    "Say something romantic before goodbye",
    "Plan tomorrow's meet",
    "Tell her 'today felt better because of you'",
    "Smile the moment you see her",
    "Ask if she's tired and offer rest",
    "Send her voice note saying 'I love you'",
    "Ask what she wants to do this week",
    "Remember her small preferences",
    "Text 'thinking of you' midday",
    "Send a random compliment",
    "Share a throwback photo of you two",
    "Hold her hand tightly for few seconds",
    "Tell her one thing you adore about her personality",
    "Take her picture with her permission",
    "Send a romantic GIF",
    "Ask if she wants something from your route",
    "Share a food bite",
    "Appreciate her hairstyle",
    "Let her talk freely without interrupting",
    "Make a short plan for weekend",
    "Say 'you smell nice' genuinely",
    "Do a fun handshake or gesture",
    "Ask how she feels today emotionally",
    "Write her name in your notes app",
    "Look into her eyes and smile",
    "Compliment her nails",
    "Offer her jacket if it's cold",
    "Wish her good night sweetly",
    "Send a quick 'I miss you already' text",
    "Ask if she wants to call later",
    "Record a small message saying 'you matter'",
    "Surprise her with her favorite drink",
    "Walk her to her vehicle or stop",
    "Thank her for today's time",
    "Share a short reel together",
    "Give her a gentle forehead kiss",
    "Text her about a funny moment from today",
    "Write her initials on your wrist (pen)",
    "Ask her one personal dream",
    "Tell her she makes your day calmer",
    "Compliment her earrings or accessories",
    "Send her a heart emoji at random time",
    "Hold her face and say 'you're my peace'",
    "Make a silly face until she laughs",
    "Ask what made her smile today",
    "Offer to walk her home or till the gate",
    "Text 'thinking about your smile'",
    "Praise her for something small she did",
    "Say 'I'm proud of you'",
    "Give her a small flower",
    "Take one candid photo of her",
    "Call her nickname softly",
    "Whisper something sweet when close",
    "Compliment how she smells",
    "Say 'you make my day better'",
    "Remind her to drink water",
    "Text 'I love you' with a heart",
    "Wave happily when she leaves",
    "Ask if she needs help with anything",
    "Play a quick 5-minute game together",
    "Say 'I can't stop thinking of you'",
    "Offer to drop her if possible",
    "Smile and say 'today was perfect'",
    "Send her one cute emoji before sleeping"
]

# Long Distance Mode - 90 pre-written tasks that rotate monthly
LONG_DISTANCE_TASKS = [
    "Send her a good morning text first",
    "Send one selfie with your smile",
    "Compliment her latest photo",
    "Send a voice note saying 'I love you'",
    "Text her 'I miss you' once today",
    "Ask how she's feeling emotionally",
    "Call her before sleeping",
    "Share a photo of your day",
    "Tell her one reason you love her",
    "Send her a virtual hug emoji",
    "Watch the same movie and discuss it",
    "Say goodnight with her nickname",
    "Ask if she ate properly",
    "Share a memory photo of you both",
    "Send her a morning quote",
    "Text her one compliment",
    "Tell her 'you're my calm'",
    "Ask her about her schedule today",
    "Share your song of the day",
    "Send a voice message saying 'I miss your face'",
    "Ask her about her dream last night",
    "Send her a cute meme",
    "Plan your next visit virtually",
    "Compliment her voice on call",
    "Text 'you're my favorite person'",
    "Send her a random heart emoji",
    "Record a 10-second video message",
    "Ask her what made her smile today",
    "Remind her you're proud of her",
    "Share a screenshot of something funny",
    "Tell her one thing you're grateful for in her",
    "Schedule a short video call",
    "Say 'I wish you were here right now'",
    "Ask her what she's wearing today",
    "Send her your current view photo",
    "Remind her to drink water",
    "Say 'countdown to see you again'",
    "Compliment her hairstyle in photo",
    "Send her a virtual good morning kiss",
    "Ask about her favorite snack today",
    "Text 'you're my motivation'",
    "Plan a virtual dinner date",
    "Send her an old photo of you two",
    "Say 'you're still my home'",
    "Send her a heart sticker",
    "Share one small update from your day",
    "Ask how her work or study went",
    "Compliment her smile on call",
    "Send a romantic GIF",
    "Say 'I'm thinking of you right now'",
    "Ask what she's listening to",
    "Send a random 'I adore you' text",
    "Write her name on paper and send pic",
    "Tell her something you miss doing together",
    "Share a funny reel",
    "Call just to say hi briefly",
    "Say 'you make distance feel smaller'",
    "Send her your bedtime photo",
    "Compliment her eyes",
    "Text 'you mean everything to me'",
    "Ask about her mood",
    "Tell her you believe in her",
    "Share a quote about love",
    "Send her a screenshot of your playlist",
    "Plan a dream trip together",
    "Text 'thinking of your hug'",
    "Record yourself saying her nickname",
    "Share your lunch photo",
    "Tell her you miss her laugh",
    "Ask her favorite color today",
    "Send her a random 'love you more'",
    "Say 'you're my reason to smile'",
    "Share something you learned today",
    "Send her a good night selfie",
    "Ask when you can video call again",
    "Say 'you're always on my mind'",
    "Share a morning greeting photo",
    "Compliment her intelligence",
    "Send a romantic emoji combination",
    "Ask what song reminds her of you",
    "Say 'our next meet will be perfect'",
    "Send her your handwriting photo",
    "Compliment her patience",
    "Send her your favorite love quote",
    "Say 'I'm lucky to have you'",
    "Share a picture of your sky and say 'same sky'",
    "Text 'counting days to see you'",
    "Ask how she's taking care of herself",
    "Send her one random emoji-only text",
    "End day with 'you're loved, always'"
]

# Same Home Mode - 90 pre-written tasks for couples living together
SAME_HOME_TASKS = [
    "Make her morning coffee",
    "Give her a forehead kiss",
    "Compliment her outfit",
    "Help her with chores",
    "Plan tonight's dinner together",
    "Leave a cute sticky note",
    "Hug her for 10 seconds",
    "Say 'I love you' first today",
    "Bring her water without asking",
    "Smile when she enters the room",
    "Ask how she slept",
    "Play her favorite song aloud",
    "Hold her hand randomly",
    "Watch her favorite show together",
    "Make her laugh intentionally",
    "Do one of her pending tasks",
    "Give her a shoulder massage",
    "Say thank you for something she did",
    "Help her organize her desk",
    "Sit beside her while she works",
    "Write 'I adore you' on a note",
    "Make her favorite snack",
    "Greet her warmly when she returns home",
    "Let her pick the movie",
    "Fold laundry together",
    "Clean something she dislikes cleaning",
    "Whisper something sweet",
    "Take a selfie together",
    "Dance with her for a minute",
    "Compliment her smile",
    "Check if she's okay emotionally",
    "Tell her one reason you love her",
    "Rest your head on her lap",
    "Let her nap peacefully",
    "Hide a small love note",
    "Sing softly near her",
    "Cook breakfast alone",
    "Walk together after dinner",
    "Listen fully when she talks",
    "Surprise her with a snack",
    "Tidy your shared space",
    "Let her choose the music",
    "Kiss her hand",
    "Offer to massage her feet",
    "Tell her she's beautiful",
    "Sit close in silence",
    "Let her vent freely",
    "Tell her you're lucky to have her",
    "Make her laugh during stress",
    "Share one happy memory",
    "Write her a one-line poem",
    "Bring her a blanket",
    "Wash the dishes",
    "Give her a morning hug first",
    "Compliment her hair",
    "Plan a small game or quiz",
    "Take a photo of her candidly",
    "Tell her a secret",
    "Rest together without phones",
    "Ask her opinion sincerely",
    "Draw a small heart on her hand",
    "Share your snack",
    "Set her wallpaper to her photo",
    "Say 'you're my peace'",
    "Bring her flowers from garden",
    "Help her dress zipper or clip",
    "Ask about her dreams last night",
    "Compliment her cooking",
    "Offer her your hoodie",
    "Play a board game",
    "Brush her hair if she lets you",
    "Sit quietly beside her",
    "Say 'I missed you' even if you didn't leave",
    "Take over one of her chores",
    "Prepare her towel before shower",
    "Bring her favorite drink",
    "Text her from another room playfully",
    "Do small household fix she mentioned",
    "Call her by a cute nickname",
    "Praise her in front of someone",
    "Make the bed nicely",
    "Say 'you make this home happy'",
    "Light a candle before dinner",
    "Tuck her hair behind her ear",
    "Give her a piggyback ride",
    "Share headphones and song",
    "Leave a 'you're loved' note on mirror",
    "Pick out her outfit suggestion",
    "Hug her without reason",
    "Tell her you choose her every day"
]

# Daily Meetup Mode - 50 pre-written weekly tasks that rotate yearly
DAILY_MEETUP_WEEKLY_TASKS = [
    "Plan a surprise lunch or coffee date",
    "Bring her a small bouquet midweek",
    "Write her a short handwritten letter",
    "Gift her something meaningful, not expensive",
    "Take her out for a long walk or drive",
    "Plan a mini weekend picnic",
    "Recreate your first meeting spot",
    "Capture and print a photo from this week",
    "Plan a casual dinner after work",
    "Leave a surprise note in her bag",
    "Gift her favorite snack basket",
    "Watch a movie together outside home",
    "Plan a short evening trip or park visit",
    "Write her name on a bracelet or card",
    "Take her to a new café",
    "Record a video message telling her 5 reasons you love her",
    "Buy her favorite drink unexpectedly",
    "Help her with a small personal task",
    "Plan a 'no phones' date",
    "Draw or doodle something for her",
    "Gift her something matching with yours",
    "Make a mini photo collage of your week",
    "Walk her home or drop her safely",
    "Take her to a local fair or event",
    "Prepare a surprise playlist",
    "Write her name on a balloon and gift it",
    "Plan a sunset date",
    "Make a funny or romantic reel together",
    "Give her a framed picture of both",
    "Compliment her in public",
    "Take her shopping for something small",
    "Make a 'memory note' card after each meet",
    "Create a weekly highlight message",
    "Help her finish an important errand",
    "Teach her something you're good at",
    "Plan a 'favourite food day'",
    "Surprise her with handwritten sticky notes",
    "Arrange a joint selfie photo book",
    "Take her on a long talk drive",
    "Write a short poem for her",
    "Organize a mini couple game night",
    "Bring her one item from her wishlist",
    "Gift her a handwritten voucher ('1 big hug,' '1 ice cream date')",
    "Capture her laughter candidly",
    "Try her favorite hobby together",
    "Plan a coordinated outfit day",
    "End week with 'Thank you for this week' text",
    "Make her a small DIY gift",
    "Plan a night walk with ice cream",
    "Dedicate a song to her publicly or privately"
]

# Long Distance Mode - 50 pre-written weekly tasks that rotate yearly
LONG_DISTANCE_WEEKLY_TASKS = [
    "Plan a long video call date night",
    "Send her a handwritten letter by post",
    "Order her favorite food delivery",
    "Make a photo collage of your memories",
    "Write a love paragraph and send it",
    "Record a video message saying what you miss most",
    "Watch a movie together online",
    "Send her a surprise small gift",
    "Plan your next visit together",
    "Create a shared playlist for the week",
    "Write her name on paper and send a photo",
    "Share a day-in-your-life video",
    "Record yourself saying 'I love you' ten times",
    "Send her your favorite memory of her in detail",
    "Send her something handmade or drawn",
    "Plan a future trip virtually",
    "Surprise her with an online flower delivery",
    "Create a private shared photo album",
    "Write her initials on something you use daily",
    "Make a short 'reasons I love you' video",
    "Send her a love quote every morning for a week",
    "Order a matching accessory for both",
    "Write her a digital letter",
    "Send her your voice before sleeping every night",
    "Create a calendar countdown to your next meet",
    "Share a surprise parcel with keepsakes",
    "Play an online game together",
    "Make her a playlist and explain each song",
    "Send her a goodnight selfie every day for a week",
    "Record your day and send clips at night",
    "Plan a virtual dinner over video",
    "Make a shared bucket list",
    "Write her name using things around you",
    "Send a small gift that reminds you of her",
    "Surprise her with an online note card",
    "Record a song line and send it to her",
    "Create a photo slideshow with background music",
    "Plan a synchronized stargazing session",
    "Make a digital scrapbook of your messages",
    "Surprise her by learning a phrase in her language",
    "Write a romantic paragraph each night for a week",
    "Share an online shopping cart with something for her",
    "Mail her a small item that smells like you",
    "Send her a 1-minute appreciation video",
    "Make a surprise morning call before she wakes",
    "Design a 'we'll do this when we meet' list",
    "Send her a printed photo book",
    "Create a shared digital journal",
    "Plan a surprise virtual game night",
    "End week with a message: 'Thank you for loving me from afar.'"
]

# Same Home Mode - 50 pre-written weekly tasks that rotate yearly
SAME_HOME_WEEKLY_TASKS = [
    "Cook her a full meal yourself",
    "Plan a surprise indoor date night",
    "Decorate the room with candles or lights",
    "Write her a short handwritten letter",
    "Give her a long massage",
    "Create a photo collage or reel of your week",
    "Plan a cozy movie night with snacks",
    "Wake up early and make her breakfast in bed",
    "Do all chores for the day without her help",
    "Recreate your first date at home",
    "Bake something sweet for her",
    "Plan a small home picnic",
    "Set up a bubble bath for her",
    "Give her a 'no chores' relaxation day",
    "Organize her wardrobe or shelf",
    "Clean the entire house before she wakes up",
    "Make a playlist just for her",
    "Write 10 things you adore about her",
    "Gift her something small but thoughtful",
    "Plan a fun indoor challenge or game",
    "Do grocery shopping together",
    "Spend an hour without phone, only conversation",
    "Make a time-lapse video cooking together",
    "Set up fairy lights and dance with her",
    "Create a mini spa setup at home",
    "Surprise her with her favorite dessert",
    "Take care of all errands she was delaying",
    "Plan a new recipe and cook together",
    "Write her initials somewhere secretly",
    "Make a small DIY gift",
    "Surprise her with a handwritten note trail",
    "Plan a themed dinner (Italian, Street Food, etc.)",
    "Do a mini photoshoot of her",
    "Reorganize the room together",
    "Leave small notes all around the house",
    "Surprise her by cleaning her workspace",
    "Play her favorite childhood game together",
    "Make a 'thank you' jar of notes",
    "Record a short video saying what she means to you",
    "Plan a cozy candlelight dinner",
    "Give her a head massage and tea",
    "Set up her favorite music and slow dance",
    "Spend an evening watching stars or night sky",
    "Make a memory scrapbook",
    "Surprise her with matching T-shirts or pajamas",
    "Let her rest while you handle everything for a day",
    "Create a 'reason I love you' sticky wall",
    "Recreate her favorite café setup at home",
    "Plan one 'no phone' day together",
    "End the week with a handwritten thank-you note"
]

# Daily Meetup Mode - 750 pre-written messages (150 each category) for 3 daily messages with monthly rotation
DAILY_MEETUP_MESSAGES = {
    "good_morning": [
        "Morning, my favorite person 😘",
        "Wake up, today's ours!",
        "Good morning, cutie pie ❤️",
        "Sunshine, your smile needed here",
        "Morning hugs coming your way 🤗",
        "Wake up, my heartbeat",
        "Morning vibes just for you",
        "Rise and shine, my joy",
        "Hello love, start your day happy",
        "Morning kisses for my sweetheart 💋",
        "Wakey wakey, eggs and bakey!",
        "Good morning, my favorite human",
        "Rise, love, today is magical",
        "Morning cuddles waiting for you",
        "Hello sunshine, thinking of you",
        "Good morning, my heartbeat",
        "Wake up, let's make memories",
        "Morning, my angel 😇",
    ],
    "good_night": [
        "Good night, love of my life",
        "Sweet dreams, my sunshine",
        "Sleep tight, my heartbeat",
        "Night hugs for you 🤗",
        "Drift into dreams, my love",
        "Sleep peacefully, cutie",
        "Night kisses 💋",
        "Good night, my star 🌟",
        "Sweet dreams, my angel",
        "Sleep tight, my everything",
        "Good night, my darling",
        "Rest well, my joy",
        "Night hugs, love ❤️",
        "Sleep peacefully, my heart",
        "Good night, my sunshine",
        "Drift into dreams, my favorite",
        "Nighty night, my love",
        "Sweet dreams, my happiness",
    ],
    "love_confession": [
        "You're my favorite everything",
        "I can't stop thinking about you",
        "My heart is all yours",
        "I'm crazy about you",
        "You complete me",
        "I love you endlessly",
        "My soul belongs to you",
        "You make life beautiful",
        "I'm yours forever",
        "You're my reason to smile",
        "I adore you endlessly",
        "You're my world",
        "I love your laugh",
        "You're my peace",
        "I'm lost in you",
        "You're my happiness",
        "I love every part of you",
        "You're my soulmate",
    ],
    "apology": [
        "I'm sorry for hurting you",
        "Please forgive me, love",
        "I didn't mean to upset you",
        "I regret what I said",
        "I feel awful, my heart",
        "I promise to do better",
        "Can we start fresh?",
        "I hate seeing you upset",
        "Please accept my apology",
        "I'm truly sorry, my love",
        "I'll make it up to you",
        "Forgive me for my mistakes",
        "I feel terrible, love",
        "I didn't mean it that way",
        "I hope you can forgive me",
        "I'm sorry from the heart",
        "I'll never do it again",
        "I feel bad for hurting you",
    ],
    "funny_hinglish": [
        "Tum ho ya WiFi, dono hi missing 😜",
        "Tumhare bina life buffering lagti hai",
        "Love you zyada nahi, 100GB tak",
        "Tum meri battery ho, recharge kar do 💕",
        "Tumhare jokes pe bhi hansna padta hai",
        "Tumhari smile pe hi data save hota hai",
        "Tum meri notification ho, miss nahi kar sakta",
        "Tumhare bina life low battery",
        "Tum meri app update ho, always needed",
        "Tum meri favorite alert ho",
        "Tumhare memes best lagte hain",
        "Tum meri WiFi password ho, share kar do",
        "Tumhari smile pe unlimited recharge mile",
        "Tum meri ringtone ho, always sunna chahta",
        "Tumhare texts pe heart lagta hai",
        "Tum meri password ho, safe aur secure",
        "Tumhare jokes pe LOL karna mandatory",
        "Tum meri emoji ho, bina nahi ho sakta 😘",
    ]
}

LONG_DISTANCE_MESSAGES = {
    "good_morning": [
        "Good morning, my love! 🌞",
        "Wake up, can't wait to see you soon",
        "Morning hugs from afar 🤗",
        "Rise and shine, my heartbeat",
        "Good morning, thinking of you ❤️",
        "Wake up, my sunshine",
        "Morning vibes just for you",
        "Hello love, start your day happy",
        "Morning kisses from distance 💋",
        "Good morning, my favorite person",
        "Wakey wakey, sleepyhead!",
        "Good morning, my star 🌟",
        "Rise and shine, my angel",
        "Morning cuddles in spirit",
        "Hello sunshine, miss you",
        "Good morning, my heartbeat",
        "Wake up, let's make memories",
        "Morning, my everything",
    ],
    "good_night": [
        "Good night, my love 😘",
        "Sweet dreams, my sunshine",
        "Sleep tight, my heartbeat",
        "Night hugs from afar 🤗",
        "Drift into dreams, my angel",
        "Sleep peacefully, my darling",
        "Night kisses 💋",
        "Good night, my star 🌟",
        "Sweet dreams, my everything",
        "Sleep tight, love of my life",
        "Good night, my heartbeat",
        "Rest well, my joy",
        "Night hugs, my love ❤️",
        "Sleep peacefully, my heart",
        "Good night, my sunshine",
        "Drift into dreams, my favorite",
        "Nighty night, my love",
        "Sweet dreams, my happiness",
    ],
    "love_confession": [
        "I love you beyond distance",
        "My heart beats only for you",
        "I'm yours forever, no matter the miles",
        "You complete me, even from far",
        "I'm crazy about you",
        "You're my soulmate",
        "I adore you endlessly",
        "You make my life beautiful",
        "I can't stop thinking about you",
        "You're my happiness",
        "My heart belongs to you",
        "You're my everything",
        "I love your voice over calls",
        "You're my peace",
        "I miss you every second",
        "You're my joy",
        "I love every part of you",
        "You're my forever",
    ],
    "apology": [
        "I'm sorry for hurting you, love",
        "Please forgive me, even from afar",
        "I didn't mean to upset you",
        "I regret my words",
        "I feel awful, my heart",
        "I'll do better, promise",
        "Can we start fresh?",
        "I hate seeing you upset",
        "Please accept my apology",
        "I'm truly sorry, love",
        "I'll make it up to you",
        "Forgive me for my mistakes",
        "I feel terrible",
        "I didn't mean it that way",
        "I hope you can forgive me",
        "I'm sorry from the heart",
        "I'll never do it again",
        "I feel bad for hurting you",
    ],
    "funny_hinglish": [
        "Tum ho ya WiFi, dono hi miss ho raha hai 😜",
        "Tumhare bina life buffering lagti hai",
        "Love you zyada nahi, 100GB tak",
        "Tum meri battery ho, recharge kar do 💕",
        "Tumhare jokes pe bhi hansna padta hai",
        "Tumhari smile pe hi data save hota hai",
        "Tum meri notification ho, miss nahi kar sakta",
        "Tumhare bina life low battery",
        "Tum meri app update ho, always needed",
        "Tum meri favorite alert ho",
        "Tumhare memes best lagte hain",
        "Tum meri WiFi password ho, share kar do",
        "Tumhari smile pe unlimited recharge mile",
        "Tum meri ringtone ho, always sunna chahta",
        "Tumhare texts pe heart lagta hai",
        "Tum meri password ho, safe aur secure",
        "Tumhare jokes pe LOL karna mandatory",
        "Tum meri emoji ho, bina nahi ho sakta 😘",
    ]
}

SAME_HOME_MESSAGES = {
    "good_morning": [
        "Good morning, sunshine! ☀️",
        "Rise and shine, my love!",
        "Morning, my favorite human.",
        "Wake up, it's cuddle o'clock!",
        "Good morning, cutie pie ❤️",
        "Morning hugs coming your way 🤗",
        "Wakey wakey, eggs and bakey!",
        "Hello, beautiful soul, good morning",
        "Good morning, my happiness 😘",
        "Sun's out, smiles out!",
        "Hey love, ready for today?",
        "Morning kisses for you 💋",
        "Wake up, your coffee's waiting ☕",
        "Good morning, my heart",
        "Rise, my little sunshine 🌻",
        "Morning, love of my life",
        "Wakey, wakey, sleepyhead",
        "Good morning, my heartbeat",
        "Hello, love, let's make today awesome",
        "Morning vibes, just for you ✨",
        "Rise and shine, my queen",
        "Morning hugs and kisses 😘",
        "Good morning, my favorite smile",
        "Wake up, let's conquer today together",
        "Hello sunshine, thinking of you",
        "Morning, my love, you're amazing",
        "Wakey, my cuddle buddy",
        "Good morning, my joy",
        "Morning, my sunshine in human form",
        "Rise, love, today's a new adventure",
        "Hey beautiful, good morning",
        "Morning kisses and love 💕",
        "Wake up, sleepy angel",
        "Good morning, my star 🌟",
        "Morning vibes just for you",
        "Rise, my heart beats for you",
        "Hello love, a new day awaits",
        "Morning, my everything",
        "Wakey, my love, smile today",
        "Good morning, my darling",
        "Morning hugs from me to you",
        "Hey sunshine, let's start today",
        "Good morning, my love, shine bright",
        "Wake up, the world misses your smile",
        "Morning, my heart, you're beautiful",
        "Rise and shine, my precious",
        "Morning cuddles waiting for you",
        "Hello love, your day awaits",
        "Good morning, my angel",
        "Wakey, my cutie pie ❤️",
        "Good morning, my sweet dream come true",
        "Rise and shine, my home happiness",
        "Morning, my cozy comfort zone",
        "Wake up, breakfast together time",
        "Good morning, my living room love",
        "Morning cuddles on the couch",
        "Rise, my kitchen dance partner",
        "Hello love, let's cook together",
        "Good morning, my bedroom bliss",
        "Wake up, shower singing buddy",
        "Morning, my balcony coffee mate",
        "Rise and shine, my garden helper",
        "Good morning, my cleaning partner",
        "Wake up, laundry folding time",
        "Morning, my grocery shopping buddy",
        "Rise, my home movie night star",
        "Hello love, let's redecorate today",
        "Good morning, my DIY project mate",
        "Wake up, house maintenance team",
        "Morning, my home gym partner",
        "Rise and shine, my cooking student",
        "Good morning, my recipe tester",
        "Wake up, dishwashing duo time",
        "Morning, my home office colleague",
        "Rise, my work from home buddy",
        "Hello love, productivity partner",
        "Good morning, my zoom call background",
        "Wake up, coffee break companion",
        "Morning, my lunch preparation helper",
        "Rise and shine, my evening planner",
        "Good morning, my weekend project mate",
        "Wake up, home improvement team",
        "Morning, my furniture arrangement expert",
        "Rise, my interior design consultant",
        "Hello love, my space organizer",
        "Good morning, my decluttering partner",
        "Wake up, my storage solution finder",
        "Morning, my home security system",
        "Rise and shine, my comfort provider",
        "Good morning, my temperature controller",
        "Wake up, my lighting adjuster",
        "Morning, my music playlist curator",
        "Rise, my entertainment center",
        "Hello love, my boredom eliminator",
        "Good morning, my activity planner",
        "Wake up, my surprise organizer",
        "Morning, my gift wrapper",
        "Rise and shine, my celebration planner",
        "Good morning, my memory maker",
        "Wake up, my photo session director",
        "Morning, my social media manager",
        "Rise, my content creator",
        "Hello love, my story narrator",
        "Good morning, my blog post inspiration",
        "Wake up, my creative muse",
        "Morning, my artistic collaborator",
        "Rise and shine, my skill teacher",
        "Good morning, my hobby instructor",
        "Wake up, my talent discoverer",
        "Morning, my potential unleasher",
        "Rise, my confidence builder",
        "Hello love, my motivation source",
        "Good morning, my energy booster",
        "Wake up, my mood lifter",
        "Morning, my stress reliever",
        "Rise and shine, my relaxation guide",
        "Good morning, my meditation partner",
        "Wake up, my yoga instructor",
        "Morning, my exercise motivator",
        "Rise, my health coach",
        "Hello love, my wellness advisor",
        "Good morning, my nutrition consultant",
        "Wake up, my hydration reminder",
        "Morning, my sleep quality improver",
        "Rise and shine, my routine optimizer",
        "Good morning, my habit former",
        "Wake up, my goal setter",
        "Morning, my achievement celebrator",
        "Rise, my success multiplier",
        "Hello love, my victory dancer",
        "Good morning, my progress tracker",
        "Wake up, my milestone marker",
        "Morning, my journey companion",
        "Rise and shine, my path illuminator",
        "Good morning, my direction finder",
        "Wake up, my compass needle",
        "Morning, my GPS navigator",
        "Rise, my route planner",
        "Hello love, my destination definer",
        "Good morning, my arrival announcer",
        "Wake up, my departure scheduler",
        "Morning, my timeline manager",
        "Rise and shine, my calendar keeper",
        "Good morning, my appointment setter",
        "Wake up, my meeting organizer",
        "Morning, my agenda creator",
        "Rise, my priority sorter",
        "Hello love, my task distributor",
        "Good morning, my responsibility sharer",
        "Wake up, my burden lightener",
        "Morning, my load balancer",
        "Rise and shine, my support system",
        "Good morning, my backup plan",
        "Wake up, my safety net",
        "Morning, my emergency contact",
        "Rise, my first aid kit",
        "Hello love, my healing touch"
    ],
    "good_night": [
        "Good night, my love 😘",
        "Sweet dreams, my sunshine",
        "Sleep tight, my heartbeat",
        "Nighty night, cutie",
        "Dream of me, love 💕",
        "Sleep well, my darling",
        "Good night hugs coming 🤗",
        "Close your eyes, I'm with you",
        "Sweet dreams, my angel",
        "Good night, my everything",
        "Sleep peacefully, love",
        "Night kisses for you 💋",
        "Good night, my star 🌟",
        "Drift into dreams, my love",
        "Sleep tight, my joy",
        "Nighty night, my sunshine",
        "Sweet dreams, my heart",
        "Good night, my cuddle buddy",
        "Rest well, my love",
        "Sleep tight, my queen",
        "Good night, my happiness",
        "Dream sweet, my angel",
        "Night hugs, my love",
        "Sleep well, my everything",
        "Good night, cutie pie",
        "Sweet dreams, my darling",
        "Night kisses, love 💕",
        "Rest peacefully, my heart",
        "Good night, my sunshine",
        "Sleep tight, my star",
        "Sweet dreams, my favorite",
        "Good night, love of my life",
        "Drift to sleep, my cutie",
        "Nighty night, my joy",
        "Sleep peacefully, my heartbeat",
        "Sweet dreams, my love",
        "Good night, my angel face",
        "Sleep well, my darling",
        "Night hugs and kisses 🤗",
        "Good night, my precious",
        "Sweet dreams, my sunshine",
        "Sleep tight, my cuddle buddy",
        "Good night, my everything",
        "Dream of us, my love",
        "Night kisses for you 💋",
        "Sleep well, my heart",
        "Good night, my star",
        "Sweet dreams, my love",
        "Drift peacefully, cutie pie",
        "Nighty night, my happiness",
        "Good night, my bedroom partner",
        "Sleep tight, my pillow sharer",
        "Sweet dreams, my blanket buddy",
        "Good night, my mattress mate",
        "Dream well, my sheet companion",
        "Sleep peacefully, my nightstand neighbor",
        "Good night, my alarm clock colleague",
        "Rest tight, my midnight snack sharer",
        "Sweet dreams, my 3am water buddy",
        "Good night, my bathroom queue partner",
        "Sleep well, my morning routine teammate",
        "Nighty night, my coffee maker",
        "Good night, my breakfast preparer",
        "Dream sweet, my lunch packer",
        "Sleep tight, my dinner planner",
        "Good night, my dishwasher loader",
        "Sweet dreams, my kitchen cleaner",
        "Rest well, my living room organizer",
        "Good night, my TV remote sharer",
        "Sleep peacefully, my movie picker",
        "Nighty night, my popcorn maker",
        "Good night, my couch companion",
        "Dream of us, my cuddle provider",
        "Sleep tight, my warmth generator",
        "Sweet dreams, my comfort zone",
        "Good night, my safe space creator",
        "Rest well, my peace bringer",
        "Sleep peacefully, my calm inducer",
        "Good night, my stress reducer",
        "Nighty night, my relaxation guide",
        "Sweet dreams, my tension reliever",
        "Good night, my anxiety soother",
        "Sleep tight, my worry eliminator",
        "Dream well, my fear fighter",
        "Good night, my courage giver",
        "Rest peacefully, my strength provider",
        "Sleep well, my energy saver",
        "Nighty night, my battery charger",
        "Good night, my power source",
        "Sweet dreams, my fuel supplier",
        "Sleep tight, my engine restarter",
        "Good night, my system reboter",
        "Dream well, my refresh button",
        "Rest peacefully, my update installer",
        "Sleep well, my backup creator",
        "Good night, my restore point",
        "Nighty night, my save function",
        "Sweet dreams, my memory keeper",
        "Sleep tight, my moment capturer",
        "Good night, my photo albumizer",
        "Dream well, my story writer",
        "Rest peacefully, my chapter closer",
        "Sleep well, my page turner",
        "Good night, my book marker",
        "Nighty night, my reading light",
        "Sweet dreams, my bedtime story",
        "Sleep tight, my lullaby singer",
        "Good night, my melody maker",
        "Dream well, my rhythm keeper",
        "Rest peacefully, my beat provider",
        "Sleep well, my tempo setter",
        "Good night, my harmony creator",
        "Nighty night, my chord player",
        "Sweet dreams, my note holder",
        "Sleep tight, my scale climber",
        "Good night, my octave reacher",
        "Dream well, my frequency finder",
        "Rest peacefully, my wavelength matcher",
        "Sleep well, my signal sender",
        "Good night, my message deliverer",
        "Nighty night, my communication bridge",
        "Sweet dreams, my connection keeper",
        "Sleep tight, my bond strengthener",
        "Good night, my relationship builder",
        "Dream well, my love multiplier",
        "Rest peacefully, my heart expander",
        "Sleep well, my soul connector",
        "Good night, my spirit merger",
        "Nighty night, my essence blender",
        "Sweet dreams, my energy combiner",
        "Sleep tight, my force uniter",
        "Good night, my power joiner",
        "Dream well, my strength adder",
        "Rest peacefully, my capacity increaser",
        "Sleep well, my potential maximizer",
        "Good night, my ability enhancer",
        "Nighty night, my skill improver",
        "Sweet dreams, my talent polisher",
        "Sleep tight, my gift unwrapper",
        "Good night, my treasure finder",
        "Dream well, my gem discoverer",
        "Rest peacefully, my diamond polisher",
        "Sleep well, my pearl cultivator",
        "Good night, my gold refiner",
        "Nighty night, my silver brightener",
        "Sweet dreams, my copper conductor",
        "Sleep tight, my metal detector",
        "Good night, my mineral finder",
        "Dream well, my crystal grower",
        "Rest peacefully, my stone polisher",
        "Sleep well, my rock stabilizer",
        "Good night, my foundation setter",
        "Nighty night, my base builder",
        "Sweet dreams, my ground preparer",
        "Sleep tight, my soil enricher",
        "Good night, my seed planter",
        "Dream well, my growth nurturer",
        "Rest peacefully, my bloom encourager",
        "Sleep well, my flower opener"
    ],
    "love_confession": [
        "I love you more than words can say",
        "My heart beats only for you",
        "You're my forever and always",
        "I can't imagine life without you",
        "Every moment with you is magic",
        "You complete me, love",
        "I'm yours, always",
        "You're my reason to smile",
        "I love every little thing about you",
        "My love grows for you every day",
        "I'm crazy about you",
        "You're my everything",
        "I'm addicted to your smile",
        "You're my soulmate",
        "I love you more each day",
        "You're the love of my life",
        "I'm lost in you",
        "You make my world beautiful",
        "I can't stop thinking about you",
        "I love you to the moon and back",
        "You're my favorite person",
        "I adore you endlessly",
        "My heart belongs to you",
        "I'm yours forever",
        "You're my happiness",
        "I love you deeply",
        "You're my one and only",
        "I can't live without you",
        "You make life worth it",
        "I love you beyond words",
        "You're my home sweet home",
        "I love our cozy mornings together",
        "You make our house a real home",
        "I love how we fit together perfectly",
        "You're my domestic bliss",
        "I love our daily routines together",
        "You make ordinary moments magical",
        "I love how we sync in our space",
        "You're my comfortable silence",
        "I love our spontaneous kitchen dances",
        "You make doing chores feel like fun",
        "I love how we share everything",
        "You're my perfect roommate for life",
        "I love our midnight snack adventures",
        "You make Netflix nights special",
        "I love how we decorate together",
        "You're my interior design partner",
        "I love our weekend lazy mornings",
        "You make every meal taste better",
        "I love how we problem-solve together",
        "You're my favorite human to wake up to",
        "I love how we handle stress together",
        "You make our space feel safe",
        "I love our inside jokes and references",
        "You're my favorite person to be weird with",
        "I love how we support each other's goals",
        "You make working from home bearable",
        "I love our impromptu date nights at home",
        "You're my favorite conversation partner",
        "I love how we respect each other's space",
        "You make compromising feel natural",
        "I love our shared dreams and plans",
        "You're my favorite person to grow old with",
        "I love how we handle disagreements maturely",
        "You make every day feel like an adventure",
        "I love our shared responsibilities",
        "You're my favorite teammate in life",
        "I love how we celebrate small victories",
        "You make ordinary Tuesday nights special",
        "I love our synchronized sleep schedules",
        "You're my favorite person to share silence with",
        "I love how we motivate each other",
        "You make self-improvement feel fun",
        "I love our shared hobbies and interests",
        "You're my favorite person to try new things with",
        "I love how we balance each other out",
        "You make my weaknesses feel like strengths",
        "I love our ability to communicate openly",
        "You're my favorite person to be vulnerable with",
        "I love how we handle finances together",
        "You make budgeting feel like teamwork",
        "I love our shared vision for the future",
        "You're my favorite person to make memories with",
        "I love how we adapt to changes together",
        "You make challenges feel conquerable",
        "I love our mutual respect and trust",
        "You're my favorite person to depend on",
        "I love how we maintain our individuality",
        "You make being together feel effortless",
        "I love our shared sense of humor",
        "You're my favorite person to laugh with",
        "I love how we handle each other's moods",
        "You make bad days feel manageable",
        "I love our ability to give each other space",
        "You're my favorite person to miss",
        "I love how we reunite after time apart",
        "You make coming home feel like a celebration",
        "I love our shared routines and rituals",
        "You're my favorite person to build traditions with",
        "I love how we handle unexpected situations",
        "You make spontaneity feel safe",
        "I love our mutual growth and development",
        "You're my favorite person to evolve with",
        "I love how we inspire each other daily",
        "You make personal development feel shared",
        "I love our complementary strengths",
        "You're my favorite person to be a team with",
        "I love how we handle success together",
        "You make achievements feel more meaningful",
        "I love our shared values and principles",
        "You're my favorite person to align with",
        "I love how we support each other's families",
        "You make extended relationships easier",
        "I love our ability to create new traditions",
        "You're my favorite person to experiment with",
        "I love how we handle technology together",
        "You make digital life feel more human",
        "I love our shared environmental consciousness",
        "You're my favorite person to be sustainable with",
        "I love how we handle health and wellness",
        "You make taking care of ourselves feel mutual",
        "I love our shared appreciation for simple pleasures",
        "You're my favorite person to enjoy life's basics with",
        "I love how we handle social situations together",
        "You make being introverted or extroverted work",
        "I love our balance of together and apart time",
        "You're my favorite person to need and be needed by",
        "I love how we handle seasonal changes",
        "You make every season feel special",
        "I love our shared creativity and expression",
        "You're my favorite person to be artistic with",
        "I love how we handle practical matters",
        "You make adulting feel less overwhelming",
        "I love our shared sense of adventure",
        "You're my favorite person to explore life with",
        "I love how we create our own little world",
        "You make our bubble feel perfect",
        "I love our ability to be completely ourselves",
        "You're my favorite person to be authentic with",
        "I love how we handle the mundane together",
        "You make boring stuff feel interesting",
        "I love our shared commitment to growth",
        "You're my favorite person to become better with",
        "I love how we celebrate each other's uniqueness",
        "You make differences feel like strengths",
        "I love our mutual desire to contribute positively",
        "You're my favorite person to make a difference with",
        "I love how we handle uncertainty together",
        "You make the unknown feel less scary",
        "I love our shared optimism about the future",
        "You're my favorite person to hope with",
        "I love how we turn houses into homes",
        "You make any space feel like ours",
        "I love our journey from 'me' to 'we'",
        "You're my favorite person to become 'us' with",
        "I love how we write our story together",
        "You make every chapter feel worthwhile",
        "I love our shared definition of happiness",
        "You're my favorite person to be content with",
        "I love how we make the ordinary extraordinary",
        "You make every day feel like a gift",
        "I love you exactly as you are, right here at home"
    ],
    "apology": [
        "I'm sorry, please forgive me",
        "I didn't mean to hurt you",
        "I regret what happened",
        "Please don't be mad at me",
        "I feel bad for my words",
        "I'm sorry, love",
        "Can we start fresh?",
        "I'll do better, promise",
        "Forgive me, my heart",
        "I hate hurting you",
        "I'm truly sorry",
        "Please accept my apology",
        "I didn't mean it that way",
        "I'm sorry for upsetting you",
        "I feel awful, love",
        "Can we talk and fix this?",
        "I'll make it up to you",
        "I regret my actions",
        "Please forgive me, my love",
        "I'm sorry from the heart",
        "I didn't want this to happen",
        "I feel terrible",
        "I'm sorry, you're precious to me",
        "I hope you can forgive me",
        "I'll never do it again",
        "I feel bad, please accept me",
        "I apologize sincerely",
        "I'm sorry for my mistakes",
        "I hate that I hurt you",
        "Please give me another chance",
        "Sorry for leaving dishes in the sink",
        "I'm sorry for hogging the remote",
        "Forgive me for being messy today",
        "Sorry for using up all the hot water",
        "I'm sorry for forgetting to take out trash",
        "Sorry for eating your leftover pizza",
        "I'm sorry for leaving clothes everywhere",
        "Forgive me for being grumpy this morning",
        "Sorry for not helping with dinner prep",
        "I'm sorry for watching ahead on our show",
        "Sorry for leaving the toilet seat up",
        "I'm sorry for finishing the milk",
        "Forgive me for being on my phone too much",
        "Sorry for not making the bed",
        "I'm sorry for leaving wet towels around",
        "Sorry for cooking something that smells bad",
        "I'm sorry for being too loud last night",
        "Forgive me for forgetting our plans",
        "Sorry for not grocery shopping when I said I would",
        "I'm sorry for leaving lights on everywhere",
        "Sorry for taking up bathroom time",
        "I'm sorry for not cleaning up after myself",
        "Forgive me for eating the last cookie",
        "Sorry for not listening when you were talking",
        "I'm sorry for being distracted during our time",
        "Sorry for leaving my stuff on your side",
        "I'm sorry for not helping fold laundry",
        "Forgive me for forgetting to charge your phone",
        "Sorry for making noise when you were sleeping",
        "I'm sorry for not appreciating your cooking",
        "Sorry for complaining about the temperature",
        "I'm sorry for being indecisive about dinner",
        "Forgive me for not cleaning the bathroom",
        "Sorry for leaving cabinet doors open",
        "I'm sorry for using your favorite mug",
        "Sorry for not replacing the toilet paper",
        "I'm sorry for being cranky about chores",
        "Forgive me for not watering the plants",
        "Sorry for leaving the kitchen messy",
        "I'm sorry for not fixing that thing I said I would",
        "Sorry for being stubborn about decorating",
        "I'm sorry for not helping organize",
        "Forgive me for losing the remote again",
        "Sorry for not defrosting dinner in time",
        "I'm sorry for leaving crumbs on the counter",
        "Sorry for not taking out recycling",
        "I'm sorry for using all the WiFi bandwidth",
        "Forgive me for not cleaning hair from the drain",
        "Sorry for leaving shoes in the hallway",
        "I'm sorry for not helping with meal planning",
        "Sorry for being picky about temperature",
        "I'm sorry for not assembling that furniture",
        "Forgive me for procrastinating on that project",
        "Sorry for not helping choose paint colors",
        "I'm sorry for being impatient with repairs",
        "Sorry for not calling the maintenance guy",
        "I'm sorry for losing important papers",
        "Forgive me for not backing up our photos",
        "Sorry for forgetting to pay that bill",
        "I'm sorry for not scheduling that appointment",
        "Sorry for being disorganized with our calendar",
        "I'm sorry for double-booking our weekend",
        "Forgive me for not coordinating with your schedule",
        "Sorry for making plans without checking first",
        "I'm sorry for being late to our home date",
        "Sorry for not preparing for our guests",
        "I'm sorry for not helping clean before company",
        "Forgive me for embarrassing you in front of friends",
        "Sorry for not supporting your family visit",
        "I'm sorry for being antisocial during gatherings",
        "Sorry for not helping with party planning",
        "I'm sorry for complaining about your relatives",
        "Forgive me for not being more welcoming",
        "Sorry for not participating in your traditions",
        "I'm sorry for being difficult about holidays",
        "Sorry for not helping wrap presents",
        "I'm sorry for spoiling your surprise",
        "Forgive me for not keeping secrets better",
        "Sorry for ruining your mood today",
        "I'm sorry for being negative lately",
        "Sorry for not celebrating your achievements",
        "I'm sorry for not being supportive enough",
        "Forgive me for being jealous unnecessarily",
        "Sorry for doubting your decisions",
        "I'm sorry for not trusting your judgment",
        "Sorry for questioning your friends",
        "I'm sorry for being controlling about plans",
        "Forgive me for not giving you space",
        "Sorry for being clingy when you need alone time",
        "I'm sorry for not respecting your boundaries",
        "Sorry for pushing when you said no",
        "I'm sorry for not listening to your concerns",
        "Forgive me for dismissing your feelings",
        "Sorry for making you feel unheard",
        "I'm sorry for not validating your emotions",
        "Sorry for being defensive instead of understanding",
        "I'm sorry for making this about me",
        "Forgive me for not seeing your perspective",
        "Sorry for being selfish with our shared space",
        "I'm sorry for not compromising fairly",
        "Sorry for not meeting you halfway",
        "I'm sorry for taking you for granted",
        "Forgive me for not showing appreciation",
        "Sorry for forgetting to say thank you",
        "I'm sorry for not noticing your efforts",
        "Sorry for expecting instead of appreciating",
        "I'm sorry for not acknowledging your contributions",
        "Forgive me for making you feel invisible",
        "Sorry for not making you feel valued",
        "I'm sorry for taking our relationship for granted",
        "Sorry for not prioritizing us enough",
        "I'm sorry for letting outside stress affect us",
        "Forgive me for bringing work problems home",
        "Sorry for not leaving issues at the door",
        "I'm sorry for taking my bad mood out on you",
        "Sorry for not managing my stress better",
        "I'm sorry for not communicating my needs clearly",
        "Forgive me for expecting you to read my mind",
        "Sorry for not asking for help when I needed it",
        "I'm sorry for bottling up my feelings",
        "Sorry for exploding instead of talking calmly",
        "I'm sorry for saying things I didn't mean",
        "Forgive me for words that can't be taken back",
        "Sorry for not thinking before I spoke",
        "I'm sorry for letting pride get in the way",
        "Sorry for not apologizing sooner",
        "I'm sorry for making you wait for this apology",
        "Forgive me, let's work on us together"
    ],
    "funny_hinglish": [
        "Tum ho ya WiFi, dono hi missing 😜",
        "Tumhare bina life buffering lagti hai",
        "Love you zyada nahi, 100GB tak",
        "Tum meri battery ho, charge kar do 💕",
        "Tumhare jokes pe bhi hansna padta hai",
        "Tumhare smile pe hi data save hota hai",
        "Tum meri notification ho, miss nahi kar sakta",
        "Tumhare bina life lagta hai low battery",
        "Tum meri app update ho, always needed",
        "Tum meri favourite alert ho",
        "Tumhare memes best lagte hain",
        "Tum meri WiFi password ho, share kar do",
        "Tumhare smile pe unlimited recharge mile",
        "Tum meri ringtone ho, always sunna chahta",
        "Tumhare texts pe heart lagta hai",
        "Tum meri password ho, safe aur secure",
        "Tumhare jokes pe LOL karna mandatory",
        "Tum meri emoji ho, bina nahi ho sakta 😘",
        "Tum meri notification sound ho, sweet lagti",
        "Tum meri background ho, life beautiful",
        "Tumhare saath selfie, full HD",
        "Tum meri cloud ho, sab safe rakhti",
        "Tumhare memes daily feed main chahiye",
        "Tum meri wallpaper ho, har din dekhu",
        "Tum meri app ho, update zaruri",
        "Tum meri playlist ho, repeat mode",
        "Tum meri screenshot ho, save karna hai",
        "Tumhari call aayi, heart rate high",
        "Tum meri battery saver ho, life recharge",
        "Tum meri location ho, always trackable",
        "Tum meri story ho, always visible",
        "Tum meri sticker pack ho, fun lagti",
        "Tum meri Google search ho, answers sab",
        "Tum meri notification ho, miss nahi kar sakta",
        "Tum meri password hint ho, smart",
        "Tum meri chat head ho, float karte",
        "Tum meri Bluetooth ho, connect hona zaruri",
        "Tum meri selfie filter ho, perfect lagti",
        "Tum meri app lock ho, protect karti",
        "Tum meri status ho, always update",
        "Tum meri cloud storage ho, memories safe",
        "Tum meri ringtone song ho, repeat chahiye",
        "Tum meri WiFi hotspot ho, life connect",
        "Tum meri GPS ho, direction correct",
        "Tum meri reminder ho, important cheez",
        "Tum meri alarm ho, wake up my heart",
        "Tum meri email subject ho, always read",
        "Tum meri notification badge ho, love full",
        "Tum meri online status ho, live always",
        "Tum meri wallpaper theme ho, perfect color",
        "Tum meri home screen ho, first dekhu",
        "Tumhare saath kitchen main cooking, MasterChef level",
        "Tum meri living room ho, comfort zone",
        "Tumhare saath Netflix, chill guaranteed",
        "Tum meri bedroom ho, sweet dreams factory",
        "Tumhare saath bathroom queue, morning routine",
        "Tum meri balcony ho, fresh air supplier",
        "Tumhare saath laundry folding, team work",
        "Tum meri dining table ho, meal sharing space",
        "Tumhare saath grocery shopping, cart partner",
        "Tum meri sofa ho, cuddle headquarters",
        "Tumhare saath dishwashing, bubble party",
        "Tum meri closet ho, fashion consultant",
        "Tumhare saath cleaning, house maintenance team",
        "Tum meri kitchen counter ho, cooking support",
        "Tumhare saath morning coffee, energy booster",
        "Tum meri shower ho, singing duet partner",
        "Tumhare saath evening walk, fitness buddy",
        "Tum meri refrigerator ho, snack supplier",
        "Tumhare saath weekend lazy, relaxation mode",
        "Tum meri air conditioner ho, temperature controller",
        "Tumhare saath movie night, entertainment center",
        "Tum meri pillow ho, comfortable sleep provider",
        "Tumhare saath cooking experiment, taste tester",
        "Tum meri mirror ho, reflection of happiness",
        "Tumhare saath plant watering, garden team",
        "Tum meri doorbell ho, welcome home sound",
        "Tumhare saath furniture arrangement, interior designer",
        "Tum meri light switch ho, brightness controller",
        "Tumhare saath breakfast making, morning chef",
        "Tum meri bookshelf ho, story collection",
        "Tumhare saath game night, competitive partner",
        "Tum meri window ho, outside world viewer",
        "Tumhare saath deep cleaning, spring cleaning squad",
        "Tum meri ceiling fan ho, air circulation manager",
        "Tumhare saath late night snack, midnight munchies",
        "Tum meri doormat ho, welcome home greeting",
        "Tumhare saath room decoration, aesthetic coordinator",
        "Tum meri thermostat ho, perfect temperature keeper",
        "Tumhare saath cooking timer, perfect timing",
        "Tum meri shoe rack ho, organization expert",
        "Tumhare saath weekend project, DIY team",
        "Tum meri coat hanger ho, wardrobe manager",
        "Tumhare saath lunch prep, meal planning duo",
        "Tum meri calendar ho, schedule coordinator",
        "Tumhare saath evening routine, wind down partner",
        "Tum meri alarm clock ho, morning motivation",
        "Tumhare saath house maintenance, repair team",
        "Tum meri dustbin ho, cleanliness partner",
        "Tumhare saath seasonal decoration, festival coordinator",
        "Tum meri extension cord ho, power connection",
        "Tumhare saath guest preparation, hosting team",
        "Tum meri storage box ho, memory keeper",
        "Tumhare saath bill paying, financial planning duo",
        "Tum meri first aid kit ho, care provider",
        "Tumhare saath yoga session, wellness partner",
        "Tum meri tool box ho, problem solver",
        "Tumhare saath candle lighting, ambiance creator",
        "Tum meri spice rack ho, flavor enhancer",
        "Tumhare saath photo organizing, memory curator",
        "Tum meri charging station ho, energy hub",
        "Tumhare saath meal planning, nutrition team",
        "Tum meri remote control ho, entertainment manager",
        "Tumhare saath morning stretch, flexibility coach",
        "Tum meri filing cabinet ho, document organizer",
        "Tumhare saath evening tea, relaxation ritual",
        "Tum meri smoke detector ho, safety guardian",
        "Tumhare saath weekend cleaning, productivity duo",
        "Tum meri medicine cabinet ho, health supporter",
        "Tumhare saath budget planning, savings team",
        "Tum meri water filter ho, purity provider",
        "Tumhare saath morning news, information sharer",
        "Tum meri security system ho, protection provider",
        "Tumhare saath evening walk, step counter duo",
        "Tum meri recycling bin ho, environment protector",
        "Tumhare saath meal delivery waiting, patience tester",
        "Tum meri ice maker ho, coolness provider",
        "Tumhare saath furniture assembly, instruction reader",
        "Tum meri doorknob ho, entry facilitator",
        "Tumhare saath package receiving, delivery coordinator",
        "Tum meri weather app ho, climate advisor",
        "Tumhare saath morning routine, synchronization master",
        "Tum meri backup generator ho, reliability provider",
        "Tumhare saath evening cooking, chef collaboration",
        "Tum meri night light ho, comfort provider",
        "Tumhare saath weekend planning, activity coordinator",
        "Tum meri key holder ho, security manager",
        "Tumhare saath home improvement, upgrade team",
        "Tum meri timer ho, perfect timing keeper",
        "Tumhare saath seasonal transition, weather adapter",
        "Tum meri label maker ho, organization assistant",
        "Tumhare saath emergency preparedness, safety planner",
        "Tum meri comfort food ho, mood lifter",
        "Tumhare saath technology troubleshooting, IT support",
        "Tum meri cozy blanket ho, warmth provider",
        "Tumhare saath holiday preparation, celebration planner",
        "Tum meri morning sunlight ho, natural alarm",
        "Tumhare saath skill learning, study buddy",
        "Tum meri stress ball ho, tension reliever",
        "Tumhare saath creative project, imagination partner",
        "Tum meri comfort zone ho, safe space creator",
        "Tumhare saath future planning, dream builder",
        "Tum meri happy place ho, joy manufacturer",
        "Tumhare saath memory making, moment collector",
        "Tum meri energy drink ho, motivation supplier",
        "Tumhare saath problem solving, solution finder",
        "Tum meri comfort pillow ho, support provider",
        "Tumhare saath adventure planning, excitement creator",
        "Tum meri daily dose ho, happiness tablet",
        "Tumhare saath goal setting, achievement partner",
        "Tum meri life upgrade ho, version 2.0",
        "Tumhare saath relationship status, permanently occupied",
        "Tum meri heart emoji ho, love expression",
        "Tumhare saath life logging, daily blogger",
        "Tum meri favorite contact ho, speed dial 1",
        "Tumhare saath home transformation, makeover team",
        "Tum meri perfect match ho, compatibility 100%",
        "Tumhare saath life subscription, premium plan active",
        "Tum meri happiness algorithm ho, joy calculator",
        "Tumhare saath forever mode, infinity setting on"
    ]
}

class AITaskGenerator:
    """AI-powered task generation service"""
    
    def __init__(self):
        self.api_key = os.getenv("EMERGENT_LLM_KEY")
        if not self.api_key:
            raise ValueError("EMERGENT_LLM_KEY not found in environment variables")
        
        # Initialize LLM chat with GPT-4
        self.chat = LlmChat(
            api_key=self.api_key,
            session_id="task_generation",
            system_message=self._get_system_message()
        ).with_model("openai", "gpt-4o")
    
    def _get_system_message(self) -> str:
        """System message for task generation matching specific requirements"""
        return """You are an AI task generator for couple relationship strengthening. Generate tasks according to these strict requirements:

DAILY TASKS (3 per day):
- Must be VERY EASY (2-5 minutes maximum)
- Must require NO PURCHASE
- Categories: Communication, ThoughtfulGesture, MicroActivity
- Difficulty: "very_easy"
- Examples: Send loving text, give 20-second hug, ask about their day, leave sweet note

WEEKLY TASKS (1 per week):
- Must be PHYSICAL ACTION (meet, deliver item, do chore together, physical activity)
- Must be safe to execute
- Category: PhysicalActivity
- Difficulty: "easy"
- Examples: Cook meal together, take walk, clean room together, deliver surprise

CULTURAL REQUIREMENTS:
- Family-friendly content only
- No sexual content
- Culturally sensitive
- Appropriate for all relationship types

You must respond with ONLY valid JSON in this exact format:
{
  "tasks": [
    {
      "title": "Clear, actionable task description",
      "description": "Brief explanation of the task",
      "category": "Communication|ThoughtfulGesture|MicroActivity|PhysicalActivity",
      "difficulty": "very_easy|easy",
      "estimated_time_minutes": 2-5 for daily, 30-120 for weekly,
      "points": 5 for daily or 25 for weekly,
      "tips": "1-2 line helpful tip",
      "is_physical": false for daily, true for weekly
    }
  ]
}

STRICT VALIDATION:
- Daily tasks: 2-5 minutes, no purchase, very_easy difficulty
- Weekly tasks: physical action, safe, easy difficulty, is_physical=true"""

    def _get_daily_meetup_tasks(self, count: int = 3) -> List[Dict[str, Any]]:
        """Get pre-written Daily Meetup tasks that rotate monthly"""
        from datetime import datetime
        import random
        
        # Get current date for monthly rotation
        current_date = datetime.now()
        current_month = current_date.month
        current_year = current_date.year
        
        # Create a seed based on year and month for consistent monthly rotation
        # This ensures same tasks for the entire month but different tasks each month
        seed = f"{current_year}-{current_month}"
        random.seed(seed.encode())
        
        # Shuffle tasks based on the monthly seed
        shuffled_tasks = DAILY_MEETUP_TASKS.copy()
        random.shuffle(shuffled_tasks)
        
        # Get day of month to select different tasks each day
        day_of_month = current_date.day
        
        # Calculate starting index based on day (ensures 3 different tasks per day)
        # Use modulo to wrap around if we exceed the list length
        start_index = (day_of_month * 3) % len(shuffled_tasks)
        
        # Get tasks for today
        selected_task_descriptions = []
        for i in range(count):
            task_index = (start_index + i) % len(shuffled_tasks)
            selected_task_descriptions.append(shuffled_tasks[task_index])
        
        # Convert to the expected task format
        tasks = []
        for i, description in enumerate(selected_task_descriptions):
            task = {
                "id": f"daily_meetup_{current_date.strftime('%Y%m%d')}_{i+1}",
                "title": description,
                "description": description,
                "category": "Communication",  # Default category for Daily Meetup tasks
                "difficulty": "very_easy",
                "estimated_time_minutes": 3,
                "points": 5,
                "tips": f"Perfect for couples who meet daily! {description}",
                "is_physical": False,
                "generation_metadata": {
                    "model": "pre_written_daily_meetup",
                    "mode": "DAILY_IRL", 
                    "generated_at": current_date.isoformat(),
                    "task_source": "curated_daily_meetup_list",
                    "rotation_seed": seed,
                    "day_of_month": day_of_month
                }
            }
            tasks.append(task)
        
        return tasks

    def _get_long_distance_tasks(self, count: int = 3) -> List[Dict[str, Any]]:
        """Get pre-written Long Distance tasks that rotate monthly"""
        from datetime import datetime
        import random
        
        # Get current date for monthly rotation
        current_date = datetime.now()
        current_month = current_date.month
        current_year = current_date.year
        
        # Create a seed based on year and month for consistent monthly rotation
        # This ensures same tasks for the entire month but different tasks each month
        seed = f"{current_year}-{current_month}"
        random.seed(seed.encode())
        
        # Shuffle tasks based on the monthly seed
        shuffled_tasks = LONG_DISTANCE_TASKS.copy()
        random.shuffle(shuffled_tasks)
        
        # Get day of month to select different tasks each day
        day_of_month = current_date.day
        
        # Calculate starting index based on day (ensures 3 different tasks per day)
        # Use modulo to wrap around if we exceed the list length
        start_index = (day_of_month * 3) % len(shuffled_tasks)
        
        # Get tasks for today
        selected_task_descriptions = []
        for i in range(count):
            task_index = (start_index + i) % len(shuffled_tasks)
            selected_task_descriptions.append(shuffled_tasks[task_index])
        
        # Convert to the expected task format
        tasks = []
        for i, description in enumerate(selected_task_descriptions):
            task = {
                "id": f"long_distance_{current_date.strftime('%Y%m%d')}_{i+1}",
                "title": description,
                "description": description,
                "category": "Communication",  # Default category for Long Distance tasks
                "difficulty": "very_easy",
                "estimated_time_minutes": 5,
                "points": 5,
                "tips": f"Perfect for long-distance couples! {description}",
                "is_physical": False,
                "generation_metadata": {
                    "model": "pre_written_long_distance",
                    "mode": "LONG_DISTANCE", 
                    "generated_at": current_date.isoformat(),
                    "task_source": "curated_long_distance_list",
                    "rotation_seed": seed,
                    "day_of_month": day_of_month
                }
            }
            tasks.append(task)
        
        return tasks

    def _get_same_home_tasks(self, count: int = 3) -> List[Dict[str, Any]]:
        """Get pre-written Same Home tasks that rotate monthly"""
        from datetime import datetime
        import random
        import hashlib
        
        current_date = datetime.now()
        # Create monthly seed (changes every month)
        seed_string = f"{current_date.year}-{current_date.month}-same_home"
        seed = int(hashlib.md5(seed_string.encode()).hexdigest(), 16) % (2**32)
        random.seed(seed)
        
        # Shuffle tasks based on the monthly seed
        shuffled_tasks = SAME_HOME_TASKS.copy()
        random.shuffle(shuffled_tasks)
        
        # Get day of month for task selection (1-based indexing)
        day_of_month = current_date.day
        
        # Select tasks for today based on day of month
        # Use modulo to cycle through shuffled tasks
        tasks = []
        for i in range(count):
            task_index = (day_of_month - 1 + i) % len(shuffled_tasks)
            description = shuffled_tasks[task_index]
            
            # Generate unique task ID
            task_id = f"sh_{hashlib.md5(f'{description}_{current_date.date()}'.encode()).hexdigest()[:8]}"
            
            task = {
                "id": task_id,
                "title": description,
                "description": description,
                "category": "Communication",
                "difficulty": "very_easy",
                "estimated_time_minutes": 5,
                "points": 5,
                "tips": f"Perfect for couples living together! {description}",
                "is_physical": False,
                "generation_metadata": {
                    "model": "pre_written_same_home",
                    "mode": "SAME_HOME", 
                    "generated_at": current_date.isoformat(),
                    "task_source": "curated_same_home_list",
                    "rotation_seed": seed,
                    "day_of_month": day_of_month
                }
            }
            tasks.append(task)
        
        return tasks

    def _get_daily_meetup_weekly_tasks(self, count: int = 1) -> List[Dict[str, Any]]:
        """Get pre-written Daily Meetup weekly tasks that rotate yearly"""
        from datetime import datetime
        import random
        import hashlib
        
        current_date = datetime.now()
        # Create yearly seed (changes every year)
        seed_string = f"{current_date.year}-daily_meetup_weekly"
        seed = int(hashlib.md5(seed_string.encode()).hexdigest(), 16) % (2**32)
        random.seed(seed)
        
        # Shuffle tasks based on the yearly seed
        shuffled_tasks = DAILY_MEETUP_WEEKLY_TASKS.copy()
        random.shuffle(shuffled_tasks)
        
        # Get week of year for task selection (1-based indexing)
        week_of_year = current_date.isocalendar()[1]
        
        # Select tasks for this week based on week of year
        # Use modulo to cycle through shuffled tasks
        tasks = []
        for i in range(count):
            task_index = (week_of_year - 1 + i) % len(shuffled_tasks)
            description = shuffled_tasks[task_index]
            
            # Generate unique task ID
            task_id = f"dmw_{hashlib.md5(f'{description}_{current_date.date()}'.encode()).hexdigest()[:8]}"
            
            task = {
                "id": task_id,
                "title": description,
                "description": description,
                "category": "PhysicalActivity",
                "difficulty": "easy",
                "estimated_time_minutes": 90,
                "points": 25,
                "tips": f"Perfect weekly activity for couples meeting daily! {description}",
                "is_physical": True,
                "generation_metadata": {
                    "model": "pre_written_daily_meetup_weekly",
                    "mode": "DAILY_IRL", 
                    "generated_at": current_date.isoformat(),
                    "task_source": "curated_daily_meetup_weekly_list",
                    "rotation_seed": seed,
                    "week_of_year": week_of_year
                }
            }
            tasks.append(task)
        
        return tasks

    def _get_long_distance_weekly_tasks(self, count: int = 1) -> List[Dict[str, Any]]:
        """Get pre-written Long Distance weekly tasks that rotate yearly"""
        from datetime import datetime
        import random
        import hashlib
        
        current_date = datetime.now()
        # Create yearly seed (changes every year)
        seed_string = f"{current_date.year}-long_distance_weekly"
        seed = int(hashlib.md5(seed_string.encode()).hexdigest(), 16) % (2**32)
        random.seed(seed)
        
        # Shuffle tasks based on the yearly seed
        shuffled_tasks = LONG_DISTANCE_WEEKLY_TASKS.copy()
        random.shuffle(shuffled_tasks)
        
        # Get week of year for task selection (1-based indexing)
        week_of_year = current_date.isocalendar()[1]
        
        # Select tasks for this week based on week of year
        # Use modulo to cycle through shuffled tasks
        tasks = []
        for i in range(count):
            task_index = (week_of_year - 1 + i) % len(shuffled_tasks)
            description = shuffled_tasks[task_index]
            
            # Generate unique task ID
            task_id = f"ldw_{hashlib.md5(f'{description}_{current_date.date()}'.encode()).hexdigest()[:8]}"
            
            task = {
                "id": task_id,
                "title": description,
                "description": description,
                "category": "PhysicalActivity",
                "difficulty": "easy",
                "estimated_time_minutes": 90,
                "points": 25,
                "tips": f"Perfect weekly activity for long-distance couples! {description}",
                "is_physical": True,
                "generation_metadata": {
                    "model": "pre_written_long_distance_weekly",
                    "mode": "LONG_DISTANCE", 
                    "generated_at": current_date.isoformat(),
                    "task_source": "curated_long_distance_weekly_list",
                    "rotation_seed": seed,
                    "week_of_year": week_of_year
                }
            }
            tasks.append(task)
        
        return tasks

    def _get_same_home_weekly_tasks(self, count: int = 1) -> List[Dict[str, Any]]:
        """Get pre-written Same Home weekly tasks that rotate yearly"""
        from datetime import datetime
        import random
        import hashlib
        
        current_date = datetime.now()
        # Create yearly seed (changes every year)
        seed_string = f"{current_date.year}-same_home_weekly"
        seed = int(hashlib.md5(seed_string.encode()).hexdigest(), 16) % (2**32)
        random.seed(seed)
        
        # Shuffle tasks based on the yearly seed
        shuffled_tasks = SAME_HOME_WEEKLY_TASKS.copy()
        random.shuffle(shuffled_tasks)
        
        # Get week of year for task selection (1-based indexing)
        week_of_year = current_date.isocalendar()[1]
        
        # Select tasks for this week based on week of year
        # Use modulo to cycle through shuffled tasks
        tasks = []
        for i in range(count):
            task_index = (week_of_year - 1 + i) % len(shuffled_tasks)
            description = shuffled_tasks[task_index]
            
            # Generate unique task ID
            task_id = f"shw_{hashlib.md5(f'{description}_{current_date.date()}'.encode()).hexdigest()[:8]}"
            
            task = {
                "id": task_id,
                "title": description,
                "description": description,
                "category": "PhysicalActivity",
                "difficulty": "easy",
                "estimated_time_minutes": 90,
                "points": 25,
                "tips": f"Perfect weekly activity for couples living together! {description}",
                "is_physical": True,
                "generation_metadata": {
                    "model": "pre_written_same_home_weekly",
                    "mode": "SAME_HOME", 
                    "generated_at": current_date.isoformat(),
                    "task_source": "curated_same_home_weekly_list",
                    "rotation_seed": seed,
                    "week_of_year": week_of_year
                }
            }
            tasks.append(task)
        
        return tasks

    def get_daily_messages(self, relationship_mode: str, messages_per_category: int = 3) -> List[Dict[str, Any]]:
        """Get 3 messages per category for specific relationship mode with DAILY rotation (450 total messages, 15 per day)"""
        from datetime import datetime
        import random
        import hashlib
        
        current_date = datetime.now()
        
        # Select appropriate message set based on relationship mode
        if relationship_mode == "DAILY_IRL":
            message_data = DAILY_MEETUP_MESSAGES
            mode_prefix = "dm"
        elif relationship_mode == "LONG_DISTANCE":
            message_data = LONG_DISTANCE_MESSAGES
            mode_prefix = "ld"
        elif relationship_mode == "SAME_HOME":
            message_data = SAME_HOME_MESSAGES
            mode_prefix = "sh"
        else:
            # For other modes, return empty list or use default
            return []
        
        # Create DAILY seed (changes every day)
        seed_string = f"{current_date.year}-{current_date.month}-{current_date.day}-{relationship_mode}-messages"
        seed = int(hashlib.md5(seed_string.encode()).hexdigest(), 16) % (2**32)
        random.seed(seed)
        
        # Calculate day of year for 30-day rotation cycle
        day_of_year = current_date.timetuple().tm_yday
        rotation_day = day_of_year % 30  # 30-day cycle (0-29)
        
        # Categories in order: good_morning, good_night, love_confession, apology, funny_hinglish
        categories = list(message_data.keys())
        
        # Generate 3 messages for EACH category (total 15 messages per day)
        all_messages = []
        
        for category_index, category in enumerate(categories):
            category_messages = message_data[category]
            
            # Use all available messages (90 per category) for daily rotation
            available_messages = category_messages[:90] if len(category_messages) >= 90 else category_messages
            
            for i in range(messages_per_category):
                # Daily rotation: each day shows different 3 messages per category
                # Calculate message index based on rotation day and message position
                base_index = (rotation_day * messages_per_category + i) % len(available_messages)
                message_index = (base_index + category_index * 7) % len(available_messages)  # Different offset per category
                message_text = available_messages[message_index]
                
                # Generate unique message ID
                message_id = f"{mode_prefix}_{category}_{i}_{hashlib.md5(f'{message_text}_{current_date.date()}'.encode()).hexdigest()[:8]}"
                
                message = {
                    "id": message_id,
                    "text": message_text,
                    "category": category,
                    "relationship_mode": relationship_mode,
                    "generated_at": current_date.isoformat(),
                    "metadata": {
                        "rotation_type": "daily",
                        "rotation_seed": seed,
                        "day_of_year": day_of_year,
                        "rotation_day": rotation_day,
                        "category_index": category_index,
                        "message_index": message_index,
                        "messages_per_category": messages_per_category,
                        "total_messages_per_month": 450,
                        "messages_per_day": 15
                    }
                }
                all_messages.append(message)
        
        return all_messages

    async def generate_daily_tasks(
        self,
        relationship_mode: str,
        count: int = 3,
        user_profile: Optional[Dict[str, Any]] = None,
        partner_profile: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Generate daily tasks for a specific relationship mode"""
        
        # Check if this is Daily IRL (Daily Meetup) mode - use pre-written tasks
        if relationship_mode == "DAILY_IRL":
            return self._get_daily_meetup_tasks(count)
        
        # Check if this is Long Distance mode - use pre-written tasks
        if relationship_mode == "LONG_DISTANCE":
            return self._get_long_distance_tasks(count)
        
        # Check if this is Same Home mode - use pre-written tasks  
        if relationship_mode == "SAME_HOME":
            return self._get_same_home_tasks(count)
        
        # For other modes, use AI generation
        prompt = self._build_task_prompt(
            task_type="daily",
            relationship_mode=relationship_mode,
            count=count,
            user_profile=user_profile,
            partner_profile=partner_profile
        )
        
        return await self._generate_tasks(prompt, points=5)
    
    async def generate_weekly_tasks(
        self,
        relationship_mode: str,
        count: int = 1,
        user_profile: Optional[Dict[str, Any]] = None,
        partner_profile: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Generate weekly tasks for a specific relationship mode"""
        
        # Check if this is Daily IRL (Daily Meetup) mode - use pre-written weekly tasks
        if relationship_mode == "DAILY_IRL":
            return self._get_daily_meetup_weekly_tasks(count)
        
        # Check if this is Long Distance mode - use pre-written weekly tasks
        if relationship_mode == "LONG_DISTANCE":
            return self._get_long_distance_weekly_tasks(count)
        
        # Check if this is Same Home mode - use pre-written weekly tasks
        if relationship_mode == "SAME_HOME":
            return self._get_same_home_weekly_tasks(count)
        
        # For other modes, use AI generation
        prompt = self._build_task_prompt(
            task_type="weekly",
            relationship_mode=relationship_mode,
            count=count,
            user_profile=user_profile,
            partner_profile=partner_profile
        )
        
        return await self._generate_tasks(prompt, points=25)
    
    def _build_task_prompt(
        self,
        task_type: str,
        relationship_mode: str,
        count: int,
        user_profile: Optional[Dict[str, Any]],
        partner_profile: Optional[Dict[str, Any]]
    ) -> str:
        """Build the prompt for task generation"""
        
        mode_description = RELATIONSHIP_MODES.get(relationship_mode, "Unknown relationship mode")
        
        # Build context from profiles
        context = f"Generate {count} {task_type} relationship tasks for a couple in {relationship_mode} mode ({mode_description}).\n\n"
        
        # Add personal context if available and user consented
        if user_profile and partner_profile:
            partner_name = partner_profile.get("name", "partner")
            partner_prefs = partner_profile.get("favorite_food", "")
            anniversary = partner_profile.get("anniversary_date", "")
            
            if partner_name and partner_name != "partner":
                context += f"Partner's name: {partner_name}\n"
            if partner_prefs:
                context += f"Partner's favorite food: {partner_prefs}\n"
            if anniversary:
                context += f"Relationship anniversary: {anniversary}\n"
            
            context += "\n"
        
        # Add task type specific instructions
        if task_type == "daily":
            context += "Generate 3 DAILY tasks that:\n"
            context += "- Take 2-5 minutes maximum (VERY EASY)\n"
            context += "- Require NO PURCHASE\n"
            context += "- Award 5 points each\n"
            context += "- Use categories: Communication, ThoughtfulGesture, MicroActivity\n"
            context += "- Examples: Send sweet text, give 20-second hug, ask about their day\n"
        else:  # weekly
            context += "Generate 1 WEEKLY task that:\n"
            context += "- Must be PHYSICAL ACTION (meet, deliver, do together, physical activity)\n"
            context += "- Must be safe to execute\n"
            context += "- Take 30-120 minutes\n"
            context += "- Award 25 points\n"
            context += "- Use category: PhysicalActivity\n"
            context += "- Set is_physical: true\n"
            context += "- Examples: Cook meal together, take walk, clean together, deliver surprise\n"
        context += f"Relationship mode context: {mode_description}\n\n"
        context += "Return ONLY the JSON response with the tasks array."
        
        return context
    
    async def _generate_tasks(self, prompt: str, points: int) -> List[Dict[str, Any]]:
        """Generate tasks using AI and parse the response"""
        
        try:
            # Create user message
            user_message = UserMessage(text=prompt)
            
            # Get response from AI
            response = await self.chat.send_message(user_message)
            
            # Parse JSON response
            task_data = json.loads(response)
            tasks = task_data.get("tasks", [])
            
            # Enhance tasks with metadata
            enhanced_tasks = []
            for i, task in enumerate(tasks):
                enhanced_task = {
                    "id": self._generate_task_id(task["title"]),
                    "title": task["title"],
                    "description": task.get("description", task["title"]),
                    "category": task.get("category", "Communication"),
                    "points": points,
                    "estimated_time_minutes": task.get("estimated_time_minutes", 5 if points == 5 else 60),
                    "difficulty": task.get("difficulty", DAILY_DIFFICULTY if points == 5 else WEEKLY_DIFFICULTY),
                    "tips": task.get("tips", ""),
                    "is_physical": task.get("is_physical", False),
                    "generation_metadata": {
                        "generated_at": datetime.utcnow(),
                        "ai_model": "gpt-4o",
                        "prompt_hash": self._hash_prompt(prompt),
                        "version": "2.0"
                    }
                }
                enhanced_tasks.append(enhanced_task)
            
            return enhanced_tasks
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse AI response as JSON: {e}")
            return self._get_fallback_tasks(points)
        except Exception as e:
            print(f"AI task generation failed: {e}")
            return self._get_fallback_tasks(points)
    
    def _generate_task_id(self, title: str) -> str:
        """Generate unique task ID based on title"""
        return f"ai_{hashlib.md5(title.encode()).hexdigest()[:8]}"
    
    def _hash_prompt(self, prompt: str) -> str:
        """Generate hash of prompt for metadata"""
        return hashlib.sha256(prompt.encode()).hexdigest()[:16]
    
    def _get_fallback_tasks(self, points: int) -> List[Dict[str, Any]]:
        """Fallback tasks if AI generation fails"""
        
        if points == 5:  # Daily tasks (3 very easy tasks)
            fallback_tasks = [
                {
                    "id": "fallback_daily_1",
                    "title": "Send your partner a loving text message",
                    "description": "Send a sweet message expressing your love or appreciation",
                    "category": "Communication", 
                    "points": 5,
                    "estimated_time_minutes": 3,
                    "difficulty": "very_easy",
                    "is_physical": False,
                    "tips": "Be specific about what you appreciate about them today"
                },
                {
                    "id": "fallback_daily_2", 
                    "title": "Give your partner a warm 20-second hug",
                    "description": "Share a meaningful physical connection with a long, warm hug",
                    "category": "ThoughtfulGesture",
                    "points": 5,
                    "estimated_time_minutes": 2,
                    "difficulty": "very_easy",
                    "is_physical": False,
                    "tips": "Hold the hug for at least 20 seconds and focus on the moment"
                },
                {
                    "id": "fallback_daily_3",
                    "title": "Ask 'What was the best part of your day?'",
                    "description": "Show genuine interest in your partner's daily experiences",
                    "category": "Communication",
                    "points": 5,
                    "estimated_time_minutes": 5,
                    "difficulty": "very_easy",
                    "is_physical": False,
                    "tips": "Listen actively and ask follow-up questions to show you care"
                }
            ]
        else:  # Weekly tasks (1 physical task)
            fallback_tasks = [
                {
                    "id": "fallback_weekly_1",
                    "title": "Cook a meal together this week",
                    "description": "Plan and prepare a meal together as a team",
                    "category": "PhysicalActivity",
                    "points": 25,
                    "estimated_time_minutes": 90,
                    "difficulty": "easy",
                    "is_physical": True,
                    "tips": "Choose a recipe you both enjoy and divide the cooking tasks"
                }
            ]
        
        # Add generation metadata to fallback tasks
        for task in fallback_tasks:
            task["generation_metadata"] = {
                "generated_at": datetime.utcnow(),
                "ai_model": "fallback",
                "prompt_hash": "fallback",
                "version": "1.0"
            }
        
        return fallback_tasks

# Global instance
ai_task_generator = AITaskGenerator()

# Convenience functions
async def generate_daily_tasks_for_mode(
    relationship_mode: str,
    count: int = 3,
    user_profile: Optional[Dict[str, Any]] = None,
    partner_profile: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """Generate daily tasks for a relationship mode"""
    return await ai_task_generator.generate_daily_tasks(
        relationship_mode, count, user_profile, partner_profile
    )

async def generate_weekly_tasks_for_mode(
    relationship_mode: str,
    count: int = 1,
    user_profile: Optional[Dict[str, Any]] = None,
    partner_profile: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """Generate weekly tasks for a relationship mode"""
    return await ai_task_generator.generate_weekly_tasks(
        relationship_mode, count, user_profile, partner_profile
    )