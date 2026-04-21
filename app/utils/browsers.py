import random

BROWSERS = ["chrome110", "chrome120", "edge101", "safari15_5"]

def get_browser() -> str:
    
    return random.choice(BROWSERS)