# test_gtts.py
try:
    from gtts import gTTS
    print("gTTS imported successfully")
except ModuleNotFoundError:
    print("Failed to import gTTS")

