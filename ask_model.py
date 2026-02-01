from google import genai
from google.genai import types
from dotenv import load_dotenv
import pathlib
import os
import re
import json
import time

if os.path.exists("config.env"):
    try:
        load_dotenv("config.env", override=False)
    except TypeError:
        load_dotenv("config.env")
client = genai.Client()

def ask_model(path, prompt):
    filepath = pathlib.Path(path)

    response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents=[
        types.Part.from_bytes(
            data=filepath.read_bytes(),
            mime_type='application/json',
        ),
        prompt
    ]
    )
    return response.text

def save_response(text, type):
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
        print('No file written. Please ensure the model output strictly uses the format {title:\'..\', author:\'..\', intro:\'..\'} with single quotes as shown.')
    else:
        out_path = pathlib.Path(f'selected_novels_{type}.json')
        out_path.write_text(json.dumps(records, ensure_ascii=False, indent=2))
        print(f"Saved {len(records)} records to {out_path}")

def main(type, prompt):
    path = f"./novels_{type}.json"
    response_text = ask_model(path, prompt)
    print("Model response received. Processing...")
    save_response(response_text, type)

if __name__ == "__main__":
    gb_prompt = "筛选出所有gb小说，将标题、作者、简介提取出来，每行为一条记录，格式为{title:'', author:'', intro:''}，不要包含其他内容。"
    main("gb", gb_prompt)
    time.sleep(60)
    mq_prompt = "筛选出所有攻受属性为美强、强强的小说，将标题、作者、简介提取出来，每行为一条记录，格式为{title:'', author:'', intro:''}，不要包含其他内容。"
    main("mq", mq_prompt)