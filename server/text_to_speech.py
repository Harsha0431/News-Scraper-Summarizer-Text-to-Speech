from gtts import gTTS


def generate_audio(text, lang="hi"):
    tts = gTTS(text=text, lang=lang, slow=False)
    tts.save("output.mp3")
    return "output.mp3"
