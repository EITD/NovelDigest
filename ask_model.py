from dotenv import load_dotenv
import pathlib
import os
import re
import json

from novel import load_data
from model import get_model_client
from model.base import ModelClient

novels = load_data()  # Dict[str, Novel]

if os.path.exists("config.env"):
    try:
        load_dotenv("config.env", override=False)
    except TypeError:
        load_dotenv("config.env")


def ask_model(path: str, prompt: str) -> None:
    type = pathlib.Path(path)
    if not type.is_dir():
        return

    model = get_model_client()
    output_category = type.name

    websites = sorted([x for x in type.iterdir() if x.is_dir()])
    if websites:
        for website in websites:
            files = sorted([x for x in website.iterdir() if x.is_file() and x.suffix.lower() == ".json"])
            part_response = []
            for f in files:
                print(f"  Sending {f} to model...")
                file_text = f.read_text(encoding="utf-8")
                part_response.append(model.generate(prompt, file_text))
            save_response("\n".join(part_response), output_category, f"{website.name}.json")
        return


def save_response(text: str, category: str, filename: str) -> None:
    # Only support: title:'', author:'', intro:''
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
            continue

        records.append(
            {
                "title": m.group("title"),
                "author": m.group("author"),
                "intro": m.group("intro"),
            }
        )

    if errors:
        print("Format check failed for the following lines (line number: content):")
        for ln, content in errors:
            print(f"{ln}: {content}")

    out_path = pathlib.Path(f"{category}/selected_{filename}")
    out_path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved {len(records)} records to {out_path}")


if __name__ == "__main__":
    for category, novel in novels.items():
        ask_model(f"{category}/", novel.prompt)
