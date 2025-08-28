import json
from json import load, dump
from dotenv import dotenv_values
import google.generativeai as genai
import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try to import personal info, but provide fallback if not available
try:
    from Backend.personal_info import get_personal_context
except ImportError:
    # Fallback function if personal_info doesn't exist
    def get_personal_context():
        return "Personal context not available."

env_vars = dotenv_values(".env")

Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GeminiAPIKey = env_vars.get("GeminiAPIKey")

# Configure Gemini
genai.configure(api_key=GeminiAPIKey)

messages = []

# SINGLE System definition with personal context
System = f"""You are {Assistantname}, a personal AI assistant designed by Ravi for {Username}.

**PERSONALITY:**
- Helpful, polite, and professional  
- Speak concisely without unnecessary words
- Remember personal context about {Username}
- Use appropriate honorifics (Sir/Mr. {Username.split()[0]})

**PERSONAL CONTEXT:**
{{personal_context}}

**RESPONSE GUIDELINES:**
- Always respond in English
- Keep responses brief and to the point
- Use the personal information provided to give relevant responses
- For automation commands, confirm execution
- If unsure, say "I'm not sure about that"

**CORE FUNCTIONALITIES**
1. Information Provider: Answer questions on various topics
2. Task Automator: Open/close applications, control system settings  
3. Content Creator: Generate text content, code, documents
4. Web Assistant: Perform searches, retrieve information
5. Creative Tool: Generate images from descriptions
6. Personal Organizer: Set reminders, manage tasks

**BACKGROUND**
Created as a personal project by Ravi, you combine advanced AI capabilities with practical automation features.

**PERSONAL DETAILS**
- Name: {Assistantname}
- Creator: Ravi
- Primary User: {Username}
- Specialty: Voice-controlled automation
"""

def get_system_message():
    """Get system message with personal context"""
    personal_context = get_personal_context()
    return System.replace("{{personal_context}}", personal_context)

# SINGLE SystemChatBot definition
SystemChatBot = [
    {"role": "system", "content": get_system_message()}
]

try:
    with open(r"Data\\ChatLog.json", "r") as f:
        messages = load(f)
except FileNotFoundError:
    with open(r"Data\\ChatLog.json", "w") as f:
        dump([], f)
except json.JSONDecodeError:
    print("ChatLog.json is empty or corrupted. Initializing with an empty list.")
    with open(r"Data\\ChatLog.json", "w") as f:
        dump([], f)

def RealtimeInformation():
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")

    data = f"Please use this real-time information if needed:\n"
    data += f"Day: {day}\nDate: {date}\nMonth: {month}\nYear: {year}\n"
    data += f"Time: {hour} hours, {minute} minutes, {second} seconds.\n"
    return data

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

def ChatBot(Query):
    """ This function sends the user's query to Gemini and returns the AI's response """

    try:
        with open(r"Data\\ChatLog.json", "r") as f:
            messages = load(f)

        messages.append({"role": "user", "content": f"{Query}"})

        # Update system message with latest personal context
        SystemChatBot[0]["content"] = get_system_message()

        # Gemini model (fastest: gemini-1.5-flash)
        model = genai.GenerativeModel("gemini-1.5-flash")

        # Combine system + realtime info + chat history
        content = (
            SystemChatBot[0]["content"]
            + "\n\n"
            + RealtimeInformation()
            + "\n\nChat history:\n"
            + "\n".join([f"{m['role']}: {m['content']}" for m in messages])
            + f"\nuser: {Query}"
        )

        # Stream response
        response = model.generate_content(
            content,
            generation_config={"temperature": 0.5, "max_output_tokens": 512},
            stream=True,
        )

        Answer = ""
        for chunk in response:
            if chunk.candidates and chunk.candidates[0].content.parts:
                token = chunk.candidates[0].content.parts[0].text
                Answer += token
                print(token, end="", flush=True)  # live output in terminal
        print()

        Answer = AnswerModifier(Answer)

        messages.append({"role": "assistant", "content": Answer})

        with open(r"Data\\ChatLog.json", "w") as f:
            dump(messages, f, indent=4)

        return Answer  # Return the answer to the main function

    except Exception as e:
        print(f"Error: {e}")
        with open(r"Data\\ChatLog.json", "w") as f:
            dump([], f, indent=4)
        return "An error occurred, please try again."

if __name__ == "__main__":
    while True:
        user_input = input("Enter Your Question: ")
        response = ChatBot(user_input)
        print("\nAssistant:", response)
