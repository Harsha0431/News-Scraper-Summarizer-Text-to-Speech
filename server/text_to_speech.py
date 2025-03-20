from gtts import gTTS
from langdetect import detect
from googletrans import Translator
import gradio as gr
import asyncio


def generate_audio(text, lang="hi"):
    text = asyncio.run(translate_text(text))
    tts = gTTS(text=text, lang=lang, slow=False)
    tts.save("output.mp3")
    return "output.mp3"


async def translate_text(text, target_lang='hi'):
    detected_lang = detect(text)
    translated_text = text

    if detected_lang != target_lang:
        async with Translator() as translator:
            translated = await translator.translate(text, src=detected_lang, dest=target_lang)
            translated_text = translated.text

    return translated_text
