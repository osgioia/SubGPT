import argparse
import openai
import re
from dotenv import load_dotenv
import os

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def is_valid_srt(srt_text):
    pattern = r"\d+\n\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\n.+"
    return bool(re.match(pattern, srt_text, re.MULTILINE | re.DOTALL))

def split_srt_by_length(srt_text, max_length=4096):
    parts = []
    current_part = ''
    
    for line in srt_text.splitlines():
        if len(current_part) + len(line) > max_length:
            parts.append(current_part)
            current_part = ''
        current_part += line + '\n'
    
    if current_part:
        parts.append(current_part)
    
    return parts

def translate_with_openai(text, target_language):
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=text,
        max_tokens=100,
        temperature=0.7,
        stop=None,
        n=1,
        temperature=0.7
    )

    translated_text = response.choices[0].text.strip()
    return translated_text

def main(srt_file, target_language, output_file, framerate=24):
    with open(srt_file, 'r', encoding='utf-8') as file:
        srt_text = file.read()

    if not is_valid_srt(srt_text):
        print("El archivo no tiene un formato SRT válido.")
        return

    srt_parts = split_srt_by_length(srt_text)

    translated_parts = []
    for part in srt_parts:
        translated_part = translate_with_openai(part, target_language)
        translated_parts.append(translated_part)

    translated_text = '\n'.join(translated_parts)

    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(translated_text)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Traduce un archivo SRT al idioma especificado usando OpenAI.")
    parser.add_argument("srt_file", help="Ruta al archivo SRT original")
    parser.add_argument("target_language", help="Idioma al que traducir (ej. 'es' para español)")
    parser.add_argument("output_file", help="Ruta donde guardar el archivo SRT traducido")
    parser.add_argument("--framerate", type=float, default=24, help="Framerate del video (por defecto: 24)")
    args = parser.parse_args()

    main(args.srt_file, args.target_language, args.output_file, args.framerate)
