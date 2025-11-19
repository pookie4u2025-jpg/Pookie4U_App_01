"""
Relationship-Specific Task Database
Contains 90 daily tasks for each relationship type (Live Together, Meet Daily, Long Distance)
Plus weekly tasks tailored to each context
"""

# ============================================================================
# LIVE TOGETHER (LT) - DAILY TASKS (90 tasks)
# Focus: Acts of Service, Physical Touch, Preventing relationship drift
# ============================================================================

LIVE_TOGETHER_DAILY_TASKS = [
    # Acts of Service (Hidden) - 30 tasks
    {"text": "Load the dishwasher before she asks", "category": "Acts of Service"},
    {"text": "Fold the laundry you left out", "category": "Acts of Service"},
    {"text": "Make the bed before she wakes up", "category": "Acts of Service"},
    {"text": "Prep her favorite breakfast without being asked", "category": "Acts of Service"},
    {"text": "Clean the bathroom counter and sink", "category": "Acts of Service"},
    {"text": "Take out the trash and recycling", "category": "Acts of Service"},
    {"text": "Vacuum the living room without mentioning it", "category": "Acts of Service"},
    {"text": "Organize the cluttered kitchen counter", "category": "Acts of Service"},
    {"text": "Fill up her car with gas", "category": "Acts of Service"},
    {"text": "Water the plants she's been tending", "category": "Acts of Service"},
    {"text": "Iron her outfit for tomorrow", "category": "Acts of Service"},
    {"text": "Unload the groceries and put everything away", "category": "Acts of Service"},
    {"text": "Fix that squeaky door she mentioned", "category": "Acts of Service"},
    {"text": "Clean out the fridge and toss expired items", "category": "Acts of Service"},
    {"text": "Replace the toilet paper roll before it runs out", "category": "Acts of Service"},
    {"text": "Sweep the kitchen floor after dinner", "category": "Acts of Service"},
    {"text": "Organize the shoe rack by the door", "category": "Acts of Service"},
    {"text": "Change the bed sheets to fresh ones", "category": "Acts of Service"},
    {"text": "Wipe down all kitchen appliances", "category": "Acts of Service"},
    {"text": "Sort through the mail and recycle junk", "category": "Acts of Service"},
    {"text": "Clean the windows in the living room", "category": "Acts of Service"},
    {"text": "Dust the shelves and decorations", "category": "Acts of Service"},
    {"text": "Take her shoes to get repaired", "category": "Acts of Service"},
    {"text": "Prep ingredients for tonight's dinner", "category": "Acts of Service"},
    {"text": "Organize the medicine cabinet", "category": "Acts of Service"},
    {"text": "Clean the stovetop after cooking", "category": "Acts of Service"},
    {"text": "Fold and put away her clean laundry", "category": "Acts of Service"},
    {"text": "Scrub the bathtub and shower", "category": "Acts of Service"},
    {"text": "Empty the dishwasher and put dishes away", "category": "Acts of Service"},
    {"text": "Pack her lunch for tomorrow", "category": "Acts of Service"},
    
    # Physical Touch / Connection - 30 tasks
    {"text": "Give a 10-second non-sexual hug when you both get home", "category": "Physical Touch"},
    {"text": "Offer a 5-minute foot rub while watching TV", "category": "Physical Touch"},
    {"text": "Hold her hand for the entire walk around the block", "category": "Physical Touch"},
    {"text": "Give her a shoulder massage for 3 minutes", "category": "Physical Touch"},
    {"text": "Cuddle on the couch for 15 minutes without phones", "category": "Physical Touch"},
    {"text": "Kiss her forehead when she's reading or working", "category": "Physical Touch"},
    {"text": "Give her a back scratch before bedtime", "category": "Physical Touch"},
    {"text": "Slow dance with her in the kitchen for one song", "category": "Physical Touch"},
    {"text": "Brush her hair gently for a few minutes", "category": "Physical Touch"},
    {"text": "Hold her close for 30 seconds without saying anything", "category": "Physical Touch"},
    {"text": "Give her a gentle head massage", "category": "Physical Touch"},
    {"text": "Spoon her in bed for 10 minutes", "category": "Physical Touch"},
    {"text": "Hold her hand while you both watch TV", "category": "Physical Touch"},
    {"text": "Give her a playful tickle or squeeze", "category": "Physical Touch"},
    {"text": "Wrap your arms around her from behind while she's cooking", "category": "Physical Touch"},
    {"text": "Give her a gentle neck massage", "category": "Physical Touch"},
    {"text": "Hold hands during dinner at home", "category": "Physical Touch"},
    {"text": "Give her a quick kiss on the cheek unexpectedly", "category": "Physical Touch"},
    {"text": "Sit close to her on the couch, legs touching", "category": "Physical Touch"},
    {"text": "Play with her hair while she rests her head on you", "category": "Physical Touch"},
    {"text": "Give her a loving squeeze when passing by", "category": "Physical Touch"},
    {"text": "Kiss the back of her neck gently", "category": "Physical Touch"},
    {"text": "Hug her for 20 seconds without letting go", "category": "Physical Touch"},
    {"text": "Touch her arm gently when talking", "category": "Physical Touch"},
    {"text": "Give her butterfly kisses on her face", "category": "Physical Touch"},
    {"text": "Rest your hand on her thigh while sitting together", "category": "Physical Touch"},
    {"text": "Give her an Eskimo kiss (rub noses)", "category": "Physical Touch"},
    {"text": "Massage her temples gently", "category": "Physical Touch"},
    {"text": "Hold her face in your hands and look into her eyes", "category": "Physical Touch"},
    {"text": "Give her a loving pat on the back", "category": "Physical Touch"},
    
    # Words of Affirmation (Proximity) - 30 tasks
    {"text": "Leave a note on her side of the bed", "category": "Words of Affirmation"},
    {"text": "Stick a kind message on the bathroom mirror", "category": "Words of Affirmation"},
    {"text": "Tell her one specific thing you love about her", "category": "Words of Affirmation"},
    {"text": "Compliment her appearance when she walks into the room", "category": "Words of Affirmation"},
    {"text": "Thank her for something she did today", "category": "Words of Affirmation"},
    {"text": "Tell her you're proud of her accomplishments", "category": "Words of Affirmation"},
    {"text": "Whisper 'I love you' in her ear unexpectedly", "category": "Words of Affirmation"},
    {"text": "Leave a love note in her purse or bag", "category": "Words of Affirmation"},
    {"text": "Tell her she makes your life better", "category": "Words of Affirmation"},
    {"text": "Compliment her cooking or meal preparation", "category": "Words of Affirmation"},
    {"text": "Say 'You're beautiful' when she least expects it", "category": "Words of Affirmation"},
    {"text": "Thank her for being patient with you", "category": "Words of Affirmation"},
    {"text": "Write 'I love you' on the steamy bathroom mirror", "category": "Words of Affirmation"},
    {"text": "Tell her you appreciate her effort in the relationship", "category": "Words of Affirmation"},
    {"text": "Compliment her smile when she laughs", "category": "Words of Affirmation"},
    {"text": "Leave a sticky note in her lunch", "category": "Words of Affirmation"},
    {"text": "Tell her you're lucky to live with her", "category": "Words of Affirmation"},
    {"text": "Compliment her outfit choice for the day", "category": "Words of Affirmation"},
    {"text": "Say 'Thank you for being you' genuinely", "category": "Words of Affirmation"},
    {"text": "Tell her one thing she did that made your day better", "category": "Words of Affirmation"},
    {"text": "Leave a love note on the coffee maker", "category": "Words of Affirmation"},
    {"text": "Tell her you miss her when she's in another room", "category": "Words of Affirmation"},
    {"text": "Compliment her intelligence or problem-solving", "category": "Words of Affirmation"},
    {"text": "Say 'You're my favorite person'", "category": "Words of Affirmation"},
    {"text": "Tell her she smells amazing", "category": "Words of Affirmation"},
    {"text": "Leave a note in her shoe she'll find in the morning", "category": "Words of Affirmation"},
    {"text": "Tell her you love the way she takes care of things", "category": "Words of Affirmation"},
    {"text": "Compliment her laugh or sense of humor", "category": "Words of Affirmation"},
    {"text": "Say 'I'm grateful for you' before bed", "category": "Words of Affirmation"},
    {"text": "Tell her one specific reason why you love her", "category": "Words of Affirmation"},
]

# ============================================================================
# MEET DAILY (MD) - DAILY TASKS (90 tasks)
# Focus: Planning/Anticipation, Small gifts, Quality listening
# ============================================================================

MEET_DAILY_TASKS = [
    # Planning/Anticipation - 30 tasks
    {"text": "Send a message asking what she's looking forward to seeing when we meet", "category": "Planning"},
    {"text": "Text her the exact time and place you'll pick her up", "category": "Planning"},
    {"text": "Ask what she wants to do when you meet today", "category": "Planning"},
    {"text": "Send her a countdown message 'Can't wait to see you in X hours'", "category": "Planning"},
    {"text": "Ask if there's anything she needs you to bring", "category": "Planning"},
    {"text": "Text her a specific activity plan for today", "category": "Planning"},
    {"text": "Send 'I'm excited to see your face today'", "category": "Planning"},
    {"text": "Ask her what she's wearing so you can match vibes", "category": "Planning"},
    {"text": "Send her a photo of something that reminded you of her", "category": "Planning"},
    {"text": "Ask if she wants to try something new together today", "category": "Planning"},
    {"text": "Text 'What do you want to talk about when we meet?'", "category": "Planning"},
    {"text": "Send her a playlist for your time together", "category": "Planning"},
    {"text": "Ask if she's had a good day so far", "category": "Planning"},
    {"text": "Send 'I have a surprise for you later'", "category": "Planning"},
    {"text": "Ask what she's craving for food when you meet", "category": "Planning"},
    {"text": "Text her your ETA with a cute emoji", "category": "Planning"},
    {"text": "Send 'I can't stop thinking about seeing you'", "category": "Planning"},
    {"text": "Ask if she wants to go somewhere new together", "category": "Planning"},
    {"text": "Send a morning text with your plans for the day", "category": "Planning"},
    {"text": "Ask if there's anything stressing her you can help with", "category": "Planning"},
    {"text": "Text 'Name one thing you want from today'", "category": "Planning"},
    {"text": "Send her options for activities and let her choose", "category": "Planning"},
    {"text": "Ask if she wants a chill day or an adventure", "category": "Planning"},
    {"text": "Text 'What's one thing you'd love to do with me?'", "category": "Planning"},
    {"text": "Send 'I'm bringing your favorite thing today'", "category": "Planning"},
    {"text": "Ask if she needs to vent about anything", "category": "Planning"},
    {"text": "Text 'Today is all about you'", "category": "Planning"},
    {"text": "Send 'Pick a movie for later, I'm down for anything'", "category": "Planning"},
    {"text": "Ask what would make her smile right now", "category": "Planning"},
    {"text": "Text 'Can't wait to hear about your day'", "category": "Planning"},
    
    # Small Gift / Surprise - 30 tasks
    {"text": "Pick up her favorite coffee on the way", "category": "Small Gifts"},
    {"text": "Bring her favorite snack when you meet", "category": "Small Gifts"},
    {"text": "Buy a single flower to give her", "category": "Small Gifts"},
    {"text": "Bring her a small dessert she loves", "category": "Small Gifts"},
    {"text": "Get her favorite drink without her asking", "category": "Small Gifts"},
    {"text": "Bring a handwritten note to give in person", "category": "Small Gifts"},
    {"text": "Pick up a magazine or book she mentioned", "category": "Small Gifts"},
    {"text": "Bring her a small bouquet", "category": "Small Gifts"},
    {"text": "Get her a cute keychain or trinket", "category": "Small Gifts"},
    {"text": "Bring her favorite candy or chocolate", "category": "Small Gifts"},
    {"text": "Buy a silly card and write something sweet", "category": "Small Gifts"},
    {"text": "Bring her a small plant or succulent", "category": "Small Gifts"},
    {"text": "Get her a lipstick or nail polish in her favorite color", "category": "Small Gifts"},
    {"text": "Bring her a cozy pair of socks", "category": "Small Gifts"},
    {"text": "Get her a scented candle she'd like", "category": "Small Gifts"},
    {"text": "Bring her favorite ice cream flavor", "category": "Small Gifts"},
    {"text": "Buy a small piece of jewelry under $20", "category": "Small Gifts"},
    {"text": "Bring her a funny mug with a sweet message", "category": "Small Gifts"},
    {"text": "Get her a scratch-off lottery ticket for fun", "category": "Small Gifts"},
    {"text": "Bring her a cute hair accessory", "category": "Small Gifts"},
    {"text": "Buy her favorite juice or smoothie", "category": "Small Gifts"},
    {"text": "Get her a small notebook or journal", "category": "Small Gifts"},
    {"text": "Bring her a face mask or skincare item", "category": "Small Gifts"},
    {"text": "Buy her a cute stuffed animal", "category": "Small Gifts"},
    {"text": "Bring her favorite bakery treat", "category": "Small Gifts"},
    {"text": "Get her a fun phone case or charm", "category": "Small Gifts"},
    {"text": "Bring her a bottle of her favorite perfume sample", "category": "Small Gifts"},
    {"text": "Buy her a scrunchie in her favorite color", "category": "Small Gifts"},
    {"text": "Bring her a packet of her favorite tea", "category": "Small Gifts"},
    {"text": "Get her a cute sticker or temporary tattoo", "category": "Small Gifts"},
    
    # Quality Listening - 30 tasks
    {"text": "Ask a specific follow-up question about something she mentioned yesterday", "category": "Quality Listening"},
    {"text": "Listen to her talk about her day for 10 minutes without interrupting", "category": "Quality Listening"},
    {"text": "Ask 'How did that thing you were worried about turn out?'", "category": "Quality Listening"},
    {"text": "Remember and bring up something she's excited about", "category": "Quality Listening"},
    {"text": "Ask her opinion on something important to you", "category": "Quality Listening"},
    {"text": "Listen to her vent without offering solutions", "category": "Quality Listening"},
    {"text": "Ask 'What was the best part of your day?'", "category": "Quality Listening"},
    {"text": "Recall a story she told and ask for an update", "category": "Quality Listening"},
    {"text": "Ask about her friends or family by name", "category": "Quality Listening"},
    {"text": "Listen to her talk about her dreams and goals", "category": "Quality Listening"},
    {"text": "Ask 'What's been on your mind lately?'", "category": "Quality Listening"},
    {"text": "Remember a small detail she mentioned weeks ago", "category": "Quality Listening"},
    {"text": "Ask how she's really feeling, not just 'fine'", "category": "Quality Listening"},
    {"text": "Listen to her describe her ideal day", "category": "Quality Listening"},
    {"text": "Ask about a hobby or interest she's passionate about", "category": "Quality Listening"},
    {"text": "Remember and follow up on her work project", "category": "Quality Listening"},
    {"text": "Ask 'What can I do to support you right now?'", "category": "Quality Listening"},
    {"text": "Listen to her fears or worries without judgment", "category": "Quality Listening"},
    {"text": "Ask about her childhood memories", "category": "Quality Listening"},
    {"text": "Remember the name of her coworker she talks about", "category": "Quality Listening"},
    {"text": "Ask 'What made you laugh today?'", "category": "Quality Listening"},
    {"text": "Listen to her talk about a book or show she loves", "category": "Quality Listening"},
    {"text": "Ask about her future plans and really listen", "category": "Quality Listening"},
    {"text": "Remember something she wanted to try and suggest it", "category": "Quality Listening"},
    {"text": "Ask 'What's something you're proud of this week?'", "category": "Quality Listening"},
    {"text": "Listen to her talk about her favorite memories together", "category": "Quality Listening"},
    {"text": "Ask about something she's learning or studying", "category": "Quality Listening"},
    {"text": "Remember her favorite things and surprise her with them", "category": "Quality Listening"},
    {"text": "Ask 'What's something you'd like to change?'", "category": "Quality Listening"},
    {"text": "Listen to her describe her perfect date", "category": "Quality Listening"},
]

# ============================================================================
# LONG DISTANCE (LD) - DAILY TASKS (90 tasks)
# Focus: Visual connection, Shared activities, Planning future
# ============================================================================

LONG_DISTANCE_DAILY_TASKS = [
    # Visual Connection - 30 tasks
    {"text": "Send a 5-10 second video message showing what you're doing", "category": "Visual Connection"},
    {"text": "Send a selfie with a cute caption", "category": "Visual Connection"},
    {"text": "Share a photo of something that reminded you of her", "category": "Visual Connection"},
    {"text": "Send a video of your view right now", "category": "Visual Connection"},
    {"text": "Share a photo of your meal with 'Wish you were here'", "category": "Visual Connection"},
    {"text": "Send a morning video saying good morning", "category": "Visual Connection"},
    {"text": "Share a photo of something funny you saw", "category": "Visual Connection"},
    {"text": "Send a video tour of where you are", "category": "Visual Connection"},
    {"text": "Share a photo of the sunset or sunrise", "category": "Visual Connection"},
    {"text": "Send a video of you saying 'I miss you'", "category": "Visual Connection"},
    {"text": "Share a photo of your workspace or environment", "category": "Visual Connection"},
    {"text": "Send a video of something interesting happening", "category": "Visual Connection"},
    {"text": "Share a photo of you wearing something she bought", "category": "Visual Connection"},
    {"text": "Send a video message answering a question she asked", "category": "Visual Connection"},
    {"text": "Share a photo of a place you want to take her", "category": "Visual Connection"},
    {"text": "Send a video of your pet or something cute", "category": "Visual Connection"},
    {"text": "Share a photo with a hand-written sign for her", "category": "Visual Connection"},
    {"text": "Send a video of you blowing her a kiss", "category": "Visual Connection"},
    {"text": "Share a photo of your current mood/expression", "category": "Visual Connection"},
    {"text": "Send a video walkthrough of your day", "category": "Visual Connection"},
    {"text": "Share a photo from a memory you shared together", "category": "Visual Connection"},
    {"text": "Send a video lip-syncing to 'your song'", "category": "Visual Connection"},
    {"text": "Share a photo of the weather where you are", "category": "Visual Connection"},
    {"text": "Send a goodnight video before bed", "category": "Visual Connection"},
    {"text": "Share a photo of something new you tried", "category": "Visual Connection"},
    {"text": "Send a video saying 'I love you' in a creative way", "category": "Visual Connection"},
    {"text": "Share a photo of you at a place she'd recognize", "category": "Visual Connection"},
    {"text": "Send a video of a song you're listening to", "category": "Visual Connection"},
    {"text": "Share a photo of your outfit asking for her opinion", "category": "Visual Connection"},
    {"text": "Send a video message making her laugh", "category": "Visual Connection"},
    
    # Shared Activity - 30 tasks
    {"text": "Play an online game together for 30 minutes", "category": "Shared Activity"},
    {"text": "Watch a Netflix episode at the same time", "category": "Shared Activity"},
    {"text": "Start a book together and discuss the first chapter", "category": "Shared Activity"},
    {"text": "Cook the same meal and video call while eating", "category": "Shared Activity"},
    {"text": "Do a 15-minute workout video together on call", "category": "Shared Activity"},
    {"text": "Take a virtual museum tour together", "category": "Shared Activity"},
    {"text": "Play 20 questions over text or call", "category": "Shared Activity"},
    {"text": "Watch a movie together via screen share", "category": "Shared Activity"},
    {"text": "Play online Pictionary or drawing game", "category": "Shared Activity"},
    {"text": "Listen to a podcast episode together", "category": "Shared Activity"},
    {"text": "Do a 10-minute meditation together on video call", "category": "Shared Activity"},
    {"text": "Play Words With Friends or online Scrabble", "category": "Shared Activity"},
    {"text": "Create a shared Spotify playlist together", "category": "Shared Activity"},
    {"text": "Watch YouTube videos together and react", "category": "Shared Activity"},
    {"text": "Play online chess or checkers", "category": "Shared Activity"},
    {"text": "Do a virtual coffee date on video call", "category": "Shared Activity"},
    {"text": "Play online trivia or quiz together", "category": "Shared Activity"},
    {"text": "Read the same article and discuss it", "category": "Shared Activity"},
    {"text": "Play a mobile game together (Among Us, etc.)", "category": "Shared Activity"},
    {"text": "Do a photo challenge (send pics of same theme)", "category": "Shared Activity"},
    {"text": "Watch a TED talk together and discuss", "category": "Shared Activity"},
    {"text": "Play online card games (Uno, etc.)", "category": "Shared Activity"},
    {"text": "Do a virtual wine/coffee tasting together", "category": "Shared Activity"},
    {"text": "Create a vision board together online", "category": "Shared Activity"},
    {"text": "Play online Monopoly or board games", "category": "Shared Activity"},
    {"text": "Do a virtual dance class together", "category": "Shared Activity"},
    {"text": "Watch the sunrise/sunset together on call", "category": "Shared Activity"},
    {"text": "Play 'Would You Rather' for 20 minutes", "category": "Shared Activity"},
    {"text": "Create a bucket list together", "category": "Shared Activity"},
    {"text": "Do a virtual escape room together", "category": "Shared Activity"},
    
    # Planning Future - 30 tasks
    {"text": "Check calendar and propose a specific date for your next visit", "category": "Planning Future"},
    {"text": "Send a photo of a place you want to take her", "category": "Planning Future"},
    {"text": "Research flights or travel options for next meetup", "category": "Planning Future"},
    {"text": "Plan a specific activity for your next visit", "category": "Planning Future"},
    {"text": "Send her a countdown to when you'll see each other", "category": "Planning Future"},
    {"text": "Discuss where you'll live together someday", "category": "Planning Future"},
    {"text": "Look up restaurants for your next visit", "category": "Planning Future"},
    {"text": "Send her a vision of your future together", "category": "Planning Future"},
    {"text": "Plan a virtual anniversary celebration", "category": "Planning Future"},
    {"text": "Discuss closing the distance timeline", "category": "Planning Future"},
    {"text": "Send her a list of things you'll do when you're together", "category": "Planning Future"},
    {"text": "Research moving options and share findings", "category": "Planning Future"},
    {"text": "Plan a surprise for her next visit", "category": "Planning Future"},
    {"text": "Send 'X days until I see your face'", "category": "Planning Future"},
    {"text": "Discuss future vacation destinations", "category": "Planning Future"},
    {"text": "Plan what you'll eat together next time", "category": "Planning Future"},
    {"text": "Send her a booking confirmation for a visit", "category": "Planning Future"},
    {"text": "Talk about your dream home together", "category": "Planning Future"},
    {"text": "Research activities in each other's cities", "category": "Planning Future"},
    {"text": "Send 'I can't wait to hold you in X days'", "category": "Planning Future"},
    {"text": "Plan a couples' trip for the future", "category": "Planning Future"},
    {"text": "Discuss career moves to be closer", "category": "Planning Future"},
    {"text": "Send her hotel options for your visit", "category": "Planning Future"},
    {"text": "Talk about engagement or marriage timeline", "category": "Planning Future"},
    {"text": "Plan outfits to match for your next meetup", "category": "Planning Future"},
    {"text": "Send her a future milestone date (moving in, etc.)", "category": "Planning Future"},
    {"text": "Research neighborhoods where you'd live together", "category": "Planning Future"},
    {"text": "Plan a special date for your reunion", "category": "Planning Future"},
    {"text": "Send 'Just booked my ticket to see you'", "category": "Planning Future"},
    {"text": "Talk about your future family plans", "category": "Planning Future"},
]

# ============================================================================
# WEEKLY TASKS (for all relationship types)
# ============================================================================

WEEKLY_TASKS_LIVE_TOGETHER = [
    {"text": "Plan a takeout night where you both wear comfy clothes and watch a movie she picked. Zero phones allowed.", "category": "Quality Time"},
    {"text": "Cook her favorite meal from scratch with no shortcuts", "category": "Acts of Service"},
    {"text": "Plan a surprise date night at home with candles and music", "category": "Quality Time"},
    {"text": "Deep clean one room together and celebrate with her favorite dessert", "category": "Acts of Service"},
    {"text": "Give her a full 30-minute massage with lotion", "category": "Physical Touch"},
    {"text": "Plan a Sunday morning breakfast in bed", "category": "Acts of Service"},
    {"text": "Create a photo album of your favorite memories this month", "category": "Quality Time"},
    {"text": "Take her on a surprise picnic in the living room", "category": "Quality Time"},
    {"text": "Rearrange furniture together to refresh the space", "category": "Quality Time"},
    {"text": "Plan a game night with her favorite board games", "category": "Quality Time"},
]

WEEKLY_TASKS_MEET_DAILY = [
    {"text": "Book tickets to a local museum, event, or new lunch spot and send her the calendar invite", "category": "Experience Planning"},
    {"text": "Plan a surprise activity she's never done before", "category": "Experience Planning"},
    {"text": "Reserve a table at a restaurant she's been wanting to try", "category": "Experience Planning"},
    {"text": "Buy tickets to a movie, concert, or show she'd love", "category": "Experience Planning"},
    {"text": "Plan a full day itinerary and surprise her with it", "category": "Experience Planning"},
    {"text": "Book a couples' spa day or massage session", "category": "Experience Planning"},
    {"text": "Plan a scenic drive to somewhere new", "category": "Experience Planning"},
    {"text": "Organize a picnic at a beautiful outdoor location", "category": "Experience Planning"},
    {"text": "Plan a shopping day and budget for her to pick something she wants", "category": "Experience Planning"},
    {"text": "Book a fun class together (cooking, art, dance)", "category": "Experience Planning"},
]

WEEKLY_TASKS_LONG_DISTANCE = [
    {"text": "Plan a themed video call date: dress up, order the same food, and watch a movie 'together' via screen share", "category": "Virtual Date"},
    {"text": "Send her a care package with her favorite things", "category": "Gifts"},
    {"text": "Order food delivery to her place as a surprise", "category": "Gifts"},
    {"text": "Create a custom playlist titled 'Songs that Remind Me of You'", "category": "Words of Affirmation"},
    {"text": "Write a handwritten letter and mail it to her", "category": "Words of Affirmation"},
    {"text": "Plan a surprise virtual game night with her friends", "category": "Virtual Date"},
    {"text": "Send her flowers or a gift delivered to her door", "category": "Gifts"},
    {"text": "Create a photo collage of your favorite moments", "category": "Quality Time"},
    {"text": "Plan a multi-day challenge (send daily themed photos)", "category": "Virtual Date"},
    {"text": "Book your next visit and send her the confirmation", "category": "Planning Future"},
]

def get_tasks_for_relationship_mode(mode: str, task_type: str = "daily"):
    """
    Get tasks based on relationship mode and type
    
    Args:
        mode: "SAME_HOME", "DAILY_IRL", or "LONG_DISTANCE"
        task_type: "daily" or "weekly"
    
    Returns:
        List of task dictionaries
    """
    if task_type == "daily":
        if mode == "SAME_HOME":
            return LIVE_TOGETHER_DAILY_TASKS
        elif mode == "DAILY_IRL":
            return MEET_DAILY_TASKS
        elif mode == "LONG_DISTANCE":
            return LONG_DISTANCE_DAILY_TASKS
    elif task_type == "weekly":
        if mode == "SAME_HOME":
            return WEEKLY_TASKS_LIVE_TOGETHER
        elif mode == "DAILY_IRL":
            return WEEKLY_TASKS_MEET_DAILY
        elif mode == "LONG_DISTANCE":
            return WEEKLY_TASKS_LONG_DISTANCE
    
    return []
