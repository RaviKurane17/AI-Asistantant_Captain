import speech_recognition as sr
import threading
import time
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from Backend.TextToSpeech import TextToSpeech
except ImportError:
    # Fallback if TextToSpeech can't be imported
    def TextToSpeech(text):
        print(f"TTS would say: {text}")

class VoiceActivator:
    def __init__(self, activation_phrase="ok captain", sensitivity=0.7):
        self.activation_phrase = activation_phrase.lower()
        self.sensitivity = sensitivity
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_listening = False
        self.callback_function = None
        
        try:
            # Adjust for ambient noise
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
            print("✅ Microphone initialized successfully")
        except Exception as e:
            print(f"❌ Microphone initialization failed: {e}")
    
    def start_listening(self, callback):
        """Start listening for activation phrase"""
        self.callback_function = callback
        self.is_listening = True
        thread = threading.Thread(target=self._listen_loop)
        thread.daemon = True
        thread.start()
        print("🎧 Voice activation started. Say 'Ok Captain' to activate.")
    
    def stop_listening(self):
        """Stop listening for activation phrase"""
        self.is_listening = False
        print("🔇 Voice activation stopped.")
    
    def _listen_loop(self):
        """Main listening loop"""
        while self.is_listening:
            try:
                with self.microphone as source:
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=2)
                
                # Recognize speech
                text = self.recognizer.recognize_google(audio).lower()
                print(f"🎤 Heard: {text}")
                
                # Check for activation phrase
                if self.activation_phrase in text:
                    print("✅ Activation phrase detected!")
                    try:
                        TextToSpeech("Yes sir? How can I help you?")
                    except Exception as e:
                        print(f"❌ TTS failed: {e}")
                    
                    if self.callback_function:
                        self.callback_function()
                    # Small delay to prevent immediate re-activation
                    time.sleep(2)
                    
            except sr.WaitTimeoutError:
                # No speech detected, continue listening
                continue
            except sr.UnknownValueError:
                # Speech detected but not understandable
                continue
            except sr.RequestError as e:
                print(f"❌ Speech recognition API error: {e}")
                time.sleep(1)
            except Exception as e:
                print(f"❌ Unexpected error in voice activation: {e}")
                time.sleep(1)

# Global activator instance
voice_activator = VoiceActivator()

def start_voice_activation(callback):
    """Start voice activation system"""
    try:
        voice_activator.start_listening(callback)
        return True
    except Exception as e:
        print(f"❌ Failed to start voice activation: {e}")
        return False

def stop_voice_activation():
    """Stop voice activation system"""
    voice_activator.stop_listening()

# Test function
def test_voice_activation():
    """Test the voice activation system"""
    def test_callback():
        print("🎯 Activation callback called!")
    
    print("Testing voice activation...")
    start_voice_activation(test_callback)
    
    # Run for 30 seconds for testing
    time.sleep(30)
    stop_voice_activation()

if __name__ == "__main__":
    test_voice_activation()