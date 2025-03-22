from gtts import gTTS
from langdetect import detect
from googletrans import Translator
import gradio as gr
import asyncio
import os
import time
import random


os.makedirs("audio", exist_ok=True)


def generate_audio(text, lang="hi"):
    print(text)
    text = asyncio.run(translate_text(text))

    tts = gTTS(text=text, lang=lang, slow=False)

    timestamp = int(time.time())  # Current timestamp
    random_value = random.randint(1000, 9999)
    filename = f"audio/{timestamp}_{random_value}.mp3"

    tts.save(filename)
    return filename


async def translate_text(text, target_lang='hi'):
    detected_lang = detect(text)
    translated_text = text

    if detected_lang != target_lang:
        async with Translator() as translator:
            translated = await translator.translate(text, src=detected_lang, dest=target_lang)
            translated_text = translated.text

    return translated_text
