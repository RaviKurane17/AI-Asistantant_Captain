from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager  # ADD THIS IMPORT
from dotenv import dotenv_values
from pathlib import Path
import os
import mtranslate as mt
import time

# Load environment variables
env_vars = dotenv_values(".env")
InputLanguage = env_vars.get("InputLanguage", "en-GB")  # default to en-US if not set




# Prepare the HTML content with Speech Recognition JS
HtmlCode = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {{
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRecognition) {{
                alert("Speech Recognition API not supported in this browser.");
                return;
            }}
            recognition = new SpeechRecognition();
            recognition.lang = '{InputLanguage}';
            recognition.continuous = true;

            recognition.onresult = function(event) {{
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript;
            }};

            recognition.onend = function() {{
                recognition.start();
            }};

            recognition.start();
        }}

        function stopRecognition() {{
            if (recognition) {{
                recognition.stop();
            }}
            output.innerHTML = "";
        }}
    </script>
</body>
</html>
'''

# Save the HTML file
data_dir = Path("Data")
data_dir.mkdir(exist_ok=True)
voice_html_path = data_dir / "Voice.html"
with open(voice_html_path, "w", encoding="utf-8") as f:
    f.write(HtmlCode)

# Create file URI for Selenium to open
Link = voice_html_path.resolve().as_uri()

# Setup Chrome options
chrome_options = Options()

# Change the binary_location path to your Chrome or Chrome Beta executable path
chrome_options.binary_location = r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
chrome_options.add_argument("--headless=new")  # modern headless mode
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.142.86 Safari/537.36"
)

# FIXED: Use webdriver-manager to automatically handle ChromeDriver
service = Service(ChromeDriverManager().install())

# Initialize the driver
driver = webdriver.Chrome(service=service, options=chrome_options)

# Setup temp status path for assistant status file
temp_dir = Path.cwd() / "Frontend" / "Files"
temp_dir.mkdir(parents=True, exist_ok=True)

def SetAssistantStatus(Status: str):
    with open(temp_dir / "Status.data", "w", encoding='utf-8') as file:
        file.write(Status)

def QueryModifier(Query: str) -> str:
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you"]

    # Check if query contains question words to append proper punctuation
    if any(word + " " in new_query for word in question_words):
        if new_query[-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if new_query[-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."

    return new_query.capitalize()

def UniversalTranslator(Text: str) -> str:
    english_translation = mt.translate(Text, "en", "auto")
    return english_translation

def SpeechRecognition() -> str:
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    try:
        driver.get(Link)
        driver.find_element(By.ID, "start").click()

        while True:
            Text = driver.find_element(By.ID, "output").text.strip()
            if Text:
                driver.find_element(By.ID, "end").click()
                if InputLanguage.lower().startswith("en"):
                    return QueryModifier(Text)
                else:
                    SetAssistantStatus("Translating...")
                    return QueryModifier(UniversalTranslator(Text))
            time.sleep(0.3)
    finally:
        driver.quit()
