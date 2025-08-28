from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os
import time

# Import TextToSpeech function
from Backend.TextToSpeech import TextToSpeech

env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

classes = ["zCubwf", "hgKELc", "LTKOO SY7ric", "ZOLcW", "gsrt vk_bk FzvWSb YwPhnf", "pclqee", "tw-Data-text tw-text-small tw-ta",
           "IZ6rdc", "05uR6d LTKOO", "vlzY6d", "webanswers-webanswers_table_webanswers-table", "dDoNo ikb4Bb gsrt", "sXLa0e", 
           "LWkfKe", "VQF4g", "qv3Wpe", "kno-rdesc", "SPZz6b"]

useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'

# Initialize Groq client only if API key exists
client = None
if GroqAPIKey:
    client = Groq(api_key=GroqAPIKey)

professional_responses = [
    "Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
    "I'm at your service for any additional questions or support you may need—don't hesitate to ask.",
]

messages = []

SystemChatBot = [{"role": "system", "content": f"Hello, I am {os.environ.get('Username', 'User')}, a content writer. You have to write content like letters, codes, applications, essays, notes, songs, poems, etc."}]


def GoogleSearch(topic):
    search(topic)
    return True


def Content(topic):
    def OpenNotepad(file):
        try:
            default_text_editor = 'notepad.exe'
            subprocess.Popen([default_text_editor, file])
            return True
        except Exception as e:
            print(f"Error opening notepad: {e}")
            return False

    def ContentWriterAI(prompt):
        if not client:
            print("Error: Groq API key not found. Please check your .env file.")
            return "Error: Unable to generate content - API key missing."
        
        try:
            messages.append({"role": "user", "content": f"{prompt}"})

            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=SystemChatBot + messages,
                max_tokens=2048,
                temperature=0.7,
                top_p=1,
                stream=True,
                stop=None
            )

            answer = ""

            for chunk in completion:
                if chunk.choices[0].delta.content:
                    answer += chunk.choices[0].delta.content

            answer = answer.replace("</s>", "")
            messages.append({"role": "assistant", "content": answer})
            return answer
        except Exception as e:
            print(f"Error generating content: {e}")
            return f"Error: Unable to generate content - {str(e)}"

    topic = topic.replace("content", "").strip()
    content_by_ai = ContentWriterAI(topic)

    # Create Data directory if it doesn't exist
    data_dir = "Data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"Created directory: {data_dir}")

    filepath = os.path.join(data_dir, f"{topic.lower().replace(' ', '_')}.txt")
    
    try:
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(content_by_ai)
        print(f"Content written to: {filepath}")
        
        OpenNotepad(filepath)
        return True
    except Exception as e:
        print(f"Error writing content to file: {e}")
        return False


def YouTubeSearch(topic):
    url = f"https://www.youtube.com/results?search_query={topic}"
    webbrowser.open(url)
    return True


def PlayYoutube(query):
    try:
        playonyt(query)
        return True
    except Exception as e:
        print(f"Error playing YouTube video: {e}")
        return False


def OpenApp(app, sess=requests.session()):
    try:
        # Try to open the app using AppOpener
        appopen(app, match_closest=True, output=True, throw_error=True)
        print(f"Successfully opened {app} using AppOpener")
        
        # Speak confirmation
        TextToSpeech(f"Opening {app}")
        return True
    except Exception as e:
        print(f"AppOpener failed for {app}: {e}")
        
        # Try direct Windows app execution
        app_commands = {
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "paint": "mspaint.exe",
            "cmd": "cmd.exe",
            "command prompt": "cmd.exe",
            "chrome": "chrome.exe",
            "browser": "chrome.exe",
            "word": "winword.exe",
            "excel": "excel.exe",
            "powerpoint": "powerpnt.exe",
            "settings": "ms-settings:",
            "control panel": "control.exe",
            "task manager": "taskmgr.exe",
            "file explorer": "explorer.exe",
            "photos": "ms-photos:",
            "calendar": "outlookcal:",
            "mail": "outlookmail:"
        }
        
        app_lower = app.lower()
        
        # Check if it's a web URL
        if app_lower.startswith(('http://', 'https://', 'www.')):
            try:
                webbrowser.open(app)
                print(f"Opened URL: {app}")
                TextToSpeech(f"Opening website {app}")
                return True
            except Exception as url_error:
                print(f"Failed to open URL {app}: {url_error}")
                TextToSpeech(f"Sorry, I couldn't open the website {app}")
                return False
        
        # Check if it's a known Windows app
        if app_lower in app_commands:
            try:
                if app_commands[app_lower].startswith(('http://', 'https://', 'ms-', 'outlook')):
                    # It's a URI scheme
                    webbrowser.open(app_commands[app_lower])
                else:
                    # It's an executable
                    subprocess.Popen(app_commands[app_lower], shell=True)
                print(f"Successfully opened {app} using direct command")
                TextToSpeech(f"Opening {app}")
                return True
            except Exception as cmd_error:
                print(f"Failed to open {app} using direct command: {cmd_error}")
                TextToSpeech(f"Sorry, I couldn't open {app}")
        
        # Fallback to web search
        try:
            search_url = f"https://www.google.com/search?q={app.replace(' ', '+')}"
            webbrowser.open(search_url)
            print(f"Opened web search for: {app}")
            TextToSpeech(f"Searching for {app} on Google")
            return True
        except Exception as search_error:
            print(f"Failed to open web search for {app}: {search_error}")
            TextToSpeech(f"Sorry, I couldn't search for {app}")
            return False


def CloseApp(app):
    # Special handling for browser
    if "chrome" in app.lower() or "browser" in app.lower():
        try:
            if os.name == 'nt':  # Windows
                subprocess.run(["taskkill", "/f", "/im", "chrome.exe"], check=True)
                print("Closed Chrome using taskkill")
                TextToSpeech("Closing Chrome browser")
            else:  # macOS/Linux
                subprocess.run(["pkill", "-f", "chrome"], check=True)
                print("Closed Chrome using pkill")
                TextToSpeech("Closing Chrome browser")
            return True
        except Exception as e:
            print(f"Error closing Chrome: {e}")
            TextToSpeech("Sorry, I couldn't close Chrome")
    
    try:
        close(app, match_closest=True, output=True, throw_error=True)
        print(f"Closed {app} using AppOpener")
        TextToSpeech(f"Closing {app}")
        return True
    except Exception as e:
        print(f"Error closing {app} using AppOpener: {e}")
        TextToSpeech(f"Sorry, I couldn't close {app}")
        
        # Try taskkill for Windows
        if os.name == 'nt':
            try:
                # Try to find the process name
                process_names = {
                    "notepad": "notepad.exe",
                    "calculator": "calculator.exe",
                    "paint": "mspaint.exe",
                    "word": "winword.exe",
                    "excel": "excel.exe",
                    "powerpoint": "powerpnt.exe"
                }
                
                app_lower = app.lower()
                process_name = process_names.get(app_lower, f"{app.lower()}.exe")
                
                subprocess.run(["taskkill", "/f", "/im", process_name], check=True)
                print(f"Closed {app} using taskkill")
                TextToSpeech(f"Closing {app}")
                return True
            except Exception as taskkill_error:
                print(f"Failed to close {app} using taskkill: {taskkill_error}")
                TextToSpeech(f"Sorry, I couldn't close {app}")
        
        return False


import keyboard
import screen_brightness_control as sbc
import psutil
from Backend.TextToSpeech import TextToSpeech

def System(command: str) -> bool:
    try:
        command = command.lower().replace("system ", "").strip()

        # ---- Volume Controls ----
        if "volume up" in command:
            keyboard.send("volume up")
            TextToSpeech("Volume increased")
            return True

        elif "volume down" in command:
            keyboard.send("volume down")
            TextToSpeech("Volume decreased")
            return True

        elif "mute" in command:
            keyboard.send("volume mute")
            TextToSpeech("Volume muted")
            return True

        # ---- Brightness Controls ----
        elif "brightness up" in command:
            current = sbc.get_brightness(display=0)[0]
            sbc.set_brightness(min(current + 10, 100))
            TextToSpeech("Brightness increased")
            return True

        elif "brightness down" in command:
            current = sbc.get_brightness(display=0)[0]
            sbc.set_brightness(max(current - 10, 0))
            TextToSpeech("Brightness decreased")
            return True

        # ---- Battery / CPU Info ----
        elif "battery" in command:
            battery = psutil.sensors_battery()
            TextToSpeech(f"Battery is at {battery.percent} percent")
            return True

        elif "cpu" in command:
            cpu = psutil.cpu_percent()
            TextToSpeech(f"CPU usage is {cpu} percent")
            return True

        # ---- Keyboard Shortcuts ----
        elif command.startswith(("ctrl", "alt", "win")):
            keyboard.send(command.replace(" ", ""))  # e.g. ctrl+c, alt+tab
            TextToSpeech(f"Shortcut {command} executed")
            return True

        else:
            TextToSpeech(f"Unknown system command {command}")
            return False

    except Exception as e:
        print("System error:", e)
        TextToSpeech("System control error")
        return False


async def TranslateAndExecute(commands: list[str]):
    funcs = []

    for command in commands:
        print(f"Processing command: {command}")
        
        if command.startswith("open "):
            app_name = command.removeprefix("open ").strip()
            fun = asyncio.to_thread(OpenApp, app_name)
            funcs.append(fun)
        elif command.startswith("close "):
            app_name = command.removeprefix("close ").strip()
            fun = asyncio.to_thread(CloseApp, app_name)
            funcs.append(fun)
        elif command.startswith("play "):
            query = command.removeprefix("play ").strip()
            fun = asyncio.to_thread(PlayYoutube, query)
            funcs.append(fun)
        elif command.startswith("content "):
            topic = command.removeprefix("content ").strip()
            fun = asyncio.to_thread(Content, topic)
            funcs.append(fun)
        elif command.startswith("google search "):
            query = command.removeprefix("google search ").strip()
            fun = asyncio.to_thread(GoogleSearch, query)
            funcs.append(fun)
        elif command.startswith("youtube search "):
            query = command.removeprefix("youtube search ").strip()
            fun = asyncio.to_thread(YouTubeSearch, query)
            funcs.append(fun)
        elif command.startswith("system "):
            sys_command = command.removeprefix("system ").strip()
            fun = asyncio.to_thread(System, sys_command)
            funcs.append(fun)
        else:
            print(f"No function found for command: {command}")
            TextToSpeech("Sorry, I didn't understand that command")

    if funcs:
        results = await asyncio.gather(*funcs, return_exceptions=True)
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"Command {i+1} failed with exception: {result}")
            else:
                print(f"Command {i+1} result: {result}")
            yield result
    else:
        print("No valid commands to execute")


async def Automation(commands: list[str]):
    print(f"Starting automation with commands: {commands}")
    results = []
    async for result in TranslateAndExecute(commands):
        results.append(result)
    print(f"Automation completed. Results: {results}")
    return True


def test_automation():
    """Test the automation functions"""
    test_commands = [
        "open notepad",
        "open calculator", 
        "open chrome",
        "open cmd",
        "open paint",
        "open settings"
    ]
    
    print("Testing automation functions...")
    for cmd in test_commands:
        print(f"\nTesting: {cmd}")
        if cmd.startswith("open "):
            app_name = cmd.removeprefix("open ").strip()
            result = OpenApp(app_name)
            print(f"Result: {result}")
            time.sleep(2)  # Give time to see the app open


if __name__ == "__main__":
    test_automation()

    