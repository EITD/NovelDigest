from google import genai
from google.genai import types
from dotenv import load_dotenv
import pathlib
import os
import re
import json
import time
from novel import load_data

novels = load_data()  # Dict[str, Novel]

if os.path.exists("config.env"):
    try:
        load_dotenv("config.env", override=False)
    except TypeError:
        load_dotenv("config.env")
client = genai.Client()

def ask_model(path, prompt):
    p = pathlib.Path(path)

    if p.is_dir():
        files = sorted([x for x in p.iterdir() if x.is_file() and x.suffix.lower() == ".json"])
        for f in files:
            print(f"  Sending {f} to model...")
            resp = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=[
                    types.Part.from_bytes(
                        data=f.read_bytes(),
                        mime_type='application/json',
                    ),
                    prompt,
                ],
            )
            save_response(resp.text, type, f.name)
            time.sleep(60)

def save_response(text, type, filename):
    # Validate each non-empty line matches the exact pattern {title:'', author:'', intro:''}
    pattern = re.compile(r"^\{title:'(?P<title>.*?)',\s*author:'(?P<author>.*?)',\s*intro:'(?P<intro>.*?)'\}$")
    records = []
    errors = []
    for idx, line in enumerate(text.splitlines(), start=1):
        s = line.strip()
        if not s:
            continue
        m = pattern.match(s)
        if not m:
            errors.append((idx, s))
        else:
            records.append({
            'title': m.group('title'),
            'author': m.group('author'),
            'intro': m.group('intro'),
            })

    if errors:
        print('Format check failed for the following lines (line number: content):')
        for ln, content in errors:
            print(f"{ln}: {content}")
        print('No file written. Please ensure the model output strictly uses the json format for records.')
    else:
        out_path = pathlib.Path(f'{type}/selected_{filename}')
        out_path.write_text(json.dumps(records, ensure_ascii=False, indent=2))
        print(f"Saved {len(records)} records to {out_path}")


if __name__ == "__main__":
    for type, novel in novels.items():
        response_text = ask_model(f"{type}/", novel.prompt)