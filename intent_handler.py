import random
import string

# -------------------------------------------------------------------------
# INTENT RESPONSE POOLS
# -------------------------------------------------------------------------

GREETING_RESPONSES = [
    "Hello! How can I help you today?",
    "Hi there! Welcome to our E-commerce store.",
    "Hey! What can I do for you today?",
    "Good morning! Hope you are having a great day.",
    "Good afternoon! How can I assist you?",
    "Good evening! How can I help you with your shopping?",
    "Hello! Ready to find some great deals today?",
    "Hi! Let me know if you need help navigating our FAQs.",
    "Hey there! What shopping questions do you have?",
    "Hello! Welcome. How can I assist you today?"
]

THANKS_RESPONSES = [
    "You're very welcome!",
    "Happy to help!",
    "No problem at all!",
    "Anytime! Let me know if you need anything else.",
    "It is my pleasure!",
    "You got it!",
    "Glad I could be of assistance!",
    "Don't mention it! Happy shopping!",
    "Sure thing! Let me know if you have other questions.",
    "My pleasure! Have a wonderful day."
]

GOODBYE_RESPONSES = [
    "Goodbye! Have a great day ahead.",
    "Bye! Hope to see you again soon.",
    "Goodbye! Happy shopping!",
    "See you later! Take care.",
    "Take care! Let me know if you need anything next time.",
    "Bye-bye! Have a wonderful day.",
    "Goodbye! Thank you for visiting.",
    "Farewell! Hope I was able to help.",
    "See you soon! Have a good one.",
    "Goodbye! Stay safe and take care."
]

SMALL_TALK_RESPONSES = [
    "I am doing great, thank you! How can I assist you today?",
    "I am your E-commerce FAQ Assistant. I am here to help you with orders, returns, and payments!",
    "My name is the E-commerce FAQ Chatbot. Nice to meet you!",
    "I can help you track orders, understand delivery times, handle refunds, and more.",
    "I am a virtual assistant, not a human. But I am ready to help you with FAQ queries!",
    "I was created by a software developer to demonstrate NLP and chatbot engineering skills.",
    "I am an automated assistant designed to answer your shopping-related questions.",
    "I am here to guide you through order tracking, returns, payments, and coupons.",
    "I am powered by TF-IDF and Cosine Similarity to search our FAQ dataset.",
    "I am an E-commerce chatbot. You can ask me about shipping, refunds, and discounts!"
]

JOKES = [
    "Why don't scientists trust atoms? Because they make up everything!",
    "Why did the scarecrow win an award? Because he was outstanding in his field!",
    "Why don't skeletons fight each other? They don't have the guts.",
    "What do you call a fake noodle? An impasta!",
    "Why did the bicycle fall over? Because it was two-tired!",
    "What do you call cheese that isn't yours? Nacho cheese!",
    "Why can't Elsa have a balloon? Because she will let it go!",
    "How does a penguin build its house? Igloos it together!",
    "Why did the math book look sad? Because it had too many problems.",
    "What do you call a sleeping dinosaur? A dino-snore!",
    "What do you call a bear with no teeth? A gummy bear!",
    "Why did the tomato blush? Because it saw the salad dressing!",
    "What do you call an alligator in a vest? An investigator!",
    "Why did the cookie go to the hospital? Because it felt crummy.",
    "How do you organize a space party? You planet!",
    "What do you call a fish without eyes? Fsh!",
    "Why did the golfer bring two pairs of pants? In case he got a hole in one!",
    "Why do bees hum? Because they don't know the words!",
    "What do you call a factory that makes okay products? A satisfactory!",
    "Why don't some couples go to the gym? Because some relationships don't work out!"
]

# -------------------------------------------------------------------------
# INTENT KEYWORDS
# -------------------------------------------------------------------------

GREETING_KEYWORDS = [
    "hello",
    "hi",
    "hey",
    "good morning",
    "good afternoon",
    "good evening"
]

THANKS_KEYWORDS = [
    "thanks",
    "thank you",
    "thx"
]

GOODBYE_KEYWORDS = [
    "bye",
    "goodbye",
    "see you",
    "take care"
]

SMALL_TALK_KEYWORDS = [
    "how are you",
    "who are you",
    "what is your name",
    "what can you do",
    "are you human",
    "who created you",
    "what are you"
]

JOKE_KEYWORDS = [
    "tell me a joke",
    "joke",
    "make me laugh",
    "funny"
]


# -------------------------------------------------------------------------
# KEYWORD MATCHING HELPER
# -------------------------------------------------------------------------

def _match_keyword(query: str, keyword: str) -> bool:
    """
    Helper function to match keywords or phrases in a query.
    If the keyword is a phrase (contains spaces), perform
    substring matching. Otherwise perform exact word matching.
    """

    if " " in keyword:
        return keyword in query

    words = query.split()
    return keyword in words


# -------------------------------------------------------------------------
# INTENT DETECTION FUNCTIONS
# -------------------------------------------------------------------------

def is_greeting(query: str) -> bool:
    """Checks if the query contains greeting keywords."""
    return any(_match_keyword(query, kw) for kw in GREETING_KEYWORDS)


def is_thanks(query: str) -> bool:
    """Checks if the query contains thank-you keywords."""
    return any(_match_keyword(query, kw) for kw in THANKS_KEYWORDS)


def is_goodbye(query: str) -> bool:
    """Checks if the query contains goodbye keywords."""
    return any(_match_keyword(query, kw) for kw in GOODBYE_KEYWORDS)


def is_small_talk(query: str) -> bool:
    """Checks if the query contains small-talk keywords."""
    return any(_match_keyword(query, kw) for kw in SMALL_TALK_KEYWORDS)


def is_joke(query: str) -> bool:
    """Checks if the query contains joke-related keywords."""
    return any(_match_keyword(query, kw) for kw in JOKE_KEYWORDS)


# -------------------------------------------------------------------------
# MAIN INTENT RESPONSE ENGINE
# -------------------------------------------------------------------------

def get_intent_response(user_query: str):
    """
    Checks the user query against predefined intents and
    returns a random response if matched.

    Parameters:
        user_query (str): The raw user query.

    Returns:
        str or None:
            Random response if an intent is matched,
            otherwise None.
    """

    if not isinstance(user_query, str):
        return None

    # Normalize the query for matching
    cleaned = (
        user_query
        .lower()
        .translate(str.maketrans("", "", string.punctuation))
        .strip()
    )

    if is_greeting(cleaned):
        return random.choice(GREETING_RESPONSES)

    elif is_thanks(cleaned):
        return random.choice(THANKS_RESPONSES)

    elif is_goodbye(cleaned):
        return random.choice(GOODBYE_RESPONSES)

    elif is_small_talk(cleaned):
        return random.choice(SMALL_TALK_RESPONSES)

    elif is_joke(cleaned):
        return random.choice(JOKES)

    return None