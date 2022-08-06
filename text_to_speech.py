from gtts import gTTS
from playsound import playsound
import os


def tts(text):
    os.remove('1.mp3')
    lang = 'ru'
    obj = gTTS(text=text, lang=lang, slow=False)
    obj.save("1.mp3")
    playsound("1.mp3")
