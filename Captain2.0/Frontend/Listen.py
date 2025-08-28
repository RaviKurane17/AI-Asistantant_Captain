# def listen_for_wake_word():
#     while True:
#         text = capture_audio()
#         if "ok captain" in text.lower():
#             if ReadMicrophoneStatus() == "False":
#                 # Still muted, but wake word should bypass mute
#                 trigger_assistant()
