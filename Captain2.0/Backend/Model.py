import google.generativeai as genai
from rich import print
from dotenv import dotenv_values
import re
import time

env_vars = dotenv_values(".env")
GOOGLE_API_KEY = env_vars["GOOGLE_API_KEY"]

# Configure Gemini (NOT Cohere)
genai.configure(api_key=GOOGLE_API_KEY)

# Use a fast Gemini model
model = genai.GenerativeModel('gemini-1.5-flash')

funcs = [
    "exit", "general", "realtime", "open", "close", "play",
    "generate image", "system", "content", "google search",
    "youtube search", "reminder"
]

messages = []

preamble = """
You are a very accurate Decision-Making Model. Your ONLY job is to classify user queries into specific categories. NEVER answer the query itself.

CATEGORIES:
- general [query]: For conversational queries, questions about history, science, etc.
- realtime [query]: For current information (news, weather, stock prices, current events)
- open [app/website]: For opening applications or websites
- close [app/website]: For closing applications
- play [song/video]: For playing media
- generate image [description]: For image generation requests
- system [command]: For system controls (volume, mute, brightness)
- content [topic]: For content writing requests
- google search [query]: For web searches
- youtube search [query]: For YouTube searches
- reminder [details]: For setting reminders
- exit: For ending conversations

EXAMPLES:
User: "open chrome" -> open chrome
User: "what's the weather?" -> realtime weather
User: "who is shah rukh khan?" -> general who is shah rukh khan
User: "play despacito" -> play despacito
User: "set reminder for meeting at 5pm" -> reminder meeting at 5pm
User: "bye" -> exit

Respond ONLY with the category and the query content. For multiple commands, separate with commas.
"""

def FirstLayerDMM(prompt: str = "test"):
    # FIRST: Check for automation commands locally (FAST PATH)
    prompt_lower = prompt.lower().strip()
    
    # Direct detection of automation commands (bypass AI for speed)
    automation_commands = {
        "open ": "open",
        "close ": "close", 
        "play ": "play",
        "system ": "system",
        "content ": "content",
        "google search ": "google search",
        "youtube search ": "youtube search",
        "generate image": "generate image",
        "remind me": "reminder",
        "set reminder": "reminder"
    }
    
    for pattern, command in automation_commands.items():
        if prompt_lower.startswith(pattern):
            target = prompt[len(pattern):].strip()
            return [f"{command} {target}"]
    
    # Check for exit commands
    if any(word in prompt_lower for word in ["exit", "bye", "goodbye", "stop", "quit"]):
        return ["exit"]
    
    # Check for obvious realtime queries
    realtime_keywords = ["weather", "time", "news", "today", "current", "temperature"]
    if any(word in prompt_lower for word in realtime_keywords):
        return [f"realtime {prompt}"]
    
    # If not detected locally, use Gemini AI
    try:
        # Create prompt for Gemini
        ai_prompt = f"""
        {preamble}
        
        User query: "{prompt}"
        
        Your response (ONLY the category + query, NOTHING else):
        """
        
        response = model.generate_content(ai_prompt)
        
        result = response.text.strip()
        print(f"Gemini response: {result}")  # Debugging
        
        # Clean up the response
        result = result.replace("\n", " ").replace('"', '').strip()
        
        # Split multiple commands
        if "," in result:
            commands = [cmd.strip() for cmd in result.split(",")]
        else:
            commands = [result]
        
        # Validate commands
        valid_commands = []
        for cmd in commands:
            for func in funcs:
                if cmd.startswith(func + " ") or cmd == func:
                    valid_commands.append(cmd)
                    break
        
        if valid_commands:
            return valid_commands
        else:
            # Fallback to general if no valid command found
            return [f"general {prompt}"]
            
    except Exception as e:
        print(f"Gemini API error: {e}")
        # Fallback to local decision making
        return fallback_decision(prompt)

def fallback_decision(prompt):
    prompt_lower = prompt.lower().strip()
    
    # Simple fallback logic
    if any(word in prompt_lower for word in ["weather", "time", "news", "today", "current", "temperature"]):
        return [f"realtime {prompt}"]
    elif any(word in prompt_lower for word in ["open ", "start ", "launch "]):
        app_name = prompt_lower.replace("open ", "").replace("start ", "").replace("launch ", "").strip()
        return [f"open {app_name}"]
    elif any(word in prompt_lower for word in ["close ", "exit ", "quit ", "stop "]):
        app_name = prompt_lower.replace("close ", "").replace("exit ", "").replace("quit ", "").replace("stop ", "").strip()
        return [f"close {app_name}"]
    else:
        return [f"general {prompt}"]

# Test function
def test_queries():
    test_cases = [
        "open chrome",
        "what's the weather like?",
        "who is Narendra Modi?",
        "play shape of you",
        "set reminder for meeting at 3pm",
        "search google for python tutorials",
        "bye"
    ]
    
    for query in test_cases:
        start_time = time.time()
        decision = FirstLayerDMM(query)
        end_time = time.time()
        print(f"'{query}' -> {decision} ({(end_time-start_time)*1000:.0f}ms)")
    
if __name__ == "__main__":
    test_queries()