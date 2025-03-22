from gtts import gTTS
from langdetect import detect
from googletrans import Translator
import gradio as gr
import asyncio
import os
import time
import random

AUDIO_DIR = "audio"
os.makedirs(AUDIO_DIR, exist_ok=True)


def clean_old_audio(max_age_seconds=7200):  # 2 hour
    """Removes audio files older than max_age_seconds."""
    now = time.time()
    for filename in os.listdir(AUDIO_DIR):
        if filename.endswith(".mp3"):
            filepath = os.path.join(AUDIO_DIR, filename)
            try:
                timestamp = int(filename.split("_")[0])
                if now - timestamp > max_age_seconds:
                    os.remove(filepath)
            except (ValueError, IndexError):
                print(f"Skipping file with invalid name: {filename}")


def generate_audio(text, lang="hi"):
    try:
        text = asyncio.run(translate_text(text, lang))
        tts = gTTS(text, lang=lang)
        timestamp = int(time.time())  # Current timestamp
        random_value = random.randint(1000, 9999)
        filename = f"{AUDIO_DIR}/{timestamp}_{random_value}.mp3"
        tts.save(filename)
        return filename
    except Exception as e:
        print(f"Error generating audio: {e}")
        return "failed_hi.mp3" if lang == "hi" else "failed_en.mp3"


async def translate_text(text, target_lang='hi'):
    try:
        detected_lang = detect(text)
        translated_text = text

        if detected_lang != target_lang:
            async with Translator() as translator:
                translated = await translator.translate(text, src=detected_lang, dest=target_lang)
                translated_text = translated.text

        return translated_text

    except Exception as e:
        print(f"Translation error: {e}")
        return text
