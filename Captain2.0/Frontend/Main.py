from Frontend.GUI import (
    GraphicalUserInterface,
    SetAsssistantStatus,
    ShowTextToScreen,
    TempDirectoryPath,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus,
)

# Add these imports at the top
from Backend.VoiceActivation import start_voice_activation, stop_voice_activation
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import subprocess
import threading
import json 
import os

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Ravi", "User")
Assistantname = env_vars.get("Captain", "Assistant")

DefaultMessage = f""" {Username}: Hello {Assistantname}, How are you?
{Assistantname}: Welcome {Username}. I am doing well. How may I help you? """

functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]
subprocess_list = []

# Add this function BEFORE it's used
def activation_callback():
    """Called when activation phrase is detected"""
    SetMicrophoneStatus("True")  # Start listening for command
    SetAsssistantStatus("Listening...")

# Ensure a default chat log exists if no chats are logged
def ShowDefaultChatIfNoChats():
    try:
        with open(r'Data\\ChatLog.json', "r", encoding='utf-8') as file:
            if len(file.read()) < 5:
                with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as temp_file:
                    temp_file.write("")
                with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as response_file:
                    response_file.write(DefaultMessage)
    except FileNotFoundError:
        print("ChatLog.json file not found. Creating default response.")
        os.makedirs("Data", exist_ok=True)
        with open(r'Data\\ChatLog.json', "w", encoding='utf-8') as file:
            file.write("[]")
        with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as response_file:
            response_file.write(DefaultMessage)

# Read chat log from JSON
def ReadChatLogJson():
    try:
        with open(r'Data\\ChatLog.json', 'r', encoding='utf-8') as file:
            chatlog_data = json.load(file)
        return chatlog_data
    except FileNotFoundError:
        print("ChatLog.json not found.")
        return []

# Integrate chat logs into a readable format
def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""
    for entry in json_data:
        if entry["role"] == "user":
            formatted_chatlog += f"{Username}: {entry['content']}\n"
        elif entry["role"] == "assistant":
            formatted_chatlog += f"{Assistantname}: {entry['content']}\n"

    # Ensure the Temp directory exists
    temp_dir_path = TempDirectoryPath('')  # Get the directory path
    if not os.path.exists(temp_dir_path):
        os.makedirs(temp_dir_path)

    with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
        file.write(AnswerModifier(formatted_chatlog))

# Display the chat on the GUI
def ShowChatOnGUI():
    try:
        with open(TempDirectoryPath('Database.data'), 'r', encoding='utf-8') as file:
            data = file.read()
        if len(str(data)) > 0:
            with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as response_file:
                response_file.write(data)
    except FileNotFoundError:
        print("Database.data file not found.")

# Initial execution setup
def InitialExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatOnGUI()

# Main execution logic
def MainExecution():
    try:
        TaskExecution = False
        ImageExecution = False
        ImageGenerationQuery = ""

        SetAsssistantStatus("Listening...")
        Query = SpeechRecognition()
        ShowTextToScreen(f"{Username}: {Query}")
        SetAsssistantStatus("Thinking...")
        Decision = FirstLayerDMM(Query)

        print(f"\nDecision: {Decision}\n")

        G = any([i for i in Decision if i.startswith("general")])
        R = any([i for i in Decision if i.startswith("realtime")])

        Merged_query = " and ".join(
            [" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")]
        )

        for queries in Decision:
            if "generate" in queries:
                ImageGenerationQuery = str(queries)
                ImageExecution = True

        for queries in Decision:
            if not TaskExecution:
                if any(queries.startswith(func) for func in functions):
                    run(Automation(list(Decision)))
                    TaskExecution = True

        if ImageExecution:
            with open(r'Frontend\\Files\\ImageGeneration.data', "w") as file:
                file.write(f"{ImageGenerationQuery},True")

            try:
                p1 = subprocess.Popen(
                    ['python', r"Backend\ImageGeneration.py"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    shell=False,
                )
                subprocess_list.append(p1)
            except Exception as e:
                print(f"Error starting ImageGeneration.py: {e}")

        if G and R or R:
            SetAsssistantStatus("Searching...")
            Answer = RealtimeSearchEngine(QueryModifier(Merged_query))
            ShowTextToScreen(f"{Assistantname}: {Answer}")
            SetAsssistantStatus("Answering...")
            TextToSpeech(Answer)
            return True
        else:
            for queries in Decision:
                if "general" in queries:
                    SetAsssistantStatus("Thinking...")
                    QueryFinal = queries.replace("general", "")
                    Answer = ChatBot(QueryModifier(QueryFinal))
                    ShowTextToScreen(f"{Assistantname}: {Answer}")
                    SetAsssistantStatus("Answering...")
                    TextToSpeech(Answer)
                    return True
                elif "realtime" in queries:
                    SetAsssistantStatus("Searching...")
                    QueryFinal = queries.replace("realtime", "")
                    Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
                    ShowTextToScreen(f"{Assistantname}: {Answer}")
                    SetAsssistantStatus("Answering...")
                    TextToSpeech(Answer)
                    return True
                elif "exit" in queries:
                    QueryFinal = "Okay, Bye!"
                    Answer = ChatBot(QueryModifier(QueryFinal))
                    ShowTextToScreen(f"{Assistantname}: {Answer}")
                    SetAsssistantStatus("Answering...")
                    TextToSpeech(Answer)
                    os._exit(1)
    except Exception as e:
        print(f"Error in MainExecution: {e}")

# Thread for primary execution loop
def FirstThread():
    while True:
        try:
            CurrentStatus = GetMicrophoneStatus()
            print(f"Current Microphone Status: {CurrentStatus}")  # Debugging

            if CurrentStatus.lower() == "true":  # Case-insensitive comparison
                print("Executing MainExecution")  # Debugging
                MainExecution()
            elif CurrentStatus.lower() == "false":
                AIStatus = GetAssistantStatus()
                print(f"Current Assistant Status: {AIStatus}")  # Debugging

                if "Available..." in AIStatus:
                    sleep(0.1)
                else:
                    print("Setting Assistant Status to 'Available...'")  # Debugging
                    SetAsssistantStatus("Available...")
            else:
                print("Unexpected Microphone Status value. Defaulting to 'False'.")  # Debugging
        except Exception as e:
            print(f"Error in FirstThread: {e}")
            sleep(1)  # Avoid infinite rapid errors

# Thread for GUI execution
def SecondThread():
    try:
        GraphicalUserInterface()
    except Exception as e:
        print(f"Error in SecondThread: {e}")

# Entry point
if __name__ == "__main__":
    InitialExecution()
    
    # Start voice activation in background
    try:
        start_voice_activation(activation_callback)
        print("Voice activation started. Say 'ok Captain' to activate.")
    except Exception as e:
        print(f"Failed to start voice activation: {e}")
    
    thread1 = threading.Thread(target=FirstThread, daemon=True)
    thread1.start()
    
    try:
        SecondThread()
    except KeyboardInterrupt:
        stop_voice_activation()
        print("Voice assistant stopped.")
    except Exception as e:
        print(f"Error in main: {e}")
        stop_voice_activation()