from dotenv import load_dotenv
import pathlib
import os
import re
import json
from novel import load_data
from openai import OpenAI

novels = load_data()  # Dict[str, Novel]

if os.path.exists("config.env"):
    try:
        load_dotenv("config.env", override=False)
    except TypeError:
        load_dotenv("config.env")

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=os.getenv("OPENROUTER_API_KEY")
)

def ask_model(path, prompt, category=None):
    p = pathlib.Path(path)

    if p.is_dir():
        websites = sorted([x for x in p.iterdir() if x.is_dir()])
        for website in websites:
            files = sorted([x for x in website.iterdir() if x.is_file() and x.suffix.lower() == ".json"]) 
            part_response = []
            for f in files:
                print(f"  Sending {f} to model...")
                file_text = f.read_text(encoding="utf-8")
                response = client.chat.completions.create(
                    model="stepfun/step-3.5-flash:free",
                    messages=[
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": file_text},
                    ],
                )
                part_response.append(response.choices[0].message.content)
    
            save_response("\n".join(part_response), category, f"{website.name}.json")

def save_response(text, type, filename):
    # Validate each non-empty line matches the exact pattern {title:'', author:'', intro:''}
    pattern = re.compile(r"^title:'(?P<title>.*?)',\s*author:'(?P<author>.*?)',\s*intro:'(?P<intro>.*?)'$")
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
    out_path = pathlib.Path(f'{type}/selected_{filename}')
    out_path.write_text(json.dumps(records, ensure_ascii=False, indent=2))
    print(f"Saved {len(records)} records to {out_path}")


if __name__ == "__main__":
    for type, novel in novels.items():
        ask_model(f"{type}/", novel.prompt, category=type)
