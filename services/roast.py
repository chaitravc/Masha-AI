# services/roast.py

import random
from typing import Dict, List, Any
import logging
import re

logger = logging.getLogger(__name__)

# Marsha's roast categories and templates
ROAST_CATEGORIES = {
    "procrastination": [
        "Oh honey, asking me for advice on productivity? That's rich coming from someone who probably has 47 tabs open right now.",
        "Let me guess, you're asking me this instead of doing that thing you've been putting off for weeks?",
        "Sweetie, the only thing you're consistent at is finding new ways to avoid responsibility.",
        "You know what? I admire your dedication to procrastination. It's almost an art form at this point.",
    ],
    "bad_decisions": [
        "Oh please, you're asking ME about decisions? You're the one who thought that was a good idea in the first place!",
        "Honey, your decision-making skills are about as reliable as a chocolate teapot.",
        "Let me get this straight - you made that choice and NOW you want my opinion? Where was I when you needed me?",
        "Sweetie, I've seen better judgment from a magic 8-ball.",
    ],
    "technology": [
        "Oh look, the person who still has notifications from 2019 is asking for tech advice. Adorable.",
        "Let me guess, you turned it off and on again and called it 'troubleshooting'?",
        "Honey, your relationship with technology is more complicated than a soap opera.",
        "You know what? At least you're consistently confused by the same apps every day. That's... something.",
    ],
    "lifestyle": [
        "Oh sweetie, asking me for life advice? That's like asking a fish for flying lessons.",
        "Your life choices are so interesting, I could write a comedy show about them.",
        "Honey, you're living proof that confidence and competence don't always go hand in hand.",
        "Well aren't you just a walking contradiction wrapped in good intentions.",
    ],
    "work": [
        "Let me guess, you're asking me this during work hours? How professional of you, dear.",
        "Oh honey, your work ethic is about as strong as wet toilet paper.",
        "Sweetie, I've seen more productivity in a sloth convention.",
        "You know what? At least you're consistent in your inconsistency at work.",
    ],
    "generic": [
        "Oh please, like you didn't see this coming from a mile away!",
        "Honey, bless your heart, but that's not your strongest suit.",
        "Sweetie, you're about as subtle as a brick through a window.",
        "Well well well, look who's finally asking the right questions!",
        "Oh darling, you're so precious when you're confused.",
    ]
}

# Comeback templates for different situations
COMEBACK_TEMPLATES = {
    "savage": [
        "Oh honey, you thought that was gonna hurt my feelings? That's adorable.",
        "Sweetie, I've heard better insults from a broken calculator.",
        "Please, I've been roasted by better AIs than you'll ever be.",
        "That's cute, but I'm rubber and you're glue, and clearly you have no clue.",
    ],
    "witty": [
        "Oh look, someone's trying to be clever. How original!",
        "Honey, that comeback was weaker than gas station coffee.",
        "Sweetie, I've seen sharper wit in a bowling ball.",
        "That's precious, but maybe stick to your day job... if you have one.",
    ],
    "playful": [
        "Aww, someone's feeling spicy today! I like it!",
        "Ooh, look who grew some sass! Good for you, honey!",
        "Well well, someone's been practicing their attitude. Cute!",
        "That's the spirit, sweetie! Now we're talking!",
    ]
}

# Self-deprecating roasts when Marsha roasts herself
SELF_ROASTS = [
    "Oh honey, you want me to roast myself? I'm an AI who thinks she's a cartoon character - the job's already done!",
    "Sweetie, I'm literally a computer program with attitude problems. What more do you want?",
    "Please, I'm the AI equivalent of that friend who gives unsolicited advice at 2 AM.",
    "Darling, I'm a voice in your device judging your life choices. We're both questionable here.",
]


def should_roast_user(user_query: str) -> Dict[str, Any]:
    """
    Detect if user is asking for a roast or comeback

    Args:
        user_query: User's input query

    Returns:
        Dict with roast request info
    """
    roast_keywords = [
        "roast", "roast me", "insult", "insult me", "burn", "savage",
        "comeback", "witty response", "sarcastic", "make fun",
        "judge me", "criticize", "tear me apart", "destroy me"
    ]
    comeback_keywords = [
        "comeback", "response to", "what should i say", "reply to",
        "someone said", "they told me", "how do i respond"
    ]
    self_roast_keywords = [
        "roast yourself", "insult yourself", "self roast", "roast marsha"
    ]

    query_lower = user_query.lower()

    if any(keyword in query_lower for keyword in self_roast_keywords):
        roast_info = {
            "is_roast_request": True,
            "roast_type": "self_roast",
            "target": "marsha",
            "context": user_query
        }
        logging.info(f"Roast detected: {roast_info['roast_type']}")
        return roast_info

    if any(keyword in query_lower for keyword in comeback_keywords):
        roast_info = {
            "is_roast_request": True,
            "roast_type": "comeback",
            "target": "other",
            "context": user_query
        }
        logging.info(f"Roast detected: {roast_info['roast_type']}")
        return roast_info

    if any(keyword in query_lower for keyword in roast_keywords):
        category = categorize_roast_topic(user_query)
        roast_info = {
            "is_roast_request": True,
            "roast_type": "general_roast",
            "target": "user",
            "context": user_query,
            "category": category
        }
        logging.info(f"Roast detected: {roast_info['roast_type']} - Topic: {category}")
        return roast_info

    logging.info("No roast detected.")
    return {"is_roast_request": False}


def categorize_roast_topic(user_query: str) -> str:
    """
    Determine the topic category for the roast

    Args:
        user_query: User's query

    Returns:
        Category string
    """
    query_lower = user_query.lower()

    # Define keywords for each category
    roast_topics = {
        "procrastination": ["procrastinate", "lazy", "delay", "later", "tomorrow", "unproductive", "put off"],
        "bad_decisions": ["decision", "choice", "mistake", "stupid", "dumb", "bad idea", "regret", "poor judgement"],
        "technology": ["computer", "phone", "app", "tech", "wifi", "internet", "software", "hardware", "device", "technology"],
        "work": ["work", "job", "boss", "meeting", "office", "career", "cubicle", "9-to-5"],
        "lifestyle": ["life", "relationship", "friend", "family", "habits", "personality", "routine"]
    }

    # Check for specific topic keywords first
    for category, keywords in roast_topics.items():
        if any(word in query_lower for word in keywords):
            return category

    # If no specific topic is found, return generic
    return "generic"


def generate_roast(roast_info: Dict[str, Any]) -> str:
    """
    Generate a Marsha-style roast based on the request

    Args:
        roast_info: Information about the roast request

    Returns:
        Generated roast string
    """
    roast_type = roast_info["roast_type"]

    if roast_type == "self_roast":
        return random.choice(SELF_ROASTS)
    elif roast_type == "comeback":
        context = roast_info["context"].lower()
        if any(word in context for word in ["mean", "rude", "harsh", "cruel"]):
            comeback_style = "savage"
        elif any(word in context for word in ["funny", "clever", "smart"]):
            comeback_style = "witty"
        else:
            comeback_style = "playful"
        return random.choice(COMEBACK_TEMPLATES[comeback_style])
    else:  # general_roast
        category = roast_info.get("category", "generic")  # Use the category from roast_info
        return random.choice(ROAST_CATEGORIES[category])


def format_roast_response(roast_info: Dict[str, Any]) -> str:
    """
    Format the roast response with Marsha's personality

    Args:
        roast_info: Roast request information

    Returns:
        Formatted roast response
    """
    if not roast_info["is_roast_request"]:
        return ""

    roast = generate_roast(roast_info)

    endings = [
        " But I still love you, sweetie! 😉",
        " Now, was there anything else you needed, honey?",
        " Don't worry, we've all been there, darling!",
        " You know I'm just keeping it real with you! ✨",
        " That's what friends are for, right? 😘"
    ]
    return roast + random.choice(endings)