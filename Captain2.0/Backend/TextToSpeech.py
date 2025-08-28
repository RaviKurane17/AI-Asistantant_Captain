import pygame
import random
import asyncio
import edge_tts
import os
from dotenv import dotenv_values

env_vars = dotenv_values(".env")
# Change this to an Indian male voice
AssistantVoice = env_vars.get("AssistantVoice", "en-GB-ThomasNeural")  # Indian male voice

async def TextToAudioFile(text) -> None:
    file_path = r"Data\speech.mp3"

    if os.path.exists(file_path):
        os.remove(file_path)

    # Use Indian male voice with appropriate settings
    communicate = edge_tts.Communicate(
        text, 
        AssistantVoice, 
        pitch='+0Hz',    # Neutral pitch for male voice
        rate='+0%'       # Normal speaking rate
    )
    await communicate.save(r"Data\speech.mp3")

def TTS(Text, func=lambda r=None: True):
    while True:
        try:
            asyncio.run(TextToAudioFile(Text))

            pygame.mixer.init()

            pygame.mixer.music.load(r"Data\speech.mp3")
            pygame.mixer.music.play()

            clock = pygame.time.Clock()

            while pygame.mixer.music.get_busy():
                if not func():
                    break
                clock.tick(10)

            return True
        except Exception as e:
            print(f"Error in TTS : {e}")

        finally:
            try:
                func(False)
                pygame.mixer.music.stop()
                pygame.mixer.quit()
            except Exception as e:
                print(f"Error in finally block: {e}")

def TextToSpeech(Text, func=lambda r=None: True):
    Data = str(Text).split(".")

    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out sir.",
        "The rest of the text is now on the chat screen, sir, please check it.",
        "You can see the rest of the text on the chat screen, sir.",
        "The remaining part of the text is now on the chat screen, sir.",
        "Sir, you'll find more text on the chat screen for you to see.",
        "The rest of the answer is now on the chat screen, sir.",
        "Sir, please look at the chat screen, the rest of the answer is there.",
        "You'll find the complete answer on the chat screen, sir.",
        "The next part of the text is on the chat screen, sir.",
        "Sir, please check the chat screen for more information.",
        "There's more text on the chat screen for you, sir.",
        "Sir, take a look at the chat screen for additional text.",
        "You'll find more to read on the chat screen, sir.",
        "Sir, check the chat screen for the rest of the text.",
        "The chat screen has the rest of the text, sir.",
        "There's more to see on the chat screen, sir, please look.",
        "Sir, the chat screen holds the continuation of the text.",
        "You'll find the complete answer on the chat screen, kindly check it out sir.",
        "Please review the chat screen for the rest of the text, sir.",
        "Sir, look at the chat screen for the complete answer."
    ]

    if len(Data) > 4 and len(Text) >= 200:
        TTS(" ".join(Text.split(".")[:20]) + "." + random.choice(responses), func)
    else:
        TTS(Text, func)

# List of available Indian voices for reference
INDIAN_VOICES = {
    "male": [
        "en-IN-PrabhatNeural",      # Indian male voice - Prabhat
        "en-IN-SameerNeural",       # Indian male voice - Sameer
        "hi-IN-MadhurNeural",       # Hindi male voice - Madhur
        "hi-IN-SwaraNeural",        # Hindi female voice - Swara (alternative)
    ],
    "female": [
        "en-IN-NeerjaNeural",       # Indian female voice - Neerja
        "en-IN-AashiNeural",        # Indian female voice - Aashi
    ]
}

def list_available_voices():
    """List all available edge-tts voices"""
    try:
        voices = asyncio.run(edge_tts.list_voices())
        indian_voices = [v for v in voices if 'IN' in v['ShortName']]
        
        print("Available Indian voices:")
        for voice in indian_voices:
            gender = "Male" if "Male" in voice['Gender'] else "Female"
            print(f"{voice['ShortName']} - {voice['LocalName']} ({gender})")
        
        return indian_voices
    except Exception as e:
        print(f"Error listing voices: {e}")
        return []

if __name__ == "__main__":
    # List available Indian voices
    print("Available Indian voices:")
    indian_voices = list_available_voices()
    
    # Test the current voice
    print(f"\nTesting current voice: {AssistantVoice}")
    TextToSpeech("Hello, I am Captain. I am your AI assistant with an Indian accent.")
    
    # Interactive test
    while True:
        try:
            text = input("\nEnter text to speak (or 'quit' to exit): ")
            if text.lower() in ['quit', 'exit', 'bye']:
                break
            TextToSpeech(text)
        except KeyboardInterrupt:
            break
    print("Text-to-speech test completed.")